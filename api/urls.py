from django.urls import path, include
from rest_framework import routers

from api.views import account_properties_view, ObtainAuthTokenByEmail
from . import views

router = routers.DefaultRouter()
router.register('cars', views.CarResultsView)
router.register('filters', views.CarFiltersView)
router.register('cities', views.CitiesView)
router.register('regions', views.RegionsView)
router.register('car_marks', views.CarMarksView)
router.register('car_models', views.CarModelsView)

router.register('account_2', views.AccountView)

urlpatterns = [
    path('', include(router.urls)),
    path('my-filters/', views.UserFilters.as_view()),
    path('auth/checkme/', views.auth_and_check_user, name="api_auth_user"),
    path('car/<slug:item_id>/', views.get_car_element_view, name="api_get_car"),
    path('account/', views.GenAccountView.as_view(), name="generic_account_view"),

    path('register/', views.registration_view, name="api_register"),
    path('auth/obtain_key/', ObtainAuthTokenByEmail.as_view(), name="login"),
    path('profile/', account_properties_view, name="user_properties")
]
