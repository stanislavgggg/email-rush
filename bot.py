"""
bot.py — Cherry Rush (email-capture focus)
Commands: /start /policy /lang
All other interactions push the user to open the Mini App.
"""
import asyncio, logging, os, sys, atexit
from telegram import Update
from telegram.error import Conflict, NetworkError
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.constants import ParseMode
from config import BOT_TOKEN, BOT_USERNAME, HOOK_IMAGE, State, TG_LANG_MAP, DEFAULT_LANG
from brand import BRAND
from storage import get_user, update_user, append_history
from conversation import (
    handle_message, handle_menu_action, main_menu,
    send_channel_join, handle_join_check, JOIN_CHECK_CB,
    handle_news, handle_news_callback, NEWS_CB_PREFIX,
)
from messages import HOOK_CAPTION
from media import send_pic
import analytics

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

LOCK_FILE = "/tmp/metaplay_bot.lock"

def _check_lock():
    if os.path.exists(LOCK_FILE):
        try:
            pid = int(open(LOCK_FILE).read().strip())
            os.kill(pid, 0)
            logger.critical(f"Already running (PID {pid}). Exiting.")
            sys.exit(1)
        except (ProcessLookupError, ValueError):
            os.remove(LOCK_FILE)
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))
    atexit.register(lambda: os.path.exists(LOCK_FILE) and os.remove(LOCK_FILE))

_check_lock()

def _detect_lang(code):
    if not code:
        return DEFAULT_LANG
    return TG_LANG_MAP.get(code.split("-")[0].lower(), DEFAULT_LANG)


# ── Privacy footer ────────────────────────────────────────────────────────────

PRIVACY_URL = (BRAND.privacy_url or "").strip()
_SHOW_PRIVACY = bool(PRIVACY_URL) and "your_channel" not in PRIVACY_URL.lower() and ".example." not in PRIVACY_URL.lower()
_PRIV_LABEL = {"en": "Privacy Policy", "es": "Política de Privacidad", "ru": "Политика конфиденциальности"}

def _priv_md(lang):
    return f"\n[{_PRIV_LABEL.get(lang, _PRIV_LABEL['en'])}]({PRIVACY_URL})" if _SHOW_PRIVACY else ""

START_LEGAL_FOOTER = {
    "en": f"\n\n———\n18+ · Informational only, not betting/financial advice.{_priv_md('en')}",
    "es": f"\n\n———\n18+ · Solo información, no es asesoramiento de apuestas/financiero.{_priv_md('es')}",
    "ru": f"\n\n———\n18+ · Только информация, не беттинг/финансовый совет.{_priv_md('ru')}",
}


# ── /start ────────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user    = update.effective_user
    chat_id = update.effective_chat.id
    detected = _detect_lang(user.language_code)
    u_check  = get_user(user.id, detected)
    lang = (u_check.get("lang", detected) if u_check.get("lang_manual") else detected)

    is_new = u_check.get("message_count", 0) == 0
    if is_new:
        update_user(user.id, lang=lang, state=State.NEW,
                    onboarding_done=False, onboarding_turn=0, stage_replies=0)
    else:
        update_user(user.id, lang=lang)

    caption = HOOK_CAPTION.get(lang, HOOK_CAPTION["en"])
    caption += START_LEGAL_FOOTER.get(lang, START_LEGAL_FOOTER["en"])
    menu = main_menu(lang)

    sent = await send_pic(context.bot, chat_id, "start", caption, lang, reply_markup=menu)
    if not sent and os.path.exists(HOOK_IMAGE):
        try:
            with open(HOOK_IMAGE, "rb") as p:
                await context.bot.send_photo(
                    chat_id=chat_id, photo=p,
                    caption=caption, parse_mode=ParseMode.MARKDOWN,
                    reply_markup=menu,
                )
            sent = True
        except Exception as e:
            logger.warning(f"Hook image fallback: {e}")
    if not sent:
        await context.bot.send_message(
            chat_id=chat_id, text=caption,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=menu,
        )

    append_history(user.id, "assistant", caption)
    logger.info(f"/start user={user.id} lang={lang}")


# ── /lang ─────────────────────────────────────────────────────────────────────

async def cmd_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    arg = (context.args[0].lower() if context.args else "")
    valid = ("en", "ru", "es")
    if arg in valid:
        update_user(user.id, lang=arg, lang_manual=True)
        msg = {
            "en": "✅ Language set to English.",
            "ru": "✅ Язык переключён на русский.",
            "es": "✅ Idioma cambiado a español.",
        }[arg]
        await update.message.reply_text(msg)
    else:
        cur = get_user(user.id).get("lang", _detect_lang(user.language_code))
        await update.message.reply_text(
            f"🌐 Current language: {cur.upper()}\n"
            "Usage: /lang en · /lang ru · /lang es"
        )


