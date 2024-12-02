import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Basic Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///topup.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Supabase Configuration
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    
    # File Upload Configuration
    UPLOAD_FOLDER = os.path.join('static', 'img', 'courses')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size