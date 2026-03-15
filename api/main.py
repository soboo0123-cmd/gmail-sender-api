import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

app = FastAPI()

# 1. 데이터 모델 정의
class EmailRequest(BaseModel):
    to: List[EmailStr]
    subject: str
    html: str

@app.get("/")
def read_root():
    return {"message": "Gmail SMTP API is running!"}

@app.post("/send-email")
async def send_email(request: EmailRequest):
    # 환경 변수에서 구글 계정 정보 가져오기
    gmail_user = os.getenv("GMAIL_USER")
    gmail_app_pass = os.getenv("GMAIL_APP_PASS")

    if not gmail_user or not gmail_app_pass:
        raise HTTPException(status_code=500, detail="서버 환경 변수 설정이 누락되었습니다.")

    try:
        # 2. SMTP 연결 설정
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # TLS 보안 연결
        server.login(gmail_user, gmail_app_pass)

        # 3. 메일 구성 및 발송
        for recipient in request.to:
            msg = MIMEMultipart()
            msg["From"] = gmail_user
            msg["To"] = recipient
            msg["Subject"] = request.subject
            msg.attach(MIMEText(request.html, "html"))
            
            server.send_message(msg)
        
        server.quit()
        return {"status": "success", "sent_to": request.to}

    except smtplib.SMTPAuthenticationError:
        raise HTTPException(status_code=401, detail="구글 로그인 실패. 앱 비밀번호를 확인하세요.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
