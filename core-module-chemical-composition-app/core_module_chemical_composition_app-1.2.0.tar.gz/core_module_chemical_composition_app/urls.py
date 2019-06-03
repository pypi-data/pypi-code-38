""" Url router for the chemical composition module
"""
from django.conf.urls import url
from core_module_chemical_composition_app.views import ChemicalCompositionModule

urlpatterns = [
    url(r'module-chemical-composition',
        ChemicalCompositionModule.as_view(),
        name='core_module_chemical_composition'),
]
