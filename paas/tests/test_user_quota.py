from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from paas.models import MyUser as User
from paas.models import Resource
from paas.serializers import UserQuotaSerializer


class UserSetup(APITestCase):
    def setUp(self):
        User.objects.create_user('user1', 'user1@gmail.com', 'pwd12345')
        u1 = User.objects.create_user('user2', 'user2@gmail.com', 'pwd12345')
        User.objects.create_superuser('admin', 'admin@gmail.com', 'pwd12345')
        User.objects.create_user('user3', 'user3@gmail.com', 'pwd12345')
        Resource.objects.create(owner=u1, resource_value="Test Resource")


class GetUserEndpointTest(UserSetup):

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


class UserQuotaTest(UserSetup):

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


class UserQuotaUpdateWithResource(UserSetup):

    def test_quota_set(self):
        us = User.objects.get(email='user3@gmail.com')
        self.client.login(username='admin', password='pwd12345')
        response = self.client.patch(reverse('get-user', args=[us.id]), data={'quota': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quota'], 2)
        self.assertEqual(response.data['quota_left'], 2)

    def test_quota_update_on_resource_create(self):
        us = User.objects.get(email='user3@gmail.com')
        self.client.login(username='admin', password='pwd12345')
        response = self.client.patch(reverse('get-user', args=[us.id]), data={'quota': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(reverse('list-resources'), data={'owner': us.id, 'resource_value': 'Test Resource'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['owner'], us.id)
        self.client.post(reverse('list-resources'), data={'owner': us.id, 'resource_value': 'Test Resource'})
        us = User.objects.get(email='user3@gmail.com')
        self.assertEqual(us.quota, 2)
        self.assertEqual(us.quota_left, 0)

    def test_quota_update_on_resource_delete(self):
        us = User.objects.get(email='user3@gmail.com')
        self.client.login(username='admin', password='pwd12345')
        response = self.client.patch(reverse('get-user', args=[us.id]), data={'quota': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(reverse('list-resources'), data={'owner': us.id, 'resource_value': 'Test Resource'})
        resource_id = response.data['id']
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['owner'], us.id)

        us = User.objects.get(email='user3@gmail.com')
        self.assertEqual(us.quota_left, 0)

        response = self.client.delete(reverse('get-resource', args=[resource_id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        us = User.objects.get(email='user3@gmail.com')
        self.assertEqual(us.quota, 1)
        self.assertEqual(us.quota_left, 1)
