from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class MyUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quota = models.IntegerField(null=True, blank=True)
    quota_left = models.IntegerField(null=True, blank=True)


class Resource(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    resource_value = models.TextField()

    def __str__(self):
        return "{} - {}".format(self.owner.username, self.resource_value[:50])
