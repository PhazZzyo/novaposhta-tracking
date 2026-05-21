# routes/packages.py
import time
import requests
from datetime import datetime, timezone, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from sqlalchemy import desc
from extensions import db
from models import Package, APIKey, UserAPITracking, Client, SyncLog
from services.novaposhta import NovaPoshtaAPI

packages_bp = Blueprint('packages', __name__)


# ============================================================
# HELPERS
# ============================================================

def _get_user_timezone():
	from app import get_user_timezone
	return get_user_timezone()


def _cooldown_ok(key):
	from app import cooldown_ok
	return cooldown_ok(key)


def _sync_packages(key, **kwargs):
	from app import sync_packages
	return sync_packages(key, **kwargs)


def _get_package_trends(api_ids, days=30):
	from app import get_package_trends
	return get_package_trends(api_ids, days)


def _get_api_ids():
	"""Get API key IDs for current user"""
	if current_user.role == 'admin':
		return [k.id for k in APIKey.query.filter_by(is_active=True).all()]
	return [t.api_key_id for t in UserAPITracking.query.filter_by(user_id=current_user.id).all()]


def _collect_seats(data):
	"""Collect seat data from request. Returns (seats_data, seats_amount, total_weight)"""
	seats_data = []
	seats_amount = 0

	for i in range(1, 100):
		weight = data.get(f'seat_{i}_weight')
		if not weight:
			break
		seats_amount += 1
		seats_data.append({
			'volumetricWidth': int(data.get(f'seat_{i}_width') or 10),
			'volumetricLength': int(data.get(f'seat_{i}_length') or 10),
			'volumetricHeight': int(data.get(f'seat_{i}_height') or 10),
			'weight': float(weight)
		})

	if seats_amount == 0:
		seats_amount = 1
		seats_data = [{
			'volumetricWidth': 10,
			'volumetricLength': 10,
			'volumetricHeight': 10,
			'weight': float(data.get('weight', 1.0))
		}]

	total_weight = sum(s['weight'] for s in seats_data)
	return seats_data, seats_amount, total_weight


def _save_or_update_client(data, recipient_cp=None):
	"""Save or update client record"""
	if not data.get('save_client') or not data.get('recipient_phone'):
		return

	client = Client.query.filter_by(
		phone=data['recipient_phone'],
		created_by=current_user.id
	).first()

	if client:
		client.name = data.get('recipient_name', '')
		client.city = data.get('recipient_city')
		client.city_ref = data.get('recipient_city_ref')
		client.warehouse = data.get('recipient_warehouse')
		client.warehouse_ref = data.get('recipient_warehouse_ref')
		client.contact_person = data.get('recipient_contact')
		client.last_used = datetime.now(_get_user_timezone())
	else:
		client = Client(
			name=data.get('recipient_name', ''),
			phone=data['recipient_phone'],
			city=data.get('recipient_city'),
			city_ref=data.get('recipient_city_ref'),
			warehouse=data.get('recipient_warehouse'),
			warehouse_ref=data.get('recipient_warehouse_ref'),
			contact_person=data.get('recipient_contact'),
			created_by=current_user.id
		)
		db.session.add(client)

	if recipient_cp:
		client.counterparty_ref = recipient_cp['counterparty_ref']
		client.contact_ref = recipient_cp['contact_ref']


def _get_recipient_uuids(data, api_key_obj):
	"""Get recipient UUIDs from cache or Nova Poshta API"""
	# Try cache first
	client = Client.query.filter_by(
		phone=data.get('recipient_phone', ''),
		created_by=current_user.id
	).first()

	if client and client.counterparty_ref and client.contact_ref:
		print(f"✅ Using cached recipient UUIDs")
		return {
			'counterparty_ref': client.counterparty_ref,
			'contact_ref': client.contact_ref
		}

	# Fetch from Nova Poshta
	print(f"⚙️ Fetching recipient UUIDs from Nova Poshta...")
	api = NovaPoshtaAPI(api_key_obj.api_key)
	return api.create_or_get_recipient(
		data['recipient_name'],
		data['recipient_phone']
	)


