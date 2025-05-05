from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    owner_image = models.ImageField(upload_to='owner_photos/', null=True, blank=True)

    def __str__(self):
        return self.user.username
