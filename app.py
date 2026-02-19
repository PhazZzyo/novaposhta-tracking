"""
Nova Poshta Package Tracking Web Application v1.1
Features: Import/Export API keys, Unified sync, Incoming packages, Detailed error logging
"""

import os
import json
import requests
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import desc
from io import BytesIO

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

# ---------------------------------------------------------------------------
# TRANSLATIONS
# ---------------------------------------------------------------------------
TRANSLATIONS = {
    'en': {
        'dashboard': 'Dashboard', 'packages': 'Packages', 'settings': 'Settings',
        'logout': 'Logout', 'change_password': 'Change Password', 'admin': 'Admin',
        'users': 'Users', 'api_keys': 'API Keys', 'add_api_key': 'Add API Key',
        'add_user': 'Add User', 'total_packages': 'Total Packages', 'active': 'Active',
        'ready_pickup': 'Ready for Pickup', 'last_sync': 'Last Sync', 'status': 'Status',
        'actions': 'Actions', 'sync': 'Sync', 'view': 'View', 'never': 'Never',
        'incoming': 'Incoming', 'outgoing': 'Outgoing', 'all': 'All',
        'delivered': 'Delivered', 'filters': 'Filters', 'direction': 'Direction',
        'date_range': 'Date Range', 'apply': 'Apply', 'reset': 'Reset', 'cancel': 'Cancel',
        'sender': 'Sender', 'recipient': 'Recipient', 'created': 'Created',
        'save': 'Save Settings', 'theme': 'Theme', 'light': 'Light', 'dark': 'Dark',
        'view_mode': 'View Mode', 'table': 'Table', 'cards': 'Cards',
        'items_per_page': 'Items per page', 'notify_pickup': 'Notify when ready for pickup',
        'track_apis': 'Tracked API Keys', 'language': 'Language',
        'package_details': 'Package Details', 'view_invoice': 'View Invoice',
        'package_cost': 'Package Cost', 'shipping_cost': 'Shipping Cost',
        'weight': 'Weight', 'planned_delivery': 'Planned Delivery',
        'description': 'Description', 'no_packages': 'No packages found',
        'no_api_keys': 'No API keys configured', 'syncing': 'Syncing...',
        'sync_success': 'Sync successful!', 'error': 'Error', 'label': 'Label',
        'sender_identifier': 'Sender Identifier', 'auto_sync': 'Auto Sync',
        'username': 'Username', 'full_name': 'Full Name', 'role': 'Role',
        'password': 'Password', 'new_password': 'New Password',
        'confirm_password': 'Confirm Password', 'current_password': 'Current Password',
        'save_changes': 'Save Changes', 'create_user': 'Create User',
        'inactive': 'Inactive', 'last_login': 'Last Login', 'edit': 'Edit',
        'login': 'Login', 'remember_me': 'Remember me (30 days)',
        'sign_in': 'Sign In', 'tracking_system': 'Package Tracking System',
        'no_account': 'No account? Contact administrator.',
        'days_1': 'Last 24 hours', 'days_5': 'Last 5 days', 'days_7': 'Last 7 days',
        'days_14': 'Last 14 days', 'days_30': 'Last 30 days', 'all_time': 'All time',
        'sync_all': 'Sync All', 'import_api_keys': 'Import', 'export_api_keys': 'Export',
    },
    'uk': {
        'dashboard': 'Головна', 'packages': 'Посилки', 'settings': 'Налаштування',
        'logout': 'Вихід', 'change_password': 'Змінити пароль', 'admin': 'Адмін',
        'users': 'Користувачі', 'api_keys': 'API Ключі', 'add_api_key': 'Додати API Ключ',
        'add_user': 'Додати користувача', 'total_packages': 'Усього посилок',
        'active': 'Активні', 'ready_pickup': 'Готові до отримання',
        'last_sync': 'Остання синхронізація', 'status': 'Статус',
        'actions': 'Дії', 'sync': 'Синхронізувати', 'view': 'Переглянути',
        'never': 'Ніколи', 'incoming': 'Вхідні', 'outgoing': 'Вихідні', 'all': 'Усі',
        'delivered': 'Доставлені', 'filters': 'Фільтри', 'direction': 'Напрямок',
        'date_range': 'Період', 'apply': 'Застосувати', 'reset': 'Скинути',
        'cancel': 'Скасувати', 'sender': 'Відправник', 'recipient': 'Отримувач',
        'created': 'Створено', 'save': 'Зберегти', 'theme': 'Тема',
        'light': 'Світла', 'dark': 'Темна', 'view_mode': 'Режим перегляду',
        'table': 'Таблиця', 'cards': 'Картки', 'items_per_page': 'Елементів на сторінці',
        'notify_pickup': 'Сповіщати при готовності до отримання',
        'track_apis': 'Відстежувані API', 'language': 'Мова',
        'package_details': 'Деталі посилки', 'view_invoice': 'Переглянути накладну',
        'package_cost': 'Вартість посилки', 'shipping_cost': 'Вартість доставки',
        'weight': 'Вага', 'planned_delivery': 'Планова доставка',
        'description': 'Опис', 'no_packages': 'Посилок не знайдено',
        'no_api_keys': 'API ключі не налаштовані', 'syncing': 'Синхронізація...',
        'sync_success': 'Синхронізація успішна!', 'error': 'Помилка', 'label': 'Назва',
        'sender_identifier': 'Ідентифікатор відправника', 'auto_sync': 'Авто синхронізація',
        'username': 'Логін', 'full_name': "Повне ім'я", 'role': 'Роль',
        'password': 'Пароль', 'new_password': 'Новий пароль',
        'confirm_password': 'Підтвердити пароль', 'current_password': 'Поточний пароль',
        'save_changes': 'Зберегти зміни', 'create_user': 'Створити користувача',
        'inactive': 'Неактивний', 'last_login': 'Останній вхід', 'edit': 'Редагувати',
        'login': 'Вхід', 'remember_me': "Запам'ятати мене (30 днів)",
        'sign_in': 'Увійти', 'tracking_system': 'Система відстеження посилок',
        'no_account': 'Немає облікового запису? Зверніться до адміністратора.',
        'days_1': 'Останні 24 години', 'days_5': 'Останні 5 днів',
        'days_7': 'Останні 7 днів', 'days_14': 'Останні 14 днів',
        'days_30': 'Останні 30 днів', 'all_time': 'Весь час',
        'sync_all': 'Синхронізувати все', 'import_api_keys': 'Імпорт', 'export_api_keys': 'Експорт',
    }
}

