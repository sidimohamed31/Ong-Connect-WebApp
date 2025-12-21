import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super_secret_key_ong_connect_CHANGE_IN_PROD'
    
    # Database
    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_USER = os.environ.get('DB_USER') or 'root'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or 'sidimedtop1'
    DB_NAME = os.environ.get('DB_NAME') or 'ong_connecte'
    
    # Paths
    UPLOAD_FOLDER = os.path.join('static', 'uploads', 'media')
    LOGO_FOLDER = os.path.join('static', 'uploads', 'logos')
