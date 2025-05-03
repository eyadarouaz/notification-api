from datetime import datetime
from uuid import uuid4

import factory
from faker import Faker

from app.models import Notification

fake = Faker()


class NotificationFactory(factory.Factory):
    class Meta:
        model = Notification

    id = factory.LazyFunction(uuid4)
    message = factory.LazyAttribute(lambda _: fake.sentence(nb_words=6))
    recipient_id = factory.LazyAttribute(lambda _: fake.random_int(min=1, max=1000))
    created_at = factory.LazyFunction(datetime.utcnow)
