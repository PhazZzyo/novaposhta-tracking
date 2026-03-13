"""
Nova Poshta Package Tracking Web Application v1.2
Complete with: Import/Export, Unified sync, Incoming packages, Timezone handling
"""

import os
import json
import requests
import pytz
from datetime import datetime, timedelta
from functools import wraps
from io import BytesIO
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import desc, and_
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-this-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///novaposhta.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = ''

NOVA_POSHTA_API = 'https://api.novaposhta.ua/v2.0/json/'
DEFAULT_TIMEZONE = 'Europe/Kyiv'

# Timezone helper
def get_user_timezone():
    if current_user.is_authenticated and current_user.timezone:
        return pytz.timezone(current_user.timezone)
    return pytz.timezone(DEFAULT_TIMEZONE)

def utc_to_local(dt):
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    return dt.astimezone(get_user_timezone())

app.jinja_env.filters['local_time'] = utc_to_local

# Translations
TRANSLATIONS = {
    'en': {
        'dashboard': 'Dashboard', 'packages': 'Packages', 'settings': 'Settings',
        'logout': 'Logout', 'change_password': 'Change Password', 'admin': 'Admin',
        'users': 'Users', 'api_keys': 'API Keys', 'add_api_key': 'Add API Key',
        'add_user': 'Add User', 'total_packages': 'Total Packages', 'active': 'Active',
        'ready_pickup': 'Ready for Pickup', 'delivering': 'Delivering', 'delivered': 'Delivered',
        'last_sync': 'Last Sync', 'status': 'Status', 'actions': 'Actions', 'sync': 'Sync',
        'view': 'View', 'never': 'Never', 'incoming': 'Incoming', 'outgoing': 'Outgoing',
        'all': 'All', 'filters': 'Filters', 'direction': 'Direction', 'date_range': 'Date Range',
        'apply': 'Apply', 'reset': 'Reset', 'cancel': 'Cancel', 'sender': 'Sender',
        'recipient': 'Recipient', 'created': 'Created', 'save': 'Save Settings',
        'theme': 'Theme', 'light': 'Light', 'dark': 'Dark', 'view_mode': 'View Mode',
        'table': 'Table', 'cards': 'Cards', 'items_per_page': 'Items per page',
        'notify_pickup': 'Notify when ready for pickup', 'track_apis': 'Tracked API Keys',
        'language': 'Language', 'timezone': 'Timezone', 'package_details': 'Package Details',
        'view_invoice': 'View Invoice', 'package_cost': 'Package Cost',
        'shipping_cost': 'Shipping Cost', 'weight': 'Weight',
        'planned_delivery': 'Planned Delivery', 'description': 'Description',
        'no_packages': 'No packages found', 'no_api_keys': 'No API keys configured',
        'syncing': 'Syncing...', 'sync_success': 'Sync successful!', 'error': 'Error',
        'label': 'Label', 'sender_identifier': 'Sender Identifier', 'auto_sync': 'Auto Sync',
        'username': 'Username', 'full_name': 'Full Name', 'role': 'Role',
        'password': 'Password', 'new_password': 'New Password',
        'confirm_password': 'Confirm Password', 'current_password': 'Current Password',
        'save_changes': 'Save Changes', 'create_user': 'Create User',
        'inactive': 'Inactive', 'last_login': 'Last Login', 'edit': 'Edit',
        'login': 'Login', 'remember_me': 'Remember me (30 days)', 'sign_in': 'Sign In',
        'tracking_system': 'Package Tracking System',
        'no_account': 'No account? Contact administrator.',
        'days_1': 'Last 24 hours', 'days_5': 'Last 5 days', 'days_7': 'Last 7 days',
        'days_14': 'Last 14 days', 'days_30': 'Last 30 days', 'all_time': 'All time',
        'sync_all': 'Sync All', 'import_api_keys': 'Import', 'export_api_keys': 'Export',
        'author': 'Author',
    },
    'uk': {
        'dashboard': 'Головна', 'packages': 'Посилки', 'settings': 'Налаштування',
        'logout': 'Вихід', 'change_password': 'Змінити пароль', 'admin': 'Адмін',
        'users': 'Користувачі', 'api_keys': 'API Ключі', 'add_api_key': 'Додати API',
        'add_user': 'Додати користувача', 'total_packages': 'Усього посилок',
        'active': 'Активні', 'ready_pickup': 'Готові до отримання',
        'delivering': 'Доставляються', 'delivered': 'Доставлені',
        'last_sync': 'Остання синхронізація', 'status': 'Статус', 'actions': 'Дії',
        'sync': 'Синхронізувати', 'view': 'Переглянути', 'never': 'Ніколи',
        'incoming': 'Вхідні', 'outgoing': 'Вихідні', 'all': 'Усі',
        'filters': 'Фільтри', 'direction': 'Напрямок', 'date_range': 'Період',
        'apply': 'Застосувати', 'reset': 'Скинути', 'cancel': 'Скасувати',
        'sender': 'Відправник', 'recipient': 'Отримувач', 'created': 'Створено',
        'save': 'Зберегти', 'theme': 'Тема', 'light': 'Світла', 'dark': 'Темна',
        'view_mode': 'Режим перегляду', 'table': 'Таблиця', 'cards': 'Картки',
        'items_per_page': 'Елементів на сторінці',
        'notify_pickup': 'Сповіщати при готовності', 'track_apis': 'Відстежувані API',
        'language': 'Мова', 'timezone': 'Часовий пояс',
        'package_details': 'Деталі посилки', 'view_invoice': 'Переглянути накладну',
        'package_cost': 'Вартість', 'shipping_cost': 'Доставка', 'weight': 'Вага',
        'planned_delivery': 'Планова доставка', 'description': 'Опис',
        'no_packages': 'Посилок не знайдено', 'no_api_keys': 'API ключі відсутні',
        'syncing': 'Синхронізація...', 'sync_success': 'Успішно!', 'error': 'Помилка',
        'label': 'Назва', 'sender_identifier': 'Ідентифікатор',
        'auto_sync': 'Авто синхронізація', 'username': 'Логін',
        'full_name': "Повне ім'я", 'role': 'Роль', 'password': 'Пароль',
        'new_password': 'Новий пароль', 'confirm_password': 'Підтвердити',
        'current_password': 'Поточний пароль', 'save_changes': 'Зберегти зміни',
        'create_user': 'Створити', 'inactive': 'Неактивний',
        'last_login': 'Останній вхід', 'edit': 'Редагувати', 'login': 'Вхід',
        'remember_me': "Запам'ятати (30 днів)", 'sign_in': 'Увійти',
        'tracking_system': 'Система відстеження', 'no_account': 'Зверніться до адміна.',
        'days_1': '24 години', 'days_5': '5 днів', 'days_7': '7 днів',
        'days_14': '14 днів', 'days_30': '30 днів', 'all_time': 'Весь час',
        'sync_all': 'Синхр. все', 'import_api_keys': 'Імпорт', 'export_api_keys': 'Експорт',
        'author': 'Автор',
    }
}

