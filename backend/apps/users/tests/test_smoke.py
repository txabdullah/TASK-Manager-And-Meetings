from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class SmokeTests(TestCase):
    def test_create_user(self):
        User.objects.create_user(
            username="ci_user",
            email="ci@example.com",
            password="testpass12345",
        )
        self.assertEqual(User.objects.count(), 1)