def t(key):
    """Get translation for current user's language"""
    lang = 'en'
    if current_user.is_authenticated:
        lang = current_user.language
    elif 'language' in session:
        lang = session['language']
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)

app.jinja_env.globals['t'] = t

# ---------------------------------------------------------------------------
# MODELS
# ---------------------------------------------------------------------------
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name     = db.Column(db.String(200))
    role          = db.Column(db.String(20), nullable=False)
    is_active     = db.Column(db.Boolean, default=True)
    must_change_password = db.Column(db.Boolean, default=False)
    theme         = db.Column(db.String(10), default='light')
    view_mode     = db.Column(db.String(10), default='table')
    items_per_page = db.Column(db.Integer, default=20)
    notify_ready_pickup = db.Column(db.Boolean, default=True)
    language      = db.Column(db.String(5), default='uk')
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    last_login    = db.Column(db.DateTime)
    tracked_apis  = db.relationship('UserAPITracking', back_populates='user', cascade='all, delete-orphan')

    def set_password(self, pw):   self.password_hash = generate_password_hash(pw)
    def check_password(self, pw): return check_password_hash(self.password_hash, pw)


class APIKey(db.Model):
    __tablename__ = 'api_keys'
    id                  = db.Column(db.Integer, primary_key=True)
    label               = db.Column(db.String(100), nullable=False)
    api_key             = db.Column(db.String(255), nullable=False, unique=True)
    sender_identifier   = db.Column(db.String(200))
    counterparty_ref    = db.Column(db.String(255))
    is_active           = db.Column(db.Boolean, default=True)
    auto_sync           = db.Column(db.Boolean, default=True)
    created_at          = db.Column(db.DateTime, default=datetime.utcnow)
    created_by          = db.Column(db.Integer, db.ForeignKey('users.id'))
    last_sync           = db.Column(db.DateTime)
    packages            = db.relationship('Package', back_populates='api_key', cascade='all, delete-orphan')
    trackers            = db.relationship('UserAPITracking', back_populates='api_key', cascade='all, delete-orphan')


