from django.http import HttpResponse
from django.template import loader


def render(request, template, context=None):
    return HttpResponse(loader.get_template(template).render(context or {}, request))
