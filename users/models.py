from django.db import models
from django.contrib.auth.models import User
from PIL import Image

from django.db.models import signals

from account.models import Account
from users.tasks import send_verification_email
import uuid


class Profile(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    image = models.ImageField(default='profile_pics/default1.png', upload_to='profile_pics')
    is_verified = models.BooleanField(verbose_name='verified', default=False)
    verification_uuid = models.UUIDField(verbose_name='Unique Verification UUID', default=uuid.uuid4)

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

# def user_post_save(sender, instance, signal, *args, **kwargs):
#     if not instance.profile.is_verified:
#         # Send verification email
#         send_verification_email.delay(instance.pk)

# signals.post_save.connect(user_post_save, sender=User)
