from django.test import TestCase

from TotumApp.models import TotumUser, Tenant

USER_PASSWORD = "123456789!ABC"


class BaseTestCase(TestCase):
    @staticmethod
    def _create_tenant(count):
        tenants = []
        for i in range(1, count + 1):
            tenants.append(Tenant.objects.create(slug=f"slug{i}", name=f"Tenant {i}"))

        return tenants

    @staticmethod
    def _create_admin_user(count):
        admin_users = []
        for i in range(1, count + 1):
            admin_users.append(
                TotumUser.objects.create_superuser(f"admin{i}", f"admin{i}@email.com", USER_PASSWORD))
        return admin_users

    @staticmethod
    def _create_user(count):
        users = []
        for i in range(1, count + 1):
            users.append(
                TotumUser.objects.create_user(f"user{i}", f"user{i}@email.com", USER_PASSWORD, first_name=f"Test{i}",
                                              last_name=f"User{i}"))
        return users

    def _request(self, user, request, mode):
        func = getattr(self.client, mode)
        self.assertIsNotNone(func)
        if user is not None:
            self.assertTrue(self.client.login(email=user.email, password=USER_PASSWORD))
        auth_resp = func(**request, content_type="application/json")
        self.client.logout()
        return auth_resp

    def _test_auth_not_auth(self, user, request, mode):
        func = getattr(self.client, mode)
        self.assertIsNotNone(func)

        non_auth_resp = func(**request, content_type="application/json")
        self.assertTrue(self.client.login(email=user.email, password=USER_PASSWORD))
        auth_resp = func(**request, content_type="application/json")
        self.client.logout()

        return non_auth_resp, auth_resp
