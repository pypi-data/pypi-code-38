from __future__ import absolute_import

from django.template import RequestContext, Template
from django.http import HttpResponse


def index(request):
    return HttpResponse("")


def exception(request):
    1 // 0
    return HttpResponse("")


def rum(request):
    template = Template('<html><head>{{ stackifyapm_inject_rum | safe }}</head></html>')
    context = RequestContext(request)
    return HttpResponse(template.render(context))
