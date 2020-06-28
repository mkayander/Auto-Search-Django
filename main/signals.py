import django.dispatch
from django.db.models.signals import post_save
from django.dispatch import receiver

from main.models import AbstractBaseFilterModel

update_counters = django.dispatch.Signal(providing_args=["city", "carMark", "carModel"])


