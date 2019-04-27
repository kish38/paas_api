from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.views import status
from paas.serializers import UserSerializer
from paas.models import MyUser as User


class UserCreateTest(APITestCase):

    def setUp(self):
        for i in range(5):
            User.objects.create_user('test_user%s' % i, 'test%s@gmail.com' % i, password="pwd12345")
        User.objects.create_superuser('test_user6', 'test6@gmail.com', password="pwd12345")

    def test_unauthorized_user_list_users(self):
        self.client.login(username='test_user6', password='pwd1234')
        response = self.client.get(reverse('list-users'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_users_with_platform_user(self):
        self.client.login(email='test2@gmail.com', password='pwd12345')
        response = self.client.get(reverse('list-users'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_users(self):
        self.client.force_authenticate(user=User.objects.get(username='test_user6'))
        response = self.client.get(reverse('list-users'))
        users = UserSerializer(User.objects.all(), many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, users.data)

    def test_create_user_without_login(self):
        response = self.client.post(reverse('list-users'), data={'username': 'test_user7',
                                                                 'email': 'test7@gmail.com',
                                                                 'password': 'pwd12345'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_user_with_platform_user(self):
        self.client.force_authenticate(user=User.objects.get(username='test_user1'))
        response = self.client.post(reverse('list-users'), data={'username': 'test_user7',
                                                                 'email': 'test7@gmail.com',
                                                                 'password': 'pwd12345'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_user_with_admin_user(self):
        self.client.force_authenticate(user=User.objects.get(username='test_user6'))
        response = self.client.post(reverse('list-users'), data={'username': 'test_user7',
                                                                 'email': 'test7@gmail.com',
                                                                 'password': 'pwd12345'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class UserLoginTest(APITestCase):
    def setUp(self):
        User.objects.create_user('user1', 'user1@gmail.com', 'pwd12345')

    def test_user_login_get(self):
        response = self.client.get(reverse('user-login'))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_user_login_invalid_credentials(self):
        response = self.client.post(reverse('user-login'), data={'email': 'user1@gmail.com', 'password': 'fake'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_login_valid_credentials(self):
        response = self.client.post(reverse('user-login'), data={'email': 'user1@gmail.com', 'password': 'pwd12345'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'user1')