class UserAPITracking(db.Model):
    __tablename__ = 'user_api_tracking'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    api_key_id = db.Column(db.Integer, db.ForeignKey('api_keys.id'), nullable=False)
    user       = db.relationship('User', back_populates='tracked_apis')
    api_key    = db.relationship('APIKey', back_populates='trackers')


class Package(db.Model):
    __tablename__ = 'packages'
    id                  = db.Column(db.Integer, primary_key=True)
    api_key_id          = db.Column(db.Integer, db.ForeignKey('api_keys.id'), nullable=False)
    tracking_number     = db.Column(db.String(100), unique=True, nullable=False, index=True)
    direction           = db.Column(db.String(10))
    sender_city         = db.Column(db.String(200))
    sender_name         = db.Column(db.String(200))
    sender_phone        = db.Column(db.String(50))
    recipient_city      = db.Column(db.String(200))
    recipient_name      = db.Column(db.String(200))
    recipient_phone     = db.Column(db.String(50))
    recipient_warehouse = db.Column(db.String(300))
    recipient_contact   = db.Column(db.String(200))
    status              = db.Column(db.String(300))
    status_code         = db.Column(db.String(10))
    date_created        = db.Column(db.DateTime)
    planned_delivery_date = db.Column(db.Date)
    actual_delivery_date  = db.Column(db.DateTime)
    package_cost        = db.Column(db.Numeric(10, 2))
    shipment_cost       = db.Column(db.Numeric(10, 2))
    weight              = db.Column(db.Numeric(10, 3))
    package_count       = db.Column(db.Integer, default=1)
    description         = db.Column(db.Text)
    is_delivered        = db.Column(db.Boolean, default=False)
    last_updated        = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    raw_data            = db.Column(db.JSON)
    api_key             = db.relationship('APIKey', back_populates='packages')


class SyncLog(db.Model):
    __tablename__ = 'sync_logs'
    id               = db.Column(db.Integer, primary_key=True)
    api_key_id       = db.Column(db.Integer, db.ForeignKey('api_keys.id'))
    api_key          = db.relationship('APIKey', foreign_keys='[SyncLog.api_key_id]')
    user_id          = db.Column(db.Integer, db.ForeignKey('users.id'))
    user             = db.relationship('User', foreign_keys='[SyncLog.user_id]')
    sync_type        = db.Column(db.String(20))
    sync_direction   = db.Column(db.String(20))
    packages_fetched = db.Column(db.Integer, default=0)
    packages_created = db.Column(db.Integer, default=0)
    packages_updated = db.Column(db.Integer, default=0)
    status           = db.Column(db.String(20))
    error_message    = db.Column(db.Text)
    api_response     = db.Column(db.JSON)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------------------------------------------------------------------
# DECORATORS
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# NOVA POSHTA API
# ---------------------------------------------------------------------------
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
            'DateTo':   datetime.now().strftime('%d.%m.%Y'),
            'Page': '1',
            'Limit': str(limit),
            'GetFullList': '1'
        })

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


