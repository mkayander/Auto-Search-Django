import logging

from django.urls import reverse
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from AutoSearch.celery import app


@app.task
def send_verification_email(user_id):
    account = get_user_model()
    try:
        user = account.objects.get(pk=user_id)
        send_mail(
            'Verify your inqer.net account',
            'Follow this link to verify your account: '
            'http://8fde093bb098.sn.mynetname.net%s' % reverse('verify',
                                                               kwargs={'uuid': str(user.profile.verification_uuid)}),
            'maksim.kayander@dellin.ru',
            [user.email],
            fail_silently=False,
        )
    except account.DoesNotExist:
        logging.warning(f"Tried to send verification email to non-existing user {user_id}")
