from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
# from users import views as user_views
from django.views.generic.base import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('api/', include('api.urls')),
    path('test/', TemplateView.as_view(template_name='test.html'), name='test'),
    # path('register/', user_views.register, name='register_page'),
    # path('profile/', user_views.profile, name='profile_page'),
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True, template_name='users/login.html'),
         name='login_page'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout_page'),
    path('accounts/', include('django.contrib.auth.urls')),
    # path('verify/<slug:uuid>/', user_views.verify, name='verify')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
