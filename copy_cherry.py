"""
copy_cherry.py — Cherry Rush (email-capture focus)
===================================================
Цель воронки: сбор EMAIL через мини-апп.
Персона: «Ruby» + команда из трёх вишен 🍒🍒🍒.

⚠️ TELEGRAM ADS COMPLIANCE:
- Только новости и данные; никаких фин/беттинг-советов.
- Не зовём ставить / депозитить / покупать / продавать.
- Никогда не обещаем выигрыш / прибыль / доход.

Языки: en (дефолт), ru, es.
"""

HOOK_CAPTION = {
    "en": (
        "🍒 *Cherry Rush — hot drops, straight to your inbox*\n\n"
        "I'm Ruby, with the Cherry crew 🍒🍒🍒.\n"
        "We send the freshest headlines, live scores and promos "
        "straight to your email — nothing you didn't ask for.\n\n"
        "✨ Early market moves and odds shifts\n"
        "🎮 Live match and tournament alerts\n"
        "📊 Quick charts & bite-size insights\n"
        "🎁 Members-only promos you won't find on site\n\n"
        "Which topics should we send you?"
    ),
    "ru": (
        "🍒 *Cherry Rush — горячие дропы прямо на почту*\n\n"
        "Я Ruby, со мной команда вишен 🍒🍒🍒.\n"
        "Отправляем свежие заголовки, live-счёт и промо "
        "прямо на email — только то, что ты выбрал.\n\n"
        "✨ Ранние движения рынка и изменения коэффициентов\n"
        "🎮 Алерты по live-матчам и турнирам\n"
        "📊 Быстрые графики и короткие инсайты\n"
        "🎁 Эксклюзивные промо только для подписчиков\n\n"
        "Какие темы отправлять тебе?"
    ),
    "es": (
        "🍒 *Cherry Rush — novedades calientes, directo a tu email*\n\n"
        "Soy Ruby, con la banda de cerezas 🍒🍒🍒.\n"
        "Enviamos los titulares más frescos, resultados en vivo y promos "
        "directo a tu email — nada que no pediste.\n\n"
        "✨ Movimientos de mercado y cambios de cuotas antes que nadie\n"
        "🎮 Alertas de partidos en vivo y torneos\n"
        "📊 Gráficos rápidos e insights en pocas palabras\n"
        "🎁 Promos exclusivos solo para suscriptores\n\n"
        "¿Qué temas te enviamos?"
    ),
}

BRIDGE = {
    "en": (
        "🔑 *Get the full feed by email — free*\n\n"
        "Pick your topics, drop your email, done.\n"
        "You'll get breaking drops and live-score alerts the moment they happen.\n\n"
        "• 🍒 every drop the moment it lands\n"
        "• 🔴 live-score alerts for matches you follow\n"
        "• ⚡ first to know, always\n\n"
        "18+ · News only — not financial or betting advice."
    ),
    "ru": (
        "🔑 *Полный фид на почту — бесплатно*\n\n"
        "Выбери темы, укажи email — готово.\n"
        "Получишь мгновенные дропы и алерты со счётом в момент события.\n\n"
        "• 🍒 каждый дроп в момент выхода\n"
        "• 🔴 алерты со счётом по матчам, за которыми следишь\n"
        "• ⚡ всегда первый\n\n"
        "18+ · Только новости — не беттинг/финансовый совет."
    ),
    "es": (
        "🔑 *Feed completo por email — gratis*\n\n"
        "Elegí tus temas, dejá tu email, listo.\n"
        "Recibís novedades y alertas de resultados al instante.\n\n"
        "• 🍒 cada novedad al instante\n"
        "• 🔴 alertas de resultados de los partidos que seguís\n"
        "• ⚡ siempre el primero en saber\n\n"
        "18+ · Solo noticias — sin consejos financieros ni de apuestas."
    ),
}

CTA_REGISTER = {
    "en": (
        "👇 *Subscribe — free*\n\n"
        "Open the app, pick your topics and drop your email.\n"
        "News only — no advice, no promises. 🍒"
    ),
    "ru": (
        "👇 *Подпишись — бесплатно*\n\n"
        "Открой приложение, выбери темы и укажи email.\n"
        "Только новости — без советов и обещаний. 🍒"
    ),
    "es": (
        "👇 *Suscribite — gratis*\n\n"
        "Abrí la app, elegí tus temas y dejá tu email.\n"
        "Solo noticias — sin consejos ni promesas. 🍒"
    ),
}

FTD_CELEBRATION = {
    "en": "🍒 *You're in!*\n\nCheck your inbox — the first drop is already on its way.",
    "ru": "🍒 *Ты в деле!*\n\nПроверь почту — первый дроп уже летит.",
    "es": "🍒 *¡Ya estás adentro!*\n\nRevisá tu inbox — el primer drop ya está en camino.",
}

REPEAT_PUSH = {
    "en": ["🍒 Today's hottest drops are already in your inbox."],
    "ru": ["🍒 Самые горячие дропы дня уже в твоей почте."],
    "es": ["🍒 Las novedades más calientes del día ya están en tu inbox."],
}

