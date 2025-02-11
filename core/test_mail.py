import smtplib
from config import settings


try:
    server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT, timeout=10)
    server.starttls()
    server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
    print("✅ SMTP connection successful!")
    server.quit()
except Exception as e:
    print(f"❌ SMTP connection failed: {e}")