def t(key):
    lang = current_user.language if current_user.is_authenticated else session.get('language', 'uk')
    return TRANSLATIONS.get(lang, TRANSLATIONS['uk']).get(key, key)

app.jinja_env.globals['t'] = t
app.jinja_env.globals['now'] = lambda: datetime.now()

# Models
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(200))
    role = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    must_change_password = db.Column(db.Boolean, default=False)
    theme = db.Column(db.String(10), default='light')
    view_mode = db.Column(db.String(10), default='table')
    items_per_page = db.Column(db.Integer, default=20)
    notify_ready_pickup = db.Column(db.Boolean, default=True)
    language = db.Column(db.String(5), default='uk')
    timezone = db.Column(db.String(50), default=DEFAULT_TIMEZONE)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    tracked_apis = db.relationship('UserAPITracking', back_populates='user', cascade='all, delete-orphan')

    def set_password(self, pw): self.password_hash = generate_password_hash(pw)
    def check_password(self, pw): return check_password_hash(self.password_hash, pw)

class APIKey(db.Model):
    __tablename__ = 'api_keys'
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(100), nullable=False)
    api_key = db.Column(db.String(255), nullable=False, unique=True)
    sender_identifier = db.Column(db.String(200))
    counterparty_ref = db.Column(db.String(255))
    sender_city_ref = db.Column(db.String(36))
    sender_city_name = db.Column(db.String(200))
    sender_warehouse_ref = db.Column(db.String(36))
    sender_warehouse_name = db.Column(db.String(300))
    sender_contact_ref = db.Column(db.String(36))
    is_active = db.Column(db.Boolean, default=True)
    auto_sync = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    last_sync = db.Column(db.DateTime)
    packages = db.relationship('Package', back_populates='api_key', cascade='all, delete-orphan')
    trackers = db.relationship('UserAPITracking', back_populates='api_key', cascade='all, delete-orphan')

class UserAPITracking(db.Model):
    __tablename__ = 'user_api_tracking'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    api_key_id = db.Column(db.Integer, db.ForeignKey('api_keys.id'), nullable=False)
    user = db.relationship('User', back_populates='tracked_apis')
    api_key = db.relationship('APIKey', back_populates='trackers')

class Package(db.Model):
    __tablename__ = 'packages'
    id = db.Column(db.Integer, primary_key=True)
    api_key_id = db.Column(db.Integer, db.ForeignKey('api_keys.id'), nullable=False)
    tracking_number = db.Column(db.String(100), unique=True, nullable=False, index=True)
    direction = db.Column(db.String(10))
    sender_city = db.Column(db.String(200))
    sender_name = db.Column(db.String(200))
    sender_phone = db.Column(db.String(50))
    recipient_city = db.Column(db.String(200))
    recipient_name = db.Column(db.String(200))
    recipient_phone = db.Column(db.String(50))
    recipient_warehouse = db.Column(db.String(300))
    recipient_contact = db.Column(db.String(200))
    status = db.Column(db.String(300))
    status_code = db.Column(db.String(10))
    date_created = db.Column(db.DateTime)
    planned_delivery_date = db.Column(db.Date)
    actual_delivery_date = db.Column(db.DateTime)
    package_cost = db.Column(db.Numeric(10, 2))
    shipment_cost = db.Column(db.Numeric(10, 2))
    weight = db.Column(db.Numeric(10, 3))
    package_count = db.Column(db.Integer, default=1)
    description = db.Column(db.Text)
    is_delivered = db.Column(db.Boolean, default=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    raw_data = db.Column(db.JSON)
    author = db.Column(db.String(100))
    draft_status = db.Column(db.String(20))
    draft_data = db.Column(db.Text)
    api_key = db.relationship('APIKey', back_populates='packages')

class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    city = db.Column(db.String(200))
    city_ref = db.Column(db.String(36))
    warehouse = db.Column(db.String(300))
    warehouse_ref = db.Column(db.String(36))
    warehouse_number = db.Column(db.String(10))
    contact_person = db.Column(db.String(200))
    notes = db.Column(db.Text)
    counterparty_ref = db.Column(db.String(36))
    contact_ref = db.Column(db.String(36))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime)

class PackageScheme(db.Model):
    __tablename__ = 'package_schemes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    cargo_type = db.Column(db.String(50))
    weight = db.Column(db.Numeric(10, 3))
    seats_amount = db.Column(db.Integer, default=1)
    package_cost = db.Column(db.Numeric(10, 2))
    description_default = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    usage_count = db.Column(db.Integer, default=0)

