from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User, Role

# Create your tests here.
class AuthTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            id="12345",
            username="Test User",
            password="password123",
        )

    def test_register_view(self):
        url = reverse("register")
        data = {
            "id": "67890",
            "username": "New User",
            "password": "newpassword",
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

    def test_login_view_success(self):
        url = reverse("token_obtain_pair")
        data = {"id": "12345", "password": "password123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_view_invalid(self):
        url = reverse("token_obtain_pair")
        data = {"id": "wrongid", "password": "wrongpass"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # self.assertEqual(response.data["error"], "Invalid Credentials")
        self.assertEqual(response.data["detail"], "No active account found with the given credentials")
