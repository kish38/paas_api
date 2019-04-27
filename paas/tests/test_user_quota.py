from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from paas.models import MyUser as User
from paas.models import Resource
from paas.serializers import UserQuotaSerializer


class GetUserEndpointTest(APITestCase):
    def setUp(self):
        User.objects.create_user('user1', 'user1@gmail.com', 'pwd12345')
        u1 = User.objects.create_user('user2', 'user1@gmail.com', 'pwd12345')
        User.objects.create_superuser('admin', 'admin@gmail.com', 'pwd12345')
        Resource.objects.create(owner=u1, resource_value="Test Resource")

    def test_get_user_without_login(self):
        us = User.objects.get(username='user1')
        response = self.client.get(reverse('get-user', args=[us.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_as_platform_user(self):
        self.client.login(username="user1", password="pwd12345")
        us = User.objects.get(username='user1')
        response = self.client.get(reverse('get-user', args=[us.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_user_as_platform_admin(self):
        self.client.login(username="admin", password="pwd12345")
        us = User.objects.get(username='user1')
        response = self.client.get(reverse('get-user', args=[us.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, UserQuotaSerializer(us).data)


class UserQuotaTest(APITestCase):
    def setUp(self):
        User.objects.create_user('user1', 'user1@gmail.com', 'pwd12345')
        u1 = User.objects.create_user('user2', 'user1@gmail.com', 'pwd12345')
        User.objects.create_superuser('admin', 'admin@gmail.com', 'pwd12345')
        Resource.objects.create(owner=u1, resource_value="Test Resource")

    def test_change_user_quota(self):
        self.client.login(username="admin", password="pwd12345")
        us = User.objects.get(username='user1')
        response = self.client.patch(reverse('get-user', args=[us.id]), data={'quota': 2})
        self.assertEqual(us.quota, None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quota'], 2)
        self.assertEqual(response.data['quota_left'], 2)

    def test_change_user_quota_with_resource(self):
        self.client.login(username="admin", password="pwd12345")
        us = User.objects.get(username='user2')
        response = self.client.patch(reverse('get-user', args=[us.id]), data={'quota': 2})
        self.assertEqual(us.quota, None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quota'], 2)
        self.assertEqual(response.data['quota_left'], 1)

    def test_change_user_quota_invalid_count(self):
        self.client.login(username="admin", password="pwd12345")
        us = User.objects.get(username='user2')
        Resource.objects.create(owner=us, resource_value="Test Resource1")
        response = self.client.patch(reverse('get-user', args=[us.id]), data={'quota': 1})
        self.assertEqual(us.quota, None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_user_quota_as_user(self):
        self.client.login(username="user1", password="pwd12345")
        us = User.objects.get(username='user1')
        response = self.client.patch(reverse('get-user', args=[us.id]), data={'quota': 100})
        self.assertEqual(us.quota, None)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
