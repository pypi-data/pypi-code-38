from django.urls import include, path
from django.contrib import admin
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', include('trosnoth.djangoapp.urls')),
    path('admin/', admin.site.urls),
    path('login', auth_views.LoginView.as_view(), name='login'),
    path('logout', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]
