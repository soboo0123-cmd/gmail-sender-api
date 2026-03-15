성공하신 것을 축하드립니다\! 여러 차례의 시행착오를 거쳐 완성된 \*\*'Gmail SMTP 기반 메일 발송 API'\*\*의 최종 가이드를 정리해 드립니다.

이 내용은 처음에 계획했던 Resend 방식 대신, **Gmail과 Vercel을 활용하여 누구나 무료로 안정적인 메일 서버를 구축**할 수 있도록 최적화된 코드와 설정을 포함하고 있습니다.

# ---

**📧 Gmail SMTP & FastAPI 메일 발송 API 구축 가이드 (최종본)**

본 문서는 \*\*Python(FastAPI)\*\*을 사용하여 메일 발송 API를 구축하고, **Vercel**에 배포하여 **Gmail 계정**으로 메일을 발송하는 전체 과정을 담고 있습니다.

## **1\. 시스템 아키텍처**

1. **호출자 (Caller):** 뉴스 스크랩 프로그램 등이 JSON 형식으로 POST 요청을 보냅니다.  
2. **API 서버 (FastAPI/Vercel):** 요청을 받아 유효성 검사를 수행하고 Google SMTP 서버와 통신합니다.  
3. **메일 엔진 (Google SMTP):** 사용자의 Gmail 앱 비밀번호를 통해 메일을 인증하고 발송합니다.

## ---

**2\. 단계별 구축 절차**

### **1단계: Google 계정 보안 설정**

1. **2단계 인증 활성화:** 메일을 보낼 Google 계정 설정에서 2단계 인증을 켭니다.  
2. **앱 비밀번호 생성:** \[구글 계정 관리 \> 보안 \> 앱 비밀번호\]에서 **16자리 비밀번호**를 발급받아 메모해 둡니다. (이 번호가 실제 비밀번호 대신 사용됩니다.)

### **2단계: 프로젝트 파일 구성 (GitHub)**

GitHub 저장소를 만들고 다음 3개 파일을 생성합니다. (폴더 구조: api/index.py, requirements.txt, vercel.json)

#### **① api/index.py (핵심 로직)**

Vercel에서 가장 안정적으로 인식하는 파일명과 구조입니다.

Python

import os  
import smtplib  
from email.mime.text import MIMEText  
from email.mime.multipart import MIMEMultipart  
from typing import List  
from fastapi import FastAPI, HTTPException  
from pydantic import BaseModel, EmailStr

app \= FastAPI()

class EmailRequest(BaseModel):  
    to: List\[EmailStr\]  
    subject: str  
    html: str

@app.get("/")  
def read\_root():  
    return {"message": "Gmail SMTP API is running\!"}

@app.post("/send-email")  
async def send\_email(request: EmailRequest):  
    gmail\_user \= os.getenv("GMAIL\_USER")  
    gmail\_app\_pass \= os.getenv("GMAIL\_APP\_PASS")

    if not gmail\_user or not gmail\_app\_pass:  
        raise HTTPException(status\_code=500, detail="환경 변수 설정이 누락되었습니다.")

    try:  
        with smtplib.SMTP("smtp.gmail.com", 587) as server:  
            server.starttls()  
            server.login(gmail\_user, gmail\_app\_pass)  
            for recipient in request.to:  
                msg \= MIMEMultipart()  
                msg\["From"\] \= gmail\_user  
                msg\["To"\] \= recipient  
                msg\["Subject"\] \= request.subject  
                msg.attach(MIMEText(request.html, "html"))  
                server.send\_message(msg)  
        return {"status": "success", "sent\_to": request.to}  
    except Exception as e:  
        raise HTTPException(status\_code=500, detail=str(e))

#### **② requirements.txt (라이브러리 설정)**

EmailStr 사용을 위해 email-validator를 반드시 포함해야 합니다.

Plaintext

fastapi  
uvicorn  
pydantic\[email\]  
email-validator

#### **③ vercel.json (배포 설정)**

런타임 버전을 명시하지 않는 가장 단순한 설정이 오류를 방지합니다.

JSON

{  
  "rewrites": \[  
    { "source": "/(.\*)", "destination": "/api/index" }  
  \]  
}

### **3단계: Vercel 배포 및 환경 변수 설정**

1. Vercel에서 GitHub 저장소를 **Import**합니다.  
2. **Environment Variables**에 다음 두 가지를 입력합니다.  
   * GMAIL\_USER: 본인의 Gmail 주소  
   * GMAIL\_APP\_PASS: 발급받은 16자리 앱 비밀번호  
3. **Deploy**를 눌러 배포를 완료합니다.

## ---

**3\. 실제 호출 방법 (Python 예시)**

API가 배포되었다면, 프로그램에서 아래와 같이 호출하여 사용할 수 있습니다.

Python

import requests

API\_URL \= "https://your-project.vercel.app/send-email"  
news\_data \= {  
    "to": \["recipient@naver.com"\],  
    "subject": "오늘의 뉴스 요약",  
    "html": "\<h1\>뉴스 브리핑\</h1\>\<p\>내용입니다.\</p\>"  
}

\# 주의: json= 매개변수를 사용하여 JSON 헤더를 자동으로 포함시킵니다.  
response \= requests.post(API\_URL, json=news\_data)

if response.status\_code \== 200:  
    print("발송 성공\!")  
else:  
    print(f"발송 실패: {response.text}")

## ---

**4\. 주의사항 및 유지보수**

* **422 에러 발생 시:** 호출 시 json=data 형식을 사용했는지, 데이터 형식이 Pydantic 모델과 일치하는지 확인하세요.  
* **500 에러 발생 시:** Vercel 대시보드의 **Logs** 탭을 확인하여 라이브러리(email-validator) 설치 여부나 앱 비밀번호 오타를 확인하세요.  
* **보안:** API가 공개되어 있으므로, 향후 X-API-KEY와 같은 헤더 인증 로직을 추가하는 것을 권장합니다.