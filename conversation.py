"""
conversation.py — Cherry Rush (email capture focus)

TWO LAYERS:

LAYER 1 — ONBOARDING (first 2 exchanges)
  Step 0: topic preference (crypto / football / esports / industry)
  Step 1: confirm → open Mini App to submit email

LAYER 2 — ASSISTANT (post-onboarding)
  Answers questions, always nudges to Mini App for email signup

No live-scores, no news feed, no channel subscription.
The only CTA is opening the Mini App.
"""
import asyncio, logging, os
from telegram import Bot, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from telegram.constants import ParseMode
from config import State
from storage import get_user, update_user, append_history
from ai_agent import get_ai_response
from onboarding import process_onboarding_answer
from media import send_pic, sanitize_markdown
import emailcfg

logger = logging.getLogger(__name__)

# ── Mini App URL ──────────────────────────────────────────────────────────────
# Falls back to PUBLIC_API_BASE (same deployment) or env override
MINI_APP_URL = os.environ.get("MINI_APP_URL", "").rstrip("/") or \
               emailcfg.PUBLIC_API_BASE.rstrip("/")


# ── Persistent menu ───────────────────────────────────────────────────────────

def main_menu(lang: str) -> ReplyKeyboardMarkup:
    """Single persistent button that opens the Mini App."""
    label = {
        "ru": "🍒 Подписаться на письма",
        "es": "🍒 Suscribirse al email",
    }.get(lang, "🍒 Get the email feed")

    btn = KeyboardButton(
        text=label,
        web_app=WebAppInfo(url=MINI_APP_URL) if MINI_APP_URL else None,
    ) if MINI_APP_URL else KeyboardButton(text=label)

    return ReplyKeyboardMarkup([[btn]], resize_keyboard=True)


