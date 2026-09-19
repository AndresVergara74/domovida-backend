# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./domovida.db")
    AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
    AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    TWILIO_SID = os.getenv("TWILIO_SID")
    TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
    TWILIO_FROM = os.getenv("TWILIO_FROM")
    SECRET_KEY = os.getenv("SECRET_KEY", "domovida-secret-key")

settings = Settings()