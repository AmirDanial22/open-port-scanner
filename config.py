import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-123')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///scans.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL', None)
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', None)