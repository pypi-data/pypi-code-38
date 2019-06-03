""" Refinement Form.
"""
from django import forms

from core_main_registry_app.components.category import api as category_api
from core_main_registry_app.utils.fancytree.widget import FancyTreeWidget


class RefinementForm(forms.Form):
    prefix = 'refinement'

    def __init__(self, *args, **kwargs):
        refinement = kwargs.pop('refinement', None)
        field_id = kwargs.pop('field_id', None)
        super(RefinementForm, self).__init__(*args, **kwargs)
        if refinement and field_id:
            categories = category_api.get_all_filtered_by_refinement_id(refinement.id)
            self.fields[field_id] = forms.ModelMultipleChoiceField(queryset=categories,
                                                                   required=False,
                                                                   label='',
                                                                   widget=FancyTreeWidget(
                                                                       queryset=categories))
