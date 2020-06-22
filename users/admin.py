from django.contrib import admin

from .models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'verification_uuid', 'is_verified')
    search_fields = ['user']


admin.site.register(Profile, ProfileAdmin)
