from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.permissions import IsAuthenticated
from paas.models import MyUser as User
from paas.serializers import UserSerializer
from paas.models import Resource
from paas.serializers import ResourceSerializer


class ListCreateUsersView(generics.ListCreateAPIView):
    permission_classes = (IsAdminUser,)

    queryset = User.objects.all()
    serializer_class = UserSerializer


class ListCreateResourceView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)

    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            resources = Resource.objects.all()
            owner_id = self.request.query_params.get('owner_id', None)
            if owner_id:
                resources = resources.filter(owner=owner_id)
            return resources
        return Resource.objects.filter(owner=self.request.user)
