from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User, Role
from api.models import ProgramStudy


class RoleViewsTestCase(TestCase):
    """Test cases for Role CRUD operations"""

    def setUp(self):
        """Set up test data before each test method"""
        self.client = APIClient()

        # Create roles
        self.admin_role = Role.objects.create(name='Admin')
        self.tracer_role = Role.objects.create(name='Tracer')
        self.user_role = Role.objects.create(name='User')

        # Create admin user
        self.admin_user = User.objects.create_user(
            id='admin001',
            username='Admin User',
            password='testpass123',
            role=self.admin_role
        )

        # Create non-admin user
        self.regular_user = User.objects.create_user(
            id='user001',
            username='Regular User',
            password='testpass123',
            role=self.user_role
        )

    def test_role_list_as_admin(self):
        print("\n[Test feature] Get role list as admin → expect 200 & list")
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('role-list-create')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_role_list_as_non_admin(self):
        print("\n[Test feature] Get role list as non-admin → expect 403")
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('role-list-create')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_role_list_unauthenticated(self):
        print("\n[Test feature] Get role list unauthenticated → expect 401")
        url = reverse('role-list-create')
        response = self.client.get(url)

        # DRF returns 401 for unauthenticated, 403 for authenticated but forbidden
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_role_create_as_admin(self):
        print("\n[Test feature] Create role as admin → expect 201")
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('role-list-create')
        data = {'name': 'Supervisor'}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Supervisor')
        self.assertEqual(Role.objects.count(), 4)

    def test_role_create_as_non_admin(self):
        print("\n[Test feature] Create role as non-admin → expect 403")
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('role-list-create')
        data = {'name': 'Supervisor'}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Role.objects.count(), 3)

    def test_role_create_invalid_data(self):
        print("\n[Test feature] Create role with invalid data → expect 400")
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('role-list-create')
        data = {}  # Missing required 'name' field
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_role_detail_as_admin(self):
        print("\n[Test feature] Get role detail as admin → expect 200")
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('role-detail', kwargs={'pk': self.admin_role.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Admin')

    def test_role_detail_not_found(self):
        print("\n[Test feature] Get role detail not found → expect 404")
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('role-detail', kwargs={'pk': 99999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)

    def test_role_update_as_admin(self):
        print("\n[Test feature] Update role as admin → expect 200")
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('role-detail', kwargs={'pk': self.tracer_role.pk})
        data = {'name': 'Senior Tracer'}
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Senior Tracer')
        self.tracer_role.refresh_from_db()
        self.assertEqual(self.tracer_role.name, 'Senior Tracer')

    def test_role_update_as_non_admin(self):
        print("\n[Test feature] Update role as non-admin → expect 403")
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('role-detail', kwargs={'pk': self.tracer_role.pk})
        data = {'name': 'Senior Tracer'}
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_role_delete_as_admin(self):
        print("\n[Test feature] Delete role as admin → expect 204")
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('role-detail', kwargs={'pk': self.user_role.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Role.objects.count(), 2)

    def test_role_delete_as_non_admin(self):
        print("\n[Test feature] Delete role as non-admin → expect 403")
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('role-detail', kwargs={'pk': self.user_role.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Role.objects.count(), 3)


class UserViewsTestCase(TestCase):
    """Test cases for User CRUD operations"""

    def setUp(self):
        """Set up test data before each test method"""
        self.client = APIClient()

        # Create roles
        self.admin_role = Role.objects.create(name='Admin')
        self.tracer_role = Role.objects.create(name='Tracer')
        self.tim_prodi_role = Role.objects.create(name='Tim Prodi')
        self.pimpinan_role = Role.objects.create(name='Pimpinan Unit')
        self.user_role = Role.objects.create(name='User')

        # Create program study
        # Note: Adjust fields based on your actual ProgramStudy model
        self.program_study = ProgramStudy.objects.create(
            name='Computer Science'
            # Remove 'code' if it doesn't exist in your model
        )

        # Create admin user
        self.admin_user = User.objects.create_user(
            id='admin001',
            username='Admin User',
            password='testpass123',
            role=self.admin_role,
            program_study=self.program_study
        )

        # Create tracer user (has read permission)
        self.tracer_user = User.objects.create_user(
            id='tracer001',
            username='Tracer User',
            password='testpass123',
            role=self.tracer_role
        )

        # Create regular user (no permissions)
        self.regular_user = User.objects.create_user(
            id='user001',
            username='Regular User',
            password='testpass123',
            role=self.user_role
        )

    def test_user_list_as_admin(self):
        print("\n[Test feature] Get user list as admin → expect 200 & list")
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('user-list-create')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_user_list_as_tracer(self):
        print("\n[Test feature] Get user list as tracer → expect 200 & list")
        self.client.force_authenticate(user=self.tracer_user)
        url = reverse('user-list-create')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_user_list_as_regular_user(self):
        print("\n[Test feature] Get user list as regular user → expect 403")
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('user-list-create')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_list_unauthenticated(self):
        print("\n[Test feature] Get user list unauthenticated → expect 401")
        url = reverse('user-list-create')
        response = self.client.get(url)

        # DRF returns 401 for unauthenticated, 403 for authenticated but forbidden
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_create_as_admin(self):
        print("\n[Test feature] Create user as admin → expect 201")
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('user-list-create')
        data = {
            'id': 'newuser001',
            'username': 'New User',
            'password': 'newpass123',
            'role': self.user_role.id,
            'program_study': self.program_study.id,
            'address': '123 Test St',
            'phone_number': '1234567890',
            'last_survey': 'none'
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'New User')
        self.assertEqual(User.objects.count(), 4)

    def test_user_create_as_tracer(self):
        print("\n[Test feature] Create user as tracer → expect 403")
        self.client.force_authenticate(user=self.tracer_user)
        url = reverse('user-list-create')
        data = {
            'id': 'newuser001',
            'username': 'New User',
            'password': 'newpass123',
            'role': self.user_role.id
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(User.objects.count(), 3)

    def test_user_create_invalid_data(self):
        print("\n[Test feature] Create user with invalid data → expect 400")
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('user-list-create')
        data = {
            'id': 'newuser001'
            # Missing required fields
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_create_duplicate_id(self):
        print("\n[Test feature] Create user with duplicate ID → expect 400")
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('user-list-create')
        data = {
            'id': 'admin001',  # Already exists
            'username': 'Duplicate User',
            'password': 'newpass123',
            'role': self.user_role.id
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_detail_as_admin(self):
        print("\n[Test feature] Get user detail as admin → expect 200")
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('user-detail', kwargs={'pk': self.tracer_user.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'Tracer User')

    def test_user_detail_as_tracer(self):
        print("\n[Test feature] Get user detail as tracer → expect 200")
        self.client.force_authenticate(user=self.tracer_user)
        url = reverse('user-detail', kwargs={'pk': self.admin_user.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'Admin User')

    def test_user_detail_not_found(self):
        print("\n[Test feature] Get user detail not found → expect 404")
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('user-detail', kwargs={'pk': 'nonexistent'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)

    def test_user_update_as_admin(self):
        print("\n[Test feature] Update user as admin → expect 200")
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('user-detail', kwargs={'pk': self.regular_user.id})
        data = {
            'username': 'Updated User',
            'address': 'New Address',
            'phone_number': '0987654321'
        }
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'Updated User')
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.username, 'Updated User')
        self.assertEqual(self.regular_user.address, 'New Address')

    def test_user_update_as_tracer(self):
        print("\n[Test feature] Update user as tracer → expect 403")
        self.client.force_authenticate(user=self.tracer_user)
        url = reverse('user-detail', kwargs={'pk': self.regular_user.id})
        data = {
            'username': 'Updated User'
        }
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_user_delete_as_admin(self):
        print("\n[Test feature] Delete user as admin → expect 204")
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('user-detail', kwargs={'pk': self.regular_user.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 2)

    def test_user_delete_as_tracer(self):
        print("\n[Test feature] Delete user as tracer → expect 403")
        self.client.force_authenticate(user=self.tracer_user)
        url = reverse('user-detail', kwargs={'pk': self.regular_user.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(User.objects.count(), 3)

    def test_user_delete_as_regular_user(self):
        print("\n[Test feature] Delete user as regular user → expect 403")
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('user-detail', kwargs={'pk': self.tracer_user.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(User.objects.count(), 3)


class PermissionEdgeCasesTestCase(TestCase):
    """Test edge cases for permissions"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.admin_role = Role.objects.create(name='Admin')
        self.tim_prodi_role = Role.objects.create(name='Tim Prodi')
        
        self.admin_user = User.objects.create_user(
            id='admin001',
            username='Admin User',
            password='testpass123',
            role=self.admin_role
        )
        
        self.tim_prodi_user = User.objects.create_user(
            id='timprodi001',
            username='Tim Prodi User',
            password='testpass123',
            role=self.tim_prodi_role
        )

    def test_tim_prodi_can_read_users(self):
        print("\n[Test feature] Tim Prodi can read users → expect 200")
        self.client.force_authenticate(user=self.tim_prodi_user)
        url = reverse('user-list-create')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tim_prodi_cannot_create_users(self):
        print("\n[Test feature] Tim Prodi cannot create users → expect 403")
        self.client.force_authenticate(user=self.tim_prodi_user)
        url = reverse('user-list-create')
        data = {
            'id': 'newuser001',
            'username': 'New User',
            'password': 'pass123',
            'role': self.tim_prodi_role.id
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_without_role(self):
        print("\n[Test feature] User without role → expect error or forbidden")
        user_no_role = User.objects.create_user(
            id='norole001',
            username='No Role User',
            password='testpass123',
            role=None
        )
        self.client.force_authenticate(user=user_no_role)
        url = reverse('user-list-create')
        # This should raise an error or be forbidden
        with self.assertRaises(AttributeError):
            response = self.client.get(url)