from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models import User, HealthRecord, AccessPermission, AccessLog

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))

    patients = User.query.filter_by(role='patient').all()
    doctors = User.query.filter_by(role='doctor').all()
    records = HealthRecord.query.all()
    permissions = AccessPermission.query.all()
    logs = AccessLog.query.order_by(AccessLog.timestamp.desc()).all()

    return render_template(
        'admin_dashboard.html', 
        patients=patients, 
        doctors=doctors, 
        records=records, 
        permissions=permissions, 
        logs=logs
    )