# app.py
import os
import time
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo, available_timezones
from collections import defaultdict
from functools import wraps

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, session
from flask_login import current_user
from extensions import db, login_manager, migrate
from translations import TRANSLATIONS

DEFAULT_TIMEZONE = 'Europe/Kyiv'


# ============================================================
# TIMEZONE HELPERS
# ============================================================

def get_user_timezone():
	tz_name = DEFAULT_TIMEZONE
	if current_user.is_authenticated and current_user.timezone:
		tz_name = current_user.timezone
	return ZoneInfo(tz_name)


def utc_to_local(dt):
	if not dt:
		return None
	if dt.tzinfo is None:
		dt = dt.replace(tzinfo=timezone.utc)
	return dt.astimezone(get_user_timezone())


# ============================================================
# TRANSLATION HELPER
# ============================================================

def t(key):
	lang = current_user.language if current_user.is_authenticated else session.get('language', 'uk')
	return TRANSLATIONS.get(lang, TRANSLATIONS['uk']).get(key, key)


# ============================================================
# BUSINESS LOGIC HELPERS
# ============================================================

def can_view_invoice(package):
	"""Invoice available only for in-transit packages with real TTN"""
	if not package.tracking_number or package.tracking_number.startswith('DRAFT-'):
		return False
	if package.status_code in ['draft', 'failed', 'deleted', '2']:
		return False
	if package.is_delivered:
		return False
	return True


def cooldown_ok(api_key_obj):
	"""Check if API key sync cooldown has passed"""
	if not api_key_obj.last_sync:
		return True, None
	now = datetime.now(timezone.utc)
	db_time = api_key_obj.last_sync
	if db_time.tzinfo is None:
		db_time = db_time.replace(tzinfo=timezone.utc)
	diff = now - db_time
	cd = timedelta(minutes=5)
	if diff < cd:
		mins = int((cd - diff).total_seconds() / 60) + 1
		return False, f'Wait {mins} min'
	return True, None


def role_required(*roles):
	"""Decorator to restrict access by user role"""
	def decorator(f):
		@wraps(f)
		def wrapped(*args, **kwargs):
			if not current_user.is_authenticated:
				from flask import redirect, url_for
				return redirect(url_for('auth.login'))
			if current_user.role not in roles:
				from flask import flash, redirect, url_for
				flash('Access denied.', 'danger')
				return redirect(url_for('packages.dashboard'))
			return f(*args, **kwargs)
		return wrapped
	return decorator


def get_package_trends(api_key_ids, days=30):
	"""Calculate daily package creation counts for trend chart"""
	from models import Package
	user_tz = get_user_timezone()
	now = datetime.now(user_tz)
	from_date = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days - 1)

	packages = Package.query.filter(Package.api_key_id.in_(api_key_ids)).all()

	trends = {
		'dates': [],
		'in_transit': [],
		'at_branch': [],
		'completed': [],
		'incoming': [],
		'outgoing': []
	}

	for i in range(days):
		day_start = from_date + timedelta(days=i)
		day_end = day_start + timedelta(days=1)
		day_start_naive = day_start.replace(tzinfo=None)
		day_end_naive = day_end.replace(tzinfo=None)

		trends['dates'].append(day_start.strftime('%d.%m'))

		in_transit = at_branch = completed = incoming = outgoing = 0

		for pkg in packages:
			if not pkg.date_created:
				continue
			pkg_created = pkg.date_created.replace(tzinfo=None) if pkg.date_created.tzinfo else pkg.date_created
			if day_start_naive <= pkg_created < day_end_naive:
				if pkg.direction == 'incoming':
					incoming += 1
				else:
					outgoing += 1
				if pkg.is_delivered:
					completed += 1
				elif pkg.status_code in ['7', '8']:
					at_branch += 1
				elif pkg.status_code != '2':
					in_transit += 1

		trends['in_transit'].append(in_transit)
		trends['at_branch'].append(at_branch)
		trends['completed'].append(completed)
		trends['incoming'].append(incoming)
		trends['outgoing'].append(outgoing)

	return trends


# ============================================================
# SYNC FUNCTION
# ============================================================

