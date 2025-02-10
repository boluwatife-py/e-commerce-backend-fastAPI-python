import smtplib
from email.mime.text import MIMEText
from core.config import settings


def send_verification_email(email: str, token: str):
    verification_link = f"{settings.BASE_URL}/verify-email?token={token}"
    
    subject = "Verify Your Email"
    body = f"Click the link to verify your email: {verification_link}\n\nThis link expires in 30 minutes."

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_USERNAME
    msg["To"] = email

    with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_USERNAME, email, msg.as_string())
