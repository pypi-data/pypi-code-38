from django.urls import path, include
from .views import *

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('new', NewMessageView.as_view(), name='new-message'),

    path('<slug:slug>/', include([
        path('', MessageView.as_view(), name='message'),
        path('edit/', EditMessageView.as_view(), name='edit-message'),
        path('delete/', DeleteMessageView.as_view(), name='delete-message'),
    ])),
]