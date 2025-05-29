import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from jose import jwt

from app.config import settings
from app.database import init_db
from app.main import app
from app.models import Notification
from tests.factories import NotificationFactory

client = TestClient(app)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def init_test_db():

    await init_db(settings.TEST_DATABASE_NAME)

    await Notification.delete_all()
    yield
    await Notification.delete_all()


######################################################################
#  H E L P E R   M E T H O D S
######################################################################


async def _create_notifications(client: AsyncClient, count):
    """Factory method to create notifications in bulk"""

    notifications = []

    for _ in range(count):
        notif = NotificationFactory()
        response = await client.post(
            "/notification",
            json={"message": notif.message, "recipient_id": notif.recipient_id},
        )
        assert response.status_code == 200, "Failed to create notification"
        notifications.append(response.json())

    return notifications


def create_test_jwt(user_id: int) -> str:
    payload = {"sub": str(user_id)}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token


######################################################################
#  T E S T   C A S E S
######################################################################


def test_read_root():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Notification API"}


@pytest.mark.asyncio
async def test_read_all_notifications():
    """Test retrieval of notifications for a specific authenticated user"""
    test_user_id = 42  # or any test user ID
    token = create_test_jwt(test_user_id)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        for i in range(3):
            payload = {
                "message": f"Test notification {i}",
                "recipient_id": test_user_id,
            }
            await client.post("/notification", json=payload)

        for i in range(2):
            payload = {
                "message": f"Other user notification {i}",
                "recipient_id": 999,  # a different user
            }
            await client.post("/notification", json=payload)

        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/notification", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3
        assert all(n["recipient_id"] == test_user_id for n in data)
