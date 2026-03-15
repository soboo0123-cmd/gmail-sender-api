import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

# Vercel 배포를 위해 app 객체를 명시적으로 선언
app = FastAPI()

class EmailRequest(BaseModel):
    to: List[EmailStr]
    subject: str
    html: str

@app.get("/")
def read_root():
    return {"message": "Gmail SMTP API is running!"}

@app.post("/send-email")
async def send_email(request: EmailRequest):
    gmail_user = os.getenv("GMAIL_USER")
    gmail_app_pass = os.getenv("GMAIL_APP_PASS")

    if not gmail_user or not gmail_app_pass:
        raise HTTPException(status_code=500, detail="Environment variables GMAIL_USER or GMAIL_APP_PASS are missing.")

    try:
        # SMTP 연결 (매번 연결하고 끊는 방식이 서버리스에 적합합니다)
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(gmail_user, gmail_app_pass)

            for recipient in request.to:
                msg = MIMEMultipart()
                msg["From"] = gmail_user
                msg["To"] = recipient
                msg["Subject"] = request.subject
                msg.attach(MIMEText(request.html, "html"))
                server.send_message(msg)
        
        return {"status": "success", "sent_to": request.to}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
