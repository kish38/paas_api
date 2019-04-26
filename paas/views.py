from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
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

    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        if request.user.is_staff and 'owner' in data:
            pass
        else:
            data['owner'] = request.user.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
