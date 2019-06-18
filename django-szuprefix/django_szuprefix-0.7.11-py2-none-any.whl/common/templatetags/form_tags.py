from collections import OrderedDict

from django import template
from django_szuprefix.utils.formutils import boundField2json, form2dict
from django_szuprefix.utils.widgetutils import element_ui_widget

register = template.Library()


@register.tag
def annotate_form_field(parser, token):
    """
    Set an attribute on a form field with the widget type

    This means templates can use the widget type to render things differently
    if they want to.  Django doesn't make this available by default.
    """
    args = token.split_contents()
    if len(args) < 2:
        raise template.TemplateSyntaxError(
            "annotate_form_field tag requires a form field to be passed")
    return FormFieldNode(args[1])


class FormFieldNode(template.Node):
    def __init__(self, field_str):
        self.field = template.Variable(field_str)

    def render(self, context):
        field = self.field.resolve(context)
        if hasattr(field, 'field'):
            field.widget_type = field.field.widget.__class__.__name__
        return ''

register.filter("form2dict", form2dict)

@register.filter("element_ui_widget")
def element_ui_widget(field):
    d = boundField2json(field)
    t = d.get("type")
    widget = element_ui_widget(field.field)
    "<el-%s"
    return dict([(f.name, boundField2json(f)) for f in form])
