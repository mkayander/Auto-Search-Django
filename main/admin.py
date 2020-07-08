from django.contrib import admin

from .models import CarResult, CarFilter, OtherFilter, City, CarMark, CarModel, Region


class CityAdmin(admin.ModelAdmin):
    # list_display = ('name', 'region', 'slug', 'isPopular')
    search_fields = ['name', 'slug']
    ordering = ('name', )


class RegionAdmin(admin.ModelAdmin):
    # list_display = ('name', 'slug', 'isPopular')
    search_fields = ['name', 'slug']
    ordering = ('name', )


class CarMarkAdmin(admin.ModelAdmin):
    # list_display = ('name', 'slug', 'isPopular')
    search_fields = ['name']


class CarModelAdmin(admin.ModelAdmin):
    # list_display = ('name', 'pk', 'slug', 'parentMark', 'isPopular')
    search_fields = ['name', 'pk']


class CarElementAdmin(admin.ModelAdmin):
    # list_display = ('e_id', 'filter', 'created_at')
    search_fields = ['e_id', 'pk']


class CarFilterAdmin(admin.ModelAdmin):
    # list_display = ('__str__', 'slug', 'owner', 'refresh_count', 'created_at')
    search_fields = ['slug']
    # readonly_fields = ['created_at', 'refresh_count', 'quantity', 'initialized', 'slug']


class OtherFilterAdmin(admin.ModelAdmin):
    # list_display = ('__str__', 'slug', 'owner', 'created_at')
    search_fields = ['slug']
    # readonly_fields = ['created_at', 'refresh_count', 'quantity', 'initialized']


admin.site.register(CarResult, CarElementAdmin)
admin.site.register(CarFilter, CarFilterAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(CarMark, CarMarkAdmin)
admin.site.register(CarModel, CarModelAdmin)
admin.site.register(OtherFilter, OtherFilterAdmin)
