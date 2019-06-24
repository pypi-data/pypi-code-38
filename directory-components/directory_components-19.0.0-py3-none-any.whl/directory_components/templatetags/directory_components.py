from bs4 import BeautifulSoup
import re

from django import template
from django.templatetags import static

from django.utils.text import slugify
try:
    # Django < 2.2
    from django.utils.test import mark_safe
except ImportError:
    # Django >= 2.2
    from django.utils.html import mark_safe


register = template.Library()


class FullStaticNode(static.StaticNode):
    def url(self, context):
        request = context['request']
        return request.build_absolute_uri(super().url(context))


@register.tag
def static_absolute(parser, token):
    return FullStaticNode.handle_token(parser, token)


def build_anchor_id(element, suffix):
    return slugify(get_label(element) + suffix)


def get_label(element):
    return re.sub(r'^.* \- ', '', element.contents[0])


@register.filter
def add_anchors(value, suffix=''):
    soup = BeautifulSoup(value, 'html.parser')
    for element in soup.findAll('h2'):
        element.attrs['id'] = build_anchor_id(element, suffix)
    return mark_safe(str(soup))


@register.filter
def add_export_elements_classes(value):
    soup = BeautifulSoup(value, 'html.parser')
    mapping = [
        ('h1', 'heading-xlarge'),
        ('h2', 'heading-large'),
        ('h3', 'heading-medium'),
        ('h4', 'heading-small'),
        ('h5', 'heading-small'),
        ('h6', 'heading-small'),
        ('ul', 'list list-bullet'),
        ('ol', 'list list-number'),
        ('p', 'body-text'),
        ('a', 'link'),
        ('blockquote', 'quote'),
    ]
    for tag_name, class_name in mapping:
        for element in soup.findAll(tag_name):
            element.attrs['class'] = class_name
    return mark_safe(str(soup))


