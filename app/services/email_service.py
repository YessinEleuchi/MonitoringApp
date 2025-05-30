import os
import smtplib
import logging
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.username = os.getenv("SMTP_USERNAME")
        self.password = os.getenv("SMTP_PASSWORD")
        self.sender_name = os.getenv("SMTP_SENDER_NAME", "Monitoring App")

        if not all([self.smtp_server, self.username, self.password]):
            raise RuntimeError("❌ Configuration SMTP manquante")

    def send_email(self, to_email: str, subject: str, html_content: str, plain_text: str = "") -> None:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = f"{self.sender_name} <{self.username}>"
        msg["To"] = to_email
        msg.set_content(plain_text or "Consultez ce message dans un client supportant HTML.")
        msg.add_alternative(html_content, subtype="html")

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
                logger.info(f"📧 Email envoyé à {to_email}")
        except Exception as e:
            logger.error(f"❌ Erreur envoi SMTP : {str(e)}")
            raise RuntimeError("Échec de l’envoi de l’e-mail.")
