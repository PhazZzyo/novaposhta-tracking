# routes/settings.py
from datetime import datetime, timezone
from zoneinfo import available_timezones
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import APIKey, UserAPITracking, TelegramLinkCode

settings_bp = Blueprint('settings', __name__)


def utc_to_local(dt):
	from app import utc_to_local as _utc_to_local
	return _utc_to_local(dt)


def t(key):
	from app import t as _t
	return _t(key)


@settings_bp.route('/set-theme', methods=['POST'])
@login_required
def set_theme():
	"""Toggle user theme preference"""
	data = request.get_json()
	theme = data.get('theme', 'light')
	if theme in ['light', 'dark']:
		current_user.theme = theme
		db.session.commit()
		return jsonify({'success': True, 'theme': theme})
	return jsonify({'success': False, 'error': 'Invalid theme'}), 400


@settings_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
	if request.method == 'POST':
		current_user.theme = request.form.get('theme', 'light')
		current_user.view_mode = request.form.get('view_mode', 'table')
		current_user.items_per_page = int(request.form.get('items_per_page', 20))
		current_user.notify_ready_pickup = bool(request.form.get('notify_ready_pickup'))
		current_user.language = request.form.get('language', 'uk')
		current_user.timezone = request.form.get('timezone', 'Europe/Kyiv')

		if current_user.role != 'admin':
			UserAPITracking.query.filter_by(user_id=current_user.id).delete()
			for aid in request.form.getlist('tracked_apis'):
				db.session.add(UserAPITracking(user_id=current_user.id, api_key_id=int(aid)))

		db.session.commit()
		flash(t('save') + ' ✓', 'success')
		return redirect(url_for('settings.settings'))

	available_apis = APIKey.query.filter_by(is_active=True).all()
	tracked_api_ids = [tr.api_key_id for tr in current_user.tracked_apis]
	timezones = sorted(list(available_timezones()))

	return render_template('settings.html',
		available_apis=available_apis,
		tracked_api_ids=tracked_api_ids,
		timezones=timezones)


@settings_bp.route('/settings/telegram', methods=['GET', 'POST'])
@login_required
def telegram_settings():
	"""Telegram bot linking settings"""
	if request.method == 'POST':
		code = request.form.get('link_code', '').strip().upper()

		if not code:
			flash('Please enter a linking code', 'error')
			return redirect(url_for('settings.telegram_settings'))

		link_obj = TelegramLinkCode.query.filter_by(code=code, used=False).first()

		if not link_obj:
			flash('Invalid or expired code', 'error')
			return redirect(url_for('settings.telegram_settings'))

		# Check expiry - handle naive datetime from SQLite
		expires_at = link_obj.expires_at
		if expires_at.tzinfo is None:
			expires_at = expires_at.replace(tzinfo=timezone.utc)

		if datetime.now(timezone.utc) > expires_at:
			flash('Code expired. Generate a new one by sending /start to @Orthotrack_bot', 'error')
			return redirect(url_for('settings.telegram_settings'))

		# Link account
		current_user.telegram_user_id = link_obj.telegram_user_id
		current_user.telegram_linked_at = datetime.now(timezone.utc)
		current_user.telegram_notifications = True
		link_obj.used = True
		link_obj.user_id = current_user.id
		db.session.commit()

		flash('Telegram account linked successfully!', 'success')
		return redirect(url_for('settings.telegram_settings'))

	return render_template('telegram_settings.html')


@settings_bp.route('/settings/telegram/unlink', methods=['POST'])
@login_required
def telegram_unlink():
	"""Unlink Telegram account"""
	current_user.telegram_user_id = None
	current_user.telegram_notifications = False
	db.session.commit()
	flash('Telegram account unlinked', 'success')
	return redirect(url_for('settings.telegram_settings'))


@settings_bp.route('/settings/telegram/toggle-notifications', methods=['POST'])
@login_required
def toggle_telegram_notifications():
	"""Toggle Telegram notifications"""
	data = request.json
	enabled = data.get('enabled', False)
	current_user.telegram_notifications = enabled
	db.session.commit()
	return jsonify({'success': True})
