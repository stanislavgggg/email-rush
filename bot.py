"""
bot.py — Cherry Rush (email-capture, CRO-optimised)
Commands: /start /policy /lang

Флоу:
  /start → картинка + hook (4 строки) + inline-кнопка «Открыть мини-апп»
  Любой текст → nudge + та же кнопка
  /policy → текст политики конфиденциальности
  /lang → смена языка
"""
import asyncio
import atexit
import logging
import os
import sys

from telegram import Update
from telegram.error import Conflict, NetworkError
from telegram.ext import (
    Application, CallbackQueryHandler, CommandHandler,
    ContextTypes, MessageHandler, filters,
)
from telegram.constants import ParseMode

from brand import BRAND
from config import BOT_TOKEN, BOT_USERNAME, DEFAULT_LANG, HOOK_IMAGE, State, TG_LANG_MAP
from conversation import (
    handle_message, main_menu,
    send_channel_join, handle_join_check, JOIN_CHECK_CB,
    handle_news, handle_news_callback, NEWS_CB_PREFIX,
    _open_btn,
)
from media import send_pic
from messages import HOOK_CAPTION
from storage import append_history, get_user, update_user
import analytics

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
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


def _detect_lang(code: str | None) -> str:
    if not code:
        return DEFAULT_LANG
    return TG_LANG_MAP.get(code.split("-")[0].lower(), DEFAULT_LANG)


# ── Privacy footer ────────────────────────────────────────────────────────────

PRIVACY_URL = (BRAND.privacy_url or "").strip()
_SHOW_PRIVACY = (
    bool(PRIVACY_URL)
    and "your_channel" not in PRIVACY_URL.lower()
    and ".example." not in PRIVACY_URL.lower()
)

_LEGAL = {
    "en": "18+ · Informational only — not betting or financial advice.",
    "ru": "18+ · Только информация — не беттинг/финансовый совет.",
    "es": "18+ · Solo información — no es asesoramiento de apuestas/financiero.",
}

def _legal_footer(lang: str) -> str:
    base = _LEGAL.get(lang, _LEGAL["en"])
    if _SHOW_PRIVACY:
        lbl = {"en": "Privacy Policy", "ru": "Политика", "es": "Privacidad"}.get(lang, "Privacy Policy")
        base += f"\n[{lbl}]({PRIVACY_URL})"
    return f"\n\n———\n{base}"


# ── /start ────────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user    = update.effective_user
    chat_id = update.effective_chat.id

    detected = _detect_lang(user.language_code)
    u_check  = get_user(user.id, detected)

    # Уважаем ручной выбор языка, не затираем его при рестарте
    lang = (
        u_check.get("lang", detected)
        if u_check.get("lang_manual")
        else detected
    )

    # Сбрасываем состояние для новых, не трогаем для возвращающихся
    is_new = u_check.get("message_count", 0) == 0
    if is_new:
        update_user(
            user.id, lang=lang, state=State.NEW,
            onboarding_done=True,   # онбординга нет — сразу готов
            onboarding_turn=0,
        )
    else:
        update_user(user.id, lang=lang, onboarding_done=True)

    caption = HOOK_CAPTION.get(lang, HOOK_CAPTION["en"]) + _legal_footer(lang)
    kb      = _open_btn(lang)

    # Пробуем брендовую картинку (pics/19.png), потом hook.png, потом текст
    sent = await send_pic(context.bot, chat_id, "start", caption, lang, reply_markup=kb)

    if not sent and os.path.exists(HOOK_IMAGE):
        try:
            with open(HOOK_IMAGE, "rb") as p:
                await context.bot.send_photo(
                    chat_id=chat_id, photo=p,
                    caption=caption, parse_mode=ParseMode.MARKDOWN,
                    reply_markup=kb,
                )
            sent = True
        except Exception as e:
            logger.warning(f"hook.png fallback failed: {e}")

    if not sent:
        await context.bot.send_message(
            chat_id=chat_id, text=caption,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=kb,
            disable_web_page_preview=True,
        )

    append_history(user.id, "assistant", caption)
    logger.info(f"/start user={user.id} lang={lang} new={is_new}")


# ── /lang ─────────────────────────────────────────────────────────────────────

