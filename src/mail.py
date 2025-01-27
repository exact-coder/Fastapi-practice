from fastapi import status
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi.background import BackgroundTasks
from typing import List
from src.config import Config
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


mail_config = ConnectionConfig(
    MAIL_USERNAME = Config.MAIL_USERNAME,
    MAIL_PASSWORD = Config.MAIL_PASSWORD,
    MAIL_FROM = Config.MAIL_FROM,
    MAIL_PORT = 587,
    MAIL_SERVER = Config.MAIL_SERVER,
    MAIL_FROM_NAME = Config.MAIL_FROM_NAME,
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True,
    TEMPLATE_FOLDER= Path(BASE_DIR, 'templates')
)

mail = FastMail(
    config=mail_config,
)

def create_message(
    recipients:list[str], 
    subject:str, 
    body: str,
    background_tasks= BackgroundTasks
    ):

    message = MessageSchema(
        recipients=recipients,
        subject=subject,
        body=body,
        subtype=MessageType.html,
    )

    background_tasks.add_task(mail.send_message,message)

    return {
        "status_code": status.HTTP_201_CREATED,
        "message": "Email has been sent",
        "mail": message

    }