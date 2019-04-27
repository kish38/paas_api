from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from paas.models import MyUser as User
from paas.models import Resource


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(min_length=7, write_only=True)

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], validated_data['email'], validated_data['password'])
        if validated_data.get('quota'):
            user.quota = validated_data['quota']
            user.save()
        return user

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password', 'quota')


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ('id', 'owner', 'resource_value')


class ListResourceSerializer(serializers.ModelSerializer):
    owner = UserSerializer()

    class Meta:
        model = Resource
        fields = ('id', 'owner', 'resource_value')


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
