"""
conversation.py — Cherry Rush (email-capture, CRO-optimised)

Флоу предельно прямой:
  /start → картинка + hook-caption + ОДНА inline-кнопка «Открыть» → мини-апп
  Любой текст → короткий nudge + та же кнопка

Онбординг убран полностью. Топики выбираются в мини-аппе.
"""
import asyncio
import logging
import os

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.constants import ParseMode

from config import State
from media import send_pic, sanitize_markdown
from storage import get_user, update_user, append_history
import emailcfg

logger = logging.getLogger(__name__)

# ── Mini App URL ──────────────────────────────────────────────────────────────
MINI_APP_URL: str = (
    os.environ.get("MINI_APP_URL", "").rstrip("/")
    or emailcfg.PUBLIC_API_BASE.rstrip("/")
)

# ── Import copy ───────────────────────────────────────────────────────────────
from messages import (
    HOOK_CAPTION, NUDGE, ALREADY_SUBSCRIBED, GENERIC_FALLBACK, OPEN_APP_BTN,
)

# Стабы для bot.py импортов (он всё ещё их импортирует)
JOIN_CHECK_CB  = "cb_join_check"
NEWS_CB_PREFIX = "cb_news_"


# ── Keyboard helpers ──────────────────────────────────────────────────────────

def _open_btn(lang: str) -> InlineKeyboardMarkup:
    """Единственная кнопка воронки — открывает мини-апп WebApp."""
    label = OPEN_APP_BTN.get(lang, OPEN_APP_BTN["en"])
    if MINI_APP_URL:
        btn = InlineKeyboardButton(label, web_app=WebAppInfo(url=MINI_APP_URL))
    else:
        # Fallback на обычную ссылку если MINI_APP_URL не задан
        btn = InlineKeyboardButton(label, url="https://t.me")
        logger.warning("MINI_APP_URL not set — falling back to plain URL")
    return InlineKeyboardMarkup([[btn]])


def main_menu(lang: str) -> InlineKeyboardMarkup:
    """Используется в bot.py как reply_markup — отдаём ту же inline-кнопку."""
    return _open_btn(lang)


# ── Send helpers ──────────────────────────────────────────────────────────────

def _typing_delay(text: str) -> float:
    return round(0.6 + min(len(text) / 200, 1.5), 1)


async def _send(bot: Bot, chat_id: int, text: str, lang: str, inline=None):
    await bot.send_chat_action(chat_id, "typing")
    await asyncio.sleep(_typing_delay(text))
    await bot.send_message(
        chat_id=chat_id,
        text=sanitize_markdown(text),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=inline or _open_btn(lang),
        disable_web_page_preview=True,
    )


# ── Main message handler ──────────────────────────────────────────────────────

async def handle_message(bot: Bot, user_id: int, chat_id: int, text: str, lang: str):
    u     = get_user(user_id, lang)
    state = u.get("state", State.NEW)

    update_user(user_id, message_count=u.get("message_count", 0) + 1)
    append_history(user_id, "user", text)

    # Уже подписан — короткое подтверждение
    if state in (State.DEPOSITED, State.REPEAT):
        msg = ALREADY_SUBSCRIBED.get(lang, ALREADY_SUBSCRIBED["en"])
        await _send(bot, chat_id, msg, lang, inline=_open_btn(lang))
        return

    # Любой текст → nudge + кнопка
    nudge = NUDGE.get(lang, NUDGE["en"])
    append_history(user_id, "assistant", nudge)
    await _send(bot, chat_id, nudge, lang)


# ── Stub handlers (импортируются в bot.py) ────────────────────────────────────

async def handle_menu_action(bot, user_id, chat_id, lang, action):
    await _send(bot, chat_id, NUDGE.get(lang, NUDGE["en"]), lang)


async def send_channel_join(bot, chat_id, lang):
    await _send(bot, chat_id, NUDGE.get(lang, NUDGE["en"]), lang)


async def handle_join_check(bot, user_id, chat_id, lang):
    await _send(bot, chat_id, NUDGE.get(lang, NUDGE["en"]), lang)
    return False


async def handle_news(bot, user_id, chat_id, lang, category=None):
    await _send(bot, chat_id, NUDGE.get(lang, NUDGE["en"]), lang)


async def handle_news_callback(bot, user_id, chat_id, lang, data):
    await _send(bot, chat_id, NUDGE.get(lang, NUDGE["en"]), lang)
