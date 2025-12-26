from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User, Role


class AuthTests(APITestCase):
    def setUp(self):
        """Set up test data before each test"""
        self.test_role = Role.objects.create(name='User')
        
        self.user = User.objects.create_user(
            id="12345",
            username="Test User",
            email="testuser@example.com",
            password="12345-1234567890",
            role=self.test_role,
            phone_number="1234567890"
        )

    def test_register_view(self):
        print("\n[Test feature] Register user with all required fields → expect 200 & user created")
        url = reverse("register")
        data = {
            "id": "67890",
            "username": "New User",
            "phone_number": "1234567890", 
            "email": "",  
            "password": "ignored",  
        }
        response = self.client.post(url, data, format="json")
        
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "register berhasil")
        
        self.assertTrue(User.objects.filter(id="67890").exists())
        
        user = User.objects.get(id="67890")
        self.assertTrue(user.check_password("67890-1234567890"))


    def test_register_view_duplicate_id(self):
        print("\n[Test feature] Register user with duplicate ID → expect 400")
        url = reverse("register")
        data = {
            "id": "12345", 
            "username": "Duplicate User",
            "phone_number": "5555555555",
            "password": "ignored",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_view_missing_required_fields(self):
        print("\n[Test feature] Register user missing required fields → expect 400")
        url = reverse("register")
        
        data = {
            "id": "67892",
            "username": "Test User",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        data = {
            "id": "67893",
            "phone_number": "1234567890",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        data = {
            "username": "Test User",
            "phone_number": "1234567890",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_view_success(self):
        print("\n[Test feature] Login with correct credentials → expect 200 & JWT tokens")
        url = reverse("token_obtain_pair")
        data = {"id": "12345", "password": "12345-1234567890"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_view_invalid_credentials(self):
        print("\n[Test feature] Login with invalid credentials → expect 401")
        url = reverse("token_obtain_pair")
        data = {"id": "wrongid", "password": "wrongpass"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"], 
            "No active account found with the given credentials"
        )

    def test_login_view_wrong_password(self):
        print("\n[Test feature] Login with correct ID but wrong password → expect 401")
        url = reverse("token_obtain_pair")
        data = {"id": "12345", "password": "wrongpassword"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_view_missing_fields(self):
        print("\n[Test feature] Login missing required fields → expect 400")
        url = reverse("token_obtain_pair")
        data = {"id": "12345"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_view_empty_credentials(self):
        print("\n[Test feature] Login with empty credentials → expect 400")
        url = reverse("token_obtain_pair")
        data = {"id": "", "password": ""}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)