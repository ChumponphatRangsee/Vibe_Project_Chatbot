import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/mydb')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL', 'http://localhost:5678/webhook/chat')
    # Klevu API Configuration
    KLEVU_STORE_URL = os.getenv('KLEVU_STORE_URL')
    KLEVU_API_KEY = os.getenv('KLEVU_API_KEY')
    KLEVU_REST_AUTH_KEY = os.getenv('KLEVU_REST_AUTH_KEY')
    KLEVU_CLOUD_SEARCH_URL = os.getenv('KLEVU_CLOUD_SEARCH_URL')