def _build_np_payload(pkg, data, seats_data, seats_amount, total_weight, recipient_cp, api_key_obj):
	"""Build Nova Poshta API request payload"""
	np_data = {
		'apiKey': api_key_obj.api_key,
		'modelName': 'InternetDocument',
		'calledMethod': 'save',
		'methodProperties': {
			'PayerType': data.get('payer_type', 'Recipient'),
			'PaymentMethod': pkg.payment_method,
			'DateTime': datetime.now(_get_user_timezone()).strftime('%d.%m.%Y'),
			'CargoType': pkg.cargo_type,
			'VolumeGeneral': '0.001',
			'Weight': str(total_weight),
			'ServiceType': 'WarehouseWarehouse',
			'SeatsAmount': str(seats_amount),
			'Description': pkg.description,
			'Cost': str(pkg.cost),
			# Sender
			'CitySender': data.get('sender_city_ref'),
			'Sender': data.get('sender_ref'),
			'SenderAddress': data.get('sender_warehouse_ref'),
			'ContactSender': data.get('sender_contact_ref'),
			'SendersPhone': data.get('sender_phone'),
			# Recipient
			'Recipient': recipient_cp['counterparty_ref'],
			'ContactRecipient': recipient_cp['contact_ref'],
			'CityRecipient': data.get('recipient_city_ref'),
			'RecipientAddress': data.get('recipient_warehouse_ref'),
			'RecipientsPhone': pkg.recipient_phone,
		}
	}

	if seats_data:
		np_data['methodProperties']['OptionsSeat'] = [
			{
				'volumetricVolume': str(s['volumetricWidth'] * s['volumetricLength'] * s['volumetricHeight'] / 4000),
				'volumetricWidth': str(s['volumetricWidth']),
				'volumetricLength': str(s['volumetricLength']),
				'volumetricHeight': str(s['volumetricHeight']),
				'weight': str(s['weight'])
			}
			for s in seats_data
		]

	return np_data


def _call_novaposhta_api(pkg, data, seats_data, seats_amount, total_weight, api_key_obj):
	"""Call Nova Poshta API to create package. Returns (success, message)"""
	try:
		recipient_cp = _get_recipient_uuids(data, api_key_obj)
		np_data = _build_np_payload(pkg, data, seats_data, seats_amount, total_weight, recipient_cp, api_key_obj)

		response = requests.post('https://api.novaposhta.ua/v2.0/json/', json=np_data, timeout=10)
		result = response.json()

		if result.get('success'):
			package_data = result['data'][0]
			pkg.tracking_number = package_data.get('IntDocNumber')
			pkg.status = 'Нова'
			pkg.draft_status = 'sent'
			pkg.error_message = None
			_save_or_update_client(data, recipient_cp)
			db.session.commit()
			return True, f'Package created! TTN: {pkg.tracking_number}'
		else:
			errors = result.get('errors', [])
			error_msg = errors[0] if errors else 'Unknown error'
			pkg.draft_status = 'failed'
			pkg.error_message = error_msg
			db.session.commit()
			return False, error_msg

	except Exception as e:
		pkg.draft_status = 'failed'
		pkg.error_message = str(e)
		db.session.commit()
		return False, str(e)


# ============================================================
# ROUTES
# ============================================================

@packages_bp.route('/dashboard')
@login_required
def dashboard():
	if current_user.role == 'admin':
		api_keys = APIKey.query.filter_by(is_active=True).all()
	else:
		api_keys = [tr.api_key for tr in current_user.tracked_apis if tr.api_key.is_active]

	api_ids = [k.id for k in api_keys]

	if api_ids:
		all_pkgs = Package.query.filter(Package.api_key_id.in_(api_ids))
		total = all_pkgs.count()
		in_transit = all_pkgs.filter(
			Package.is_delivered == False,
			Package.status_code != '2',
			~Package.status_code.in_(['7', '8'])
		).count()
		at_branch = all_pkgs.filter(Package.status_code.in_(['7', '8'])).count()
		completed = all_pkgs.filter(Package.is_delivered == True).count()
		trends = _get_package_trends(api_ids, days=30)
	else:
		total = in_transit = at_branch = completed = 0
		trends = {'dates': [], 'in_transit': [], 'at_branch': [], 'completed': []}

	return render_template('dashboard.html',
		api_keys=api_keys,
		total_packages=total,
		in_transit=in_transit,
		at_branch=at_branch,
		completed=completed,
		trends=trends,
		now=datetime.now(_get_user_timezone()))


