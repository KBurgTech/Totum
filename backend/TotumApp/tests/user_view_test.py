from django.urls import reverse
from rest_framework import status

from TotumApp.models import TotumUser
from TotumApp.tests.helpers import BaseTestCase, USER_PASSWORD


class UserViewModelTest(BaseTestCase):
    def setUp(self):
        self.admin_users = self._create_admin_user(1)
        self.users = self._create_user(5)

    def test_create(self):
        data = {
            "first_name": "Firstname",
            "last_name": "Lastname",
            "email": "user@example.com",
            "password": USER_PASSWORD
        }
        create_user_resp = self.client.post(reverse("core:users-list"), data, format='json')
        self.assertEqual(create_user_resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_user_resp.data['first_name'], data['first_name'])
        self.assertEqual(create_user_resp.data['last_name'], data['last_name'])
        self.assertEqual(create_user_resp.data['email'], data['email'])
        self.assertNotIn("password", create_user_resp.data)
        self.assertIn("uuid", create_user_resp.data)

        user = TotumUser.objects.get(uuid=create_user_resp.data['uuid'])
        self.assertIsNotNone(user)
        self.assertNotEquals(user.password, data['password'])

    def test_list(self):
        # Test Non-Admin cannot list
        list_not_auth_resp = self.client.get(reverse("core:users-list"), format='json')
        self.assertEqual(list_not_auth_resp.status_code, status.HTTP_403_FORBIDDEN)

        # Test Admin can list
        self.client.login(email=self.admin_users[0].email, password=USER_PASSWORD)
        list_auth_resp = self.client.get(reverse("core:users-list"), format='json')
        self.assertEqual(list_auth_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_auth_resp.data), 6)

    def test_get(self):
        adminuser = TotumUser.objects.filter(is_superuser=True).first()
        user = TotumUser.objects.filter(is_superuser=False).first()

        get_not_auth_resp = self.client.get(reverse("core:users-detail", args=[f"{user.uuid}"]))
        self.assertEqual(get_not_auth_resp.status_code, status.HTTP_403_FORBIDDEN)
        self.client.login(email=user.email, password=USER_PASSWORD)
        get_auth_resp = self.client.get(reverse("core:users-detail", args=[f"{user.uuid}"]))
        self.assertEqual(get_auth_resp.status_code, status.HTTP_200_OK)
        get_auth_resp_not_user = self.client.get(reverse("core:users-detail", args=[f"{adminuser.uuid}"]))
        self.assertEqual(get_auth_resp_not_user.status_code, status.HTTP_403_FORBIDDEN)

        self.client.logout()
        self.client.login(email=adminuser.email, password=USER_PASSWORD)
        get_auth_resp_not_self = self.client.get(reverse("core:users-detail", args=[f"{user.uuid}"]))
        self.assertEqual(get_auth_resp_not_self.status_code, status.HTTP_200_OK)

    def test_put(self):
        data = {
            "first_name": "NewFirst",
            "last_name": "NewLast",
            "email": "newemail@example.com",
            "password": "1234567890abc!NEW"
        }
        user = TotumUser.objects.filter(is_superuser=False).first()

        get_not_auth_resp = self.client.put(reverse("core:users-detail", args=[f"{user.uuid}"]), data, format='json',
                                            content_type="application/json")
        self.assertEqual(get_not_auth_resp.status_code, status.HTTP_403_FORBIDDEN)

        self.client.login(email=user.email, password=USER_PASSWORD)
        get_auth_resp = self.client.put(reverse("core:users-detail", args=[f"{user.uuid}"]), data, format='json',
                                        content_type="application/json")
        self.assertEqual(get_auth_resp.status_code, status.HTTP_200_OK)

        updated_user = TotumUser.objects.get(uuid=user.uuid)
        self.assertEqual(updated_user.first_name, data['first_name'])
        self.assertEqual(updated_user.last_name, data['last_name'])
        self.assertEqual(updated_user.email, data['email'])

        self.client.logout()
        self.assertTrue(self.client.login(email=data['email'], password=data['password']))

    def test_patch(self):
        data = {
            "first_name": "NewFirst",
            "last_name": "NewLast",
        }
        user = TotumUser.objects.filter(is_superuser=False).first()

        get_not_auth_resp = self.client.patch(reverse("core:users-detail", args=[f"{user.uuid}"]), data, format='json',
                                              content_type="application/json")
        self.assertEqual(get_not_auth_resp.status_code, status.HTTP_403_FORBIDDEN)

        self.client.login(email=user.email, password=USER_PASSWORD)
        get_auth_resp = self.client.patch(reverse("core:users-detail", args=[f"{user.uuid}"]), data, format='json',
                                          content_type="application/json")
        self.assertEqual(get_auth_resp.status_code, status.HTTP_200_OK)

        updated_user = TotumUser.objects.get(uuid=user.uuid)
        self.assertEqual(updated_user.first_name, data['first_name'])
        self.assertEqual(updated_user.last_name, data['last_name'])

    def test_delete(self):
        user = TotumUser.objects.filter(is_superuser=False).first()
        get_not_auth_resp = self.client.delete(reverse("core:users-detail", args=[f"{user.uuid}"]), format='json')
        self.assertEqual(get_not_auth_resp.status_code, status.HTTP_403_FORBIDDEN)

        self.client.login(email=user.email, password=USER_PASSWORD)
        get_auth_resp = self.client.delete(reverse("core:users-detail", args=[f"{user.uuid}"]), format='json')
        self.assertEqual(get_auth_resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_set_password(self):
        data = {
            "password": "NewPassword"
        }
        user = TotumUser.objects.filter(is_superuser=False).first()

        no_auth, auth = self._test_auth_not_auth(
            user,
            {
                "path": reverse("core:users-set-password", args=[f"{user.uuid}"]),
                "data": data,
                "format": "json"
            },
            "post"
        )
        self.assertEqual(no_auth.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(auth.status_code, status.HTTP_200_OK)
        self.assertTrue(self.client.login(email=user.email, password="NewPassword"))
