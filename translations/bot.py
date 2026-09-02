# translations/bot.py
"""Translation strings for the Telegram bot"""

BOT_TRANSLATIONS = {
	'en': {
		# /start - already linked
		'welcome_back': "👋 Welcome back, {username}!\n\nChoose an option below:",

		# Menu buttons (also used to match handle_menu text)
		'btn_in_transit': "🚚 In Transit",
		'btn_at_branch': "📍 At Branch",
		'btn_settings': "⚙️ Settings",
		'btn_help': "❓ Help",

		# /start - new user linking
		'start_hello': (
			"👋 Hello, {username}! Welcome to <b>Orthotrack Bot</b>!\n\n"
			"I'll notify you when your packages:\n"
			"📍 Arrive at the branch\n"
			"✅ Are delivered\n\n"
			"<b>To get started, link your account:</b>\n\n"
			"1️⃣ Open your <b>Nova Poshta Tracking</b> web app\n"
			"2️⃣ Go to <b>Settings → Telegram Bot</b>\n"
			"3️⃣ Enter this code: <code>{code}</code>\n\n"
			"⏰ Code expires in 10 minutes.\n\n"
			"<i>Don't have an account? Contact your administrator.</i>"
		),

		# Common errors
		'not_linked': "❌ Your account is not linked.\n\nUse /start to link your account first.",
		'no_api_keys': "📦 No API keys found.\n\nPlease add an API key in the web app first.",

		# /packages
		'no_packages_in_transit': "🚚 No packages in transit.\n\nUse /atbranch to check packages ready for pickup.",
		'packages_in_transit_title': "🚚 <b>Packages In Transit</b>\n\n",
		'package_line': "🚚 {status}\nTTN: <code>{ttn}</code>\nRecipient: {recipient}\nBranch: {branch}\nEst. delivery: {delivery_date}\n\n",
		'btn_refresh': "🔄 Refresh",

		# /atbranch
		'no_packages_at_branch': "📍 No packages at branch.\n\nUse /packages to check packages in transit.",
		'packages_at_branch_title': "📍 <b>Packages At Branch</b>\n<i>Ready for pickup!</i>\n\n",
		'branch_package_line': "📍 <b>{recipient}</b>\nTTN: <code>{ttn}</code>\nBranch: {branch}\n\n",

		# /help
		'help_text': (
			"🤖 <b>Orthotrack Bot - Help</b>\n\n"
			"<b>Commands:</b>\n\n"
			"/packages - 🚚 Packages in transit\n"
			"/atbranch - 📍 Packages at branch (ready for pickup)\n"
			"/sync - 🔄 Force sync packages (admin only)\n"
			"/settings - ⚙️ Configure notifications\n"
			"/help - Show this message\n\n"
			"<b>Notifications:</b>\n"
			"You'll receive automatic notifications when:\n"
			"• Package arrives at branch 📍\n"
			"• Package is delivered ✅"
		),

		# /settings
		'settings_title': "⚙️ <b>Settings</b>\n\nConfigure your bot preferences:",
		'notifications_on': "🔔 Notifications: ON",
		'notifications_off': "🔕 Notifications: OFF",
		'btn_unlink': "🔗 Unlink Account",
		'unlinked': "✅ Account unlinked.\n\nUse /start to link again.",

		# /sync (admin only) - reserved for future implementation
		'sync_admin_only': "❌ Only admins can trigger sync.",
		'sync_running': "🔄 Syncing packages...",
		'sync_results_title': "📊 <b>Sync Results:</b>\n\n",
		'sync_line_ok': "✅ {label}: {message}",
		'sync_line_fail': "❌ {label}: {message}",
		'sync_line_skipped': "⏳ {label}: {message}",
	},
	'uk': {
		'welcome_back': "👋 З поверненням, {username}!\n\nОберіть опцію нижче:",

		'btn_in_transit': "🚚 В дорозі",
		'btn_at_branch': "📍 У відділенні",
		'btn_settings': "⚙️ Налаштування",
		'btn_help': "❓ Допомога",

		'start_hello': (
			"👋 Вітаю, {username}! Ласкаво просимо до <b>Orthotrack Bot</b>!\n\n"
			"Я повідомлятиму вас, коли ваші посилки:\n"
			"📍 Прибудуть у відділення\n"
			"✅ Будуть отримані\n\n"
			"<b>Щоб почати, прив'яжіть свій акаунт:</b>\n\n"
			"1️⃣ Відкрийте вебзастосунок <b>Nova Poshta Tracking</b>\n"
			"2️⃣ Перейдіть у <b>Налаштування → Telegram Bot</b>\n"
			"3️⃣ Введіть цей код: <code>{code}</code>\n\n"
			"⏰ Код дійсний 10 хвилин.\n\n"
			"<i>Немає акаунту? Зверніться до адміністратора.</i>"
		),

		'not_linked': "❌ Ваш акаунт не прив'язаний.\n\nВикористайте /start, щоб прив'язати акаунт.",
		'no_api_keys': "📦 API ключі не знайдено.\n\nБудь ласка, додайте API ключ у вебзастосунку.",

		'no_packages_in_transit': "🚚 Немає посилок у дорозі.\n\nВикористайте /atbranch, щоб перевірити посилки, готові до отримання.",
		'packages_in_transit_title': "🚚 <b>Посилки в дорозі</b>\n\n",
		'package_line': "🚚 {status}\nТТН: <code>{ttn}</code>\nОтримувач: {recipient}\nВідділення: {branch}\nОрієнтовна доставка: {delivery_date}\n\n",
		'btn_refresh': "🔄 Оновити",

		'no_packages_at_branch': "📍 Немає посилок у відділенні.\n\nВикористайте /packages, щоб перевірити посилки в дорозі.",
		'packages_at_branch_title': "📍 <b>Посилки у відділенні</b>\n<i>Готові до отримання!</i>\n\n",
		'branch_package_line': "📍 <b>{recipient}</b>\nТТН: <code>{ttn}</code>\nВідділення: {branch}\n\n",

		'help_text': (
			"🤖 <b>Orthotrack Bot - Довідка</b>\n\n"
			"<b>Команди:</b>\n\n"
			"/packages - 🚚 Посилки в дорозі\n"
			"/atbranch - 📍 Посилки у відділенні (готові до отримання)\n"
			"/sync - 🔄 Примусова синхронізація (тільки адмін)\n"
			"/settings - ⚙️ Налаштування сповіщень\n"
			"/help - Показати це повідомлення\n\n"
			"<b>Сповіщення:</b>\n"
			"Ви автоматично отримаєте сповіщення, коли:\n"
			"• Посилка прибуде у відділення 📍\n"
			"• Посилку буде отримано ✅"
		),

		'settings_title': "⚙️ <b>Налаштування</b>\n\nНалаштуйте параметри бота:",
		'notifications_on': "🔔 Сповіщення: УВІМК",
		'notifications_off': "🔕 Сповіщення: ВИМК",
		'btn_unlink': "🔗 Відв'язати акаунт",
		'unlinked': "✅ Акаунт відв'язано.\n\nВикористайте /start, щоб прив'язати знову.",

		'sync_admin_only': "❌ Тільки адміністратори можуть запускати синхронізацію.",
		'sync_running': "🔄 Синхронізація посилок...",
		'sync_results_title': "📊 <b>Результати синхронізації:</b>\n\n",
		'sync_line_ok': "✅ {label}: {message}",
		'sync_line_fail': "❌ {label}: {message}",
		'sync_line_skipped': "⏳ {label}: {message}",
	}
}


def t_bot(key, lang='uk', **kwargs):
	"""Get translated bot string, formatted with kwargs. Falls back to 'uk' then to key itself."""
	lang_dict = BOT_TRANSLATIONS.get(lang, BOT_TRANSLATIONS['uk'])
	text = lang_dict.get(key, BOT_TRANSLATIONS['uk'].get(key, key))
	if kwargs:
		return text.format(**kwargs)
	return text