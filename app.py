from flask import Flask, redirect, url_for
from flask_login import LoginManager
from config import Config
from models import db, User
from modules.auth import auth_bp
from modules.patient import patient_bp
from modules.doctor import doctor_bp
from modules.admin import admin_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Module Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(admin_bp)

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    with app.app_context():
        db.create_all()
        # Create Default Admin account if not exists
        if not User.query.filter_by(email='admin@healthwallet.com').first():
            admin = User(name='System Admin', email='admin@healthwallet.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)