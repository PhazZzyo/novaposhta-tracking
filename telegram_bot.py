#!/usr/bin/env python3
"""
Telegram Bot for Nova Poshta Package Tracking
Bot: @Orthotrack_bot
"""

import asyncio
import logging
import os
import secrets
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
import sys
sys.path.append('/home/sysadmin/projects/novaposhta-tracking')

from app import db, TelegramLinkCode, User
from flask import Flask

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables!")

# Flask app context
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///novaposhta.db'  # Same as your main app
db.init_app(app)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Temporary storage for linking codes (in production, use database)
# Format: {code: {'user_id': 123, 'created_at': datetime, 'telegram_user_id': None}}
linking_codes = {}

# Temporary user storage (in production, use database)
# Format: {telegram_user_id: {'linked': True, 'app_user_id': 123}}
users = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_user_id = update.effective_user.id
    
    with app.app_context():
        # Check if already linked
        user = User.query.filter_by(telegram_user_id=telegram_user_id).first()
        if user:
            await update.message.reply_text(...)
            return
        
        # Generate code
        link_code = secrets.token_hex(4).upper()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
        
        # Save to database
        code_obj = TelegramLinkCode(
            code=link_code,
            telegram_user_id=telegram_user_id,
            expires_at=expires_at
        )
        db.session.add(code_obj)
        db.session.commit()
        
        await update.message.reply_text(
        f"👋 Welcome to Orthotrack Bot!\n\n"
        f"To link your account:\n\n"
        f"1. Open your Nova Poshta Tracking web app\n"
        f"2. Go to Settings → Telegram Bot\n"
        f"3. Enter this code: <code>{link_code}</code>\n\n"
        f"⏰ This code expires in 10 minutes.\n\n"
        f"<i>Don't have an account? Register at your web app first!</i>",
        parse_mode='HTML'
    )
    
    logger.info(f"Generated linking code {link_code} for Telegram user {telegram_user_id}")


async def link_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle linking code submission"""
    telegram_user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide your linking code.\n\n"
            "Usage: /link <code>\n"
            "Example: /link A1B2C3D4"
        )
        return
    
    code = context.args[0].upper()
    
    # Check if code exists
    if code not in linking_codes:
        await update.message.reply_text(
            "❌ Invalid code.\n\n"
            "Please use /start to get a new linking code."
        )
        return
    
    # Check if code expired (10 minutes)
    code_data = linking_codes[code]
    if datetime.now() - code_data['created_at'] > timedelta(minutes=10):
        del linking_codes[code]
        await update.message.reply_text(
            "❌ Code expired.\n\n"
            "Please use /start to get a new linking code."
        )
        return
    
    # Link account (in production, this would update database)
    users[telegram_user_id] = {
        'linked': True,
        'app_user_id': code_data.get('app_user_id'),  # Set by web app
        'notifications_enabled': True
    }
    
    # Mark code as used
    linking_codes[code]['linked'] = True
    
    await update.message.reply_text(
        "✅ Account linked successfully!\n\n"
        "You'll now receive notifications about your incoming packages.\n\n"
        "Try /packages to see your packages!"
    )
    
    logger.info(f"Linked Telegram user {telegram_user_id} with code {code}")


async def packages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's incoming packages"""
    telegram_user_id = update.effective_user.id
    
    # Check if linked
    if telegram_user_id not in users or not users[telegram_user_id].get('linked'):
        await update.message.reply_text(
            "❌ Your account is not linked.\n\n"
            "Use /start to link your account first."
        )
        return
    
    # In production, fetch from database
    # For now, show demo data
    demo_packages = [
        {
            'ttn': '20400514075081',
            'recipient': 'Мандрик Олександр',
            'status': 'В дорозі',
            'emoji': '🚚'
        },
        {
            'ttn': '20400514075082',
            'recipient': 'Іваненко Петро',
            'status': 'У відділенні',
            'emoji': '📍'
        },
        {
            'ttn': '20400514075083',
            'recipient': 'Коваленко Марія',
            'status': 'Отримано',
            'emoji': '✅'
        }
    ]
    
    if not demo_packages:
        await update.message.reply_text(
            "📦 You have no incoming packages.\n\n"
            "Packages will appear here when they are created in the system."
        )
        return
    
    # Build message
    message = "📦 <b>Your Incoming Packages</b>\n\n"
    
    for pkg in demo_packages:
        message += (
            f"{pkg['emoji']} <b>{pkg['status']}</b>\n"
            f"TTN: <code>{pkg['ttn']}</code>\n"
            f"Recipient: {pkg['recipient']}\n\n"
        )
    
    # Add keyboard
    keyboard = [
        [InlineKeyboardButton("🔄 Refresh", callback_data='refresh_packages')],
        [InlineKeyboardButton("⚙️ Settings", callback_data='settings')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        message,
        parse_mode='HTML',
        reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message"""
    help_text = """
🤖 <b>Orthotrack Bot - Help</b>

<b>Available Commands:</b>

/start - Link your account
/packages - Show your incoming packages
/settings - Configure notifications
/help - Show this help message

<b>Notifications:</b>
You'll receive automatic notifications when:
• New incoming package is created
• Package arrives at branch (ready for pickup)
• Package is received

<b>Need help?</b>
Contact support through the web app.
"""
    
    await update.message.reply_text(help_text, parse_mode='HTML')


async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show settings"""
    telegram_user_id = update.effective_user.id
    
    # Check if linked
    if telegram_user_id not in users or not users[telegram_user_id].get('linked'):
        await update.message.reply_text(
            "❌ Your account is not linked.\n\n"
            "Use /start to link your account first."
        )
        return
    
    notifications_enabled = users[telegram_user_id].get('notifications_enabled', True)
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
    
    await update.message.reply_text(
        "⚙️ <b>Settings</b>\n\n"
        "Configure your bot preferences:",
        parse_mode='HTML',
        reply_markup=reply_markup
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    telegram_user_id = query.from_user.id
    
    await query.answer()
    
    if query.data == 'refresh_packages':
        # Refresh package list
        await query.edit_message_text("🔄 Refreshing...")
        await asyncio.sleep(1)
        # Re-send packages command output
        await packages(update, context)
    
    elif query.data == 'toggle_notifications':
        if telegram_user_id in users:
            current = users[telegram_user_id].get('notifications_enabled', True)
            users[telegram_user_id]['notifications_enabled'] = not current
            
            new_status = "enabled" if not current else "disabled"
            await query.edit_message_text(
                f"✅ Notifications {new_status}!"
            )
    
    elif query.data == 'unlink_account':
        if telegram_user_id in users:
            del users[telegram_user_id]
            await query.edit_message_text(
                "✅ Account unlinked.\n\n"
                "Use /start to link again."
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


def main():
    """Start the bot"""
    logger.info("Starting Orthotrack Telegram Bot...")
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("link", link_account))
    application.add_handler(CommandHandler("packages", packages))
    application.add_handler(CommandHandler("settings", settings))
    application.add_handler(CommandHandler("help", help_command))
    
    # Add callback handler for buttons
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Start bot
    logger.info("Bot started! Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()