#!/usr/bin/env python3
"""
Telegram Bot for Nova Poshta Package Tracking
Bot: @Orthotrack_bot
WITH DATABASE INTEGRATION AND UK/EN TRANSLATIONS
"""


import os
from dotenv import load_dotenv
load_dotenv()
import logging
import secrets
import sys
from datetime import datetime, timezone, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.request import HTTPXRequest

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app
    from extensions import db
    from models import User, Package, APIKey, UserAPITracking, TelegramLinkCode
    from translations import t_bot
    app = create_app()
    DB_AVAILABLE = True
    logger.info("Database connected")
except Exception as e:
    DB_AVAILABLE = False
    logger.warning(f"Database not available: {e}")

# Bot token
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables!")


# ============================================================
# HELPERS
# ============================================================

def get_user_by_telegram_id(telegram_user_id):
    """Get user by Telegram ID"""
    with app.app_context():
        return User.query.filter_by(telegram_user_id=telegram_user_id).first()


def get_reply(update):
    """Get the correct reply function based on update type"""
    if update.message:
        return update.message.reply_text
    return update.callback_query.message.reply_text


def get_user_id(update):
    """Get telegram user ID regardless of update type"""
    return update.effective_user.id


def get_lang(user):
    """Get user's preferred language, default to 'uk' if not linked/set"""
    if user and user.language:
        return user.language
    return 'uk'


def get_lang_by_telegram_id(telegram_user_id):
    """Convenience: fetch user and return their language"""
    user = get_user_by_telegram_id(telegram_user_id)
    return get_lang(user)


