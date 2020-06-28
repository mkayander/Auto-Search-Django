from django.contrib.auth.decorators import login_required
from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from api.views import account_properties_view, ObtainAuthTokenByEmail
from . import views

router = routers.DefaultRouter()
router.register('cars', views.CarElementView)
router.register('filters', views.CarFilterView)
router.register('cities', views.CityDBView)
router.register('regions', views.RegionDBView)
router.register('carmarks', views.CarMarkView)
router.register('carmodels', views.CarModelView)

router.register('account_2', views.AccountView)

urlpatterns = [
    path('', include(router.urls)),
    path('myfilter/', views.UserFilters.as_view()),
    path('city/<slug:cityname>/', login_required(views.CityUrls.as_view())),
    path('utils/', views.Utils.as_view()),
    # path('auth/', include('rest_framework.urls')),
    path('auth/checkme/', views.auth_and_check_user, name="api_auth_user"),
    path('car/<slug:item_id>/', views.get_car_element_view, name="api_get_car"),
    path('account/', views.GenAccountView.as_view(), name="generic_account_view"),

    path('register/', views.registration_view, name="api_register"),
    path('auth/obtain_key/', ObtainAuthTokenByEmail.as_view(), name="login"),
    path('profile/', account_properties_view, name="user_properties")
]
