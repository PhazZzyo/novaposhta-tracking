#!/usr/bin/env python3
"""
Telegram Bot for Nova Poshta Package Tracking
Bot: @Orthotrack_bot
WITH DATABASE INTEGRATION
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

# Bot token
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables!")

# Database import - ensure we can access the Flask app context and models
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db, User, Package, APIKey, UserAPITracking, TelegramLinkCode
    DB_AVAILABLE = True
    logger.info("✅ Database connected")
except Exception as e:
    DB_AVAILABLE = False
    logger.warning(f"⚠️ Database not available: {e}")

# Helper function to get user by Telegram ID
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

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle menu button presses"""
    text = update.message.text
    
    if text == "🚚 In Transit":
        await packages(update, context)
    elif text == "📍 At Branch":
        await at_branch(update, context)
    elif text == "⚙️ Settings":
        await settings(update, context)
    elif text == "❓ Help":
        await help_command(update, context)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    telegram_user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    # Check if already linked
    user = get_user_by_telegram_id(telegram_user_id)
    if user:
        keyboard = ReplyKeyboardMarkup([
            [KeyboardButton("🚚 In Transit"), KeyboardButton("📍 At Branch")],
            [KeyboardButton("⚙️ Settings"), KeyboardButton("❓ Help")]
        ], resize_keyboard=True)
        
        await update.message.reply_text(
            f"👋 Welcome back, {username}!\n\n"
            "Choose an option below:",
            reply_markup=keyboard
        )
        return

    # New user - generate linking code
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
        f"👋 Hello, {username}! Welcome to <b>Orthotrack Bot</b>!\n\n"
        "I'll notify you when your packages:\n"
        "📍 Arrive at the branch\n"
        "✅ Are delivered\n\n"
        "<b>To get started, link your account:</b>\n\n"
        "1️⃣ Open your <b>Nova Poshta Tracking</b> web app\n"
        "2️⃣ Go to <b>Settings → Telegram Bot</b>\n"
        f"3️⃣ Enter this code: <code>{link_code}</code>\n\n"
        "⏰ Code expires in 10 minutes.\n\n"
        "<i>Don't have an account? Contact your administrator.</i>",
        parse_mode='HTML'
    )

    logger.info(f"Generated linking code {link_code} for Telegram user {telegram_user_id}")