def sync_packages(api_key_obj, days=7, sync_type='manual', user_id=None, direction='both'):
	"""Sync packages from Nova Poshta API"""
	from models import Package, SyncLog
	from services.novaposhta import NovaPoshtaAPI, _parse_dt, is_delivered
	from services.notifications import notify_package_status_change

	# ✅ One instance = one session = all calls reuse same TCP connection
	api = NovaPoshtaAPI(api_key_obj.api_key)
	results = []

	# STEP 1: FETCH OUTGOING PACKAGES
	if direction in ['outgoing', 'both']:
		try:
			date_from = datetime.now() - timedelta(days=days)
			docs, full_response = api.get_documents_list(date_from)
			fetched, created = 0, 0

			for doc in docs:
				tn = doc.get('IntDocNumber')
				if not tn:
					continue
				fetched += 1
				pkg = Package.query.filter_by(tracking_number=tn).first()
				if not pkg:
					pkg = Package(api_key_id=api_key_obj.id, tracking_number=tn)
					db.session.add(pkg)
					created += 1

				pkg.direction = 'outgoing'
				pkg.sender_city = doc.get('CitySenderDescription')
				pkg.sender_name = doc.get('SenderFullNameEW') or doc.get('SenderDescription')
				pkg.sender_phone = doc.get('PhoneSender')
				pkg.recipient_city = doc.get('CityRecipientDescription')
				pkg.recipient_name = doc.get('RecipientFullName') or doc.get('RecipientDescription')
				pkg.recipient_phone = doc.get('PhoneRecipient')
				pkg.recipient_warehouse = doc.get('RecipientAddressDescription')
				pkg.status = doc.get('StateName')
				pkg.status_code = str(doc.get('StateId', ''))
				pkg.date_created = _parse_dt(doc.get('DateTime'))
				pkg.planned_delivery_date = _parse_dt(doc.get('ScheduledDeliveryDate'))
				if pkg.planned_delivery_date:
					pkg.planned_delivery_date = pkg.planned_delivery_date.date()
				pkg.actual_delivery_date = _parse_dt(doc.get('ActualDeliveryDate'))
				pkg.package_cost = float(doc.get('Cost') or 0)
				pkg.shipment_cost = float(doc.get('DocumentCost') or 0)
				pkg.weight = float(doc.get('DocumentWeight') or 0)
				pkg.package_count = int(doc.get('SeatsAmount') or 1)
				pkg.description = doc.get('Description')
				pkg.is_delivered = is_delivered(pkg.status_code)
				pkg.raw_data = doc

			db.session.commit()

			if fetched > 0:
				summary = f'Out: {fetched}📦 ({created}🆕)'
				results.append(summary)
				log = SyncLog(
					api_key_id=api_key_obj.id, user_id=user_id, sync_type=sync_type,
					sync_direction='outgoing', packages_fetched=fetched,
					packages_created=created, packages_updated=0,
					status='success', sync_summary=summary, api_response=full_response
				)
				db.session.add(log)
				db.session.commit()

		except Exception as e:
			summary = f'Out: ❌ {str(e)[:50]}'
			results.append(summary)
			log = SyncLog(
				api_key_id=api_key_obj.id, user_id=user_id, sync_type=sync_type,
				sync_direction='outgoing', status='error',
				error_message=str(e), sync_summary=summary
			)
			db.session.add(log)
			db.session.commit()

	# STEP 2: FETCH INCOMING PACKAGES
	if direction in ['incoming', 'both'] and api_key_obj.sender_identifier:
		try:
			incoming_docs, full_response = api.get_incoming_documents(api_key_obj.sender_identifier)
			fetched, created = 0, 0

			for result_group in incoming_docs:
				for doc in result_group.get('result', []):
					tn = doc.get('Number')
					if not tn:
						continue
					fetched += 1
					pkg = Package.query.filter_by(tracking_number=tn).first()
					if not pkg:
						pkg = Package(api_key_id=api_key_obj.id, tracking_number=tn)
						db.session.add(pkg)
						created += 1

					pkg.direction = 'incoming'
					pkg.sender_city = doc.get('CitySenderDescription')
					pkg.sender_name = doc.get('SenderName')
					pkg.sender_phone = doc.get('PhoneSender')
					pkg.recipient_city = doc.get('CityRecipientDescription')
					pkg.recipient_name = doc.get('RecipientName')
					pkg.recipient_phone = doc.get('PhoneRecipient')
					pkg.recipient_warehouse = doc.get('RecipientAddressDescription')
					pkg.status = doc.get('TrackingStatusName')
					pkg.status_code = str(doc.get('TrackingStatusCode', ''))
					pkg.date_created = _parse_dt(doc.get('DateTime'))
					pkg.planned_delivery_date = _parse_dt(doc.get('ScheduledDeliveryDate'))
					if pkg.planned_delivery_date:
						pkg.planned_delivery_date = pkg.planned_delivery_date.date()
					pkg.actual_delivery_date = _parse_dt(doc.get('ReceivingDateTime'))
					pkg.package_cost = float(doc.get('Cost') or 0)
					pkg.shipment_cost = float(doc.get('DocumentCost') or 0)
					pkg.weight = float(doc.get('DocumentWeight') or 0)
					pkg.package_count = int(doc.get('SeatsAmount') or 1)
					pkg.description = doc.get('CargoDescription')
					pkg.is_delivered = is_delivered(pkg.status_code)
					pkg.raw_data = doc

			db.session.commit()

			if fetched > 0:
				summary = f'In: {fetched}📦 ({created}🆕)'
				results.append(summary)
				log = SyncLog(
					api_key_id=api_key_obj.id, user_id=user_id, sync_type=sync_type,
					sync_direction='incoming', packages_fetched=fetched,
					packages_created=created, packages_updated=0,
					status='success', sync_summary=summary, api_response=full_response
				)
				db.session.add(log)
				db.session.commit()

		except Exception as e:
			summary = f'In: ❌ {str(e)[:50]}'
			results.append(summary)
			log = SyncLog(
				api_key_id=api_key_obj.id, user_id=user_id, sync_type=sync_type,
				sync_direction='incoming', status='error',
				error_message=str(e), sync_summary=summary
			)
			db.session.add(log)
			db.session.commit()

	# STEP 3: UPDATE STATUS FOR ACTIVE PACKAGES
	try:
		active_packages = Package.query.filter_by(
			api_key_id=api_key_obj.id,
			is_delivered=False
		).all()

		if active_packages:
			tracking_numbers = [pkg.tracking_number for pkg in active_packages]
			updated = 0

			for i in range(0, len(tracking_numbers), 100):
				batch = tracking_numbers[i:i + 100]
				try:
					status_data, _ = api.get_status_documents(batch)

					for status_doc in status_data:
						tn = status_doc.get('Number')
						if not tn:
							continue
						pkg = Package.query.filter_by(tracking_number=tn).first()
						if not pkg:
							continue

						old_status = pkg.status_code
						new_status = str(status_doc.get('StatusCode', ''))

						if old_status != new_status:
							pkg.status_code = new_status
							pkg.status = status_doc.get('Status', '')
							pkg.is_delivered = is_delivered(new_status)

							if pkg.is_delivered and not pkg.actual_delivery_date:
								pkg.actual_delivery_date = datetime.now(timezone.utc)

							# Send Telegram notification
							notify_package_status_change(pkg, old_status, new_status)

							updated += 1

				except Exception as e:
					print(f"Status update batch error: {e}")
					continue

			db.session.commit()

			if updated > 0:
				status_summary = f'Status: {len(active_packages)}🔄 ({updated}✅)'
				results.append(status_summary)
				log = SyncLog(
					api_key_id=api_key_obj.id, user_id=user_id, sync_type=sync_type,
					sync_direction='status_update', packages_fetched=len(active_packages),
					packages_updated=updated, status='success', sync_summary=status_summary
				)
				db.session.add(log)
				db.session.commit()

	except Exception as e:
		print(f"Status update error: {e}")

	# Update last sync time
	api_key_obj.last_sync = datetime.now(timezone.utc)
	db.session.commit()

	# ✅ Close session - releases TCP connection
	api.session.close()

	return True, ' | '.join(results) if results else 'No updates'