async def cmd_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    arg  = (context.args[0].lower() if context.args else "")
    if arg in ("en", "ru", "es"):
        update_user(user.id, lang=arg, lang_manual=True)
        reply = {
            "en": "✅ Language set to English.",
            "ru": "✅ Язык переключён на русский.",
            "es": "✅ Idioma cambiado a español.",
        }[arg]
        await update.message.reply_text(reply)
        logger.info(f"lang set user={user.id} → {arg}")
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
            f"{BRAND.display_name} собирает email и Telegram ID исключительно "
            "для отправки выбранной тобой рассылки.\n"
            "Платёжные данные не хранятся. Отписка — в любой момент по ссылке в письме."
        )
    elif lang == "es":
        text = (
            "🔒 *Política de Privacidad*\n\n"
            f"{BRAND.display_name} recopila tu email e ID de Telegram únicamente "
            "para enviar el newsletter que elegiste.\n"
            "No almacenamos datos de pago. Podés darte de baja en cualquier momento."
        )
    else:
        text = (
            "🔒 *Privacy Policy*\n\n"
            f"{BRAND.display_name} collects your email and Telegram ID solely "
            "to send the newsletter you signed up for.\n"
            "No payment data stored. Unsubscribe anytime via the link in any email."
        )

    if _SHOW_PRIVACY:
        lbl = {"ru": "Читать полностью →", "es": "Leer completo →"}.get(lang, "Read full policy →")
        text += f"\n\n[{lbl}]({PRIVACY_URL})"

    await update.message.reply_text(
        text, parse_mode="Markdown", disable_web_page_preview=True
    )


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
        logger.error(f"handle_text error user={user.id}: {e}", exc_info=True)
        err = {
            "ru": "⚠️ Что-то пошло не так — попробуй ещё раз.",
            "es": "⚠️ Algo salió mal — intentá de nuevo.",
        }.get(lang, "⚠️ Something went wrong — try again.")
        try:
            await update.message.reply_text(err)
        except Exception:
            pass


# ── Callbacks ─────────────────────────────────────────────────────────────────

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
    # Все коллбэки → та же кнопка открытия аппа
    from messages import NUDGE
    nudge = NUDGE.get(lang, NUDGE["en"])
    try:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=nudge,
            reply_markup=_open_btn(lang),
        )
    except Exception as e:
        logger.error(f"on_callback error: {e}")


# ── Admin /funnel ─────────────────────────────────────────────────────────────

def _admin_ids():
    return [int(x.strip()) for x in os.environ.get("ADMIN_IDS", "").split(",") if x.strip()]


async def cmd_funnel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in _admin_ids():
        return
    snap = analytics.snapshot()
    f, r = snap["funnel"], snap["rates"]
    lines = ["📊 *Funnel snapshot*", ""]
    for k in ("cta_view", "cta_tap", "channel_open", "membership_check", "join_confirmed"):
        lines.append(f"{k}: {f.get(k, 0)}")
    lines += [
        "",
        f"unique joins: {snap['unique_joins']}",
        f"tap/view: {r['tap_per_view']}%",
        f"join/tap: {r['join_per_tap']}%",
        f"join/view: {r['join_per_view']}%",
    ]
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


# ── Post-init ─────────────────────────────────────────────────────────────────

async def post_init(application: Application):
    from telegram import BotCommand
    await application.bot.set_my_commands([
        BotCommand("start",  "Start / reset"),
        BotCommand("policy", "Privacy policy"),
        BotCommand("lang",   "Language: en / ru / es"),
    ])
    logger.info(f"{BRAND.display_name} bot ready (email-capture mode)")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start",  cmd_start))
    app.add_handler(CommandHandler("policy", cmd_policy))
    app.add_handler(CommandHandler("lang",   cmd_lang))
    app.add_handler(CommandHandler("funnel", cmd_funnel))
    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    async def _error_handler(update, context):
        if isinstance(context.error, (Conflict, NetworkError)):
            logger.warning(f"Recoverable error: {context.error}")
            return
        logger.exception(context.error)

    app.add_error_handler(_error_handler)
    logger.info(f"Starting {BOT_USERNAME}...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
