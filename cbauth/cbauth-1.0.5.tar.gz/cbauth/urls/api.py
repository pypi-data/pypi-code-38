from django.urls import path
from cbauth.views import (
    APIMeView,
    APILoginView,
    APILogoutView,
    APIPasswordResetView,
    APIPasswordResetConfirmView
)
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView,
                                            TokenVerifyView)


urlpatterns = [
    path('me/', APIMeView.as_view(), name='api_me'),
    path('login/', APILoginView.as_view(), name='api_login'),
    path('logout/', APILogoutView.as_view(), name='api_logout'),

    path('token/', TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(),
         name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(),
         name='token_verify'),

    path('password_reset',
         APIPasswordResetView.as_view(),
         name='api_password_reset'),
    path('reset/<uidb64>/<token>/',
         APIPasswordResetConfirmView.as_view(),
         name='api_password_reset_confirm'),
]