class SyncLog(db.Model):
    __tablename__ = 'sync_logs'
    id = db.Column(db.Integer, primary_key=True)
    api_key_id = db.Column(db.Integer, db.ForeignKey('api_keys.id'))
    api_key = db.relationship('APIKey', foreign_keys='[SyncLog.api_key_id]')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', foreign_keys='[SyncLog.user_id]')
    sync_type = db.Column(db.String(20))
    sync_direction = db.Column(db.String(20))
    packages_fetched = db.Column(db.Integer, default=0)
    packages_created = db.Column(db.Integer, default=0)
    packages_updated = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20))
    error_message = db.Column(db.Text)
    sync_summary = db.Column(db.Text)
    api_response = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if current_user.role not in roles:
                flash('Access denied.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return wrapped
    return decorator

# Nova Poshta API
class NovaPoshtaAPI:
    def __init__(self, api_key):
        self.api_key = api_key

    def _post(self, model, method, props=None):
        payload = {
            'apiKey': self.api_key,
            'modelName': model,
            'calledMethod': method,
            'methodProperties': props or {}
        }
        r = requests.post(NOVA_POSHTA_API, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        if not data.get('success'):
            raise Exception(', '.join(data.get('errors', ['Unknown error'])))
        return data.get('data', []), data

    def get_documents_list(self, date_from, limit=100):
        return self._post('InternetDocument', 'getDocumentList', {
            'DateFrom': date_from.strftime('%d.%m.%Y'),
            'DateTo': datetime.now().strftime('%d.%m.%Y'),
            'Page': '1',
            'Limit': str(limit),
            'GetFullList': '1'
        })

    
    
    def get_incoming_documents(self, phone):
        """Get INCOMING packages by phone number (10 digits: 0XXXXXXXXX)"""
        if not phone:
            return [], {}
        
        phone = str(phone).strip()
        
        # Validate: must be exactly 10 digits starting with 0
        if len(phone) != 10 or not phone.startswith('0') or not phone.isdigit():
            raise Exception(f"Phone must be 10 digits (0XXXXXXXXX), got: {phone}")
        
        return self._post('InternetDocument', 'getIncomingDocumentsByPhone', {
            'Phone': phone
        })

    def create_internet_document(self, sender_data, recipient_data, package_data):
        # Get current time in Kyiv timezone
        kyiv_tz = pytz.timezone('Europe/Kyiv')
        current_date = datetime.now(kyiv_tz).strftime('%d.%m.%Y')

        #debug log
        payload = {
        'PayerType': package_data.get('payer_type', 'Recipient'),
        'PaymentMethod': package_data.get('payment_method', 'Cash'),
        'DateTime': current_date,
        'CargoType': package_data.get('cargo_type', 'Parcel'),
        'Weight': str(package_data['weight']),
        'ServiceType': 'WarehouseWarehouse',
        'SeatsAmount': str(package_data.get('seats', 1)),
        'Description': package_data['description'],
        'Cost': str(package_data['cost']),
        
        # Sender
        'CitySender': sender_data['city_ref'],
        'Sender': sender_data['counterparty_ref'],
        'SenderAddress': sender_data['warehouse_ref'],
        'ContactSender': sender_data['contact_ref'],
        'SendersPhone': sender_data['phone'],
        
        # Recipient
        'CityRecipient': recipient_data['city_ref'],
        'Recipient': recipient_data['counterparty_ref'],
        'RecipientAddress': recipient_data['warehouse_ref'],
        'ContactRecipient': recipient_data['contact_ref'],
        'RecipientsPhone': recipient_data['phone'],
        'RecipientName': recipient_data.get('name', ''),
        'RecipientType': 'PrivatePerson'

        }
    
        print(f"📨 Full API payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        """Create package via Nova Poshta API - requires UUIDs for all refs"""
        return self._post('InternetDocument', 'save', {
            'PayerType': package_data.get('payer_type', 'Recipient'),
            'PaymentMethod': package_data.get('payment_method', 'Cash'),
            #'DateTime': datetime.now().strftime('%d.%m.%Y'),
            'CargoType': package_data.get('cargo_type', 'Parcel'),
            'Weight': str(package_data['weight']),
            'ServiceType': 'WarehouseWarehouse',
            'SeatsAmount': str(package_data.get('seats', 1)),
            'Description': package_data['description'],
            'Cost': str(package_data['cost']),
            
            # Sender
            'CitySender': sender_data['city_ref'],
            'Sender': sender_data['counterparty_ref'],
            'SenderAddress': sender_data['warehouse_ref'],
            'ContactSender': sender_data['contact_ref'],
            'SendersPhone': sender_data['phone'],
            
            # Recipient
            'CityRecipient': recipient_data['city_ref'],
            'Recipient': recipient_data['counterparty_ref'],
            'RecipientAddress': recipient_data['warehouse_ref'],
            'ContactRecipient': recipient_data['contact_ref'],
            'RecipientsPhone': recipient_data['phone'],
            'RecipientName': recipient_data.get('name', ''),
            'RecipientType': 'PrivatePerson'
        })
    
    def search_cities(self, query):
        """Search cities by name"""
        return self._post('Address', 'getCities', {
            'FindByString': query,
            'Limit': '20'
        })
    
    def get_warehouses(self, city_ref):
        """Get warehouses in city"""
        return self._post('Address', 'getWarehouses', {
            'CityRef': city_ref,
            'Limit': '100'
        })

    # Fetch a recipient counterparty by phone and name, and create if not exists

    def create_or_get_recipient(self, name, phone):
        """
        Step 4A: Create or find recipient counterparty
        Returns: {'counterparty_ref': '...', 'contact_ref': '...'}
        """
        # Split name into parts (Nova Poshta requires FirstName, LastName)
        name_parts = name.strip().split()
        first_name = name_parts[0] if len(name_parts) > 0 else name
        last_name = name_parts[-1] if len(name_parts) > 1 else ''
        middle_name = ' '.join(name_parts[1:-1]) if len(name_parts) > 2 else ''
        
        # Create new recipient (Counterparty/save)
        result, response = self._post('Counterparty', 'save', {
            'CounterpartyType': 'PrivatePerson',
            'CounterpartyProperty': 'Recipient',
            'FirstName': first_name,
            'LastName': last_name,
            'MiddleName': middle_name,
            'Phone': phone
        })
        
        # Check if successful
        if not result or len(result) == 0:
            error_msg = response.get('errors', ['Unknown error'])[0] if response.get('errors') else 'No data returned'
            raise Exception(f'Failed to create recipient: {error_msg}')
        
        # Extract UUIDs from response
        recipient_data = result[0]
        counterparty_ref = recipient_data.get('Ref')
        
        # ContactPerson is nested in the response
        contact_person_data = recipient_data.get('ContactPerson', {}).get('data', [])
        contact_ref = contact_person_data[0].get('Ref') if contact_person_data else None
        
        if not counterparty_ref or not contact_ref:
            raise Exception('Response missing Ref or ContactPerson.Ref')
        
        return {
            'counterparty_ref': counterparty_ref,
            'contact_ref': contact_ref
        }

    def get_status_documents(self, tracking_numbers):
            """Fixed: API requires a list of objects"""
            if not tracking_numbers: return [], {}
            documents = [{'DocumentNumber': str(tn)} for tn in tracking_numbers[:100]]
            return self._post('TrackingDocument', 'getStatusDocuments', {'Documents': documents})

    def get_counterparty_documents(self, counterparty_ref, date_from, limit=100):
        return self._post('InternetDocument', 'getDocumentList', {
            'CounterpartyRef': counterparty_ref,
            'DateFrom': date_from.strftime('%d.%m.%Y'),
            'DateTo': datetime.now().strftime('%d.%m.%Y'),
            'Page': '1',
            'Limit': str(limit),
            'GetFullList': '1'
        })

def _parse_dt(s, fmt='%Y-%m-%d %H:%M:%S'):
    try:
        return datetime.strptime(s, fmt) if s and s != '0001-01-01 00:00:00' else None
    except Exception:
        return None

def is_delivered(status_code):
    """Delivered: status codes 2 (deleted), 9, 10, or 11"""
    return str(status_code).strip() in ['2', '9', '10', '11']

def is_ready_pickup(status_code):
    """Ready for pickup: status codes 7 or 8"""
    return str(status_code).strip() in ['7', '8']

def sync_packages(api_key_obj, days=7, sync_type='manual', user_id=None, direction='both'):
    """
    Enhanced sync:
    1. Fetch incoming packages (if phone available)
    2. Fetch outgoing packages
    3. Update status for ALL active packages in DB
    """
    results = []
    api = NovaPoshtaAPI(api_key_obj.api_key)
    
    # STEP 1: FETCH OUTGOING PACKAGES
    if direction in ['outgoing', 'both']:
        try:
            documents, full_response = api.get_documents_list(datetime.now() - timedelta(days=days))
            fetched, created = len(documents), 0

            for doc in documents:
                tn = doc.get('IntDocNumber')
                if not tn:
                    continue

                pkg = Package.query.filter_by(tracking_number=tn).first()
                if not pkg:
                    pkg = Package(api_key_id=api_key_obj.id, tracking_number=tn)
                    db.session.add(pkg)
                    created += 1

                # Set initial data from document list
                pkg.author = 'api'
                pkg.direction = 'outgoing'
                pkg.sender_city = doc.get('CitySenderDescription')
                pkg.sender_name = doc.get('SenderDescription')
                pkg.sender_phone = doc.get('SendersPhone')
                pkg.recipient_city = doc.get('CityRecipientDescription')
                pkg.recipient_name = doc.get('RecipientDescription')
                pkg.recipient_phone = doc.get('RecipientsPhone')
                pkg.recipient_warehouse = doc.get('RecipientAddressDescription')
                pkg.recipient_contact = doc.get('RecipientContactPerson')
                pkg.status = doc.get('StateName')
                pkg.status_code = str(doc.get('StateId', ''))
                pkg.date_created = _parse_dt(doc.get('DateTime'))
                pkg.planned_delivery_date = _parse_dt(doc.get('ScheduledDeliveryDate'))
                if pkg.planned_delivery_date:
                    pkg.planned_delivery_date = pkg.planned_delivery_date.date()
                pkg.actual_delivery_date = _parse_dt(doc.get('RecipientDateTime'))
                pkg.package_cost = float(doc.get('Cost') or 0)
                pkg.shipment_cost = float(doc.get('CostOnSite') or 0)
                pkg.weight = float(doc.get('Weight') or 0)
                pkg.package_count = int(doc.get('SeatsAmount') or 1)
                pkg.description = doc.get('Description')
                pkg.is_delivered = is_delivered(pkg.status_code)
                pkg.raw_data = doc

            db.session.commit()
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
            log = SyncLog(api_key_id=api_key_obj.id, user_id=user_id, sync_type=sync_type,
                          sync_direction='outgoing', status='error', 
                          error_message=str(e), sync_summary=summary)
            db.session.add(log)
            db.session.commit()

    
    # STEP 2: FETCH INCOMING PACKAGES (if phone configured)
    if direction in ['incoming', 'both'] and api_key_obj.sender_identifier:
        try:
            incoming_docs, full_response = api.get_incoming_documents(api_key_obj.sender_identifier)
            
            # Process nested response structure
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

                    # Set data from incoming document
                    pkg.direction = 'incoming'
                    pkg.sender_city = doc.get('CitySenderDescription')
                    pkg.sender_name = doc.get('SenderName')
                    pkg.sender_phone = doc.get('PhoneSender')
                    pkg.recipient_city = doc.get('CityRecipientDescription')
                    pkg.recipient_name = doc.get('RecipientName')
                    pkg.recipient_phone = doc.get('PhoneRecipient')
                    pkg.recipient_warehouse = doc.get('RecipientAddressDescription')
                    
                    # Extract warehouse number from settlement data
                    settlement_data = doc.get('SettlmentAddressData', {})
                    pkg.recipient_warehouse_number = settlement_data.get('RecipientWarehouseNumber')
                    
                    pkg.recipient_contact = doc.get('RecipientFullName')
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
            log = SyncLog(api_key_id=api_key_obj.id, user_id=user_id, sync_type=sync_type,
                          sync_direction='incoming', status='error', 
                          error_message=str(e), sync_summary=summary)
            db.session.add(log)
            db.session.commit()


    # STEP 3: UPDATE STATUS FOR ALL ACTIVE PACKAGES
    try:
        # Get all active packages for this API key (not delivered yet)
        active_packages = Package.query.filter_by(
            api_key_id=api_key_obj.id,
            is_delivered=False
        ).all()
        
        if active_packages:
            tracking_numbers = [pkg.tracking_number for pkg in active_packages]
            updated = 0
            
            # Split into batches of 100 (API limit)
            for i in range(0, len(tracking_numbers), 100):
                batch = tracking_numbers[i:i+100]
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
                        
                        # Update if status changed
                        if old_status != new_status:
                            pkg.status_code = new_status
                            pkg.status = status_doc.get('Status', '')
                            pkg.is_delivered = is_delivered(new_status)
                            
                            # Update delivery date if delivered
                            if pkg.is_delivered and not pkg.actual_delivery_date:
                                pkg.actual_delivery_date = datetime.now(pytz.UTC)
                            
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
    api_key_obj.last_sync = datetime.now(pytz.UTC)
    db.session.commit()
    
    return len(results) > 0, ' | '.join(results)

# Cooldown check: allow sync if last_sync is more than 5 minutes ago
def cooldown_ok(api_key_obj):
    if not api_key_obj.last_sync:
        return True, None
    diff = datetime.utcnow() - api_key_obj.last_sync  # ✅ Both naive
    cd = timedelta(minutes=5)
    if diff < cd:
        mins = int((cd - diff).total_seconds() / 60) + 1
        return False, f'Wait {mins} min'
    return True, None

# Routes - Auth
@app.route('/set-language/<lang>')
@login_required
def set_language(lang):
    if lang in ('en', 'uk'):
        current_user.language = lang
        db.session.commit()
    return redirect(request.referrer or url_for('dashboard'))

@app.route('/')
def index():
    return redirect(url_for('dashboard') if current_user.is_authenticated else url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and user.check_password(request.form.get('password')) and user.is_active:
            login_user(user, remember=bool(request.form.get('remember')))
            user.last_login = datetime.now(pytz.UTC)
            db.session.commit()
            if user.must_change_password:
                flash('Please change your password.', 'warning')
                return redirect(url_for('change_password'))
            return redirect(request.args.get('next') or url_for('dashboard'))
        flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        if not current_user.check_password(request.form.get('current_password')):
            flash('Incorrect current password.', 'danger')
        elif request.form.get('new_password') != request.form.get('confirm_password'):
            flash('Passwords do not match.', 'danger')
        elif len(request.form.get('new_password', '')) < 6:
            flash('Password must be at least 6 characters.', 'danger')
        else:
            current_user.set_password(request.form.get('new_password'))
            current_user.must_change_password = False
            db.session.commit()
            flash('Password changed successfully.', 'success')
            return redirect(url_for('dashboard'))
    return render_template('change_password.html')

# Routes - Main
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        api_keys = APIKey.query.filter_by(is_active=True).all()
    else:
        api_keys = [tr.api_key for tr in current_user.tracked_apis if tr.api_key.is_active]

    api_ids = [k.id for k in api_keys]
    if api_ids:
        all_pkgs = Package.query.filter(Package.api_key_id.in_(api_ids))
        Package.draft_status == 'sent'   # Only count sent packages
        total = all_pkgs.count()
        
        # Delivering: active packages, excluding ready incoming
        delivering = all_pkgs.filter(
            Package.is_delivered == False,
            ~db.and_(Package.direction == 'incoming', Package.status_code.in_(['7','8']))
        ).count()
        
        # Ready: ONLY incoming packages with status 7-8
        ready = all_pkgs.filter(
            Package.direction == 'incoming',
            Package.status_code.in_(['7','8'])
        ).count()
        
        # Delivered: status 2, 9, 10, 11
        delivered = all_pkgs.filter(Package.is_delivered == True).count()
    else:
        total = delivering = ready = delivered = 0

    return render_template('dashboard.html', api_keys=api_keys,
                           total_packages=total, delivering_packages=delivering,
                           ready_pickup=ready, delivered_packages=delivered,
                           now=datetime.now(pytz.timezone(DEFAULT_TIMEZONE)))

@app.route('/packages')
@login_required
def packages():
    page = request.args.get('page', 1, type=int)
    per_page = current_user.items_per_page
    view = request.args.get('view', current_user.view_mode)
    filter_type = request.args.get('filter', 'all')

    # Build API keys list
    if current_user.role == 'admin':
        available_keys = APIKey.query.filter_by(is_active=True).all()
        api_ids = [k.id for k in available_keys]
    else:
        tracked = UserAPITracking.query.filter_by(user_id=current_user.id).all()
        api_ids = [t.api_key_id for t in tracked]
        available_keys = APIKey.query.filter(APIKey.id.in_(api_ids), APIKey.is_active == True).all()

    # Build query
    q = Package.query.filter(Package.api_key_id.in_(api_ids)) if api_ids else Package.query.filter_by(id=-1)

    # Filter by type
    if filter_type == 'delivering':
        # Active packages, excluding ready incoming
        q = q.filter(
            Package.is_delivered == False,
            ~db.and_(Package.direction == 'incoming', Package.status_code.in_(['7','8']))
        )
    elif filter_type == 'ready':
        # ONLY incoming packages with status 7-8
        q = q.filter(
            Package.direction == 'incoming',
            Package.status_code.in_(['7','8'])
        )
    elif filter_type == 'delivered':
        # Status 2, 9, 10, 11
        q = q.filter(Package.is_delivered == True)
    # 'all' shows everything - no additional filter

    # Other filters
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
    available_apis = APIKey.query.filter(APIKey.id.in_(api_ids)).all() if api_ids else []    

    return render_template('packages.html',
                        packages=pagination.items,
                        pagination=pagination,
                        api_keys=available_keys,
                        view_mode=view,
                        current_filter=filter_type)

@app.route('/package/<int:package_id>')
@login_required
def package_detail(package_id):
    pkg = Package.query.get_or_404(package_id)
    if current_user.role != 'admin':
        ids = [tr.api_key_id for tr in current_user.tracked_apis]
        if pkg.api_key_id not in ids:
            return jsonify({'error': 'Access denied'}), 403
    return render_template('package_detail.html', package=pkg)

@app.route('/package/invoice/<tracking_number>')
@login_required
def package_invoice(tracking_number):
    pkg = Package.query.filter_by(tracking_number=tracking_number).first_or_404()
        
    if not pkg.api_key:
        flash('Package has no API key', 'danger')
        return redirect(url_for('packages'))
    
    api_key = pkg.api_key.api_key
    url = f'https://my.novaposhta.ua/orders/printDocument/orders[]/{tracking_number}/type/pdf/apiKey/{api_key}'
    
    print(f"DEBUG: URL = {url}")
    return redirect(url)

@app.route('/sync/<int:api_key_id>', methods=['POST'])
@login_required
def sync_api(api_key_id):
    key = APIKey.query.get_or_404(api_key_id)
    if current_user.role != 'admin':
        ids = [tr.api_key_id for tr in current_user.tracked_apis]
        if api_key_id not in ids:
            return jsonify({'error': 'Access denied'}), 403
    
    ok, msg = cooldown_ok(key)
    if not ok:
        return jsonify({'error': msg}), 429
    
    success, message = sync_packages(key, days=5, sync_type='manual', user_id=current_user.id, direction='both')
    
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'error': message}), 500

@app.route('/sync/all', methods=['POST'])
@login_required
def sync_all():
    if current_user.role == 'admin':
        keys = APIKey.query.filter_by(is_active=True).all()
    else:
        keys = [tr.api_key for tr in current_user.tracked_apis if tr.api_key.is_active]
    
    results = []
    for i, key in enumerate(keys):
        if i > 0:
            time.sleep(7)  # delay between syncs to avoid rate limiting
        
        ok, msg = cooldown_ok(key)
        if not ok:
            results.append(f"<strong>{key.label}</strong>: {msg}")
            continue
        
        success, message = sync_packages(key, days=5, sync_type='manual', user_id=current_user.id, direction='both')
        results.append(f"<strong>{key.label}</strong>: {message}")
    
    return jsonify({'success': True, 'message': '<br>'.join(results)})

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        current_user.theme = request.form.get('theme', 'light')
        current_user.view_mode = request.form.get('view_mode', 'table')
        current_user.items_per_page = int(request.form.get('items_per_page', 20))
        current_user.notify_ready_pickup = bool(request.form.get('notify_ready_pickup'))
        current_user.language = request.form.get('language', 'uk')
        current_user.timezone = request.form.get('timezone', DEFAULT_TIMEZONE)
        if current_user.role != 'admin':
            UserAPITracking.query.filter_by(user_id=current_user.id).delete()
            for aid in request.form.getlist('tracked_apis'):
                db.session.add(UserAPITracking(user_id=current_user.id, api_key_id=int(aid)))
        db.session.commit()
        flash(t('save') + ' ✓', 'success')
        return redirect(url_for('settings'))
    available_apis = APIKey.query.filter_by(is_active=True).all()
    tracked_api_ids = [tr.api_key_id for tr in current_user.tracked_apis]
    timezones = pytz.common_timezones
    return render_template('settings.html', available_apis=available_apis,
                           tracked_api_ids=tracked_api_ids, timezones=timezones)

# Routes - Admin
@app.route('/admin/users')
@role_required('admin')
def admin_users():
    return render_template('admin/users.html', users=User.query.all())

@app.route('/admin/user/add', methods=['GET', 'POST'])
@role_required('admin')
def admin_add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
        else:
            u = User(username=username, full_name=request.form.get('full_name'),
                     role=request.form.get('role'))
            u.set_password(request.form.get('password'))
            db.session.add(u)
            db.session.commit()
            flash(f'User {username} created.', 'success')
            return redirect(url_for('admin_users'))
    return render_template('admin/add_user.html')

@app.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
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
        return redirect(url_for('admin_users'))
    return render_template('admin/edit_user.html', user=user)

@app.route('/admin/api-keys')
@role_required('admin')
def admin_api_keys():
    return render_template('admin/api_keys.html', api_keys=APIKey.query.all())

@app.route('/admin/api-key/add', methods=['GET', 'POST'])
@role_required('admin')
def admin_add_api_key():
    if request.method == 'POST':
        key = request.form.get('api_key')
        if APIKey.query.filter_by(api_key=key).first():
            flash('API key already exists.', 'danger')
        else:
            k = APIKey(label=request.form.get('label'), api_key=key,
                       sender_identifier=request.form.get('sender_identifier'),
                       counterparty_ref=request.form.get('counterparty_ref'),
                       auto_sync=bool(request.form.get('auto_sync')),
                       created_by=current_user.id)
            db.session.add(k)
            db.session.commit()
            flash(f'API key "{k.label}" added.', 'success')
            return redirect(url_for('admin_api_keys'))
    return render_template('admin/add_api_key.html')

@app.route('/admin/api-key/<int:key_id>/edit', methods=['GET', 'POST'])
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
        key.auto_sync = bool(request.form.get('auto_sync'))
        key.is_active = bool(request.form.get('is_active'))
        db.session.commit()
        flash(f'API key "{key.label}" updated.', 'success')
        return redirect(url_for('admin_api_keys'))
    return render_template('admin/edit_api_key.html', api_key=key)

@app.route('/admin/api-keys/export')
@role_required('admin')
def admin_export_api_keys():
    keys = APIKey.query.all()
    data = [{'label': k.label, 'api_key': k.api_key, 'sender_identifier': k.sender_identifier,
             'counterparty_ref': k.counterparty_ref, 'auto_sync': k.auto_sync, 'is_active': k.is_active}
            for k in keys]
    
    json_data = json.dumps(data, indent=2, ensure_ascii=False)
    buffer = BytesIO(json_data.encode('utf-8'))
    buffer.seek(0)
    
    return send_file(buffer, mimetype='application/json', as_attachment=True,
                     download_name=f'api_keys_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')

@app.route('/admin/api-keys/import', methods=['POST'])
@role_required('admin')
def admin_import_api_keys():
    if 'file' not in request.files:
        flash('No file selected.', 'danger')
        return redirect(url_for('admin_api_keys'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected.', 'danger')
        return redirect(url_for('admin_api_keys'))
    
    try:
        data = json.load(file)
        imported, skipped = 0, 0
        
        for item in data:
            if APIKey.query.filter_by(api_key=item['api_key']).first():
                skipped += 1
                continue
            
            k = APIKey(label=item.get('label', 'Imported'), api_key=item['api_key'],
                       sender_identifier=item.get('sender_identifier'),
                       counterparty_ref=item.get('counterparty_ref'),
                       auto_sync=item.get('auto_sync', True),
                       is_active=item.get('is_active', True),
                       created_by=current_user.id)
            db.session.add(k)
            imported += 1
        
        db.session.commit()
        flash(f'Imported {imported} API keys, skipped {skipped} duplicates.', 'success')
    except Exception as e:
        flash(f'Import failed: {str(e)}', 'danger')
    
    return redirect(url_for('admin_api_keys'))

@app.route('/admin/log')
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
    if f_days: q = q.filter(SyncLog.created_at >= datetime.now(pytz.UTC) - timedelta(days=f_days))

    pagination = q.order_by(desc(SyncLog.created_at)).paginate(page=page, per_page=per_page, error_out=False)
    api_keys = APIKey.query.all()
    users = User.query.all()
    return render_template('admin/log.html', logs=pagination.items, pagination=pagination,
                           api_keys=api_keys, users=users)

@app.route('/admin/log/<int:log_id>/details')
@role_required('admin')
def admin_log_details(log_id):
    log = SyncLog.query.get_or_404(log_id)
    return render_template('admin/log_details.html', log=log)

# ============================================================================
# PACKAGE CREATION ROUTES
# ============================================================================

@app.route('/package/create', methods=['POST'])
@login_required
def create_package():
    """Create new package via Nova Poshta API or save as draft"""
    try:
        data = request.json
        action = data.get('action', 'create')  # 'create' or 'draft'
        
        # Validate API key access
        api_key_id = data.get('api_key_id')
        if not api_key_id or api_key_id == '':
            return jsonify({'success': False, 'error': 'Please select an API key'})

        api_key_id = int(api_key_id)
        api_key_obj = APIKey.query.get_or_404(api_key_id)
        
        if current_user.role != 'admin':
            # Check if user has access to this API key
            tracked = UserAPITracking.query.filter_by(
                user_id=current_user.id,
                api_key_id=api_key_id
            ).first()
            if not tracked:
                return jsonify({'success': False, 'error': 'Access denied'}), 403
        
        # Save client if requested
        if data.get('save_client'):
            existing_client = Client.query.filter_by(
                phone=data['recipient_phone'],
                created_by=current_user.id
            ).first()
            
            if existing_client:
                # Update existing
                existing_client.name = data['recipient_name']
                existing_client.city = data.get('recipient_city')
                existing_client.city_ref = data.get('city_recipient_ref')
                existing_client.warehouse = data.get('recipient_warehouse')
                existing_client.warehouse_ref = data.get('recipient_address_ref')
                existing_client.contact_person = data.get('recipient_contact')
                existing_client.last_used = datetime.now(pytz.UTC)
            else:
                # Create new
                new_client = Client(
                    name=data['recipient_name'],
                    phone=data['recipient_phone'],
                    city=data.get('recipient_city'),
                    city_ref=data.get('city_recipient_ref'),
                    warehouse=data.get('recipient_warehouse'),
                    warehouse_ref=data.get('recipient_address_ref'),
                    contact_person=data.get('recipient_contact'),
                    created_by=current_user.id
                )
                db.session.add(new_client)
        
        # Create package record (starts as draft)
        pkg = Package(
            api_key_id=api_key_id,
            tracking_number=f'DRAFT_{datetime.now().strftime("%Y%m%d%H%M%S")}_{current_user.id}' if action == 'draft' else '',
            status='Draft',
            status_code='draft',
            direction='outgoing',
            author=current_user.username,
            draft_status='draft' if action == 'draft' else 'pending',
            draft_data=json.dumps(data),
            recipient_name=data.get('recipient_name', ''),
            recipient_phone=data.get('recipient_phone', ''),
            recipient_city=data.get('recipient_city', ''),
            weight=float(data.get('weight')) if data.get('weight') else None,
            package_cost=float(data.get('cost')) if data.get('cost') else None,
            description=data.get('description', ''),
            date_created=datetime.now(pytz.UTC)
        )
        db.session.add(pkg)
        db.session.commit()
        
        # If saving as draft, stop here
        if action == 'draft':
            return jsonify({
                'success': True,
                'message': t('Saved as draft'),
                'draft_id': pkg.id
            })
        
        # Try to create via Nova Poshta API
        try:
            api = NovaPoshtaAPI(api_key_obj.api_key)

            # Check if we have cached UUIDs for this client
            recipient_cp = None
            
            # If client was saved, check for cached UUIDs
            if data.get('save_client'):
                existing_client = Client.query.filter_by(
                    phone=data['recipient_phone'],
                    created_by=current_user.id
                ).first()
                
                # Use cached UUIDs if available
                if existing_client and existing_client.counterparty_ref:
                    recipient_cp = {
                        'counterparty_ref': existing_client.counterparty_ref,
                        'contact_ref': existing_client.contact_ref
                    }
                    print(f"✅ Using cached UUIDs for {existing_client.name}")
            
            # If no cached UUIDs, create or get from Nova Poshta
            if not recipient_cp:
                print(f"⚙️  Fetching recipient UUIDs from Nova Poshta...")
                recipient_cp = api.create_or_get_recipient(
                    data['recipient_name'],
                    data['recipient_phone']
                )

                # debug log
                print(f"✅ Got recipient UUIDs: {recipient_cp}")

                # Prepare data for API
                package_data = {
                    'weight': data['weight'],
                    'cost': data['cost'],
                    'description': data['description'],
                    'seats': data.get('seats', 1),
                    'cargo_type': data.get('cargo_type', 'Parcel'),
                    'payer_type': data.get('payer_type', 'Recipient'),
                    'payment_method': data.get('payment_method', 'Cash')
                }
                
                sender_data = {
                    'city_ref': data['city_sender_ref'],
                    'counterparty_ref': data['sender_ref'],
                    'warehouse_ref': data['sender_address_ref'],
                    'contact_ref': data.get('contact_sender_ref') if data.get('contact_sender_ref') not in ['None', None, ''] else '',
                    'phone': data['sender_phone']
                }
                
                recipient_data = {
                    'city_ref': data['city_recipient_ref'],
                    'counterparty_ref': recipient_cp['counterparty_ref'],
                    'contact_ref': recipient_cp['contact_ref'],
                    'warehouse_ref': data['recipient_address_ref'],
                    'phone': data['recipient_phone'],
                    'name': data['recipient_name']
                }
                            
                result, response = api.create_internet_document(
                    sender_data, recipient_data, package_data
                )

                print(f"🔍 Nova Poshta response: {response}")
                
                # SAVE UUIDs to client for next time
                if data.get('save_client'):
                    client = Client.query.filter_by(
                        phone=data['recipient_phone'],
                        created_by=current_user.id
                    ).first()
                    
                    if not client:
                        client = Client(
                            name=data['recipient_name'],
                            phone=data['recipient_phone'],
                            city=data.get('recipient_city'),
                            city_ref=data.get('city_recipient_ref'),
                            warehouse=data.get('recipient_warehouse'),
                            warehouse_ref=data.get('recipient_address_ref'),
                            contact_person=data.get('recipient_contact'),
                            created_by=current_user.id
                        )
                        db.session.add(client)
                    
                    # Save the UUIDs we just got
                    client.counterparty_ref = recipient_cp['counterparty_ref']
                    client.contact_ref = recipient_cp['contact_ref']
                    client.last_used = datetime.now(pytz.UTC)
                    db.session.flush()
                    
                    print(f"💾 Saved UUIDs to client: {client.name}")
            
            if result and len(result) > 0:
                # Success!
                doc = result[0]
                pkg.tracking_number = doc.get('IntDocNumber')
                pkg.draft_status = 'sent'
                pkg.status = 'Створено'
                pkg.status_code = '1'
                pkg.raw_data = doc
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'message': f'Package created! TTN: {pkg.tracking_number}',
                    'tracking_number': pkg.tracking_number,
                    'package_id': pkg.id
                })
            else:
                raise Exception('No document returned from API')
        
        except Exception as api_error:
            # API failed - save as failed draft
            pkg.draft_status = 'failed'
            error_data = json.loads(pkg.draft_data)
            error_data['api_error'] = str(api_error)
            pkg.draft_data = json.dumps(error_data)
            db.session.commit()
            
            return jsonify({
                'success': False,
                'error': str(api_error),
                'draft_id': pkg.id,
                'message': f'API Error: {str(api_error)}. Saved as draft.'
            })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/search-cities')
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


@app.route('/api/warehouses/<city_ref>')
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


@app.route('/api/clients/recent')
@login_required
def get_recent_clients():
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

@app.route('/api/fetch-sender-uuids', methods=['POST'])
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
        
        # Get contact persons for this counterparty
        contacts, _ = api._post('Counterparty', 'getCounterpartyContactPersons', {
            'Ref': counterparty_ref,
            'Page': '1'
        })

        contact_ref = contacts[0]['Ref'] if contacts else None

        # Get addresses - ADD DEBUG HERE
        addresses, _ = api._post('Counterparty', 'getCounterpartyAddresses', {
            'Ref': counterparty_ref,
            'CounterpartyProperty': 'Sender'
        })
        
        print(f"DEBUG addresses: {addresses}")

        contact_description = None
        if contacts and len(contacts) > 0:
            contact_ref = contacts[0]['Ref']
            contact_description = contacts[0].get('Description', '')
        
        # Get addresses/warehouses
        addresses, _ = api._post('Counterparty', 'getCounterpartyAddresses', {
            'Ref': counterparty_ref,
            'CounterpartyProperty': 'Sender'
        })
        
        warehouse_ref = addresses[0]['Ref'] if addresses else None
        city_ref = addresses[0].get('CityRef') if addresses else None
        
        print(f"DEBUG city_ref: {city_ref}, warehouse_ref: {warehouse_ref}")
        
        # Get phone from contact person
        phone = None
        if contacts and len(contacts) > 0:
            # Phones is a string like "380931234567" or array
            phones_data = contacts[0].get('Phones', '')
            if phones_data:
                # Convert to 10-digit format
                phone_str = str(phones_data).strip().replace('+', '')
                if phone_str.startswith('380') and len(phone_str) == 12:
                    phone = '0' + phone_str[3:]  # 380931234567 → 0931234567
                elif len(phone_str) == 10:
                    phone = phone_str

        return jsonify({
            'success': True,
            'counterparty_ref': counterparty_ref,
            'city_ref': city_ref,
            'warehouse_ref': warehouse_ref,
            'contact_ref': contact_ref,
            'phone': phone,
            'description': contact_description or cp.get('Description', ''),  # ← Use contact description first
            'city_description': addresses[0].get('CityDescription', '') if addresses else ''
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Init
def init_db():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='sysadmin').first():
            admin = User(username='sysadmin', full_name='System Administrator',
                         role='admin', must_change_password=True, language='en')
            admin.set_password('sysadmin')
            db.session.add(admin)
            db.session.commit()
            print('✅ Default admin created: sysadmin / sysadmin')

# Draft deletion route
@app.route('/package/<int:package_id>/delete', methods=['POST'])
@login_required
def delete_package(package_id):
    """Delete draft/failed package (only author or admin)"""
    
    pkg = Package.query.get_or_404(package_id)    
    
    # Check permissions
    if current_user.role != 'admin' and pkg.author != current_user.username:        
        flash('You can only delete your own drafts', 'danger')
        return redirect(url_for('packages'))
    
    # Only allow deleting drafts and failed packages
    if pkg.draft_status not in ['draft', 'failed']:        
        flash('Only draft or failed packages can be deleted', 'warning')
        return redirect(url_for('packages'))
    
    # Delete
    ttn = pkg.tracking_number or f"Draft #{pkg.id}"
    db.session.delete(pkg)
    db.session.commit()
    
    flash(f'Package {ttn} deleted', 'success')
    return redirect(url_for('packages'))

# Run app
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)