from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from paas.models import MyUser as User
from paas.serializers import UserSerializer


class ListCreateUsersView(generics.ListCreateAPIView):
    permission_classes = (IsAdminUser,)

    queryset = User.objects.all()
    serializer_class = UserSerializer
