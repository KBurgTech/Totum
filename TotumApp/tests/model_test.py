import datetime

from django.test import TestCase

from TotumApp.models import TotumUser, ApiToken, Tenant


class GenericModelTests(TestCase):
    def setUp(self):
        user = TotumUser.objects.create_user("testuser", "email@test.com", "1234567890abc!", first_name="Test",
                                             last_name="User")
        tenant = Tenant.objects.create(slug="tt", name="Test Tenant")

        ApiToken.objects.create(user=user, tenant=tenant,
                                expiry_date=datetime.datetime.now() + datetime.timedelta(days=200), key="ABCDEFG")

    def test_user_has_uuid(self):
        obj = TotumUser.objects.get(email="email@test.com")
        self.assertIsNotNone(obj.uuid)

    def test_tenant_has_uuid(self):
        obj = Tenant.objects.get(slug="tt")
        self.assertIsNotNone(obj.uuid)

    def test_api_token_has_uuid(self):
        obj = ApiToken.objects.get(key="ABCDEFG")
        self.assertIsNotNone(obj.uuid)
