# models.py
from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

DEFAULT_TIMEZONE = 'Europe/Kyiv'


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
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime(timezone=True))
    tracked_apis = db.relationship('UserAPITracking', back_populates='user', cascade='all, delete-orphan')
    telegram_user_id = db.Column(db.BigInteger, unique=True, nullable=True)
    telegram_notifications = db.Column(db.Boolean, default=True)
    telegram_linked_at = db.Column(db.DateTime, nullable=True)

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
    sender_contact_name = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    auto_sync = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    last_sync = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
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
    date_created = db.Column(db.DateTime(timezone=True))
    planned_delivery_date = db.Column(db.Date)
    actual_delivery_date = db.Column(db.DateTime(timezone=True))
    package_cost = db.Column(db.Numeric(10, 2))
    shipment_cost = db.Column(db.Numeric(10, 2))
    weight = db.Column(db.Numeric(10, 3))
    package_count = db.Column(db.Integer, default=1)
    seats_amount = db.Column(db.Integer, default=1)
    seats_data = db.Column(db.JSON)
    cost = db.Column(db.Numeric(10, 2))
    payment_method = db.Column(db.String(50))
    cargo_type = db.Column(db.String(50))
    description = db.Column(db.Text)
    is_delivered = db.Column(db.Boolean, default=False)
    last_updated = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    raw_data = db.Column(db.JSON)
    author = db.Column(db.String(100))
    draft_status = db.Column(db.String(20))
    draft_data = db.Column(db.Text)
    api_key = db.relationship('APIKey', back_populates='packages')


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
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    usage_count = db.Column(db.Integer, default=0)


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
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_used = db.Column(db.DateTime(timezone=True))


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
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class TelegramLinkCode(db.Model):
    """Temporary codes for linking Telegram accounts to web app users"""
    __tablename__ = 'telegram_link_codes'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16), unique=True, nullable=False, index=True)
    telegram_user_id = db.Column(db.BigInteger, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    used = db.Column(db.Boolean, default=False)
    user = db.relationship('User', backref='telegram_link_codes')