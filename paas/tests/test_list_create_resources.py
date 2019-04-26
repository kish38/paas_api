from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.views import status
from paas.models import MyUser as User
from paas.models import Resource
from paas.serializers import ResourceSerializer


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
        expected = Resource.objects.all()
        serialized = ResourceSerializer(expected, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serialized.data)


class CreateResourceEndpointTest(APITestCase):

    def setUp(self):
        user = User.objects.create_user('user1', 'user1@gmail.com', 'pwd12345')
        Resource.objects.create(owner=user, resource_value="Test Resource1")
        User.objects.create_superuser('admin', 'admin@gmail.com', 'pwd12345')

    def test_create_resource_without_login(self):
        response = self.client.post(reverse('list-resources'), data={'resource_value': 'Sample Resource'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_resource_with_login(self):
        self.client.login(email='user1@gmail.com', password='pwd12345')
        response = self.client.post(reverse('list-resources'), data={'resource_value': 'Sample Resource'})
        expected = Resource.objects.filter(owner=response.wsgi_request.user)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(expected.count(), 2)

    def test_create_resource_without_value(self):
        self.client.login(email='user1@gmail.com', password='pwd12345')
        response = self.client.post(reverse('list-resources'))
        expected = Resource.objects.filter(owner=response.wsgi_request.user)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(expected.count(), 1)

    def test_create_resource_admin(self):
        self.client.login(email='admin@gmail.com', password='pwd12345')
        user = User.objects.get(email='user1@gmail.com')
        response = self.client.post(reverse('list-resources'), data={'resource_value': 'Sample Resource',
                                                                     'owner': user.id})
        expected = Resource.objects.filter(owner=user)
        not_expected = Resource.objects.filter(owner__username='admin')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(expected.count(), 2)
        self.assertEqual(not_expected.count(), 0)
