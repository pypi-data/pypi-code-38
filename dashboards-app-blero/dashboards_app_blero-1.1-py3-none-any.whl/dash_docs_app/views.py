from django.http import HttpResponse
from django.template import loader

from .models import DashDoc
from dashboards_app.models import Dashboard

import os
from dashboards_app.blero_utils.client_utils.logging_helpers import BleroLogger

cwd=os.path.dirname(os.path.realpath(__file__))+"/"
logger=BleroLogger(path=cwd,source=__name__)

def index(request):

    template = loader.get_template('dash_docs_app/base.html')
    context = {
        'test_context': '56',
    }
    return HttpResponse(template.render(context, request))

def dashboard_doc_view(request,dashboard_id):
    template=loader.get_template('dash_docs_app/doc_detail.html')

    dashboard_parent=Dashboard.objects.get(id=dashboard_id)
    logger.debug(type(dashboard_parent))
    dash_doc=DashDoc.objects.get(dashboard_id=dashboard_parent)
    logger.debug(type(dash_doc))

    if not dash_doc:
        doc_exist=False
        logger.debug('doc not excist')
    else:
        doc_exist=True
        dashboard_title=Dashboard.objects.filter(id=dashboard_id)[0].title

        #get Parent Model title




    context = {
        'doc_exist':doc_exist,
        'dashboard_id': dashboard_id,
        'dashboard_title':dashboard_title,
        'instance':dash_doc,
    }
    return HttpResponse(template.render(context, request))


