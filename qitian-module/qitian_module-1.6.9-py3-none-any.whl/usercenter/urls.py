from django.urls import path
from .views import *

app_name = 'uc'

urlpatterns = [
    path('logout/', LogoutView.as_view(), name='logout'),
    path('login/', LoginView.as_view(), name='login'),
    path('login_check/', LoginCheckView.as_view(), name='login_check'),
    path('join_vip/', MemberView.as_view(), name='join_vip'),
    path('register/', RegisterView.as_view(), name='register'),
    path('', UserHomeView.as_view(), name=''),
    path('home/', UserHomeView.as_view(), name='home'),
    path('my_vip/', MyVipView.as_view(), name='my_vip'),
    path('code/', SendCodeView.as_view(), name='code'),
    path('change_profile/', ChangeProfileView.as_view(), name='change_profile'),
    path('check_password/', CheckPasswordView.as_view(), name='check_password'),
    path('reset_password/', ResetPasswordView.as_view(), name='reset_password'),
    path('do_reset/', DoRestView.as_view(), name='do_reset'),
    path('account/', AccountView.as_view(), name='account'),
    path('wallet_log/', WalletLogView.as_view(), name='wallet_log'),
    path('charge/', ChargeView.as_view(), name='charge'),
    path('go_pay/<int:type>/<int:goods>/', GoPayView.as_view(), name='go_pay'),
    path('notice/<str:key>/', PayNoticeView.as_view(), name='notice'),
]
