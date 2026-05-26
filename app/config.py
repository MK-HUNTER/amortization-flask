import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'enterprise_secret_token_key_001')
    DB_FILE = os.environ.get('DB_FILE', 'amortization.db')