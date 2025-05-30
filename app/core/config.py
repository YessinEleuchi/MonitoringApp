from dotenv import load_dotenv
import os

# Charge le fichier .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL non défini dans .env")