def sync_packages(api_key_obj, days=5, sync_type='manual', user_id=None, direction='both'):
    """
    Unified sync function - syncs outgoing, incoming, or both based on direction parameter
    direction: 'outgoing', 'incoming', or 'both'
    """
    results = []
    
    # Sync outgoing (packages created by us)
    if direction in ['outgoing', 'both']:
        try:
            api = NovaPoshtaAPI(api_key_obj.api_key)
            documents, full_response = api.get_documents_list(datetime.now() - timedelta(days=days))

            fetched = len(documents)
            created = 0
            updated = 0

            for doc in documents:
                tn = doc.get('IntDocNumber')
                if not tn:
                    continue

                pkg = Package.query.filter_by(tracking_number=tn).first()
                is_new = pkg is None
                if is_new:
                    pkg = Package(api_key_id=api_key_obj.id, tracking_number=tn)
                    db.session.add(pkg)
                    created += 1

                old_status = pkg.status_code

                pkg.direction           = 'outgoing'
                pkg.sender_city         = doc.get('CitySenderDescription')
                pkg.sender_name         = doc.get('SenderDescription')
                pkg.sender_phone        = doc.get('SendersPhone')
                pkg.recipient_city      = doc.get('CityRecipientDescription')
                pkg.recipient_name      = doc.get('RecipientDescription')
                pkg.recipient_phone     = doc.get('RecipientsPhone')
                pkg.recipient_warehouse = doc.get('RecipientAddressDescription')
                pkg.recipient_contact   = doc.get('RecipientContactPerson')
                pkg.status              = doc.get('StateName')
                pkg.status_code         = str(doc.get('StateId', ''))
                pkg.date_created        = _parse_dt(doc.get('DateTime'))
                pkg.planned_delivery_date = _parse_dt(doc.get('ScheduledDeliveryDate'))
                if pkg.planned_delivery_date:
                    pkg.planned_delivery_date = pkg.planned_delivery_date.date()
                pkg.actual_delivery_date = _parse_dt(doc.get('RecipientDateTime'))
                pkg.package_cost        = float(doc.get('Cost') or 0)
                pkg.shipment_cost       = float(doc.get('CostOnSite') or 0)
                pkg.weight              = float(doc.get('Weight') or 0)
                pkg.package_count       = int(doc.get('SeatsAmount') or 1)
                pkg.description         = doc.get('Description')
                pkg.is_delivered        = doc.get('StateId') in [9, 10]
                pkg.raw_data            = doc

                if not is_new and old_status != pkg.status_code:
                    updated += 1

            db.session.commit()
            api_key_obj.last_sync = datetime.utcnow()

            log = SyncLog(
                api_key_id       = api_key_obj.id,
                user_id          = user_id,
                sync_type        = sync_type,
                sync_direction   = 'outgoing',
                packages_fetched = fetched,
                packages_created = created,
                packages_updated = updated,
                status           = 'success',
                api_response     = full_response
            )
            db.session.add(log)
            db.session.commit()
            results.append(f'Out: {fetched}📦 ({created}🆕 {updated}🔄)')
        except Exception as e:
            db.session.rollback()
            log = SyncLog(api_key_id=api_key_obj.id, user_id=user_id, sync_type=sync_type,
                          sync_direction='outgoing', status='error', error_message=str(e))
            db.session.add(log)
            db.session.commit()
            results.append(f'Out: ❌ {str(e)[:50]}')

    # Sync incoming (packages sent to us)
    if direction in ['incoming', 'both'] and api_key_obj.counterparty_ref:
        try:
            api = NovaPoshtaAPI(api_key_obj.api_key)
            documents, full_response = api.get_counterparty_documents(
                api_key_obj.counterparty_ref,
                datetime.now() - timedelta(days=days)
            )

            fetched = len(documents)
            created = 0
            updated = 0

            for doc in documents:
                tn = doc.get('IntDocNumber')
                if not tn:
                    continue

                pkg = Package.query.filter_by(tracking_number=tn).first()
                is_new = pkg is None
                if is_new:
                    pkg = Package(api_key_id=api_key_obj.id, tracking_number=tn)
                    db.session.add(pkg)
                    created += 1

                old_status = pkg.status_code

                pkg.direction           = 'incoming'
                pkg.sender_city         = doc.get('CitySenderDescription')
                pkg.sender_name         = doc.get('SenderDescription')
                pkg.sender_phone        = doc.get('SendersPhone')
                pkg.recipient_city      = doc.get('CityRecipientDescription')
                pkg.recipient_name      = doc.get('RecipientDescription')
                pkg.recipient_phone     = doc.get('RecipientsPhone')
                pkg.recipient_warehouse = doc.get('RecipientAddressDescription')
                pkg.recipient_contact   = doc.get('RecipientContactPerson')
                pkg.status              = doc.get('StateName')
                pkg.status_code         = str(doc.get('StateId', ''))
                pkg.date_created        = _parse_dt(doc.get('DateTime'))
                pkg.planned_delivery_date = _parse_dt(doc.get('ScheduledDeliveryDate'))
                if pkg.planned_delivery_date:
                    pkg.planned_delivery_date = pkg.planned_delivery_date.date()
                pkg.actual_delivery_date = _parse_dt(doc.get('RecipientDateTime'))
                pkg.package_cost        = float(doc.get('Cost') or 0)
                pkg.shipment_cost       = float(doc.get('CostOnSite') or 0)
                pkg.weight              = float(doc.get('Weight') or 0)
                pkg.package_count       = int(doc.get('SeatsAmount') or 1)
                pkg.description         = doc.get('Description')
                pkg.is_delivered        = doc.get('StateId') in [9, 10]
                pkg.raw_data            = doc

                if not is_new and old_status != pkg.status_code:
                    updated += 1

            db.session.commit()

            log = SyncLog(
                api_key_id       = api_key_obj.id,
                user_id          = user_id,
                sync_type        = sync_type,
                sync_direction   = 'incoming',
                packages_fetched = fetched,
                packages_created = created,
                packages_updated = updated,
                status           = 'success',
                api_response     = full_response
            )
            db.session.add(log)
            db.session.commit()
            results.append(f'In: {fetched}📦 ({created}🆕 {updated}🔄)')
        except Exception as e:
            db.session.rollback()
            log = SyncLog(api_key_id=api_key_obj.id, user_id=user_id, sync_type=sync_type,
                          sync_direction='incoming', status='error', error_message=str(e))
            db.session.add(log)
            db.session.commit()
            results.append(f'In: ❌ {str(e)[:50]}')
    elif direction in ['incoming', 'both'] and not api_key_obj.counterparty_ref:
        results.append('In: ⚠️ No counterparty_ref')

    return len(results) > 0, ' | '.join(results)


