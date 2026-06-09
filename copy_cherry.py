"""
copy_cherry.py — копирайт бренда Cherry Rush (азартный слот-вайб + live score, режим КАНАЛ)
============================================================================================
Цель воронки: ПОДПИСКА на Telegram-канал. Не продукт, не ставки.
Персона: «Ruby» + команда из трёх вишен 🍒🍒🍒. Тон бодрый, lucky-streak флёр.

⚠️ TELEGRAM ADS COMPLIANCE (строго):
- «lucky/jackpot» — только ФЛЁР про горячие НОВОСТИ, не реальный азарт;
- только новости и счёт; никаких фин/беттинг-советов;
- не зовём ставить/депозитить/покупать/продавать;
- НИКОГДА не обещаем выигрыш/джекпот/прибыль/доход.

Языки: en (дефолт), ru, es. {url} в CTA_REGISTER = ссылка на канал.
"""
from config import CHANNEL_HANDLE

_RAW_HANDLE = CHANNEL_HANDLE or "@your_channel"
CH = _RAW_HANDLE.replace("_", "\\_")

HOOK_CAPTION = {
    "en": (
        "🍒 *Cherry Rush — hot drops & live scores*\n\n"
        "I'm Ruby, with the Cherry crew 🍒🍒🍒. We line up the freshest headlines and live "
        "scores so you hit the good stuff first:\n\n"
        "• 🍒 breaking drops across crypto, markets, esports & football\n"
        "• 🔴 live scores in real time\n"
        "• ⚡ first alerts before the crowd\n\n"
        "Pure news — no advice, no promises.\n\nWhich topics should we line up for you?"
    ),
    "ru": (
        "🍒 *Cherry Rush — горячие новости и live-счёт*\n\n"
        "Я Ruby, со мной команда вишен 🍒🍒🍒. Выстраиваем самые свежие заголовки и счёт, "
        "чтобы ты ловил лучшее первым:\n\n"
        "• 🍒 свежие дропы по крипте, рынкам, киберспорту и футболу\n"
        "• 🔴 счёт в реальном времени\n"
        "• ⚡ первые алерты раньше всех\n\n"
        "Чистые новости — без советов и обещаний.\n\nКакие темы выстроить для тебя?"
    ),
    "es": (
        "🍒 *Cherry Rush — novedades calientes y resultados en vivo*\n\n"
        "Soy Ruby, con la banda de cerezas 🍒🍒🍒. Alineamos los titulares más frescos y los "
        "resultados para que agarres lo bueno primero:\n\n"
        "• 🍒 novedades de cripto, mercados, esports y fútbol\n"
        "• 🔴 resultados en vivo en tiempo real\n"
        "• ⚡ primeras alertas antes que nadie\n\n"
        "Solo noticias — sin consejos ni promesas.\n\n¿Qué temas alineamos para vos?"
    ),
}

WARMUP_FOOTBALL = {
    "en": [
        "🍒 The drop that lights up a feed usually lands here first.",
        "🔴 Live scores update in real time, no refresh needed.",
        "⚡ Crypto, markets, esports, football — all the hot ones, one feed.",
    ],
    "ru": [
        "🍒 Дроп, который зажигает ленту, обычно прилетает сюда первым.",
        "🔴 Live-счёт обновляется в реальном времени, без перезагрузки.",
        "⚡ Крипта, рынки, киберспорт, футбол — все горячие, одна лента.",
    ],
    "es": [
        "🍒 La novedad que enciende un feed suele caer acá primero.",
        "🔴 Los resultados en vivo se actualizan en tiempo real.",
        "⚡ Cripto, mercados, esports, fútbol — todas las calientes, un feed.",
    ],
}
WARMUP_ESPORTS = WARMUP_FOOTBALL