# ============================================================
# MENU HANDLER
# ============================================================

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle menu button presses (matches translated button labels in any language)"""
    text = update.message.text
    telegram_user_id = get_user_id(update)
    lang = get_lang_by_telegram_id(telegram_user_id)

    if text in (t_bot('btn_in_transit', 'uk'), t_bot('btn_in_transit', 'en')):
        await packages(update, context)
    elif text in (t_bot('btn_at_branch', 'uk'), t_bot('btn_at_branch', 'en')):
        await at_branch(update, context)
    elif text in (t_bot('btn_settings', 'uk'), t_bot('btn_settings', 'en')):
        await settings(update, context)
    elif text in (t_bot('btn_help', 'uk'), t_bot('btn_help', 'en')):
        await help_command(update, context)


# ============================================================
# /start
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    telegram_user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    # Check if already linked
    user = get_user_by_telegram_id(telegram_user_id)
    if user:
        lang = get_lang(user)
        keyboard = ReplyKeyboardMarkup([
            [KeyboardButton(t_bot('btn_in_transit', lang)), KeyboardButton(t_bot('btn_at_branch', lang))],
            [KeyboardButton(t_bot('btn_settings', lang)), KeyboardButton(t_bot('btn_help', lang))]
        ], resize_keyboard=True)

        await update.message.reply_text(
            t_bot('welcome_back', lang, username=username),
            reply_markup=keyboard
        )
        return

    # New user - generate linking code (not linked yet, so default to 'uk')
    lang = 'uk'
    link_code = secrets.token_hex(4).upper()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    with app.app_context():
        code_obj = TelegramLinkCode(
            code=link_code,
            telegram_user_id=telegram_user_id,
            expires_at=expires_at
        )
        db.session.add(code_obj)
        db.session.commit()

    await update.message.reply_text(
        t_bot('start_hello', lang, username=username, code=link_code),
        parse_mode='HTML'
    )

    logger.info(f"Generated linking code {link_code} for Telegram user {telegram_user_id}")


# ============================================================
# /packages
# ============================================================

async def packages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = get_reply(update)
    telegram_user_id = get_user_id(update)

    with app.app_context():
        user = User.query.filter_by(telegram_user_id=telegram_user_id).first()
        lang = get_lang(user)

        if not user:
            await reply(t_bot('not_linked', lang))
            return

        # Admin sees ALL api keys, regular users see tracked ones
        if user.role == 'admin':
            api_key_ids = [k.id for k in APIKey.query.filter_by(is_active=True).all()]
        else:
            tracked = UserAPITracking.query.filter_by(user_id=user.id).all()
            api_key_ids = [t.api_key_id for t in tracked]

        if not api_key_ids:
            await reply(t_bot('no_api_keys', lang))
            return

        # Fetch active incoming packages
        in_transit = Package.query.filter(
            Package.api_key_id.in_(api_key_ids),
            Package.direction == 'incoming',
            db.or_(Package.draft_status == None, Package.draft_status != 'draft'),
            Package.is_delivered == False,
            Package.status_code != '2',
            ~Package.status_code.in_(['7', '8'])
        ).order_by(Package.date_created.desc()).limit(20).all()

        if not in_transit:
            await reply(t_bot('no_packages_in_transit', lang))
            return

        # Build message
        message = t_bot('packages_in_transit_title', lang)

        for pkg in in_transit:
            message += t_bot(
                'package_line', lang,
                status=pkg.status or 'В дорозі',
                ttn=pkg.tracking_number,
                recipient=pkg.recipient_name or '-'
            )

    keyboard = [
        [InlineKeyboardButton(t_bot('btn_refresh', lang), callback_data='refresh_packages')],
        [InlineKeyboardButton(t_bot('btn_at_branch', lang), callback_data='at_branch')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await reply(
        message,
        parse_mode='HTML',
        reply_markup=reply_markup
    )


# ============================================================
# /atbranch
# ============================================================

async def at_branch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show packages at branch ready for pickup"""
    telegram_user_id = get_user_id(update)
    reply = get_reply(update)

    with app.app_context():
        user = User.query.filter_by(telegram_user_id=telegram_user_id).first()
        lang = get_lang(user)

        if not user:
            await reply(t_bot('not_linked', lang))
            return

        if user.role == 'admin':
            api_key_ids = [k.id for k in APIKey.query.filter_by(is_active=True).all()]
        else:
            tracked = UserAPITracking.query.filter_by(user_id=user.id).all()
            api_key_ids = [t.api_key_id for t in tracked]

        if not api_key_ids:
            await reply(t_bot('no_api_keys', lang))
            return

        # Only AT BRANCH - status codes 7 and 8
        at_branch_pkgs = Package.query.filter(
            Package.api_key_id.in_(api_key_ids),
            Package.direction == 'incoming',
            Package.is_delivered == False,
            Package.status_code.in_(['7', '8'])
        ).order_by(Package.date_created.desc()).all()

        if not at_branch_pkgs:
            await reply(t_bot('no_packages_at_branch', lang))
            return

        message = t_bot('packages_at_branch_title', lang)

        for pkg in at_branch_pkgs:
            message += t_bot(
                'branch_package_line', lang,
                recipient=pkg.recipient_name or '-',
                ttn=pkg.tracking_number,
                branch=pkg.recipient_warehouse or '-'
            )

    keyboard = [
        [InlineKeyboardButton(t_bot('btn_refresh', lang), callback_data='at_branch')],
        [InlineKeyboardButton(t_bot('btn_in_transit', lang), callback_data='refresh_packages')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await reply(
        message,
        parse_mode='HTML',
        reply_markup=reply_markup
    )


# ============================================================
# /help
# ============================================================

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_user_id = get_user_id(update)
    lang = get_lang_by_telegram_id(telegram_user_id)
    await update.message.reply_text(
        t_bot('help_text', lang),
        parse_mode='HTML'
    )


# ============================================================
# /settings
# ============================================================

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show settings"""
    reply = get_reply(update)
    telegram_user_id = get_user_id(update)

    user = get_user_by_telegram_id(telegram_user_id)
    lang = get_lang(user)

    if not user:
        await reply(t_bot('not_linked', lang))
        return

    with app.app_context():
        user = User.query.get(user.id)  # Refresh from DB
        notifications_enabled = user.telegram_notifications if user.telegram_notifications is not None else True

    notif_label = t_bot('notifications_on', lang) if notifications_enabled else t_bot('notifications_off', lang)

    keyboard = [
        [InlineKeyboardButton(notif_label, callback_data='toggle_notifications')],
        [InlineKeyboardButton(t_bot('btn_unlink', lang), callback_data='unlink_account')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await reply(
        t_bot('settings_title', lang),
        parse_mode='HTML',
        reply_markup=reply_markup
    )


# ============================================================
# Button callbacks
# ============================================================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()

    telegram_user_id = query.from_user.id
    lang = get_lang_by_telegram_id(telegram_user_id)

    if query.data == 'refresh_packages':
        await packages(update, context)

    elif query.data == 'at_branch':
        await at_branch(update, context)

    elif query.data == 'unlink_account':
        with app.app_context():
            user = User.query.filter_by(telegram_user_id=telegram_user_id).first()
            if user:
                user.telegram_user_id = None
                user.telegram_notifications = False
                db.session.commit()
        await query.edit_message_text(t_bot('unlinked', lang))

    elif query.data == 'settings':
        await settings(update, context)


# ============================================================
# Notifications (used by services/notifications.py flow)
# ============================================================

async def send_notification(telegram_user_id: int, message: str):
    """Send notification to a specific user"""
    try:
        bot = Application.builder().token(BOT_TOKEN).build().bot
        await bot.send_message(
            chat_id=telegram_user_id,
            text=message,
            parse_mode='HTML'
        )
        logger.info(f"Sent notification to {telegram_user_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to send notification to {telegram_user_id}: {e}")
        return False


# ============================================================
# Error handler
# ============================================================

async def error_handler(update, context):
    """Handle errors gracefully"""
    from telegram.error import TimedOut, NetworkError

    if isinstance(context.error, TimedOut):
        logger.warning("Telegram timeout - will retry automatically")
        return

    if isinstance(context.error, NetworkError):
        logger.warning(f"Network error: {context.error}")
        return

    logger.error(f"Unexpected error: {context.error}")


# ============================================================
# Bot commands menu (Telegram's built-in / menu, English labels
# since Telegram doesn't support per-user localized command lists
# without extra API calls per language - keeping it simple for now)
# ============================================================

async def set_commands(app):
    """Set bot commands visible in Telegram menu"""
    await app.bot.set_my_commands([
        ('start', 'Start / Link account'),
        ('packages', '🚚 Packages in transit'),
        ('atbranch', '📍 Packages at branch'),
        ('settings', '⚙️ Settings'),
        ('help', '❓ Help'),
    ])


# ============================================================
# Main
# ============================================================

def main():
    """Start the bot"""
    logger.info("Starting Orthotrack Telegram Bot with database integration...")

    # Add timeouts to prevent hanging
    request = HTTPXRequest(
        connection_pool_size=8,
        connect_timeout=30.0,
        read_timeout=30.0,
        write_timeout=30.0,
        pool_timeout=30.0,
    )

    # Create application
    application = Application.builder()\
        .token(BOT_TOKEN)\
        .request(request)\
        .post_init(set_commands)\
        .build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("packages", packages))
    application.add_handler(CommandHandler("atbranch", at_branch))
    application.add_handler(CommandHandler("settings", settings))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))

    # Add callback handler for buttons
    application.add_handler(CallbackQueryHandler(button_callback))

    # Add error handler
    application.add_error_handler(error_handler)

    # Start bot
    logger.info("Bot started! Press Ctrl+C to stop.")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )


if __name__ == '__main__':
    main()