def cooldown_ok(api_key_obj):
    if not api_key_obj.last_sync:
        return True, None
    diff = datetime.utcnow() - api_key_obj.last_sync
    cd   = timedelta(minutes=5)
    if diff < cd:
        mins = int((cd - diff).total_seconds() / 60) + 1
        return False, f'Wait {mins} min'
    return True, None

# ---------------------------------------------------------------------------
# ROUTES – AUTH
# ---------------------------------------------------------------------------
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
            user.last_login = datetime.utcnow()
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

# ---------------------------------------------------------------------------
# ROUTES – MAIN
# ---------------------------------------------------------------------------
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        api_keys = APIKey.query.filter_by(is_active=True).all()
    else:
        api_keys = [tr.api_key for tr in current_user.tracked_apis if tr.api_key.is_active]

    api_ids = [k.id for k in api_keys]
    total   = Package.query.filter(Package.api_key_id.in_(api_ids)).count() if api_ids else 0
    active  = Package.query.filter(Package.api_key_id.in_(api_ids), Package.is_delivered == False).count() if api_ids else 0
    ready   = Package.query.filter(Package.api_key_id.in_(api_ids), Package.status_code == '7').count() if api_ids else 0

    return render_template('dashboard.html', api_keys=api_keys,
                           total_packages=total, active_packages=active,
                           ready_pickup=ready, now=datetime.now())


@app.route('/packages')
@login_required
def packages():
    page     = request.args.get('page', 1, type=int)
    per_page = current_user.items_per_page
    view     = request.args.get('view', current_user.view_mode)

    if current_user.role == 'admin':
        api_ids = [k.id for k in APIKey.query.filter_by(is_active=True).all()]
    else:
        api_ids = [tr.api_key_id for tr in current_user.tracked_apis if tr.api_key.is_active]

    q = Package.query.filter(Package.api_key_id.in_(api_ids)) if api_ids else Package.query.filter_by(id=-1)

    direction = request.args.get('direction')
    if direction and direction != 'all':
        q = q.filter_by(direction=direction)

    api_filter = request.args.getlist('api')
    if api_filter:
        q = q.filter(Package.api_key_id.in_([int(x) for x in api_filter]))

    status_filter = request.args.get('status')
    if status_filter == 'active':
        q = q.filter_by(is_delivered=False)
    elif status_filter == 'delivered':
        q = q.filter_by(is_delivered=True)

    days = request.args.get('days', type=int)
    if days:
        q = q.filter(Package.date_created >= datetime.now() - timedelta(days=days))

    q = q.order_by(desc(Package.date_created))
    pagination   = q.paginate(page=page, per_page=per_page, error_out=False)
    available_apis = APIKey.query.filter(APIKey.id.in_(api_ids)).all() if api_ids else []

    return render_template('packages.html', packages=pagination.items,
                           pagination=pagination, available_apis=available_apis,
                           view_mode=view)


@app.route('/package/<int:package_id>')
@login_required
def package_detail(package_id):
    pkg = Package.query.get_or_404(package_id)
    if current_user.role != 'admin':
        ids = [tr.api_key_id for tr in current_user.tracked_apis]
        if pkg.api_key_id not in ids:
            return jsonify({'error': 'Access denied'}), 403
    return render_template('package_detail.html', package=pkg)


