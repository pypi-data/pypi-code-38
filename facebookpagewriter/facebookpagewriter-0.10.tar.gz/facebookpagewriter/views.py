import hashlib
import random
import string

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponse
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from facebook import GraphAPI
from facebookpagewriter.models import FacebookConfig

APP_ID = getattr(settings, 'FB_APP_ID')
APP_SECRET = getattr(settings, 'FB_APP_SECRET')


def fblogin(request):
    current_site = get_current_site(request)
    if 'code' not in request.GET:
        state = hashlib.sha224(''.join(random.sample(string.printable, 40))).hexdigest()
        dialog_url = "https://www.facebook.com/dialog/oauth?client_id=%(id)s&redirect_uri=http://%(site)s%(url)s&state=%(state)s&scope=publish_actions,status_update,publish_stream,manage_pages" % {'id': APP_ID, 'state': state, 'url': reverse('fblogin'), 'site': current_site.domain}
        return HttpResponseRedirect(dialog_url)
    else:
        code = request.GET['code']
        result = GraphAPI.get_access_token_from_code(code, 'http://%(site)s%(url)s' % {'site': current_site.domain, 'url': reverse('fblogin')}, APP_ID, APP_SECRET)
        token = result.get('access_token', '')
        config, created = FacebookConfig.objects.get_or_create(app_id=APP_ID, app_secret=APP_SECRET)
        config.access_token = token
        config.save()
        return HttpResponse('token: %(token)s' % {'token': token})
