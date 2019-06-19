from django.urls import path, include
from .views import IndexView, ProfileView, RoadTripView

urlpatterns = [
    path('trip/<slug:roadtrip_slug>/', RoadTripView.as_view(), name='roadtrip'),
    path('profile/<slug:profile_username>/', ProfileView.as_view(), name='profil'),
    path('', IndexView.as_view(), name='index'),
]
