from django.contrib.auth.models import User
from django.db import models
import uuid
import os

def user_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.user.username}_{uuid.uuid4().hex}.{ext}"
    return os.path.join('owner_photos/', filename)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    owner_image = models.ImageField(upload_to=user_image_path, null=True, blank=True)

    def __str__(self):
        return self.user.username
