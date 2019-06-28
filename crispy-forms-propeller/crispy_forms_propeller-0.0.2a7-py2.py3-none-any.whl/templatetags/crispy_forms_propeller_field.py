"""
Re implementation of ``crispy_forms.templatetags.crispy_forms_field`` needed to
have correct Propeller error class on input element.

TODO: Changes stand on ``CRISPY_CLASS_CONVERTERS`` usage so it may be included
      in ``django-crispy-forms``, this needs a Pull request.
"""
from django import template, forms
from django.conf import settings

from crispy_forms.templatetags.crispy_forms_field import (is_checkbox,
                                                          is_file,
                                                          is_multivalue,
                                                          pairwise,
                                                          CrispyFieldNode)

register = template.Library()


@register.filter
def is_textfield(field):
    return isinstance(field.field.widget, forms.TextInput)


@register.filter
def is_textarea(field):
    return isinstance(field.field.widget, forms.TextArea)


@register.filter
def is_email(field):
    return isinstance(field.field.widget, forms.EmailInput)


class CrispyPropellerFieldNode(CrispyFieldNode):
    def __init__(self, field, attrs):
        self.field = field
        self.attrs = attrs
        self.html5_required = 'html5_required'

    def render(self, context):
        # Nodes are not threadsafe so we must store and look up our instance
        # variables in the current rendering context first
        if self not in context.render_context:
            context.render_context[self] = (
                template.Variable(self.field),
                self.attrs,
                template.Variable(self.html5_required)
            )

        field, attrs, html5_required = context.render_context[self]
        field = field.resolve(context)
        try:
            html5_required = html5_required.resolve(context)
        except template.VariableDoesNotExist:
            html5_required = False

        widgets = getattr(field.field.widget, 'widgets', [field.field.widget])

        if isinstance(attrs, dict):
            attrs = [attrs] * len(widgets)

        converters = {
            'textinput': 'form-control',
            'fileinput': 'fileinput fileUpload',
            'passwordinput': 'form-control',
            'inputelement': 'form-control',
            'errorcondition': 'form-control-danger',
        }
        converters.update(getattr(settings, 'CRISPY_CLASS_CONVERTERS', {}))

        for widget, attr in zip(widgets, attrs):
            class_name = widget.__class__.__name__.lower()
            class_name = converters.get(class_name, class_name)
            css_class = widget.attrs.get('class', '')
            if css_class:
                if css_class.find(class_name) == -1:
                    css_class += " %s" % class_name
            else:
                css_class = class_name

            if ( not is_checkbox(field)
                and not is_file(field)
                and not is_multivalue(field)
            ):
                css_class += ' form-control'
                if field.errors:
                    css_class += ' form-control-danger'

            widget.attrs['class'] = css_class

            # HTML5 required attribute
            if html5_required and field.field.required and 'required' not in widget.attrs:
                if field.field.widget.__class__.__name__ is not 'RadioSelect':
                    widget.attrs['required'] = 'required'

            for attribute_name, attribute in attr.items():
                attribute_name = template.Variable(attribute_name).resolve(context)

                if attribute_name in widget.attrs:
                    widget.attrs[attribute_name] += " " + template.Variable(attribute).resolve(context)
                else:
                    widget.attrs[attribute_name] = template.Variable(attribute).resolve(context)

        return field


@register.tag(name="crispy_field")
def crispy_field(parser, token):
    """
    {% crispy_field field attrs %}
    """
    token = token.split_contents()
    field = token.pop(1)
    attrs = {}

    # We need to pop tag name, or pairwise would fail
    token.pop(0)
    for attribute_name, value in pairwise(token):
        attrs[attribute_name] = value

    return CrispyPropellerFieldNode(field, attrs)
