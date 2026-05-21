# routes/admin.py
import json
from datetime import datetime, timezone, timedelta
from io import BytesIO
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from sqlalchemy import desc
from extensions import db
from models import User, APIKey, UserAPITracking, SyncLog

admin_bp = Blueprint('admin', __name__)


def role_required(*roles):
	def decorator(f):
		@wraps(f)
		def decorated_function(*args, **kwargs):
			if current_user.role not in roles:
				flash('Access denied', 'danger')
				return redirect(url_for('packages.dashboard'))
			return f(*args, **kwargs)
		return decorated_function
	return decorator


@admin_bp.route('/admin/users')
@role_required('admin')
def admin_users():
	return render_template('admin/users.html', users=User.query.all())


@admin_bp.route('/admin/user/add', methods=['GET', 'POST'])
@role_required('admin')
def admin_add_user():
	if request.method == 'POST':
		username = request.form.get('username')
		if User.query.filter_by(username=username).first():
			flash('Username already exists.', 'danger')
		else:
			u = User(
				username=username,
				full_name=request.form.get('full_name'),
				role=request.form.get('role')
			)
			u.set_password(request.form.get('password'))
			db.session.add(u)
			db.session.commit()
			flash(f'User {username} created.', 'success')
			return redirect(url_for('admin.admin_users'))
	return render_template('admin/add_user.html')


@admin_bp.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
@role_required('admin')
def admin_edit_user(user_id):
	user = User.query.get_or_404(user_id)
	if request.method == 'POST':
		user.full_name = request.form.get('full_name')
		user.role = request.form.get('role')
		user.is_active = bool(request.form.get('is_active'))
		pw = request.form.get('new_password')
		if pw:
			user.set_password(pw)
		db.session.commit()
		flash(f'User {user.username} updated.', 'success')
		return redirect(url_for('admin.admin_users'))
	return render_template('admin/edit_user.html', user=user)


@admin_bp.route('/admin/api-keys')
@role_required('admin')
def admin_api_keys():
	return render_template('admin/api_keys.html', api_keys=APIKey.query.all())


@admin_bp.route('/admin/api-key/add', methods=['GET', 'POST'])
@role_required('admin')
def admin_add_api_key():
	if request.method == 'POST':
		key = request.form.get('api_key')
		if APIKey.query.filter_by(api_key=key).first():
			flash('API key already exists.', 'danger')
		else:
			k = APIKey(
				label=request.form.get('label'),
				api_key=key,
				sender_identifier=request.form.get('sender_identifier'),
				counterparty_ref=request.form.get('counterparty_ref'),
				auto_sync=bool(request.form.get('auto_sync')),
				created_by=current_user.id
			)
			db.session.add(k)
			db.session.commit()
			flash(f'API key "{k.label}" added.', 'success')
			return redirect(url_for('admin.admin_api_keys'))
	return render_template('admin/add_api_key.html')


@admin_bp.route('/admin/api-key/<int:key_id>/edit', methods=['GET', 'POST'])
@role_required('admin')
def admin_edit_api_key(key_id):
	key = APIKey.query.get_or_404(key_id)
	if request.method == 'POST':
		key.label = request.form.get('label')
		key.sender_identifier = request.form.get('sender_identifier')
		key.counterparty_ref = request.form.get('counterparty_ref')
		key.sender_city_ref = request.form.get('sender_city_ref')
		key.sender_city_name = request.form.get('sender_city_name')
		key.sender_warehouse_ref = request.form.get('sender_warehouse_ref')
		key.sender_warehouse_name = request.form.get('sender_warehouse_name')
		key.sender_contact_ref = request.form.get('sender_contact_ref')
		key.sender_contact_name = request.form.get('sender_contact_name')
		key.auto_sync = bool(request.form.get('auto_sync'))
		key.is_active = bool(request.form.get('is_active'))
		db.session.commit()
		flash(f'API key "{key.label}" updated.', 'success')
		return redirect(url_for('admin.admin_api_keys'))
	return render_template('admin/edit_api_key.html', api_key=key)


@admin_bp.route('/admin/api-keys/export')
@role_required('admin')
def admin_export_api_keys():
	keys = APIKey.query.all()
	data = [{
		'label': k.label,
		'api_key': k.api_key,
		'sender_identifier': k.sender_identifier,
		'counterparty_ref': k.counterparty_ref,
		'auto_sync': k.auto_sync,
		'is_active': k.is_active
	} for k in keys]

	json_data = json.dumps(data, indent=2, ensure_ascii=False)
	buffer = BytesIO(json_data.encode('utf-8'))
	buffer.seek(0)

	return send_file(
		buffer,
		mimetype='application/json',
		as_attachment=True,
		download_name=f'api_keys_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
	)


@admin_bp.route('/admin/api-keys/import', methods=['POST'])
@role_required('admin')
def admin_import_api_keys():
	if 'file' not in request.files:
		flash('No file selected.', 'danger')
		return redirect(url_for('admin.admin_api_keys'))

	file = request.files['file']
	if file.filename == '':
		flash('No file selected.', 'danger')
		return redirect(url_for('admin.admin_api_keys'))

	try:
		data = json.load(file)
		imported, skipped = 0, 0

		for item in data:
			if APIKey.query.filter_by(api_key=item['api_key']).first():
				skipped += 1
				continue
			k = APIKey(
				label=item.get('label', 'Imported'),
				api_key=item['api_key'],
				sender_identifier=item.get('sender_identifier'),
				counterparty_ref=item.get('counterparty_ref'),
				auto_sync=item.get('auto_sync', True),
				is_active=item.get('is_active', True),
				created_by=current_user.id
			)
			db.session.add(k)
			imported += 1

		db.session.commit()
		flash(f'Imported {imported} API keys, skipped {skipped} duplicates.', 'success')
	except Exception as e:
		flash(f'Import failed: {str(e)}', 'danger')

	return redirect(url_for('admin.admin_api_keys'))


@admin_bp.route('/admin/log')
@role_required('admin')
def admin_log():
	page = request.args.get('page', 1, type=int)
	per_page = 50
	q = SyncLog.query

	f_status = request.args.get('status')
	f_type = request.args.get('type')
	f_api = request.args.get('api', type=int)
	f_user = request.args.get('user', type=int)
	f_days = request.args.get('days', type=int)

	if f_status: q = q.filter(SyncLog.status == f_status)
	if f_type: q = q.filter(SyncLog.sync_type == f_type)
	if f_api: q = q.filter(SyncLog.api_key_id == f_api)
	if f_user: q = q.filter(SyncLog.user_id == f_user)
	if f_days: q = q.filter(SyncLog.created_at >= datetime.now(timezone.utc) - timedelta(days=f_days))

	pagination = q.order_by(desc(SyncLog.created_at)).paginate(
		page=page, per_page=per_page, error_out=False
	)

	return render_template('admin/log.html',
		logs=pagination.items,
		pagination=pagination,
		api_keys=APIKey.query.all(),
		users=User.query.all())


@admin_bp.route('/admin/log/<int:log_id>/details')
@role_required('admin')
def admin_log_details(log_id):
	log = SyncLog.query.get_or_404(log_id)
	return render_template('admin/log_details.html', log=log)