@app.route('/package/<tracking_number>/invoice')
@login_required
def package_invoice(tracking_number):
    pkg = Package.query.filter_by(tracking_number=tracking_number).first_or_404()
    if current_user.role != 'admin':
        ids = [tr.api_key_id for tr in current_user.tracked_apis]
        if pkg.api_key_id not in ids:
            flash('Access denied.', 'danger')
            return redirect(url_for('packages'))
    url = f"https://my.novaposhta.ua/orders/printDocument/orders[]/{tracking_number}/type/pdf/apiKey/{pkg.api_key.api_key}"
    return redirect(url)


@app.route('/sync/<int:api_key_id>', methods=['POST'])
@login_required
def sync_api(api_key_id):
    """Unified sync - syncs single API key (both directions)"""
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
    """Sync all API keys available to user"""
    if current_user.role == 'admin':
        keys = APIKey.query.filter_by(is_active=True).all()
    else:
        keys = [tr.api_key for tr in current_user.tracked_apis if tr.api_key.is_active]
    
    results = []
    for key in keys:
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
        current_user.theme          = request.form.get('theme', 'light')
        current_user.view_mode      = request.form.get('view_mode', 'table')
        current_user.items_per_page = int(request.form.get('items_per_page', 20))
        current_user.notify_ready_pickup = bool(request.form.get('notify_ready_pickup'))
        current_user.language       = request.form.get('language', 'uk')
        if current_user.role != 'admin':
            UserAPITracking.query.filter_by(user_id=current_user.id).delete()
            for aid in request.form.getlist('tracked_apis'):
                db.session.add(UserAPITracking(user_id=current_user.id, api_key_id=int(aid)))
        db.session.commit()
        flash(t('save') + ' ✓', 'success')
        return redirect(url_for('settings'))
    available_apis  = APIKey.query.filter_by(is_active=True).all()
    tracked_api_ids = [tr.api_key_id for tr in current_user.tracked_apis]
    return render_template('settings.html', available_apis=available_apis,
                           tracked_api_ids=tracked_api_ids)

# ---------------------------------------------------------------------------
# ROUTES – ADMIN
# ---------------------------------------------------------------------------
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
        user.role      = request.form.get('role')
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
        key.label             = request.form.get('label')
        key.sender_identifier = request.form.get('sender_identifier')
        key.counterparty_ref  = request.form.get('counterparty_ref')
        key.auto_sync         = bool(request.form.get('auto_sync'))
        key.is_active         = bool(request.form.get('is_active'))
        db.session.commit()
        flash(f'API key "{key.label}" updated.', 'success')
        return redirect(url_for('admin_api_keys'))
    return render_template('admin/edit_api_key.html', api_key=key)


@app.route('/admin/api-keys/export')
@role_required('admin')
def admin_export_api_keys():
    keys = APIKey.query.all()
    data = []
    for k in keys:
        data.append({
            'label': k.label,
            'api_key': k.api_key,
            'sender_identifier': k.sender_identifier,
            'counterparty_ref': k.counterparty_ref,
            'auto_sync': k.auto_sync,
            'is_active': k.is_active
        })
    
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
        imported = 0
        skipped = 0
        
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
    
    return redirect(url_for('admin_api_keys'))


@app.route('/admin/log')
@role_required('admin')
def admin_log():
    page      = request.args.get('page', 1, type=int)
    per_page  = 50
    q         = SyncLog.query

    f_status  = request.args.get('status')
    f_type    = request.args.get('type')
    f_api     = request.args.get('api', type=int)
    f_user    = request.args.get('user', type=int)
    f_days    = request.args.get('days', type=int)

    if f_status:  q = q.filter(SyncLog.status == f_status)
    if f_type:    q = q.filter(SyncLog.sync_type == f_type)
    if f_api:     q = q.filter(SyncLog.api_key_id == f_api)
    if f_user:    q = q.filter(SyncLog.user_id == f_user)
    if f_days:    q = q.filter(SyncLog.created_at >= datetime.utcnow() - timedelta(days=f_days))

    pagination = q.order_by(desc(SyncLog.created_at)).paginate(page=page, per_page=per_page, error_out=False)
    api_keys   = APIKey.query.all()
    users      = User.query.all()
    return render_template('admin/log.html', logs=pagination.items, pagination=pagination,
                           api_keys=api_keys, users=users)


@app.route('/admin/log/<int:log_id>/details')
@role_required('admin')
def admin_log_details(log_id):
    log = SyncLog.query.get_or_404(log_id)
    return render_template('admin/log_details.html', log=log)


# ---------------------------------------------------------------------------
# INIT
# ---------------------------------------------------------------------------
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


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