BRIDGE = {
    "en": (
        "🔑 *Where the full feed drops*\n\n"
        f"The complete feed — instant breaking drops and live-score pushes — runs in the {CH} channel.\n\n"
        "• 🍒 every drop the moment it lands\n"
        "• 🔴 live-score pings for matches you follow\n"
        "• ⚡ first alerts before the crowd\n\n"
        "It's free, and it's news — not advice. Want the link?"
    ),
    "ru": (
        "🔑 *Где сыплется полный фид*\n\n"
        f"Полная лента — мгновенные дропы и пуши со счётом — идёт в канале {CH}.\n\n"
        "• 🍒 каждый дроп в момент выхода\n"
        "• 🔴 пинги со счётом по матчам, за которыми следишь\n"
        "• ⚡ первые алерты раньше толпы\n\n"
        "Бесплатно, и это новости — не советы. Скинуть ссылку?"
    ),
    "es": (
        "🔑 *Dónde cae el feed completo*\n\n"
        f"El feed completo — novedades instantáneas y avisos de resultados — corre en el canal {CH}.\n\n"
        "• 🍒 cada novedad al instante\n"
        "• 🔴 avisos de resultados de los partidos que seguís\n"
        "• ⚡ primeras alertas antes que el resto\n\n"
        "Es gratis, y son noticias — no consejos. ¿Te paso el link?"
    ),
}

CTA_REGISTER = {
    "en": (
        "👇 *Subscribe to the channel — free*\n\n{url}\n\n"
        "Turn on notifications and catch every drop and live score the moment it lands. "
        "News only — no advice, no promises. 🍒"
    ),
    "ru": (
        "👇 *Подписывайся на канал — бесплатно*\n\n{url}\n\n"
        "Включи уведомления — лови каждый дроп и счёт в момент события. "
        "Только новости — без советов и обещаний. 🍒"
    ),
    "es": (
        "👇 *Suscribite al canal — gratis*\n\n{url}\n\n"
        "Activá notificaciones y agarrá cada novedad y resultado al instante. "
        "Solo noticias — sin consejos ni promesas. 🍒"
    ),
}

FTD_CELEBRATION = {
    "en": "🍒 *You're in*\n\nNotifications on so you don't miss a single drop or live-score push.",
    "ru": "🍒 *Ты в деле*\n\nУведомления включены — не пропустишь ни одного дропа и пуша со счётом.",
    "es": "🍒 *Estás adentro*\n\nNotificaciones activadas para no perderte ninguna novedad ni resultado.",
}

REPEAT_PUSH = {
    "en": ["🍒 Today's hottest drops are live in the channel.",
           "🔴 Live scores are rolling — check the channel.",
           "⚡ Notifications off? That's how you miss the hot ones."],
    "ru": ["🍒 Самые горячие дропы дня уже в канале.",
           "🔴 Live-счёт идёт — загляни в канал.",
           "⚡ Уведомления выключены? Так и теряются горячие."],
    "es": ["🍒 Las novedades más calientes del día están en el canal.",
           "🔴 Los resultados en vivo están corriendo — mirá el canal.",
           "⚡ ¿Notificaciones apagadas? Así te perdés las calientes."],
}

BARRIER_FALLBACK = {
    "en": {
        "no_trust": "Fair. Open the channel and read a few posts first — no signup, judge the feed yourself.",
        "not_urgent": "No rush. The channel's free and drops are time-sensitive — that's the only catch.",
        "thinking": "Take your time. Which topics are you most into — crypto, markets, esports or football?",
    },
    "ru": {
        "no_trust": "Справедливо. Открой канал и почитай пару постов — без регистрации, оцени ленту сам.",
        "not_urgent": "Без спешки. Канал бесплатный, а дропы привязаны ко времени — единственный нюанс.",
        "thinking": "Подумай спокойно. Какие темы тебе ближе — крипта, рынки, киберспорт или футбол?",
    },
    "es": {
        "no_trust": "Válido. Abrí el canal y leé algunos posts — sin registro, juzgá el feed vos mismo.",
        "not_urgent": "Sin apuro. El canal es gratis y las novedades dependen del tiempo — ese es el único detalle.",
        "thinking": "Tomate tu tiempo. ¿Qué temas te interesan más — cripto, mercados, esports o fútbol?",
    },
}

GENERIC_FALLBACK = {
    "en": "🍒 Lining up the latest drops — one sec.",
    "ru": "🍒 Выстраиваю свежие дропы — секунду.",
    "es": "🍒 Alineando las últimas novedades — un segundo.",
}

