from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = CloudinaryField('image', default='default')
    display_name = models.CharField(max_length=30, unique=True, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        """
        store username as display name if the field 'dislay_name'
        is left blank.
        """
        if not self.display_name:
            self.display_name = self.user.username
        super().save(*args, **kwargs)
