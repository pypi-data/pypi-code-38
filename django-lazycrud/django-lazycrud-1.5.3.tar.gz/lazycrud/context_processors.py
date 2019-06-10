from crispy_forms.helper import FormHelper

from .forms import get_form_horizontal_helper, get_table_inline_formset_helper

def form_horizontal_helper(request):
    return {
        'form_horizontal_helper': get_form_horizontal_helper()
    }

def table_inline_formset(request):
    return {
        'table_inline_formset': get_table_inline_formset_helper()
    }
