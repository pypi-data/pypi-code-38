from django.urls import path

from . import views

app_name = 'oauth'
urlpatterns = [
    path('authorized', views.callback_view, name='callback'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('login-loop-detected', views.login_loop_detected, name='login_loop_detected'),
]
