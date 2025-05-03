import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mongodb://mongo:27017")
    TEST_DATABASE_NAME: str = os.getenv("TEST_DATABASE_NAME", "test-notif-db")
    CONNECTION_STRING: str = os.getenv("AZURE_SERVICE_BUS_CONNECTION_STRING")
    QUEUE_NAME: str = os.getenv("AZURE_SERVICE_BUS_QUEUE_NAME")
    API_KEY: str = os.getenv("MAILERSEND_API_KEY")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL")


settings = Settings()
