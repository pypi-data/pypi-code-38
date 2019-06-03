""" Url router for the fancy tree module
"""
from django.conf.urls import url

from core_module_fancy_tree_registry_app.views.views import FancyTreeModule

urlpatterns = [
    url(r'module-fancy-tree-registry',
        FancyTreeModule.as_view(),
        name='core_module_fancy_tree_registry'),
]
