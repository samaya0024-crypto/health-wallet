import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'health_wallet_super_secret_key_123')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///health_wallet.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Max 16MB per upload
    
    # AES-256 Encryption key (32 bytes urlsafe base64 string)
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', 'dGhpcy1pcy1hLXN1cGVyLXNlY3JldC0zMi1ieXRlLWtleSE=')
    
    # Web3 / Ethereum RPC (Ganache / Sepolia)
    WEB3_PROVIDER = os.environ.get('WEB3_PROVIDER', 'http://127.0.0.1:8545')