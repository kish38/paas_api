from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.views import status
from paas.models import MyUser as User
from paas.models import Resource
from paas.serializers import ResourceSerializer


class ResourceSetup(APITestCase):

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


class GetResourceTest(ResourceSetup):
    def test_get_resource_without_login(self):
        resource = Resource.objects.filter(owner__username='test_user1').first()
        response = self.client.get(reverse('get-resource', args=[resource.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_resource_with_login(self):
        self.client.login(username="test_user1", password="pwd12345")
        resource = Resource.objects.filter(owner__username='test_user1').first()
        response = self.client.get(reverse('get-resource', args=[resource.id]))
        expected = ResourceSerializer(resource)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected.data)

    def test_get_resource_of_another_user(self):
        self.client.login(username="test_user1", password="pwd12345")
        resource = Resource.objects.filter(owner__username='test_user2').first()
        response = self.client.get(reverse('get-resource', args=[resource.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_resource_as_admin(self):
        self.client.login(username="admin", password="pwd12345")
        resource = Resource.objects.filter(owner__username='test_user1').first()
        response = self.client.get(reverse('get-resource', args=[resource.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UpdateResourceTest(ResourceSetup):
    def test_update_resource_without_login(self):
        resource = Resource.objects.filter(owner__username='test_user1').first()
        response = self.client.patch(reverse('get-resource', args=[resource.id]), data={'resource_value': 'New Value'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_resource_with_login(self):
        self.client.login(username="test_user1", password="pwd12345")
        resource = Resource.objects.filter(owner__username='test_user1').first()
        response = self.client.patch(reverse('get-resource', args=[resource.id]), data={'resource_value': 'New Value'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['resource_value'], 'New Value')

    def test_update_resource_of_another_user(self):
        self.client.login(username="test_user1", password="pwd12345")
        resource = Resource.objects.filter(owner__username='test_user2').first()
        response = self.client.patch(reverse('get-resource', args=[resource.id]), data={'resource_value': 'New Value'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_resource_as_admin(self):
        self.client.login(username="admin", password="pwd12345")
        resource = Resource.objects.filter(owner__username='test_user1').first()
        response = self.client.patch(reverse('get-resource', args=[resource.id]), data={'resource_value': 'New Value'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DeleteResourceTest(ResourceSetup):
    def test_delete_resource_without_login(self):
        resource = Resource.objects.filter(owner__username='test_user1').first()
        response = self.client.delete(reverse('get-resource', args=[resource.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_resource_with_login(self):
        self.client.login(username="test_user1", password="pwd12345")
        resource = Resource.objects.filter(owner__username='test_user1').first()
        response = self.client.delete(reverse('get-resource', args=[resource.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_resource_of_another_user(self):
        self.client.login(username="test_user1", password="pwd12345")
        resource = Resource.objects.filter(owner__username='test_user2').first()
        response = self.client.delete(reverse('get-resource', args=[resource.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_resource_as_admin(self):
        self.client.login(username="admin", password="pwd12345")
        resource = Resource.objects.filter(owner__username='test_user1').first()
        response = self.client.delete(reverse('get-resource', args=[resource.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
