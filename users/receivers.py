from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from account.models import Account
from users.tasks import send_verification_email


@receiver(post_save, sender=Account)
def create_profile(sender, instance, created, **kwargs):
    if created:
        # Profile.objects.create(user=instance)
        Token.objects.create(user=instance)
        print(f'New profile created and token assigned by signal! {created=} {sender=} {instance=}', sep='\n')

        # Send verification email
        send_verification_email.delay(instance.pk)
        print('email sent')

# @receiver(post_save, sender=User)
# def save_profile(sender, instance, **kwargs):
#     print(f'Profile edited by signal! {sender=} {instance=}', sep='\n')
#     instance.profile.save()
