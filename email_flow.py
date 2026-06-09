"""
email_flow.py — collect email INSIDE the bot chat (same core as the landing).

Telegram never hands you a user's email, so we ask for it explicitly with a
proper opt-in: show the consent text → user taps "I'm 18+ & agree" → user types
their email → we create a pending contact and send the double-opt-in mail.

Wiring (in bot.py):
    from email_flow import build_email_conversation
    app.add_handler(build_email_conversation(_detect_lang))
and add a button/command somewhere that triggers /subscribe.
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ContextTypes, ConversationHandler, CommandHandler,
                          CallbackQueryHandler, MessageHandler, filters)

import capture
import emailcfg

logger = logging.getLogger(__name__)
ASK_EMAIL = 1

_PROMPT = {
    "en": "Want {b} promos & drops by email too? Pick your topics in the app, or just tap below.",
    "ru": "Хочешь промо и дропы {b} ещё и на почту? Темы выберешь в приложении, или просто жми ниже.",
    "es": "¿Quieres promos y novedades de {b} también por email? Elige temas en la app, o pulsa abajo.",
}
_AGREE = {"en": "✅ I'm 18+ & agree", "ru": "✅ Мне 18+, согласен", "es": "✅ Soy 18+ y acepto"}
_CANCEL = {"en": "Cancel", "ru": "Отмена", "es": "Cancelar"}
_ASK = {"en": "Great — send me your email address.",
        "ru": "Отлично — пришли свой email.",
        "es": "Genial — envíame tu email."}
_BAD = {"en": "That doesn't look like an email. Try again, or /cancel.",
        "ru": "Это не похоже на email. Попробуй ещё раз или /cancel.",
        "es": "Eso no parece un email. Inténtalo de nuevo o /cancel."}
_DONE = {"en": "Check your inbox ✉️ and tap the confirm link to finish.",
         "ru": "Проверь почту ✉️ и нажми ссылку подтверждения.",
         "es": "Revisa tu correo ✉️ y pulsa el enlace de confirmación."}
_GEO = {"en": "Email signup isn't available in your region right now.",
        "ru": "Подписка по email сейчас недоступна в твоём регионе.",
        "es": "El registro por email no está disponible en tu región ahora."}
_OK = {"en": "No problem.", "ru": "Без проблем.", "es": "Sin problema."}


def build_email_conversation(detect_lang):
    async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        lang = detect_lang(update.effective_user.language_code)
        ctx.user_data["lang"] = lang
        consent = emailcfg.CONSENT_TEXT.get(lang, emailcfg.CONSENT_TEXT["en"])
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(_AGREE.get(lang, _AGREE["en"]), callback_data="email_agree")],
            [InlineKeyboardButton(_CANCEL.get(lang, _CANCEL["en"]), callback_data="email_cancel")],
        ])
        await update.effective_message.reply_text(
            f"{_PROMPT.get(lang, _PROMPT['en']).format(b=emailcfg.BRAND_NAME)}\n\n_{consent}_",
            reply_markup=kb, parse_mode="Markdown", disable_web_page_preview=True)
        return ASK_EMAIL

    async def agree(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()
        lang = ctx.user_data.get("lang", "en")
        ctx.user_data["consent"] = True
        await q.edit_message_text(_ASK.get(lang, _ASK["en"]))
        return ASK_EMAIL

    async def got_email(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        lang = ctx.user_data.get("lang", "en")
        if not ctx.user_data.get("consent"):
            return await start(update, ctx)
        email = (update.message.text or "").strip()
        code, data = await capture.subscribe(dict(
            email=email, consent=True, lang=lang,
            verticals=ctx.user_data.get("verticals", []),
            source="bot_chat", wrapper=emailcfg.WRAPPER,
            tg_id=update.effective_user.id,
            country=ctx.user_data.get("country", ""),
        ))
        if data.get("error") == "invalid_email":
            await update.message.reply_text(_BAD.get(lang, _BAD["en"]))
            return ASK_EMAIL
        if data.get("error") == "geo_restricted":
            await update.message.reply_text(_GEO.get(lang, _GEO["en"]))
            return ConversationHandler.END
        await update.message.reply_text(_DONE.get(lang, _DONE["en"]))
        return ConversationHandler.END

    async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        lang = ctx.user_data.get("lang", "en")
        msg = update.callback_query.message if update.callback_query else update.message
        if update.callback_query:
            await update.callback_query.answer()
        await msg.reply_text(_OK.get(lang, _OK["en"]))
        return ConversationHandler.END

    return ConversationHandler(
        entry_points=[CommandHandler("subscribe", start)],
        states={ASK_EMAIL: [
            CallbackQueryHandler(agree, pattern="^email_agree$"),
            CallbackQueryHandler(cancel, pattern="^email_cancel$"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, got_email),
        ]},
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False,
    )
