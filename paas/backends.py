from django.contrib.auth import backends, get_user_model
from django.db.models import Q
UserModel = get_user_model()


class ModelEmailBackend(backends.ModelBackend):
    def authenticate(self, request, username=None, email=None, password=None, **kwargs):
        try:
            user = UserModel.objects.get(Q(username__iexact=username) |
                                         Q(email__iexact=email) |
                                         Q(email__iexact=username))
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        return super().authenticate(request, username, password, **kwargs)

    def get_user(self, user_id):
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
