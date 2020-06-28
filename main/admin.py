from django.contrib import admin

from .models import CarElement, CarFilter, OtherFilter, CityDB, CarMark, CarModel, RegionDB


class CityDBAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'slug', 'isPopular')
    search_fields = ['name', 'slug']
    ordering = ('name', )


class RegionDBAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'isPopular')
    search_fields = ['name', 'slug']
    ordering = ('name', )


class CarMarkAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'isPopular')
    search_fields = ['name']


class CarModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'pk', 'slug', 'parentMark', 'isPopular')
    search_fields = ['name', 'pk']


class CarElementAdmin(admin.ModelAdmin):
    list_display = ('e_id', 'parentFilter', 'created_at')
    search_fields = ['e_id', 'pk']


class CarFilterAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'slug', 'owner', 'refresh_count', 'created_at')
    search_fields = ['slug']
    readonly_fields = ['created_at', 'refresh_count', 'quantity', 'initialized', 'slug']


class OtherFilterAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'slug', 'owner', 'created_at')
    search_fields = ['slug']
    readonly_fields = ['created_at', 'refresh_count', 'quantity', 'initialized']


admin.site.register(CarElement, CarElementAdmin)
admin.site.register(CarFilter, CarFilterAdmin)
admin.site.register(RegionDB, RegionDBAdmin)
admin.site.register(CityDB, CityDBAdmin)
admin.site.register(CarMark, CarMarkAdmin)
admin.site.register(CarModel, CarModelAdmin)
admin.site.register(OtherFilter, OtherFilterAdmin)
