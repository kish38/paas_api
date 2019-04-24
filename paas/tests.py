from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from paas.serializers import UserSerializer
from paas.models import MyUser as User


class UserCreateTest(APITestCase):
    client = APIClient()

    def setUp(self):
        for i in range(5):
            User.objects.create_user('test_user%s' % i, 'test%s@gmail.com' % i, password="pwd12345")
        User.objects.create_superuser('test_user6', 'test6@gmail.com', password="pwd12345")

    def test_unauthorized_user_list_users(self):
        response = self.client.get(reverse('list-users'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_users_with_platform_user(self):
        self.client.force_authenticate(user=User.objects.get(username='test_user1'))
        response = self.client.get(reverse('list-users'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_users(self):
        self.client.force_authenticate(user=User.objects.get(username='test_user6'))
        response = self.client.get(reverse('list-users'))
        users = UserSerializer(User.objects.all(), many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, users.data)

    def test_create_user_without_login(self):
        pass

    def test_create_user_with_platform_user(self):
        pass

    def test_create_user_with_admin_user(self):
        pass