@register.filter
def convert_headings_to(value, heading):
    soup = BeautifulSoup(value, 'html.parser')
    for element in soup.findAll(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        element.name = heading
    return str(soup)


@register.filter
def override_elements_css_class(value, element_and_override):
    arguments = element_and_override.split(',')
    element_type = arguments[0]
    override = arguments[1]
    soup = BeautifulSoup(value, 'html.parser')
    for element in soup.findAll(element_type):
        element.attrs['class'] = override
    return str(soup)


@register.inclusion_tag('directory_components/form_widgets/form.html')
def render_form(form):
    return {'form': form}


@register.inclusion_tag('directory_components/cta_box.html')
def cta_box(**kwargs):
    return kwargs


@register.inclusion_tag('directory_components/message_box.html')
def message_box(**kwargs):
    return kwargs


@register.inclusion_tag('directory_components/message_box_with_icon.html')
def message_box_with_icon(**kwargs):
    return kwargs


@register.inclusion_tag('directory_components/banner.html')
def banner(**kwargs):
    return kwargs


@register.inclusion_tag('directory_components/hero.html')
def hero(**kwargs):
    return kwargs


@register.inclusion_tag('directory_components/card.html')
def card(**kwargs):
    return kwargs


@register.inclusion_tag('directory_components/card_with_icon.html')
def card_with_icon(**kwargs):
    return kwargs


@register.inclusion_tag('directory_components/labelled_card.html')
def labelled_card(**kwargs):
    return kwargs


@register.inclusion_tag('directory_components/labelled_image_card.html')
def labelled_image_card(**kwargs):
    return kwargs


@register.inclusion_tag('directory_components/image_with_caption.html')
def image_with_caption(**kwargs):
    return kwargs


@register.inclusion_tag('directory_components/cta_card.html')
def cta_card(**kwargs):
    return kwargs


@register.inclusion_tag('directory_components/cta_link.html')
def cta_link(**kwargs):
    return kwargs


@register.inclusion_tag('directory_components/statistics_card_grid.html')
def statistics_card_grid(**kwargs):
    return kwargs


@register.inclusion_tag('directory_components/hero_with_cta.html')
def hero_with_cta(**kwargs):
    return kwargs


@register.inclusion_tag('directory_components/informative_banner.html')
def informative_banner(**kwargs):
    return kwargs


@register.inclusion_tag('directory_components/case_study.html')
def case_study(**kwargs):
    return kwargs


@register.tag
def breadcrumbs(parser, token):
    nodelist = parser.parse(('endbreadcrumbs',))
    parser.delete_first_token()
    try:
        bit = token.split_contents()[1]
    except IndexError:
        raise ValueError('Please specify the label of the current page')
    return Breadcrumbs(nodelist, bit)


class Breadcrumbs(template.Node):
    template = """
        <nav aria-label="Breadcrumb" class="breadcrumbs">
          <ol>
          </ol>
        </nav>
    """

    def __init__(self, nodelist, bit):
        self.nodelist = nodelist
        self.bit = bit

    def render(self, context):
        html = self.nodelist.render(context)
        input_soup = BeautifulSoup(html, 'html.parser')
        output_soup = BeautifulSoup(self.template, 'html.parser')
        links = input_soup.findAll('a')
        if not links:
            raise ValueError('Please specify some links')
        # adding level 1...n
        for link in links:
            if not link.get('href'):
                raise ValueError('Missing href in breadcrumb')
            element = output_soup.new_tag('li')
            element.append(link)
            output_soup.find('ol').append(element)

        # adding the current page
        current = template.Variable(self.bit).resolve(context)
        output_soup.find('ol').append(
            f'<li aria-current="page"><span>{current}</span></li>'
        )
        return output_soup.decode(formatter=None)


@register.tag
def ga360_data(parser, token):
    nodelist = parser.parse(('end_ga360_data',))
    parser.delete_first_token()

    # the ga360_data tag expects arguments in the following format
    # <target> action=<action> type=<type> element=<element> value=<value>
    parameters = token.split_contents()

    target = parameters[1]
    action = None
    ga_type = None
    element = None
    value = None
    include_form_data = None

    for parameter in parameters[2:]:
        action_param_name = 'action='
        type_param_name = 'type='
        element_param_name = 'element='
        value_param_name = 'value='
        include_form_data_param_name = 'include_form_data='

        if parameter.startswith(action_param_name):
            action = parameter[len(action_param_name):]

        elif parameter.startswith(type_param_name):
            ga_type = parameter[len(type_param_name):]

        elif parameter.startswith(element_param_name):
            element = parameter[len(element_param_name):]

        elif parameter.startswith(value_param_name):
            value = parameter[len(value_param_name):]

        elif parameter.startswith(include_form_data_param_name):
            include_form_data = parameter[len(include_form_data_param_name):]

    return GA360Data(nodelist, target, action,
                     ga_type, element, value, include_form_data)


class GA360Data(template.Node):
    def __init__(self, nodelist,
                 target,
                 action=None,
                 ga_type=None,
                 element=None,
                 value=None,
                 include_form_data=None):
        self.nodelist = nodelist
        self.target = template.Variable(target)
        self.action = template.Variable(action) if action is not None else None
        self.ga_type = template.Variable(ga_type) if ga_type is not None else None  # noqa
        self.element = template.Variable(element) if element is not None else None  # noqa
        self.value = template.Variable(value) if value is not None else None
        self.include_form_data = template.Variable(include_form_data) if include_form_data is not None else None  # noqa

    def render(self, context):
        html = self.nodelist.render(context)
        soup = BeautifulSoup(html, 'html.parser')

        selector = self.target.resolve(context)
        for element in soup.findAll(selector):
            if self.action is not None:
                element.attrs['data-ga-action'] = self.action.resolve(context)
            if self.ga_type is not None:
                element.attrs['data-ga-type'] = self.ga_type.resolve(context)
            if self.element is not None:
                element.attrs['data-ga-element'] = self.element.resolve(context)  # noqa
            if self.value is not None:
                element.attrs['data-ga-value'] = self.value.resolve(context)
            if self.include_form_data is not None:
                element.attrs['data-ga-include-form-data'] = self.include_form_data.resolve(context)  # noqa

        # Use formatter=None so that `&` is not converted to `&amp;`
        return soup.decode(formatter=None)
