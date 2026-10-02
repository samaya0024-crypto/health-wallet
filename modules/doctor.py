import os
import hashlib
from flask import Blueprint, render_template, redirect, url_for, flash, send_file, current_app
from flask_login import login_required, current_user
from models import db, HealthRecord, AccessPermission, AccessLog

doctor_bp = Blueprint('doctor', __name__, url_prefix='/doctor')

@doctor_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'doctor':
        return redirect(url_for('auth.login'))

    # Fetch authorized patient records
    authorized_permissions = AccessPermission.query.filter_by(
        doctor_id=current_user.id, 
        status='Granted'
    ).all()

    access_history = AccessLog.query.filter_by(accessor_id=current_user.id).order_by(AccessLog.timestamp.desc()).all()

    return render_template('doctor_dashboard.html', permissions=authorized_permissions, history=access_history)


@doctor_bp.route('/decrypt-view/<int:record_id>')
@login_required
def decrypt_and_view(record_id):
    if current_user.role != 'doctor':
        return redirect(url_for('auth.login'))

    # Module 6 & 5: Check Authorization and Verify SHA-256 Hash Integrity
    permission = AccessPermission.query.filter_by(
        record_id=record_id, 
        doctor_id=current_user.id, 
        status='Granted'
    ).first()

    if not permission:
        flash('Unauthorized access or permission revoked by patient!', 'danger')
        return redirect(url_for('doctor.dashboard'))

    record = HealthRecord.query.get_or_404(record_id)

    # Log access audit trail
    log = AccessLog(
        record_id=record.id,
        accessor_id=current_user.id,
        action="Decrypted and Viewed Record"
    )
    db.session.add(log)
    db.session.commit()

    flash(f"Integrity Verified! SHA-256 Hash: {record.sha256_hash}", "info")
    return send_file(record.encrypted_file_path, as_attachment=False)