# ============================================================
# APP FACTORY
# ============================================================

def create_app():
	app = Flask(__name__)

	# Config
	app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-this-in-production')
	app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///novaposhta.db')
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
	app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

	# Init extensions
	db.init_app(app)
	migrate.init_app(app, db)
	login_manager.init_app(app)
	login_manager.login_view = 'auth.login'
	login_manager.login_message = ''

	# Register Jinja globals and filters
	app.jinja_env.filters['local_time'] = utc_to_local
	app.jinja_env.filters['warehouse_number'] = _warehouse_number_filter
	app.jinja_env.filters['warehouse_street'] = _warehouse_street_filter
	app.jinja_env.globals['can_view_invoice'] = can_view_invoice
	app.jinja_env.globals['t'] = t
	app.jinja_env.globals['now'] = lambda: datetime.now()

	# Context processors
	@app.context_processor
	def inject_timezone_helpers():
		def format_datetime(dt, fmt='%d.%m.%Y %H:%M'):
			if not dt:
				return '-'
			local = utc_to_local(dt)
			return local.strftime(fmt) if local else '-'

		def format_date(dt):
			return format_datetime(dt, '%d.%m.%Y')

		def format_time(dt):
			return format_datetime(dt, '%H:%M')

		return {
			'format_datetime': format_datetime,
			'format_date': format_date,
			'format_time': format_time
		}

	# Register blueprints
	from routes.auth import auth_bp
	from routes.packages import packages_bp
	from routes.admin import admin_bp
	from routes.settings import settings_bp
	from routes.api import api_bp

	app.register_blueprint(auth_bp)
	app.register_blueprint(packages_bp)
	app.register_blueprint(admin_bp)
	app.register_blueprint(settings_bp)
	app.register_blueprint(api_bp)

	return app