def _open_app_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Inline button that opens the Mini App WebApp."""
    label = {
        "ru": "🍒 Открыть и подписаться",
        "es": "🍒 Abrir y suscribirse",
    }.get(lang, "🍒 Open & subscribe — free")

    if MINI_APP_URL:
        btn = InlineKeyboardButton(label, web_app=WebAppInfo(url=MINI_APP_URL))
    else:
        btn = InlineKeyboardButton(label, url=MINI_APP_URL or "https://t.me")

    return InlineKeyboardMarkup([[btn]])


# ── CTA copy ──────────────────────────────────────────────────────────────────

_CTA_TEXT = {
    "en": (
        "🔑 *Set up your email feed*\n\n"
        "Pick topics below in the app — we send only what you follow.\n"
        "No noise, no advice, no hidden catches.\n\n"
        "👇 Tap to open and drop your email:"
    ),
    "ru": (
        "🔑 *Настройте ленту на почту*\n\n"
        "Выберите темы прямо в приложении — отправляем только то, за чем следишь.\n"
        "Без шума, советов и скрытых условий.\n\n"
        "👇 Нажми, чтобы открыть и указать email:"
    ),
    "es": (
        "🔑 *Configurá tu feed por email*\n\n"
        "Elegí temas en la app — te enviamos solo lo que seguís.\n"
        "Sin ruido, sin consejos, sin letra chica.\n\n"
        "👇 Tocá para abrir y dejar tu email:"
    ),
}

_GENERIC_FALLBACK = {
    "en": "🍒 Tap the button below to subscribe — it only takes a second.",
    "ru": "🍒 Нажми кнопку ниже, чтобы подписаться — займёт секунду.",
    "es": "🍒 Tocá el botón para suscribirte — es un segundo.",
}


# ── Send helpers ──────────────────────────────────────────────────────────────

def _delay(text: str) -> float:
    return round(1.0 + min(len(text) / 160, 2.0), 1)


async def _send(bot: Bot, chat_id: int, text: str, lang: str, inline=None):
    await bot.send_chat_action(chat_id, "typing")
    await asyncio.sleep(_delay(text))
    await bot.send_message(
        chat_id=chat_id,
        text=sanitize_markdown(text),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=inline or main_menu(lang),
        disable_web_page_preview=True,
    )


async def _send_cta(bot: Bot, chat_id: int, lang: str):
    """Send the Mini App open button with copy."""
    text = _CTA_TEXT.get(lang, _CTA_TEXT["en"])
    sent = await send_pic(bot, chat_id, "cta", text, lang,
                          reply_markup=_open_app_keyboard(lang))
    if not sent:
        await _send(bot, chat_id, text, lang, inline=_open_app_keyboard(lang))


# ── Main message handler ──────────────────────────────────────────────────────

async def handle_message(bot: Bot, user_id: int, chat_id: int, text: str, lang: str):
    u = get_user(user_id, lang)
    onboarding_done = u.get("onboarding_done", False)
    onboarding_step = u.get("onboarding_turn", 0)
    state = u.get("state", State.NEW)

    update_user(user_id, message_count=u.get("message_count", 0) + 1)
    append_history(user_id, "user", text)

    # ── Onboarding: 2 steps, then open app ───────────────────────────────────
    if not onboarding_done:
        await _run_onboarding(bot, user_id, chat_id, text, lang, onboarding_step)
        return

    # ── Post-onboarding: always nudge to Mini App ────────────────────────────
    # If user already submitted email (state=DEPOSITED), send a short ack
    if state in (State.DEPOSITED, State.REPEAT):
        ack = {
            "en": "✅ You're already subscribed! Check your inbox for our latest drops.",
            "ru": "✅ Ты уже подписан! Проверь почту — последние дропы уже там.",
            "es": "✅ ¡Ya estás suscripto! Revisá tu inbox — los últimos drops ya están ahí.",
        }
        await _send(bot, chat_id, ack.get(lang, ack["en"]), lang)
        return

    # Let AI respond, then append CTA
    history = u.get("history", [])
    ai = await get_ai_response(
        user_message=text,
        lang=lang,
        state=state,
        history=history,
        barriers=u.get("barriers", []),
        real_live=[],
        real_upcoming=[],
        prefs=u.get("preferences", {}),
    )
    reply = ai.get("text") or _GENERIC_FALLBACK.get(lang, _GENERIC_FALLBACK["en"])
    append_history(user_id, "assistant", reply)
    await _send(bot, chat_id, reply, lang)
    await asyncio.sleep(0.8)
    await _send_cta(bot, chat_id, lang)


# ── Onboarding ────────────────────────────────────────────────────────────────

async def _run_onboarding(bot, user_id, chat_id, text, lang, step):
    next_question, complete = await process_onboarding_answer(user_id, text, step, lang)
    update_user(user_id, onboarding_turn=step + 1)

    if not complete:
        append_history(user_id, "assistant", next_question)
        pic = "onboarding1" if step == 0 else "onboarding2"
        sent = await send_pic(bot, chat_id, pic, next_question, lang)
        if not sent:
            await _send(bot, chat_id, next_question, lang)
    else:
        # Onboarding done → open the Mini App
        update_user(user_id, onboarding_done=True, state=State.BRIDGE)
        append_history(user_id, "assistant", next_question)
        if next_question:
            await _send(bot, chat_id, next_question, lang)
            await asyncio.sleep(1.2)
        await _send_cta(bot, chat_id, lang)


# ── Stub: keep bot.py imports happy ──────────────────────────────────────────

async def handle_menu_action(bot, user_id, chat_id, lang, action):
    """All menu actions now just open the Mini App CTA."""
    await _send_cta(bot, chat_id, lang)


async def send_channel_join(bot, chat_id, lang):
    await _send_cta(bot, chat_id, lang)


async def handle_join_check(bot, user_id, chat_id, lang):
    await _send_cta(bot, chat_id, lang)
    return False


async def handle_news(bot, user_id, chat_id, lang, category=None):
    await _send_cta(bot, chat_id, lang)


async def handle_news_callback(bot, user_id, chat_id, lang, data):
    await _send_cta(bot, chat_id, lang)


JOIN_CHECK_CB = "cb_join_check"
NEWS_CB_PREFIX = "cb_news_"
