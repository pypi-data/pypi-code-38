from crispy_forms.helper import FormHelper

def form_horizontal_helper(request):
    helper = FormHelper()
    helper.form_tag = False
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-4'
    helper.field_class = 'col-lg-8'
    helper.include_media = False
    return {
        'form_horizontal_helper': helper
    }

def table_inline_formset(request):
    helper = FormHelper()
    helper.form_tag = False
    helper.template = 'lazycrud/table_inline_formset.html'
    return {
        'table_inline_formset': helper
    }