# ============================================================
# JINJA FILTERS
# ============================================================

def _warehouse_number_filter(warehouse_name):
	"""Extract warehouse number"""
	import re
	if not warehouse_name:
		return ''
	match = re.search(r'Відділення\s*№?\s*(\d+)', warehouse_name, re.IGNORECASE)
	if match:
		return f"№{match.group(1)}"
	match = re.search(r'Поштомат.*?№?\s*(\d+)', warehouse_name, re.IGNORECASE)
	if match:
		return f"Поштомат №{match.group(1)}"
	return warehouse_name[:20]


def _warehouse_street_filter(warehouse_name):
	"""Extract street address"""
	if not warehouse_name:
		return ''
	if ':' in warehouse_name:
		return warehouse_name.split(':', 1)[1].strip()
	if '(' in warehouse_name:
		return warehouse_name.split('(')[0].strip()
	return warehouse_name


# ============================================================
# LOGIN MANAGER
# ============================================================

@login_manager.user_loader
def load_user(user_id):
	from models import User
	return db.session.get(User, int(user_id))


# ============================================================
# DATABASE INIT
# ============================================================

def init_db(app):
	with app.app_context():
		db.create_all()

		# Safe migrations for new columns
		migrations = [
			"ALTER TABLE packages ADD COLUMN seats_amount INTEGER DEFAULT 1",
			"ALTER TABLE packages ADD COLUMN seats_data JSON",
			"ALTER TABLE packages ADD COLUMN cost NUMERIC(10,2)",
			"ALTER TABLE packages ADD COLUMN payment_method VARCHAR(50)",
			"ALTER TABLE packages ADD COLUMN cargo_type VARCHAR(50)",
			"ALTER TABLE users ADD COLUMN telegram_user_id BIGINT",
			"ALTER TABLE users ADD COLUMN telegram_notifications BOOLEAN DEFAULT 1",
			"ALTER TABLE users ADD COLUMN telegram_linked_at DATETIME",
		]

		for migration in migrations:
			try:
				db.session.execute(db.text(migration))
				db.session.commit()
			except Exception:
				db.session.rollback()

		# Create default admin if not exists
		from models import User
		if not User.query.filter_by(username='sysadmin').first():
			admin = User(
				username='sysadmin',
				full_name='System Administrator',
				role='admin',
				must_change_password=True,
				language='en'
			)
			admin.set_password('sysadmin')
			db.session.add(admin)
			db.session.commit()
			print('✅ Default admin created: sysadmin / sysadmin')


# ============================================================
# ENTRY POINT
# ============================================================

app = create_app()  # Module-level app for Flask-Migrate CLI

if __name__ == '__main__':
	init_db(app)
	is_debug = os.getenv('DEBUG', 'False').lower() == 'true'
	app.run(host='0.0.0.0', port=5000, debug=is_debug)
