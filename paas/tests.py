from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from paas.serializers import UserSerializer
from paas.models import MyUser as User
from paas.models import Resource
from paas.serializers import ResourceSerializer


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


class ResourceBasicTest(APITestCase):

    def setUp(self):
        user = User.objects.create_user('user1', 'user1@gmail.com', 'pwd12345', quota=2)
        Resource.objects.create(owner=user, resource_value="Test Resource1")

    def test_resource_created(self):
        user = User.objects.get(email='user1@gmail.com')
        resources = Resource.objects.filter(owner=user)
        self.assertEqual(user.username, 'user1')
        self.assertEqual(user.quota, 2)
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0].owner, user)


class ListResourceEndPointsTestCase(APITestCase):

    def setUp(self):
        for i in range(4):
            User.objects.create_user('test_user%s' % i, 'test%s@gmail.com' % i, password="pwd12345")
        User.objects.create_superuser('admin', 'admin@gmail.com', password="pwd12345")

        user = User.objects.get(username='test_user1')
        Resource.objects.create(owner=user, resource_value="User1 Resource1")
        Resource.objects.create(owner=user, resource_value="User1 Resource2")
        Resource.objects.create(owner=user, resource_value="User1 Resource3")

        user = User.objects.get(username='test_user2')
        Resource.objects.create(owner=user, resource_value="User2 Resource1")
        Resource.objects.create(owner=user, resource_value="User2 Resource2")

    def test_list_resources(self):
        response = self.client.get(reverse('list-resources'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_resources_with_login(self):
        self.client.login(email='test1@gmail.com', password='pwd12345')
        response = self.client.get(reverse('list-resources'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_resources_of_user(self):
        self.client.login(email='test2@gmail.com', password='pwd12345')
        response = self.client.get(reverse('list-resources'))
        expected = Resource.objects.filter(owner__username='test_user2')
        serialized = ResourceSerializer(expected, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serialized.data)

    def test_list_resources_as_admin(self):
        self.client.login(email='admin@gmail.com', password='pwd12345')
        response = self.client.get(reverse('list-resources'))
        expected = Resource.objects.filter(owner__username='test_user2')
        serialized = ResourceSerializer(expected, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serialized.data)