FTD_CONFIRM_PROMPT = {
    "en": "Subscribed? Say yes and I'll line up today's hottest drops.",
    "ru": "Подписался? Скажи «да» — и выстрою главные дропы дня.",
    "es": "¿Te suscribiste? Decí sí y alineo las novedades top de hoy.",
}

MORNING_DIGEST_HEADER = {
    "en": "📅 *Good morning — today's fixtures*\n\n",
    "ru": "📅 *Доброе утро — матчи на сегодня*\n\n",
    "es": "📅 *Buen día — los partidos de hoy*\n\n",
}
MORNING_DIGEST_FOOTER = {
    "en": f"\n\n🍒 Live-score pushes + full feed — in the channel {CH}.",
    "ru": f"\n\n🍒 Пуши со счётом + полный фид — в канале {CH}.",
    "es": f"\n\n🍒 Avisos de resultados + feed completo — en el canal {CH}.",
}

JOIN_PROMPT = {
    "en": "🍒 *Subscribe to the channel*\n\nFull feed, breaking drops and live-score pushes — free. Tap subscribe, then come back and check access. 👇",
    "ru": "🍒 *Подписывайся на канал*\n\nПолный фид, мгновенные дропы и пуши со счётом — бесплатно. Нажми «Подписаться», затем вернись и проверь доступ. 👇",
    "es": "🍒 *Suscribite al canal*\n\nFeed completo, novedades y avisos de resultados — gratis. Tocá suscribirte, después volvé y verificá el acceso. 👇",
}
JOIN_CHECK_BTN = {"en": "✅ I subscribed", "ru": "✅ Я подписался", "es": "✅ Ya me suscribí"}
JOIN_OK = {
    "en": "✅ Done — access unlocked. The full feed is live in the channel.",
    "ru": "✅ Готово — доступ открыт. Полный фид уже в канале.",
    "es": "✅ Listo — acceso desbloqueado. El feed completo está en el canal.",
}
JOIN_NOT_YET = {
    "en": "🔒 Don't see your subscription yet. Join the channel and tap “I subscribed” again.",
    "ru": "🔒 Пока не вижу подписки. Подпишись на канал и нажми «Я подписался» ещё раз.",
    "es": "🔒 Todavía no veo tu suscripción. Unite al canal y tocá «Ya me suscribí» de nuevo.",
}

NEWS_HEADER = {
    "en": "🍒 *Latest — Cherry Rush*\n\n",
    "ru": "🍒 *Свежее — Cherry Rush*\n\n",
    "es": "🍒 *Lo último — Cherry Rush*\n\n",
}
NEWS_EMPTY = {
    "en": "🍒 Feed is spinning up — try again in a moment.",
    "ru": "🍒 Лента раскручивается — попробуй ещё раз через минуту.",
    "es": "🍒 El feed está arrancando — probá de nuevo en un momento.",
}
NEWS_FOOTER = {
    "en": f"\n\n🍒 *This is the preview.* The full feed + instant breaking drops run in the channel {CH}.",
    "ru": f"\n\n🍒 *Это превью.* Полный фид + мгновенные дропы идут в канале {CH}.",
    "es": f"\n\n🍒 *Esto es la vista previa.* El feed completo + novedades instantáneas corren en el canal {CH}.",
}
NEWS_CAT_LABELS = {
    "en": {"all": "🌐 All", "crypto": "₿ Crypto", "casino": "🏦 Industry", "esports": "🎮 Esports"},
    "ru": {"all": "🌐 Все", "crypto": "₿ Крипто", "casino": "🏦 Индустрия", "esports": "🎮 Киберспорт"},
    "es": {"all": "🌐 Todo", "crypto": "₿ Cripto", "casino": "🏦 Industria", "esports": "🎮 Esports"},
}
LIVE_CHANNEL_LINE = {
    "en": f"\n\n🍒 _Live-score pushes for these — in the channel {CH}._",
    "ru": f"\n\n🍒 _Пуши со счётом по этим матчам — в канале {CH}._",
    "es": f"\n\n🍒 _Avisos de resultados de estos — en el canal {CH}._",
}
