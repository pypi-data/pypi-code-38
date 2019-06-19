from django.urls import path
from .views import ListDomainView, PartialEditView, PartialDeleteView

urlpatterns = [
    path(r'', ListDomainView.as_view(), name='index'),
    path(r'ajax/edit-popup/<int:domain_pk>',
         view=PartialEditView.as_view(),
         name='ajax-edit-popup'),
    path(r'ajax/delete-popup/<int:domain_pk>',
         view=PartialDeleteView.as_view(),
         name='ajax-delete-popup'),
]
