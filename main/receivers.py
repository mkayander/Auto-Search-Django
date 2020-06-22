from django.db.models.signals import post_save
from django.dispatch import receiver
from transliterate import slugify

from .models import AbstractBaseFilterModel, CarFilter


# @receiver(update_counters)
# def add_count(sender, carmark, **kwargs):
#     CarMark.objects.get(name=carmark).update(popularCount=F('popularCount') + 10)
#     print(sender)


@receiver(post_save)
def specify_slug_post_save(sender, instance, **kwargs):
    if issubclass(sender, AbstractBaseFilterModel) and not instance.initialized:
        instance.on_post_save()
        # print("AbstractBaseFilterModel: on_post_save: called")
