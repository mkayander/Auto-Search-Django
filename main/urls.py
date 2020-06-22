from django.urls import path, include
from . import views

from django.views.generic import ListView, DetailView

from rest_framework import routers

urlpatterns = [
    path('', views.index, name="index"),
    path('search/', views.search, name="search"),
    path('other-search/', views.otherSearch, name="otherSearch"),
    path('newfilt/', views.createFilter, name="newfilt"),
    path('result/', views.result, name="result"),
    path('result_other/', views.other_result, name="otherResult"),
    path('filters/', views.filterCarList, name='filter_list'),
    path('archive/', views.archiveAll, name='archiveAll'),
    path('filters/<slug:slug>/', views.saved, name='saved'),
    path('filters/<slug:saved_filter>/edit/', views.search, name='edit_filter'),
    path('filters/<slug:slug>/<slug:archived>', views.saved, name='saved_archive'),

    path('baseform/', views.filter_form, name="baseform")
    #path('archivelist/', views.saved, name='archive_list'),
]
