from django.contrib.auth import authenticate
from django.contrib.auth import login
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from rest_framework.exceptions import AuthenticationFailed
from paas.models import MyUser as User
from paas.serializers import UserSerializer
from paas.models import Resource
from paas.serializers import ResourceSerializer
from paas.serializers import ListResourceSerializer
from paas.serializers import UserLoginSerializer
from paas.serializers import UserQuotaSerializer
from paas.permissions import ResourceOwnerReadOnly


class ListCreateUsersView(generics.ListCreateAPIView):
    """
    post:
        Create a User
    get:
        List all Users
    """
    permission_classes = (IsAdminUser,)

    queryset = User.objects.all()
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    """
    get:
        Retrieve a User based with id
    put:
        Update User data
    patch:
        Update User data
    delete:
        Delete a User with id
    """
    permission_classes = (IsAdminUser,)

    queryset = User.objects.all()
    serializer_class = UserQuotaSerializer

    def perform_update(self, serializer):
        user = self.get_object()
        serializer.validated_data.pop('quota_left', None)
        resource_count = Resource.objects.filter(owner=user).count()
        quota = serializer.validated_data['quota']

        if resource_count > quota:
            raise ParseError("More Resources exists than quota")
        user = serializer.save()
        user.quota_left = quota - resource_count
        user.save()


class ListCreateResourceView(generics.ListCreateAPIView):
    """
    post:
        Create a Resource
    get:
        List all Resources
    """
    permission_classes = (IsAuthenticated,)

    serializer_class = ResourceSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            resources = Resource.objects.all()
            owner_id = self.request.query_params.get('owner_id', None)
            if owner_id:
                resources = resources.filter(owner=owner_id)
            return resources
        return Resource.objects.filter(owner=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = ListResourceSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        if request.user.is_staff and 'owner' in data:
            pass
        else:
            data['owner'] = request.user.id

        owner = User.objects.get(pk=data['owner'])
        if owner.quota is not None and owner.quota_left == 0:
            raise ParseError("User Quota Exceeded ")

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ManageResource(generics.RetrieveUpdateDestroyAPIView):
    """
    get:
        Retrieve a Resource based on its id
    put:
        Update a Resource based on its id
    patch:
        Update a Resource based on its id
    delete:
        Delete a Resource based on its id
    """

    permission_classes = (ResourceOwnerReadOnly, )

    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer

    def perform_update(self, serializer):
        owner = serializer.validated_data.pop('owner', None)
        if owner:
            raise ParseError("Change owner not allowed")
        serializer.save()


class LoginView(generics.GenericAPIView):
    """
    post:
        User Login with email and password
    """

    authentication_classes = ()
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(email=serializer.validated_data['email'],
                                password=serializer.validated_data['password'])
            if user:
                login(request, user)
                return Response(UserSerializer(user).data)
            raise AuthenticationFailed("Invalid credentials")
        else:
            raise AuthenticationFailed(serializer.errors)