@packages_bp.route('/packages')
@login_required
def packages():
	page = request.args.get('page', 1, type=int)
	per_page = current_user.items_per_page
	view = request.args.get('view', current_user.view_mode)
	filter_type = request.args.get('filter', 'all')

	if current_user.role == 'admin':
		available_keys = APIKey.query.filter_by(is_active=True).all()
		api_ids = [k.id for k in available_keys]
	else:
		tracked = UserAPITracking.query.filter_by(user_id=current_user.id).all()
		api_ids = [t.api_key_id for t in tracked]
		available_keys = APIKey.query.filter(
			APIKey.id.in_(api_ids),
			APIKey.is_active == True
		).all()

	q = Package.query.filter(Package.api_key_id.in_(api_ids)) if api_ids else Package.query.filter_by(id=-1)

	if filter_type == 'delivering':
		q = q.filter(
			Package.is_delivered == False,
			~db.and_(Package.direction == 'incoming', Package.status_code.in_(['7', '8']))
		)
	elif filter_type == 'ready':
		q = q.filter(
			Package.direction == 'incoming',
			Package.status_code.in_(['7', '8'])
		)
	elif filter_type == 'delivered':
		q = q.filter(Package.is_delivered == True)

	direction = request.args.get('direction')
	if direction and direction != 'all':
		q = q.filter_by(direction=direction)

	api_filter = request.args.getlist('api')
	if api_filter:
		q = q.filter(Package.api_key_id.in_([int(x) for x in api_filter]))

	days = request.args.get('days', type=int)
	if days:
		q = q.filter(Package.date_created >= datetime.now() - timedelta(days=days))

	q = q.order_by(desc(Package.date_created))
	pagination = q.paginate(page=page, per_page=per_page, error_out=False)

	return render_template('packages.html',
		packages=pagination.items,
		pagination=pagination,
		api_keys=available_keys,
		view_mode=view,
		current_filter=filter_type)


@packages_bp.route('/package/<int:package_id>')
@login_required
def package_detail(package_id):
	pkg = Package.query.get_or_404(package_id)
	if current_user.role != 'admin':
		ids = [tr.api_key_id for tr in current_user.tracked_apis]
		if pkg.api_key_id not in ids:
			return jsonify({'error': 'Access denied'}), 403
	return render_template('package_detail.html', package=pkg)


@packages_bp.route('/package/invoice/<tracking_number>')
@login_required
def package_invoice(tracking_number):
	pkg = Package.query.filter_by(tracking_number=tracking_number).first_or_404()
	if not pkg.api_key:
		flash('Package has no API key', 'danger')
		return redirect(url_for('packages.packages'))
	api_key = pkg.api_key.api_key
	url = f'https://my.novaposhta.ua/orders/printDocument/orders[]/{tracking_number}/type/pdf/apiKey/{api_key}'
	return redirect(url)


@packages_bp.route('/sync/<int:api_key_id>', methods=['POST'])
@login_required
def sync_api(api_key_id):
	key = APIKey.query.get_or_404(api_key_id)
	if current_user.role != 'admin':
		ids = [tr.api_key_id for tr in current_user.tracked_apis]
		if api_key_id not in ids:
			return jsonify({'error': 'Access denied'}), 403

	ok, msg = _cooldown_ok(key)
	if not ok:
		return jsonify({'error': msg}), 429

	success, message = _sync_packages(key, days=5, sync_type='manual', user_id=current_user.id, direction='both')
	if success:
		return jsonify({'success': True, 'message': message})
	return jsonify({'error': message}), 500


@packages_bp.route('/sync/all', methods=['POST'])
@login_required
def sync_all():
	if current_user.role == 'admin':
		keys = APIKey.query.filter_by(is_active=True).all()
	else:
		keys = [tr.api_key for tr in current_user.tracked_apis if tr.api_key.is_active]

	results = []
	for i, key in enumerate(keys):
		if i > 0:
			time.sleep(7)
		ok, msg = _cooldown_ok(key)
		if not ok:
			results.append(f"<strong>{key.label}</strong>: {msg}")
			continue
		success, message = _sync_packages(key, days=5, sync_type='manual', user_id=current_user.id, direction='both')
		results.append(f"<strong>{key.label}</strong>: {message}")

	return jsonify({'success': True, 'message': '<br>'.join(results)})


