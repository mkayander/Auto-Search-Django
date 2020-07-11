from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('filters/', views.filter_car_list, name='filter_list'),
    path('filters/<slug:slug>/', views.saved, name='saved'),
    path('filters/<slug:slug>/<slug:archived>', views.saved, name='saved_archive'),
]
