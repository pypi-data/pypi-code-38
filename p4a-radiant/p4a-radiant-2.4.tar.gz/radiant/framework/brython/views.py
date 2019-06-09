"""
Brython Framework: Debug views
==============================

"""


from django.views.generic import View
from django.http import JsonResponse
from radiant.framework.shortcuts import brython_render
from django.conf import settings

import os
from .permissions import Permission


########################################################################
class BrythonView(View):
    """Handle the connection between Brython and Python interpreter.


    """
    # ----------------------------------------------------------------------

    def post(self, request):
        """"""
        self.request = request
        name = request.POST.get('name', None)
        args = eval(request.POST.get('args', '[]'))
        kwargs = eval(request.POST.get('kwargs', '{}'))

        if hasattr(self, name):
            v = getattr(self, name)(*args, **kwargs)

            if v is None:
                return JsonResponse({'__RDNT__': 0, })
            else:
                return JsonResponse({'__RDNT__': v, })
        else:
            return JsonResponse({'__RDNT__': 'no attribute {}'.format(name), })

    # ----------------------------------------------------------------------
    def test(self):
        """"""
        return True


########################################################################
class BrythonFramework(View):
    """"""
    template = 'base.py'
    debug = 2

    # ----------------------------------------------------------------------
    def get(self, request):
        """"""

        show_splash = getattr(settings, 'SHOW_SPLASH', True)
        title_page = settings.ANDROID['APK']['name']
        splash_name = os.path.split(settings.ANDROID['SPLASH']['static_html'])[-1]

        return brython_render(request, self.template, self.debug, locals())





