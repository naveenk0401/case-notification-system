from datetime import date
import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client
from sqlalchemy.orm import Session
from database import SessionLocal
import models
import os
from dotenv import load_dotenv

load_dotenv()

# 🔹 Email config
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# 🔹 Twilio config
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")

def send_email(to_email: str, subject: str, message: str):
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, to_email, msg.as_string())

def send_sms(to_number: str, message: str):
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=message,
        from_=TWILIO_PHONE,
        to=to_number
    )

def notify_upcoming_cases():
    db: Session = SessionLocal()
    today = date.today()

    # Fetch cases where next_hearing_date >= today
    cases = db.query(models.Case).filter(models.Case.next_hearing_date >= today).all()

    for case in cases:
        user = db.query(models.User).filter(models.User.id == case.user_id).first()
        if not user:
            continue

        msg = f"Hello {user.name},\nYour case '{case.case_details}' has next hearing on {case.next_hearing_date}.\nStatus: {case.status}"

        # Send email
        send_email(user.email, "Upcoming Case Hearing", msg)

        # Send SMS
        send_sms(user.mobile, msg)

    db.close()
