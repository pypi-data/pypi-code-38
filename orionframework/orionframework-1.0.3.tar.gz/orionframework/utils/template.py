from django.template.context import Context, RequestContext
from django.template.loader import render_to_string
from django.template.base import Template
from orionframework.middleware import get_request


def parse(template, context=None):
    """
    Parse the given template String or template name using the given context dictionary
    and return its result as a String

    @param template: the template name (if ending with *.html) or the template
    String itself

    @param context the dictionary holding additional variables

    @return: parsed template content
    """
    context = context or {}

    if template.endswith(".html") or template.endswith(".text"):

        return render_to_string(template, context=context)

    else:

        request = get_request()
        context = RequestContext(request, context) if request else Context(context)

        template = Template(template)

        return template.render(context)
