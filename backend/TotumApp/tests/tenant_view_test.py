from django.urls import reverse
from rest_framework import status

from TotumApp.models import Tenant
from TotumApp.tests.helpers import BaseTestCase


class TenantViewModelTest(BaseTestCase):

    def setUp(self):
        self.admin_users = self._create_admin_user(1)
        self.users = self._create_user(5)

    def test_create(self):
        data = {
            "slug": "slugcreate",
            "name": "Tenant from API",
        }

        no_auth, auth = self._test_auth_not_auth(
            self.users[0],
            {
                "path": reverse("core:tenants-list"),
                "data": data,
                "format": "json"
            },
            "post"
        )

        self.assertEqual(no_auth.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(auth.status_code, status.HTTP_201_CREATED)

        tenant = Tenant.objects.get(uuid=auth.data["uuid"])
        self.assertIsNotNone(tenant)
        self.assertIn(self.users[0], tenant.users.all())

    def test_list(self):
        tenants = self._create_tenant(3)

        tenants[0].users.add(self.users[0])
        tenants[0].save()
        tenants[1].users.add(self.users[0], self.users[1])
        tenants[1].save()

        no_auth, auth = self._test_auth_not_auth(
            self.users[1],
            {
                "path": reverse("core:tenants-list"),
                "data": None,
                "format": "json"
            },
            "get"
        )
        self.assertEqual(no_auth.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(auth.status_code, status.HTTP_200_OK)
        self.assertEqual(len(auth.data), 1)

        no_auth, auth = self._test_auth_not_auth(
            self.admin_users[0],
            {
                "path": reverse("core:tenants-list"),
                "data": None,
                "format": "json"
            },
            "get"
        )
        self.assertEqual(no_auth.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(auth.status_code, status.HTTP_200_OK)
        self.assertEqual(len(auth.data), 3)

    def test_get(self):
        tenants = self._create_tenant(2)

        tenants[0].users.add(self.users[0])
        tenants[0].save()
        tenants[1].users.add(self.users[0], self.users[1])
        tenants[1].save()

        no_auth, auth = self._test_auth_not_auth(
            self.users[1],
            {
                "path": reverse("core:tenants-detail", args=[f"{tenants[0].uuid}"]),
                "data": "",
                "format": "json"
            },
            "get"
        )
        self.assertEqual(no_auth.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(auth.status_code, status.HTTP_403_FORBIDDEN)

        no_auth, auth = self._test_auth_not_auth(
            self.users[1],
            {
                "path": reverse("core:tenants-detail", args=[f"{tenants[1].uuid}"]),
                "data": "",
                "format": "json"
            },
            "get"
        )
        self.assertEqual(no_auth.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(auth.status_code, status.HTTP_200_OK)

        no_auth, auth = self._test_auth_not_auth(
            self.admin_users[0],
            {
                "path": reverse("core:tenants-detail", args=[f"{tenants[1].uuid}"]),
                "data": None,
                "format": "json"
            },
            "get"
        )
        self.assertEqual(no_auth.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(auth.status_code, status.HTTP_200_OK)

    def test_put(self):
        tenants = self._create_tenant(2)
        tenants[0].users.add(self.users[0])
        tenants[0].save()
        tenants[1].users.add(self.users[0], self.users[1])
        tenants[1].save()

        data = {
            "slug": "newslug",
            "name": "newname",
        }
        no_auth, auth = self._test_auth_not_auth(
            self.users[0],
            {
                "path": reverse("core:tenants-detail", args=[f"{tenants[0].uuid}"]),
                "data": data,
                "format": "json"
            },
            "put"
        )

        self.assertEqual(no_auth.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(auth.status_code, status.HTTP_200_OK)
        self.assertEqual(auth.data["slug"], data["slug"])
        self.assertEqual(auth.data["name"], data["name"])

        resp = self._request(
            self.users[1],
            {
                "path": reverse("core:tenants-detail", args=[f"{tenants[0].uuid}"]),
                "data": data,
                "format": "json"
            },
            "put"
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        resp = self._request(
            self.admin_users[0],
            {
                "path": reverse("core:tenants-detail", args=[f"{tenants[0].uuid}"]),
                "data": data,
                "format": "json"
            },
            "put"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_patch(self):
        tenants = self._create_tenant(2)
        tenants[0].users.add(self.users[0])
        tenants[0].save()
        tenants[1].users.add(self.users[0], self.users[1])
        tenants[1].save()

        data = {
            "slug": "newslug",
        }
        no_auth, auth = self._test_auth_not_auth(
            self.users[0],
            {
                "path": reverse("core:tenants-detail", args=[f"{tenants[0].uuid}"]),
                "data": data,
                "format": "json"
            },
            "patch"
        )

        self.assertEqual(no_auth.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(auth.status_code, status.HTTP_200_OK)
        self.assertEqual(auth.data["slug"], data["slug"])

        resp = self._request(
            self.users[1],
            {
                "path": reverse("core:tenants-detail", args=[f"{tenants[0].uuid}"]),
                "data": data,
                "format": "json"
            },
            "patch"
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        resp = self._request(
            self.admin_users[0],
            {
                "path": reverse("core:tenants-detail", args=[f"{tenants[0].uuid}"]),
                "data": data,
                "format": "json"
            },
            "patch"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_delete(self):
        tenants = self._create_tenant(1)
        tenants[0].users.add(self.users[0])
        tenants[0].save()

        no_auth, auth = self._test_auth_not_auth(
            self.users[0],
            {
                "path": reverse("core:tenants-detail", args=[f"{tenants[0].uuid}"]),
                "data": None,
                "format": "json"
            },
            "delete"
        )

        self.assertEqual(no_auth.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(auth.status_code, status.HTTP_204_NO_CONTENT)

        tenants = self._create_tenant(1)
        resp = self._request(
            self.admin_users[0],
            {
                "path": reverse("core:tenants-detail", args=[f"{tenants[0].uuid}"]),
                "data": None,
                "format": "json"
            },
            "delete"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_users(self):
        tenants = self._create_tenant(1)
        tenants[0].users.add(self.users[0])
        tenants[0].users.add(self.users[1])
        tenants[0].users.add(self.users[2])
        tenants[0].save()

        no_auth, auth = self._test_auth_not_auth(
            self.users[0],
            {
                "path": reverse("core:tenants-users", args=[f"{tenants[0].uuid}"]),
                "data": None,
                "format": "json"
            },
            "get"
        )
        self.assertEqual(no_auth.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(auth.status_code, status.HTTP_200_OK)
        self.assertEqual(len(auth.data), 3)

        resp = self._request(
            self.admin_users[0],
            {
                "path": reverse("core:tenants-users", args=[f"{tenants[0].uuid}"]),
                "data": None,
                "format": "json"
            },
            "get"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 3)

    def test_add_users(self):
        tenants = self._create_tenant(1)
        tenants[0].users.add(self.users[0])
        tenants[0].save()
        no_auth, auth = self._test_auth_not_auth(
            self.users[0],
            {
                "path": reverse("core:tenants-add-users", args=[f"{tenants[0].uuid}"]),
                "data": {'uuids': [user.uuid for user in self.users]},
                "format": "json"
            },
            "post"
        )
        self.assertEqual(no_auth.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(auth.status_code, status.HTTP_200_OK)
        self.assertEqual(Tenant.objects.get(uuid=tenants[0].uuid).users.count(), len(self.users))

    def test_remove_users(self):
        tenants = self._create_tenant(1)
        tenants[0].users.add(*self.users)
        tenants[0].save()
        no_auth, auth = self._test_auth_not_auth(
            self.users[0],
            {
                "path": reverse("core:tenants-remove-users", args=[f"{tenants[0].uuid}"]),
                "data": {'uuids': [user.uuid for user in self.users]},
                "format": "json"
            },
            "post"
        )
        self.assertEqual(no_auth.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(auth.status_code, status.HTTP_200_OK)
        self.assertEqual(Tenant.objects.get(uuid=tenants[0].uuid).users.count(), 0)


