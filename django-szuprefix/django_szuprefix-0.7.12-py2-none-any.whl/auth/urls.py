from django.conf.urls import include, url
from django_szuprefix.utils.views import csrf_token, LoginRequiredJsView

from . import views

app_name = "auth"
urlpatterns = [
    url(r'^csrf_token/$', csrf_token, name='csrf_token'),
    url(r'^login_required/$', LoginRequiredJsView.as_view()),
    url(r'^login/', views.LoginView.as_view(), name="login"),
    url(r'^logout/', views.LogoutView.as_view(), name="logout"),
    url(r'^change_password/', views.PasswordChangeView.as_view(), name="change_password"),
    url(r'^get_user_info/', views.GetUserInfoView.as_view(), name="get_user_info"),
]
