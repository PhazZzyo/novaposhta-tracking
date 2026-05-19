# routes/auth.py
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/set-language/<lang>')
@login_required
def set_language(lang):
    if lang in ('en', 'uk'):
        current_user.language = lang
        db.session.commit()
    return redirect(request.referrer or url_for('packages.dashboard'))


@auth_bp.route('/')
def index():
    return redirect(url_for('packages.dashboard') if current_user.is_authenticated else url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('packages.dashboard'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and user.check_password(request.form.get('password')) and user.is_active:
            login_user(user, remember=bool(request.form.get('remember')))
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            if user.must_change_password:
                flash('Please change your password.', 'warning')
                return redirect(url_for('auth.change_password'))
            return redirect(request.args.get('next') or url_for('packages.dashboard'))
        flash('Invalid username or password.', 'danger')
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
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
            return redirect(url_for('packages.dashboard'))
    return render_template('change_password.html')
