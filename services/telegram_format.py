# services/telegram_format.py
"""Single source of truth for how a package looks in Telegram messages."""
from html import escape
from translations import t_bot
from services.np_status_codes import is_at_branch_status


def status_emoji(status_code, is_delivered=False):
	if is_at_branch_status(status_code):
		return '📍'
	if is_delivered:
		return '✅'
	return '🚚'


def format_package(pkg, lang='uk', status_code=None):
	"""One package as an HTML block. Used by /packages, /atbranch and auto-notifications."""
	code = status_code or pkg.status_code
	emoji = status_emoji(code, pkg.is_delivered)

	lines = [
		f"{emoji} <b>{escape(pkg.status or '-')}</b>",
		f"{t_bot('lbl_ttn', lang)}: <code>{pkg.tracking_number}</code>",
		f"{t_bot('lbl_recipient', lang)}: {escape(pkg.recipient_name or '-')}",
		f"{t_bot('lbl_branch', lang)}: {escape(pkg.recipient_warehouse or '-')}",
	]

	# Estimated delivery only makes sense while the package is still on its way
	if pkg.planned_delivery_date and not pkg.is_delivered and not is_at_branch_status(code):
		lines.append(f"{t_bot('lbl_delivery', lang)}: {pkg.planned_delivery_date.strftime('%d.%m.%Y')}")

	return "\n".join(lines) + "\n\n"