BARRIER_FALLBACK = {
    "en": {
        "no_trust": "Fair. Open the app and see what we cover first — no signup needed to browse.",
        "not_urgent": "No rush. Just know the drops are time-sensitive — that's the only catch.",
        "thinking": "Take your time. Which topics are you most into — crypto, markets, esports or football?",
    },
    "ru": {
        "no_trust": "Справедливо. Открой приложение и посмотри, что мы освещаем — без регистрации.",
        "not_urgent": "Без спешки. Просто знай, что дропы привязаны ко времени — единственный нюанс.",
        "thinking": "Подумай спокойно. Какие темы ближе — крипта, рынки, киберспорт или футбол?",
    },
    "es": {
        "no_trust": "Válido. Abrí la app y mirá qué cubrimos — sin registro para navegar.",
        "not_urgent": "Sin apuro. Solo tené en cuenta que las novedades son tiempo-dependientes.",
        "thinking": "Tomate tu tiempo. ¿Qué temas te interesan más — cripto, mercados, esports o fútbol?",
    },
}

GENERIC_FALLBACK = {
    "en": "🍒 Tap the button below to subscribe and get the full feed by email.",
    "ru": "🍒 Нажми кнопку ниже, чтобы подписаться и получать полный фид на почту.",
    "es": "🍒 Tocá el botón para suscribirte y recibir el feed completo por email.",
}

FTD_CONFIRM_PROMPT = {
    "en": "Subscribed? Check your inbox — confirmation is on its way.",
    "ru": "Подписался? Проверь почту — письмо уже летит.",
    "es": "¿Te suscribiste? Revisá tu inbox — el correo ya está en camino.",
}

MORNING_DIGEST_HEADER = {
    "en": "📅 *Good morning — today's top drops*\n\n",
    "ru": "📅 *Доброе утро — главные дропы дня*\n\n",
    "es": "📅 *Buen día — los drops top de hoy*\n\n",
}
MORNING_DIGEST_FOOTER = {
    "en": "\n\n🍒 Get these by email — subscribe below.",
    "ru": "\n\n🍒 Получай это на почту — подпишись ниже.",
    "es": "\n\n🍒 Recibí esto por email — suscribite abajo.",
}

JOIN_PROMPT = {
    "en": "🍒 *Get the email feed*\n\nPick topics, drop your email — that's it. 👇",
    "ru": "🍒 *Получай фид на почту*\n\nВыбери темы, укажи email — всё. 👇",
    "es": "🍒 *Recibí el feed por email*\n\nElegí temas, dejá tu email — listo. 👇",
}

JOIN_CHECK_BTN = {"en": "✅ I subscribed", "ru": "✅ Я подписался", "es": "✅ Ya me suscribí"}
JOIN_OK = {
    "en": "✅ Done — check your inbox for the confirmation.",
    "ru": "✅ Готово — проверь почту, там письмо с подтверждением.",
    "es": "✅ Listo — revisá tu inbox para confirmar.",
}
JOIN_NOT_YET = {
    "en": "Didn't get the email? Try again or check your spam folder.",
    "ru": "Письмо не пришло? Попробуй ещё раз или проверь папку «Спам».",
    "es": "¿No llegó el email? Intentá de nuevo o revisá la carpeta de spam.",
}

NEWS_HEADER = {
    "en": "🍒 *Latest drops — Cherry Rush*\n\n",
    "ru": "🍒 *Свежие дропы — Cherry Rush*\n\n",
    "es": "🍒 *Últimas novedades — Cherry Rush*\n\n",
}
NEWS_EMPTY = {
    "en": "🍒 Feed is loading — try again in a moment.",
    "ru": "🍒 Лента загружается — попробуй ещё раз.",
    "es": "🍒 El feed está cargando — probá de nuevo.",
}
NEWS_FOOTER = {
    "en": "\n\n🍒 *Get the full feed by email* — subscribe below.",
    "ru": "\n\n🍒 *Получай полный фид на почту* — подпишись ниже.",
    "es": "\n\n🍒 *Recibí el feed completo por email* — suscribite abajo.",
}
NEWS_CAT_LABELS = {
    "en": {"all": "🌐 All", "crypto": "₿ Crypto", "casino": "🏦 Industry", "esports": "🎮 Esports"},
    "ru": {"all": "🌐 Все", "crypto": "₿ Крипто", "casino": "🏦 Индустрия", "esports": "🎮 Киберспорт"},
    "es": {"all": "🌐 Todo", "crypto": "₿ Cripto", "casino": "🏦 Industria", "esports": "🎮 Esports"},
}
LIVE_CHANNEL_LINE = {
    "en": "\n\n🍒 _Get email alerts for these matches — subscribe below._",
    "ru": "\n\n🍒 _Алерты по этим матчам на почту — подпишись ниже._",
    "es": "\n\n🍒 _Alertas de resultados por email — suscribite abajo._",
}

WARMUP_FOOTBALL = {
    "en": ["🍒 The freshest drops land in your inbox first."],
    "ru": ["🍒 Самые свежие дропы — первыми в твоей почте."],
    "es": ["🍒 Las novedades más frescas llegan primero a tu inbox."],
}
WARMUP_ESPORTS = WARMUP_FOOTBALL
