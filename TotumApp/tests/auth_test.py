import datetime

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from TotumApp.models import TotumUser, ApiToken, Tenant


class AuthTests(APITestCase):
    def setUp(self):
        user = TotumUser.objects.create_user("testuser", "email@test.com", "1234567890abc!", first_name="Test",
                                             last_name="User")
        tenant = Tenant.objects.create(slug="tt", name="Test Tenant")

        ApiToken.objects.create(user=user, tenant=tenant,
                                expiry_date=datetime.datetime.now() + datetime.timedelta(days=200), key="ABCDEFG")

    def test_password_auth(self):
        """
        Ensure we can log in with username/email and password.
        """
        data = {'email': 'email@test.com', 'password': "1234567890abc!"}
        response = self.client.post(reverse('core:auth_login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        current_user_data = self.client.get(reverse('core:auth_me'), format='json')
        self.assertEqual(current_user_data.status_code, status.HTTP_200_OK)
        self.assertEqual(current_user_data.data['email'], "email@test.com")

        response = self.client.post(reverse('core:auth_login'), format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_token_auth(self):
        """
        Ensure we can log in with username and password.
        """
        current_user_data = self.client.get(reverse('core:auth_me'), format='json', headers={'X-API-Key': 'ABCDEFG'})
        self.assertEqual(current_user_data.status_code, status.HTTP_200_OK)
        self.assertEqual(current_user_data.data['email'], "email@test.com")

    def test_logout(self):
        """
        Ensure we can logout
        """
        data = {'email': 'email@test.com', 'password': "1234567890abc!"}

        login_response = self.client.post(reverse('core:auth_login'), data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get(reverse('core:auth_me')).status_code, status.HTTP_200_OK)

        logout_response = self.client.get(reverse('core:auth_logout'), format='json')
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get(reverse('core:auth_me')).status_code, status.HTTP_403_FORBIDDEN)
