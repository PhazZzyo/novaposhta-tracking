# services/notifications.py
import os
import requests
from models import User, APIKey, UserAPITracking
import logging
logger = logging.getLogger(__name__)


def send_telegram_notification(telegram_user_id: int, message: str):
    """Send Telegram notification synchronously using requests"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        logger.error("No bot token found!")
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': telegram_user_id,
        'text': message,
        'parse_mode': 'HTML'
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()        
        logger.debug(f"Telegram API response: {result}")
        return result.get('ok', False)
    except Exception as e:        
        logger.error(f"Failed to send: {e}")
        return False


def notify_package_status_change(package, old_status_code, new_status_code):
    """Send notification when package status changes"""
    # Only notify for incoming packages
    if package.direction != 'incoming':
        return

    # Only notify for important status changes
    if new_status_code not in ['7', '8', '9']:
        return

    # Find the user who owns this package's API key
    api_key = APIKey.query.get(package.api_key_id)
    if not api_key:
        return

    # Find tracked users + admins
    tracked = UserAPITracking.query.filter_by(api_key_id=api_key.id).all()
    admin_users = User.query.filter_by(role='admin').all()

    user_ids = set([t.user_id for t in tracked])
    for admin in admin_users:
        user_ids.add(admin.id)

    users_to_notify = User.query.filter(
        User.id.in_(user_ids),
        User.telegram_user_id != None,
        User.telegram_notifications == True
    ).all()

    logger.debug(f"Notifying {len(users_to_notify)} users: {[u.username for u in users_to_notify]}")

    if not users_to_notify:
        logger.error("No users to notify!")
        return

    # Build message
    if new_status_code in ['7', '8']:
        emoji = '📍'
        urgent = '\n⚠️ <b>Ready for pickup!</b>'
    elif new_status_code == '9':
        emoji = '✅'
        urgent = ''
    else:
        emoji = '🚚'
        urgent = ''

    message = (
        f"{emoji} <b>Package Update</b>\n\n"
        f"TTN: <code>{package.tracking_number}</code>\n"
        f"Recipient: {package.recipient_name or '-'}\n"
        f"Status: {package.status}\n"
        f"{urgent}"
    )

    logger.debug(f"Sending message: {message}")

    # Send to all relevant users
    for user in users_to_notify:
        result = send_telegram_notification(user.telegram_user_id, message)
        if result:
            logger.debug(f"Notified {user.username} (TG: {user.telegram_user_id})")            
        else:
            logger.error(f"Failed to notify {user.username}")