@packages_bp.route('/api/draft/<int:draft_id>', methods=['GET'])
@login_required
def get_draft(draft_id):
	pkg = Package.query.get_or_404(draft_id)
	if current_user.role != 'admin' and pkg.author != current_user.username:
		return jsonify({'success': False, 'error': 'Unauthorized'}), 403
	if pkg.draft_status not in ['draft', 'failed']:
		return jsonify({'success': False, 'error': 'Only drafts can be edited'}), 400

	def safe_get(obj, attr, default=None):
		return getattr(obj, attr, default) if hasattr(obj, attr) else default

	return jsonify({
		'success': True,
		'draft': {
			'id': pkg.id,
			'api_key_id': pkg.api_key_id,
			'direction': safe_get(pkg, 'direction', 'outgoing'),
			'sender_name': safe_get(pkg, 'sender_name'),
			'sender_phone': safe_get(pkg, 'sender_phone'),
			'sender_city': safe_get(pkg, 'sender_city'),
			'recipient_name': pkg.recipient_name,
			'recipient_phone': safe_get(pkg, 'recipient_phone'),
			'recipient_city': pkg.recipient_city,
			'recipient_warehouse': safe_get(pkg, 'recipient_warehouse'),
			'recipient_contact': safe_get(pkg, 'recipient_contact'),
			'weight': float(pkg.weight) if pkg.weight else 1.0,
			'seats': safe_get(pkg, 'seats_amount', 1),
			'cost': float(safe_get(pkg, 'cost', 0)) if safe_get(pkg, 'cost') else 0,
			'description': pkg.description or '',
			'payment_method': safe_get(pkg, 'payment_method', 'Cash'),
			'cargo_type': safe_get(pkg, 'cargo_type', 'Parcel')
		}
	})


@packages_bp.route('/package/create', methods=['POST'])
@login_required
def create_package():
	data = request.json
	action = data.get('action', 'send')

	if action == 'send':
		api_key_id = data.get('api_key_id')
		if not api_key_id:
			return jsonify({'success': False, 'error': 'Please select an API key'}), 400
		api_key_id = int(api_key_id)
		APIKey.query.get_or_404(api_key_id)
		if current_user.role != 'admin':
			if not UserAPITracking.query.filter_by(user_id=current_user.id, api_key_id=api_key_id).first():
				return jsonify({'success': False, 'error': 'Access denied'}), 403
		if not data.get('recipient_city_ref'):
			return jsonify({'success': False, 'error': 'Recipient city required'}), 400
		if not data.get('recipient_warehouse_ref'):
			return jsonify({'success': False, 'error': 'Recipient warehouse required'}), 400

	seats_data, seats_amount, total_weight = _collect_seats(data)

	# Save client early (without UUIDs yet)
	_save_or_update_client(data)

	# Generate temp TTN
	temp_ttn = f'DRAFT-{datetime.now().strftime("%Y%m%d%H%M%S")}-{current_user.id}' \
		if action == 'draft' \
		else f'PENDING-{datetime.now().strftime("%Y%m%d%H%M%S")}-{current_user.id}'

	# Always save to DB first
	pkg = Package(
		api_key_id=data.get('api_key_id'),
		author=current_user.username,
		draft_status='draft',
		tracking_number=temp_ttn,
		recipient_name=data.get('recipient_name', ''),
		recipient_phone=data.get('recipient_phone', ''),
		recipient_city=data.get('recipient_city', ''),
		recipient_warehouse=data.get('recipient_warehouse', ''),
		recipient_contact=data.get('recipient_contact', ''),
		description=data.get('description', 'Посилка'),
		weight=total_weight,
		seats_amount=seats_amount,
		seats_data=seats_data,
		cost=float(data.get('cost', 0)),
		payment_method=data.get('payment_method', 'Cash'),
		cargo_type=data.get('cargo_type', 'Parcel'),
		direction='outgoing',
		date_created=datetime.now(_get_user_timezone())
	)
	db.session.add(pkg)
	db.session.commit()

	if action == 'draft':
		return jsonify({'success': True, 'message': 'Draft saved!', 'package_id': pkg.id})

	# Send to Nova Poshta
	api_key_obj = APIKey.query.get(pkg.api_key_id)
	if not api_key_obj:
		return jsonify({'success': False, 'error': 'API key not found'}), 400

	success, message = _call_novaposhta_api(pkg, data, seats_data, seats_amount, total_weight, api_key_obj)

	if success:
		return jsonify({'success': True, 'message': message})
	return jsonify({'success': False, 'error': message, 'package_id': pkg.id})


