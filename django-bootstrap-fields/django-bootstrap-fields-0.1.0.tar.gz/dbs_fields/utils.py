from django.template import Context
from django.template.loader import get_template


class DbsField(object):

    def __init__(self, templates, field):
        self.field = field
        self.templates = templates
        self.widget = field.field.widget.__class__.__name__
        # Return Values
        self.field_type = ''
        self.field_class = ''
        # Set Meta Data
        self.set_meta()

    def set_meta(self):
        if self.templates == 'bootstrap4':
            self.set_bootstrap4_meta(custom=False)
        elif self.templates == 'bootstrap4custom':
            self.set_bootstrap4_meta(custom=True)
        elif self.templates == 'bootstrap3':
            self.set_bootstrap3_meta()
        else:
            self.set_general_meta()

    def is_text(self):
        widgets = [
            'TextInput',
            'NumberInput',
            'EmailInput',
            'URLInput',
            'PasswordInput',
            'HiddenInput',
            'DateInput',
            'DateTimeInput',
            'TimeInput',
            'Textarea'
        ]
        return self.widget in widgets

    def is_select(self):
        widgets = [
            'Select',
            'NullBooleanSelect',
            'SelectMultiple',
        ]
        return self.widget in widgets

    def is_checkbox(self):
        widgets = [
            'CheckboxInput'
        ]
        return self.widget in widgets

    def is_multi_checkbox(self):
        widgets = [
            'CheckboxSelectMultiple',
        ]
        return self.widget in widgets

    def is_radio(self):
        widgets = [
            'RadioSelect',
            'CheckboxSelectMultiple',
        ]
        return self.widget in widgets

    def is_file(self):
        widgets = [
            'FileInput',
            'ClearableFileInput'
        ]
        return self.widget in widgets

    def set_bootstrap4_meta(self, custom=False):
        """
        Get the Field Type and Class for Bootstrap 4
        """
        # Select Widgets
        if self.is_select():
            field_type = 'select'
            field_class = 'form-control'
            if custom:
                field_class = 'custom-select'
        # Checkbox Widget
        elif self.is_checkbox():
            field_type = 'checkbox'
            field_class = 'form-check-input'
            if custom:
                field_class = 'custom-control-input'
        # Multi-Checkbox Widget
        elif self.is_multi_checkbox():
            field_type = 'multi_checkbox'
            field_class = 'form-check-input'
            if custom:
                field_class = 'custom-control-input'
        # Radio Widget
        elif self.is_radio():
            field_type = 'radio'
            field_class = 'form-check-input'
            if custom:
                field_class = 'custom-control-input'
        # File Widgets
        elif self.is_file():
            field_type = 'file'
            field_class = 'form-control-file'
            if custom:
                field_class = 'custom-file-input'
        # General
        else:
            field_type = ''
            field_class = 'form-control'

        # Set Values
        self.field_type = field_type
        self.field_class = field_class
        if self.field.errors:
            self.field_class = '{0} {1}'.format(self.field_class, 'is-invalid')

    def set_bootstrap3_meta(self):
        """
        Get the Field Type and Class for Bootstrap 3
        """
        # Checkbox Widget
        if self.is_checkbox():
            field_type = 'checkbox'
            field_class = ''
        # Multi-Checkbox Widget
        elif self.is_multi_checkbox():
            field_type = 'multi_checkbox'
            field_class = ''
        # Radio Widget
        elif self.is_radio():
            field_type = 'radio'
            field_class = ''
        # File Widgets
        elif self.is_file():
            field_type = 'file'
            field_class = ''
        # General
        else:
            field_type = ''
            field_class = 'form-control'

        # Set Values
        self.field_type = field_type
        self.field_class = field_class

    def set_general_meta(self):
        # Select Widgets
        if self.is_select():
            field_type = 'select'
        # Checkbox Widget
        elif self.is_checkbox():
            field_type = 'checkbox'
        # Multi-Checkbox Widget
        elif self.is_multi_checkbox():
            field_type = 'multi_checkbox'
        # Radio Widget
        elif self.is_radio():
            field_type = 'radio'
        # File Widgets
        elif self.is_file_input():
            field_type = 'file'
        # General
        else:
            field_type = ''

        # Set Values
        self.field_type = field_type
        self.field_class = ''


def render_dbs_field(templates, field, inline, sr_label, prepend, append):
    dbs_field = DbsField(templates, field)

    # Add Field Class
    dbs_classes = field.field.widget.attrs.get('class', '')
    dbs_classes = '{0} {1}'.format(dbs_field.field_class, dbs_classes)
    field.field.widget.attrs['class'] = dbs_classes.strip()

    # Field Attributes
    attrs = {
        'field': field,
        'field_type': dbs_field.field_type,
        'widget': field,
        'inline': inline,
        'sr_label': sr_label,
        'prepend': prepend,
        'append': append
    }

    # Field Template
    if templates == 'bootstrap4custom':
        template_name = 'bootstrap4/custom_field.html'
    else:
        template_name = '{0}/field.html'.format(templates)

    # Render
    context = Context(attrs).flatten()
    template = get_template(template_name)
    return template.render(context)