async def packages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = get_reply(update)
    telegram_user_id = get_user_id(update)

    with app.app_context():
        user = User.query.filter_by(telegram_user_id=telegram_user_id).first()

        if not user:
            await reply(
                "❌ Your account is not linked.\n\n"
                "Use /start to link your account first."
            )
            return

        # Admin sees ALL api keys, regular users see tracked ones
        if user.role == 'admin':
            api_key_ids = [k.id for k in APIKey.query.filter_by(is_active=True).all()]
        else:
            tracked = UserAPITracking.query.filter_by(user_id=user.id).all()
            api_key_ids = [t.api_key_id for t in tracked]

        if not api_key_ids:
            await reply(
                "📦 No API keys found.\n\n"
                "Please add an API key in the web app first."
            )
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
            await reply(
                "🚚 No packages in transit.\n\n"
                "Use /atbranch to check packages ready for pickup."
            )
            return

        # Build message
        message = "🚚 <b>Packages In Transit</b>\n\n"

        for pkg in in_transit:
            message += (
                f"🚚 {pkg.status or 'В дорозі'}\n"
                f"TTN: <code>{pkg.tracking_number}</code>\n"
                f"Recipient: {pkg.recipient_name or '-'}\n\n"
            )

    # Ad keyboard for refresh and at branch
    keyboard = [
        [InlineKeyboardButton("🔄 Refresh", callback_data='refresh_packages')],
        [InlineKeyboardButton("📍 At Branch", callback_data='at_branch')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await reply(
        message,
        parse_mode='HTML',
        reply_markup=reply_markup
    )

async def at_branch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show packages at branch ready for pickup"""
    telegram_user_id = get_user_id(update)
    reply = get_reply(update)

    with app.app_context():
        user = User.query.filter_by(telegram_user_id=telegram_user_id).first()

        if not user:
            await reply(
                "❌ Your account is not linked.\n\n"
                "Use /start to link your account first."
            )
            return

        if user.role == 'admin':
            api_key_ids = [k.id for k in APIKey.query.filter_by(is_active=True).all()]
        else:
            tracked = UserAPITracking.query.filter_by(user_id=user.id).all()
            api_key_ids = [t.api_key_id for t in tracked]

        if not api_key_ids:
            await reply("📦 No API keys found.")
            return

        # Only AT BRANCH - status codes 7 and 8
        at_branch_pkgs = Package.query.filter(
            Package.api_key_id.in_(api_key_ids),
            Package.direction == 'incoming',
            Package.is_delivered == False,
            Package.status_code.in_(['7', '8'])
        ).order_by(Package.date_created.desc()).all()

        if not at_branch_pkgs:
            await reply(
                "📍 No packages at branch.\n\n"
                "Use /packages to check packages in transit."
            )
            return

        message = "📍 <b>Packages At Branch</b>\n"
        message += "<i>Ready for pickup!</i>\n\n"

        for pkg in at_branch_pkgs:
            message += (
                f"📍 <b>{pkg.recipient_name or '-'}</b>\n"
                f"TTN: <code>{pkg.tracking_number}</code>\n"
                f"Branch: {pkg.recipient_warehouse or '-'}\n\n"
            )

    keyboard = [
        [InlineKeyboardButton("🔄 Refresh", callback_data='at_branch')],
        [InlineKeyboardButton("🚚 In Transit", callback_data='refresh_packages')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await reply(
        message,
        parse_mode='HTML',
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 <b>Orthotrack Bot - Help</b>\n\n"
        "<b>Commands:</b>\n\n"
        "/packages - 🚚 Packages in transit\n"
        "/atbranch - 📍 Packages at branch (ready for pickup)\n"
        "/settings - ⚙️ Configure notifications\n"
        "/help - Show this message\n\n"
        "<b>Notifications:</b>\n"
        "You'll receive automatic notifications when:\n"
        "• Package arrives at branch 📍\n"
        "• Package is delivered ✅",
        parse_mode='HTML'
    )


async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show settings"""
    reply = get_reply(update)
    telegram_user_id = get_user_id(update)
    
    # Check if linked
    user = get_user_by_telegram_id(telegram_user_id)
    if not user:
        await reply(
            "❌ Your account is not linked.\n\n"
            "Use /start to link your account first."
        )
        return
    
    with app.app_context():
        user = User.query.get(user.id)  # Refresh from DB
        notifications_enabled = user.telegram_notifications if user.telegram_notifications is not None else True
        status_emoji = "🔔" if notifications_enabled else "🔕"
        status_text = "ON" if notifications_enabled else "OFF"
    
    keyboard = [
        [InlineKeyboardButton(
            f"{status_emoji} Notifications: {status_text}",
            callback_data='toggle_notifications'
        )],
        [InlineKeyboardButton("🔗 Unlink Account", callback_data='unlink_account')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await reply(
        "⚙️ <b>Settings</b>\n\n"
        "Configure your bot preferences:",
        parse_mode='HTML',
        reply_markup=reply_markup
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'refresh_packages':
        await packages(update, context)
    
    elif query.data == 'at_branch':
        await at_branch(update, context)
    
    elif query.data == 'unlink_account':
        with app.app_context():
            user = User.query.filter_by(
                telegram_user_id=query.from_user.id
            ).first()
            if user:
                user.telegram_user_id = None
                user.telegram_notifications = False
                db.session.commit()
        await query.edit_message_text(
            "✅ Account unlinked.\n\nUse /start to link again."
        )
    
    elif query.data == 'settings':
        await settings(update, context)


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
    
async def error_handler(update, context):
    """Handle errors gracefully"""
    from telegram.error import TimedOut, NetworkError
    
    if isinstance(context.error, TimedOut):
        logger.warning("⚠️ Telegram timeout - will retry automatically")
        return
    
    if isinstance(context.error, NetworkError):
        logger.warning(f"⚠️ Network error: {context.error}")
        return
    
    logger.error(f"❌ Unexpected error: {context.error}")

async def set_commands(app):
    """Set bot commands visible in Telegram menu"""
    await app.bot.set_my_commands([
        ('start', 'Start / Link account'),
        ('packages', '🚚 Packages in transit'),
        ('atbranch', '📍 Packages at branch'),
        ('settings', '⚙️ Settings'),
        ('help', '❓ Help'),
    ])

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