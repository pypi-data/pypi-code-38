""" Url router for the chemical composition simple module
"""
from django.conf.urls import url
from core_module_chemical_composition_simple_app.views import ChemicalCompositionSimpleModule

urlpatterns = [
    url(r'module-chemical-composition-simple',
        ChemicalCompositionSimpleModule.as_view(),
        name='core_module_chemical_composition_simple'),
]
