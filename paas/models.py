from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class MyUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quota = models.IntegerField(null=True, blank=True)