@packages_bp.route('/api/package/<int:package_id>/update', methods=['PUT'])
@login_required
def update_draft(package_id):
	pkg = Package.query.get_or_404(package_id)

	if current_user.role != 'admin' and pkg.author != current_user.username:
		return jsonify({'success': False, 'error': 'Unauthorized'}), 403
	if pkg.draft_status not in ['draft', 'failed']:
		return jsonify({'success': False, 'error': 'Only drafts can be updated'}), 400

	data = request.json
	action = data.get('action', 'send')

	if action == 'send':
		if not data.get('api_key_id'):
			return jsonify({'success': False, 'error': 'API key is required'}), 400
		api_key_id = int(data.get('api_key_id'))
		APIKey.query.get_or_404(api_key_id)
		if current_user.role != 'admin':
			if not UserAPITracking.query.filter_by(user_id=current_user.id, api_key_id=api_key_id).first():
				return jsonify({'success': False, 'error': 'Access denied'}), 403
		if not data.get('recipient_city_ref'):
			return jsonify({'success': False, 'error': 'Recipient city required'}), 400
		if not data.get('recipient_warehouse_ref'):
			return jsonify({'success': False, 'error': 'Recipient warehouse required'}), 400

	seats_data, seats_amount, total_weight = _collect_seats(data)
	_save_or_update_client(data)

	# Update package fields
	pkg.api_key_id = data.get('api_key_id')
	pkg.recipient_name = data.get('recipient_name', '')
	pkg.recipient_phone = data.get('recipient_phone', '')
	pkg.recipient_city = data.get('recipient_city', '')
	pkg.recipient_warehouse = data.get('recipient_warehouse', '')
	pkg.recipient_contact = data.get('recipient_contact', '')
	pkg.description = data.get('description', 'Посилка')
	pkg.weight = total_weight
	pkg.seats_amount = seats_amount
	pkg.seats_data = seats_data
	pkg.cost = float(data.get('cost', 0))
	pkg.payment_method = data.get('payment_method', 'Cash')
	pkg.cargo_type = data.get('cargo_type', 'Parcel')
	db.session.commit()

	if action == 'draft':
		pkg.draft_status = 'draft'
		pkg.error_message = None
		db.session.commit()
		return jsonify({'success': True, 'message': 'Draft updated!'})

	api_key_obj = APIKey.query.get(pkg.api_key_id)
	if not api_key_obj:
		return jsonify({'success': False, 'error': 'API key not found'}), 400

	success, message = _call_novaposhta_api(pkg, data, seats_data, seats_amount, total_weight, api_key_obj)

	if success:
		return jsonify({'success': True, 'message': message})
	return jsonify({'success': False, 'error': message})


@packages_bp.route('/package/<int:package_id>/delete', methods=['POST'])
@login_required
def delete_package(package_id):
	pkg = Package.query.get_or_404(package_id)
	if current_user.role != 'admin' and pkg.author != current_user.username:
		flash('You can only delete your own drafts', 'danger')
		return redirect(url_for('packages.packages'))
	if pkg.draft_status not in ['draft', 'failed'] and pkg.status_code != '2':
		flash('Only draft or failed packages can be deleted', 'warning')
		return redirect(url_for('packages.packages'))
	ttn = pkg.tracking_number or f"Draft #{pkg.id}"
	db.session.delete(pkg)
	db.session.commit()
	flash(f'Package {ttn} deleted', 'success')
	return redirect(url_for('packages.packages'))
