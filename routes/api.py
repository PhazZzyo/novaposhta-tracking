# routes/api.py
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from extensions import db
from models import APIKey, Client
from services.novaposhta import NovaPoshtaAPI

api_bp = Blueprint('api', __name__)


def role_required(*roles):
	def decorator(f):
		@wraps(f)
		def decorated_function(*args, **kwargs):
			if current_user.role not in roles:
				return jsonify({'error': 'Access denied'}), 403
			return f(*args, **kwargs)
		return decorated_function
	return decorator


@api_bp.route('/api/search-cities')
@login_required
def search_cities_api():
	"""Search cities for autocomplete"""
	query = request.args.get('q', '').strip()
	if len(query) < 2:
		return jsonify([])
	try:
		api_key = APIKey.query.filter_by(is_active=True).first()
		if not api_key:
			return jsonify({'error': 'No API key'}), 400
		api = NovaPoshtaAPI(api_key.api_key)
		cities, _ = api.search_cities(query)
		return jsonify([{
			'ref': city['Ref'],
			'name': city['Description']
		} for city in cities[:10]])
	except Exception as e:
		return jsonify({'error': str(e)}), 500


@api_bp.route('/api/warehouses/<city_ref>')
@login_required
def get_warehouses_api(city_ref):
	"""Get warehouses for selected city"""
	try:
		api_key = APIKey.query.filter_by(is_active=True).first()
		if not api_key:
			return jsonify({'error': 'No API key'}), 400
		api = NovaPoshtaAPI(api_key.api_key)
		warehouses, _ = api.get_warehouses(city_ref)
		return jsonify([{
			'ref': wh['Ref'],
			'description': wh['Description'],
			'number': wh.get('Number', '')
		} for wh in warehouses])
	except Exception as e:
		return jsonify({'error': str(e)}), 500


@api_bp.route('/api/clients/recent')
@login_required
def get_recent_clients():
	"""Get recently used clients"""
	clients = Client.query.filter_by(
		created_by=current_user.id
	).order_by(
		Client.last_used.desc().nullslast(),
		Client.created_at.desc()
	).limit(20).all()

	return jsonify([{
		'id': c.id,
		'name': c.name,
		'phone': c.phone,
		'city': c.city,
		'city_ref': c.city_ref,
		'warehouse': c.warehouse,
		'warehouse_ref': c.warehouse_ref,
		'contact_person': c.contact_person,
		'counterparty_ref': c.counterparty_ref,
		'contact_ref': c.contact_ref,
		'has_uuids': bool(c.counterparty_ref)
	} for c in clients])


@api_bp.route('/api/fetch-sender-uuids', methods=['POST'])
@role_required('admin')
def fetch_sender_uuids():
	"""Auto-fetch sender UUIDs from Nova Poshta API"""
	try:
		data = request.json
		api_key = data['api_key']
		api = NovaPoshtaAPI(api_key)

		# Get counterparty
		counterparties, _ = api._post('Counterparty', 'getCounterparties', {
			'CounterpartyProperty': 'Sender',
			'Page': '1'
		})
		if not counterparties:
			return jsonify({'success': False, 'error': 'No sender found'})

		cp = counterparties[0]
		counterparty_ref = cp['Ref']

		# Get contact persons
		contacts, _ = api._post('Counterparty', 'getCounterpartyContactPersons', {
			'Ref': counterparty_ref,
			'Page': '1'
		})
		contact_ref = contacts[0]['Ref'] if contacts else None
		contact_description = contacts[0].get('Description', '') if contacts else ''

		# Get addresses
		addresses, _ = api._post('Counterparty', 'getCounterpartyAddresses', {
			'Ref': counterparty_ref,
			'CounterpartyProperty': 'Sender'
		})
		warehouse_ref = addresses[0]['Ref'] if addresses else None
		city_ref = addresses[0].get('CityRef') if addresses else None

		# Get phone
		phone = None
		if contacts:
			phones_data = contacts[0].get('Phones', '')
			if phones_data:
				phone_str = str(phones_data).strip().replace('+', '')
				if phone_str.startswith('380') and len(phone_str) == 12:
					phone = '0' + phone_str[3:]
				elif len(phone_str) == 10:
					phone = phone_str

		return jsonify({
			'success': True,
			'counterparty_ref': counterparty_ref,
			'city_ref': city_ref,
			'warehouse_ref': warehouse_ref,
			'contact_ref': contact_ref,
			'contact_name': contact_description,
			'phone': phone,
			'description': contact_description or cp.get('Description', ''),
			'city_description': addresses[0].get('CityDescription', '') if addresses else ''
		})
	except Exception as e:
		return jsonify({'success': False, 'error': str(e)})
