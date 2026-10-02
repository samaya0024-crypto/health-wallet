import os
import hashlib
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import login_required, current_user
from cryptography.fernet import Fernet
from models import db, User, HealthRecord, AccessPermission, AccessLog

patient_bp = Blueprint('patient', __name__, url_prefix='/patient')

def get_cipher():
    # Helper to generate AES Fernet cipher
    key = Fernet.generate_key()
    return Fernet(key)

@patient_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'patient':
        return redirect(url_for('auth.login'))
    
    records = HealthRecord.query.filter_by(patient_id=current_user.id).all()
    permissions = AccessPermission.query.filter_by(patient_id=current_user.id).all()
    logs = AccessLog.query.join(HealthRecord).filter(HealthRecord.patient_id == current_user.id).order_by(AccessLog.timestamp.desc()).all()
    
    return render_template('patient_dashboard.html', records=records, permissions=permissions, logs=logs)


@patient_bp.route('/profile')
@login_required
def profile():
    if current_user.role != 'patient':
        return redirect(url_for('auth.login'))
        
    total_records = HealthRecord.query.filter_by(patient_id=current_user.id).count()
    granted_count = AccessPermission.query.filter_by(patient_id=current_user.id, status='Granted').count()
    
    return render_template('patient_profile.html', total_records=total_records, granted_count=granted_count)


@patient_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_record():
    if current_user.role != 'patient':
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        file = request.files.get('file')

        if file:
            file_data = file.read()
            
            # Module 3: AES Encryption & SHA-256 Hashing
            sha256_hash = hashlib.sha256(file_data).hexdigest()
            
            cipher = Fernet(Fernet.generate_key())
            encrypted_data = cipher.encrypt(file_data)

            filename = f"{current_user.id}_{int(datetime.utcnow().timestamp())}_{file.filename}.enc"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            with open(filepath, 'wb') as f:
                f.write(encrypted_data)

            # Simulated Web3 Mock Tx Hash (Replace with real Web3 deployment logic if needed)
            mock_tx_hash = f"0x{hashlib.sha256((sha256_hash + str(datetime.utcnow())).encode()).hexdigest()}"

            new_record = HealthRecord(
                patient_id=current_user.id,
                title=title,
                category=category,
                encrypted_file_path=filepath,
                sha256_hash=sha256_hash,
                tx_hash=mock_tx_hash
            )
            db.session.add(new_record)
            db.session.commit()

            flash('Health record encrypted and anchored to Blockchain successfully!', 'success')
            return redirect(url_for('patient.dashboard'))

    return render_template('upload_record.html')


@patient_bp.route('/grant-access', methods=['GET', 'POST'])
@login_required
def grant_access():
    if current_user.role != 'patient':
        return redirect(url_for('auth.login'))
        
    doctors = User.query.filter_by(role='doctor').all()
    records = HealthRecord.query.filter_by(patient_id=current_user.id).all()

    if request.method == 'POST':
        record_id = request.form.get('record_id')
        doctor_id = request.form.get('doctor_id')

        existing = AccessPermission.query.filter_by(
            record_id=record_id, 
            patient_id=current_user.id, 
            doctor_id=doctor_id
        ).first()

        if existing:
            existing.status = 'Granted'
        else:
            perm = AccessPermission(
                record_id=record_id,
                patient_id=current_user.id,
                doctor_id=doctor_id,
                status='Granted'
            )
            db.session.add(perm)

        db.session.commit()
        flash('Access granted successfully.', 'success')
        return redirect(url_for('patient.dashboard'))

    return render_template('grant_access.html', doctors=doctors, records=records)


@patient_bp.route('/revoke-access/<int:perm_id>')
@login_required
def revoke_access(perm_id):
    if current_user.role != 'patient':
        return redirect(url_for('auth.login'))

    perm = AccessPermission.query.get_or_404(perm_id)
    if perm.patient_id == current_user.id:
        perm.status = 'Revoked'
        
        # Log event
        log = AccessLog(
            record_id=perm.record_id,
            accessor_id=current_user.id,
            action=f"Access Revoked for Doctor ID {perm.doctor_id}"
        )
        db.session.add(log)
        db.session.commit()
        flash('Access revoked successfully.', 'warning')

    return redirect(url_for('patient.dashboard'))