"""
Radiant Framework: Views
========================


"""


from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse, HttpResponse
from django.conf import settings
import xml.etree.ElementTree as ET

# from radiant.framework.shortcuts import brython_render

from .theme import THEME, CSS


try:
    from jnius import autoclass, cast
except:
    pass

import os


########################################################################
class OpenURL(View):
    """OpenURL my doc.

    Seccond Line.

    """
    # ----------------------------------------------------------------------

    def get(self, request):
        """Constructor"""

        url = request.GET.get('url', '')

        try:
            context = autoclass('org.kivy.android.PythonActivity').mActivity
            Uri = autoclass('android.net.Uri')
            Intent = autoclass('android.content.Intent')
            intent = Intent()
            intent.setAction(Intent.ACTION_VIEW)
            intent.setData(Uri.parse(url))
            currentActivity = cast('android.app.Activity', context)
            currentActivity.startActivity(intent)

            return JsonResponse({'success': True, })

        except:

            return JsonResponse({'success': False, })


########################################################################
class Logs(View):
    """"""

    template = "radiant/logs.html"

    # ----------------------------------------------------------------------
    def get(self, request):
        """"""
        stdout = os.environ.get('STDOUT', None)
        stderr = os.environ.get('STDERR', None)

        logs = {}

        if stdout and os.path.exists(stdout):
            logs['stdout'] = open(stdout).read()

        if stderr and os.path.exists(stderr):
            logs['stderr'] = open(stderr).read()

        return render(request, self.template, locals())


########################################################################
class Theme(View):
    """"""

    # ----------------------------------------------------------------------
    def get(self, request):
        """"""
        theme_settings = settings.ANDROID.get('THEME', None)

        if theme_settings:

            if 'colors' in theme_settings:
                tree = ET.parse(theme_settings['colors'])
                theme = {child.attrib['name']: child.text for child in tree.getroot()}

                equivalents = {
                    'primaryColor': '--mdc-theme-primary',
                    'primaryLightColor': '--mdc-theme-primary-light',
                    'primaryDarkColor': '--mdc-theme-primary-dark',

                    'secondaryColor': '--mdc-theme-secondary',
                    'secondaryLightColor': '--mdc-theme-secondary-light',
                    'secondaryDarkColor': '--mdc-theme-secondary-dark',

                    'primaryTextColor': '--mdc-theme-text-primary-on-primary',
                    'secondaryTextColor': '--mdc-theme-text-primary-on-secondary',

                    'primaryTextColor': '--mdc-theme-on-primary',
                    'secondaryTextColor': '--mdc-theme-on-secondary',
                }

                if 'primaryColor' in theme:
                    THEME[equivalents['primaryColor']] = theme['primaryColor']
                    THEME[equivalents['primaryLightColor']] = theme['primaryLightColor']
                    THEME[equivalents['primaryDarkColor']] = theme['primaryDarkColor']

                    THEME[equivalents['secondaryColor']] = theme.get('secondaryColor', theme['primaryColor'])
                    THEME[equivalents['secondaryLightColor']] = theme.get('secondaryLightColor', theme['primaryLightColor'])
                    THEME[equivalents['secondaryDarkColor']] = theme.get('secondaryDarkColor', theme['primaryDarkColor'])

                if 'primaryTextColor' in theme:
                    THEME['--mdc-theme-text-primary-on-primary'] = theme['primaryTextColor']
                    THEME['--mdc-theme-text-primary-on-primary-dark'] = theme['primaryTextColor']
                    THEME['--mdc-theme-on-primary'] = theme['primaryTextColor']

                if 'secondaryTextColor' in theme:
                    THEME['--mdc-theme-text-primary-on-secondary'] = theme['secondaryTextColor']
                    THEME['--mdc-theme-text-primary-on-secondary-dark'] = theme['secondaryTextColor']
                    THEME['--mdc-theme-on-secondary'] = theme['secondaryTextColor']

            else:
                THEME.update(theme_settings)

        content = ":root{\n"
        for key in THEME:
            color = THEME[key]
            content += "{}: {} !important;\n".format(key, color)

        content += "\n"

        save_for_var = ["--mdc-theme-primary", "--mdc-theme-secondary", "--mdc-theme-primary-light", "--mdc-theme-secondary-light", "--mdc-theme-primary-dark", "--mdc-theme-secondary-dark"]
        for c in save_for_var:
            color = THEME[c]
            name = c.replace('--mdc', '--var')
            color = color.lstrip('#')
            color = color.replace('!important', '').strip()
            color = [int(color[i:i + 2], 16) for i in range(0, len(color), 2)]
            content += '{}: {}, {}, {} !important;\n'.format(name, *color)

        content += "\n}"
        content += CSS

        self.save_theme(content)

        response = HttpResponse(content=content)
        response['Content-Type'] = 'text/css'
        response['Content-Disposition'] = 'attachment; filename="mdc-theme.css"'

        return response

    # ----------------------------------------------------------------------

    def save_theme(self, theme):
        """"""
        file = open(os.path.join(settings.STATICFILES_DIRS[0], 'theme.css'), 'w')
        file.write(theme)
        file.close()



