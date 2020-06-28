from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
# from users import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('api/', include('api.urls')),
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True, template_name='users/login.html'),
         name='login_page'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout_page'),
    path('accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
