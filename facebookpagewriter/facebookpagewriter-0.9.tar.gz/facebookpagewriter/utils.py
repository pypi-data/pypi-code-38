import facebook

from .models import FacebookConfig
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.sites.models import Site

APP_ID = getattr(settings, 'FB_APP_ID')
APP_SECRET = getattr(settings, 'FB_APP_SECRET')

def _mail_admin(message):
    send_mail(u'FPW notification', message , getattr(settings, 'DEFAULT_FROM_EMAIL', None),
    [email[1] for email in getattr(settings, 'ADMINS', ((None, None),))], fail_silently=False)

def _get_token():
    conf, created = FacebookConfig.objects.get_or_create(app_id=APP_ID, app_secret=APP_SECRET)
    return conf.access_token

def _get_auth(init_token=''):
    if not init_token:
        token = _get_token()
    else:
        token = init_token
    if token:
        graph = facebook.GraphAPI(token)
        return graph
    else:
        site_id = getattr(settings, 'SITE_ID',1)
        current_site = Site.objects.get(id=site_id)
        _mail_admin(u'No active token, please login in http://%(site)s%(url)s' % {'site': current_site.domain, 'url': reverse('fblogin')})

def post(page_id, component, message, **kwargs):
    graph = _get_auth()
    if graph:
        page_access_token = graph.get_object(page_id, fields='access_token').get('access_token')
        if page_access_token:
            page_graph = _get_auth(page_access_token)
            result =  page_graph.put_object(page_id, component,message=message,**kwargs)
            if result.has_key('error'):
                _mail_admin(result['error']['message'])
    return None