# ── /policy ───────────────────────────────────────────────────────────────────

async def cmd_policy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u    = get_user(update.effective_user.id)
    lang = u.get("lang", _detect_lang(update.effective_user.language_code))
    if lang == "ru":
        text = (
            "🔒 *Политика конфиденциальности*\n\n"
            f"{BRAND.display_name} собирает только email и Telegram ID для рассылки.\n"
            "Платёжные данные не собираются. Отписка — в любой момент.\n\n"
            + (f"[Читать полностью →]({PRIVACY_URL})" if _SHOW_PRIVACY else "")
        )
    elif lang == "es":
        text = (
            "🔒 *Política de Privacidad*\n\n"
            f"{BRAND.display_name} recopila solo email e ID de Telegram para el envío.\n"
            "No almacenamos datos de pago. Podés darte de baja en cualquier momento.\n\n"
            + (f"[Leer política completa →]({PRIVACY_URL})" if _SHOW_PRIVACY else "")
        )
    else:
        text = (
            "🔒 *Privacy Policy*\n\n"
            f"{BRAND.display_name} collects only your email and Telegram ID for the newsletter.\n"
            "No payment data stored. Unsubscribe anytime.\n\n"
            + (f"[Read full policy →]({PRIVACY_URL})" if _SHOW_PRIVACY else "")
        )
    await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)


# ── Text messages ─────────────────────────────────────────────────────────────

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (update.message.text or "").strip()
    if not text:
        return
    u    = get_user(user.id)
    lang = u.get("lang", _detect_lang(user.language_code))
    try:
        await handle_message(context.bot, user.id, update.effective_chat.id, text, lang)
    except Exception as e:
        logger.error(f"handle_text crashed user={user.id}: {e}", exc_info=True)
        err = "⚠️ Algo salió mal — intentá de nuevo." if lang == "es" else "⚠️ Something went wrong — try again."
        try:
            await update.message.reply_text(err)
        except Exception:
            pass


# ── Callbacks (стабы для совместимости) ──────────────────────────────────────

async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    user = update.effective_user
    u    = get_user(user.id)
    lang = u.get("lang", _detect_lang(user.language_code))
    try:
        await query.answer()
    except Exception:
        pass
    # All callbacks now just re-open CTA
    from conversation import _send_cta
    await _send_cta(context.bot, update.effective_chat.id, lang)


# ── /funnel (admin) ───────────────────────────────────────────────────────────

def _admin_ids():
    raw = os.environ.get("ADMIN_IDS", "")
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


async def cmd_funnel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in _admin_ids():
        return
    snap = analytics.snapshot()
    f, r = snap["funnel"], snap["rates"]
    lines = ["📊 *Funnel*", ""]
    for k in ("cta_view", "cta_tap", "channel_open", "membership_check", "join_confirmed"):
        lines.append(f"{k}: {f.get(k, 0)}")
    lines.append("")
    lines.append(f"unique joins: {snap['unique_joins']}")
    def _r(v): return f"{v}%" if v is not None else "—"
    lines.append(f"tap/view: {_r(r['tap_per_view'])}")
    lines.append(f"join/tap: {_r(r['join_per_tap'])}")
    lines.append(f"join/view: {_r(r['join_per_view'])}")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


# ── Post-init ─────────────────────────────────────────────────────────────────

async def post_init(application: Application):
    from telegram import BotCommand
    await application.bot.set_my_commands([
        BotCommand("start",  "Start / reset"),
        BotCommand("policy", "Privacy policy"),
        BotCommand("lang",   "Language: en / ru / es"),
    ])
    logger.info(f"{BRAND.display_name} bot started (email-capture mode)")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start",  cmd_start))
    app.add_handler(CommandHandler("policy", cmd_policy))
    app.add_handler(CommandHandler("lang",   cmd_lang))
    app.add_handler(CommandHandler("funnel", cmd_funnel))
    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    logger.info(f"Starting {BOT_USERNAME}...")

    async def _error_handler(update, context):
        if isinstance(context.error, (Conflict, NetworkError)):
            logger.warning(f"Recoverable error: {context.error}")
            return
        logger.exception(context.error)

    app.add_error_handler(_error_handler)
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
