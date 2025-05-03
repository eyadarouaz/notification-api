import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

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
    """Test the retrieval of all notifications"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        await _create_notifications(client, 3)

        response = await client.get("/notification")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3
