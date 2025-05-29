import asyncio
import json
import logging

from azure.servicebus import ServiceBusMessage
from azure.servicebus.aio import ServiceBusClient
from fastapi import Depends, FastAPI, HTTPException
from mailersend import emails

from app.config import settings
from app.database import init_db
from app.logging_config import setup_logging
from app.models import Notification, NotificationCreate
from app.utils import TokenData, get_current_user

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()

mailer = emails.NewEmail(settings.API_KEY)


async def send_verification_email(to_email: str, code: str):
    try:
        mail_body = {
            "from": {"email": settings.FROM_EMAIL},
            "to": [{"email": to_email}],
            "subject": "Your Verification Code",
            "text": f"Your verification code is: {code}",
        }

        response = mailer.send(mail_body)
        logger.info(f"Sent verification email to {to_email}, status code:{response}")

    except Exception as e:
        logger.error(f"MailerSend failed to send email to {to_email}: {str(e)}")


async def handle_message(msg: ServiceBusMessage):
    try:
        body_parts = list(msg.body)
        body_bytes = b"".join(body_parts)
        raw_body = body_bytes.decode("utf-8", errors="replace")

        payload = json.loads(raw_body)

        if payload.get("eventType") == "SEND_VALIDATION_CODE":
            email = payload["email"]
            user_id = payload["userId"]
            code = payload["code"]
            action = payload["action"]

            logger.info(f"Received SEND_VALIDATION_CODE for {email} (action: {action})")
            await send_verification_email(email, code)

            if payload.get("action") == "register":
                message = "Welcome! You have just created your account."
            elif payload.get("action") == "reset_password":
                message = "You requested to reset your password."
            else:
                message = "Verification code sent."

            notification = Notification(message=message, recipient_id=int(user_id))
            await notification.insert()
            logger.info(f"Notification saved for user {user_id} with action {action}")

        else:
            logger.warning(f"Ignoring unknown event type: {payload.get('eventType')}")
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")


async def listen_for_messages():
    async with ServiceBusClient.from_connection_string(
        settings.CONNECTION_STRING
    ) as client:
        receiver = client.get_queue_receiver(queue_name=settings.QUEUE_NAME)
        async with receiver:
            async for msg in receiver:
                await handle_message(msg)
                await receiver.complete_message(msg)


@app.on_event("startup")
async def on_startup():
    await init_db()
    asyncio.create_task(listen_for_messages())
    logger.info("Collections created (if not already existing)")
    logger.info("Notification service started and listening for messages")


@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the Notification API"}


@app.get("/notification", response_model=list[Notification])
async def read_notification(current_user: TokenData = Depends(get_current_user)):
    notifications = await Notification.find(
        Notification.recipient_id == current_user.user_id
    ).to_list()
    if not notifications:
        raise HTTPException(
            status_code=404, detail="No notifications found for this user"
        )
    return notifications


@app.post("/notification", response_model=Notification)
async def create_notification(notification_data: NotificationCreate):
    notification = Notification(**notification_data.dict())
    await notification.insert()
    logger.info(f"Created notification for recipient {notification.recipient_id}")
    return notification
