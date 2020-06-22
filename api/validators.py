from django.forms import EmailField
from django.core.exceptions import ValidationError


def is_email_address_valid(email):
    try:
        EmailField().clean(email)
        return True
    except ValidationError:
        return False
