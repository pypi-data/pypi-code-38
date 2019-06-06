from server.contrib.flatpages import views
from server.urls import path

urlpatterns = [
    path('<path:url>', views.flatpage, name='server.contrib.flatpages.views.flatpage'),
]
