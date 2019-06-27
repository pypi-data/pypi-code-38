from .forms import Form


def filter_form_factory(model):
    fields = []

    for field in model._meta.fields:
        formfield = field.formfield()
        if formfield:
            formfield.required = False
            field_name = field.column if field.rel else field.name
            fields.append((field_name, formfield))

    fields = dict(fields)

    return type(Form)(model.__name__ + str('FilterForm'), (Form,), fields)


class QuerysetFilter(object):
    def __init__(self, queryset, form_class=None):
        self.form_class = form_class or filter_form_factory(queryset.model)
        self.queryset = queryset

    def narrow(self, data):
        form = self.form_class(data)
        if form.is_valid():
            data = form.cleaned_data
            really_cleaned_data = {}
            for key, value in data.items():
                if value is not None and value is not '' and value is not u'':
                    really_cleaned_data[key] = value
            return self.queryset.filter(**really_cleaned_data)
        return self.queryset
