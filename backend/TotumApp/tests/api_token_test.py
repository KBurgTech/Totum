import datetime

from django.urls import reverse
from rest_framework import status

from TotumApp.tests.helpers import BaseTestCase


class ApiTokenViewModelTest(BaseTestCase):

    def setUp(self):
        self.admin_users = self._create_admin_user(1)
        self.users = self._create_user(5)
        self.tenants = self._create_tenant(2)

    def test_create(self):
        data = {
            'tenant': f"{self.tenants[0].uuid}",
            'expiry_date': datetime.datetime.now() + datetime.timedelta(days=10)
        }
        no_auth, auth = self._test_auth_not_auth(
            self.users[0],
            {
                "path": reverse("core:users-create-api-token", args=[f"{self.users[0].uuid}"]),
                "data": data,
                "format": "json"
            },
            "post"
        )
        self.assertEqual(no_auth.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(auth.status_code, status.HTTP_404_NOT_FOUND)

        self.tenants[0].users.add(self.users[0])
        self.tenants[0].save()
        resp = self._request(
            self.users[0],
            {
                "path": reverse("core:users-create-api-token", args=[f"{self.users[0].uuid}"]),
                "data": data,
                "format": "json"
            },
            "post"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertNotEquals(resp.data["key"], "")

    def test_get(self):
        data = {
            'tenant': f"{self.tenants[0].uuid}",
            'expiry_date': datetime.datetime.now() + datetime.timedelta(days=10)
        }
        self.tenants[0].users.add(self.users[0])
        self.tenants[0].save()

        self._request(
            self.users[0],
            {
                "path": reverse("core:users-create-api-token", args=[f"{self.users[0].uuid}"]),
                "data": data,
                "format": "json"
            },
            "post"
        )
        no_auth, auth = self._test_auth_not_auth(
            self.users[0],
            {
                "path": reverse("core:users-get-api-tokens", args=[f"{self.users[0].uuid}"]),
                "data": None,
                "format": "json"
            },
            "get"
        )
        self.assertEqual(no_auth.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(auth.status_code, status.HTTP_200_OK)
        self.assertEqual(len(auth.data), 1)

    def test_delete(self):
        data = {
            'tenant': f"{self.tenants[0].uuid}",
            'expiry_date': datetime.datetime.now() + datetime.timedelta(days=10)
        }
        self.tenants[0].users.add(self.users[0])
        self.tenants[0].save()

        create_req = self._request(
            self.users[0],
            {
                "path": reverse("core:users-create-api-token", args=[f"{self.users[0].uuid}"]),
                "data": data,
                "format": "json"
            },
            "post"
        )
        no_auth, auth = self._test_auth_not_auth(
            self.users[0],
            {
                "path": reverse("core:users-delete-api-token", args=[f"{self.users[0].uuid}"]),
                "data": {'id': create_req.data['uuid']},
                "format": "json"
            },
            "delete"
        )
        self.assertEqual(no_auth.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(auth.status_code, status.HTTP_200_OK)
