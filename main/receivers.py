# @receiver(post_save)
# def specify_slug_post_save(sender, instance, **kwargs):
#     if issubclass(sender, AbstractBaseFilterModel) and not instance.initialized:
#         instance.on_post_save()
