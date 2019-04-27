from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save


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


@receiver(post_save, sender=Resource)
def update_user_quota(sender, instance, created, *args, **kwargs):
    if created and instance.owner.quota:
        instance.owner.quota_left -= 1
        instance.owner.save()


@receiver(post_delete, sender=Resource)
def quota_left_add(sender, instance, *args, **kwargs):
    if instance.owner.quota:
        instance.owner.quota_left += 1
        instance.owner.save()