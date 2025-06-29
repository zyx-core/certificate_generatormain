from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import smtplib
from email.message import EmailMessage

router = APIRouter()

class EmailSchema(BaseModel):
    to: str
    subject: str
    content: str

@router.post("/send")
async def send_email(email: EmailSchema):
    try:
        sender_email = "ershadpersonal123@gmail.com"
        sender_password = "cxyt tthe gkvu alei"  # NOT your Gmail password

        message = EmailMessage()
        message["From"] = sender_email
        message["To"] = email.to
        message["Subject"] = email.subject
        message.set_content(email.content)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(message)

        return JSONResponse(content={"message": "Email sent successfully"})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
