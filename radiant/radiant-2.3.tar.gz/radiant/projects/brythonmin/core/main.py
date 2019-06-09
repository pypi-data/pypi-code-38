import socket
import os

if os.getenv('TEMPLATE_DEBUG', False) == 'True':
    from radiant.framework.brython.views import BrythonView
else:
    from radiant.framework.brython.static_views import BrythonView


# import json
# import os
# import webbrowser

# This file is interpreted by a real Python in interpreter not Python


try:
    from jnius import autoclass, cast
except:
    pass


########################################################################
class Brython(BrythonView):
    """"""

    #----------------------------------------------------------------------
    def local_ip(self):
        """"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('google.com', 0))
            return s.getsockname()[0]
        except:
            return None


    #----------------------------------------------------------------------
    def my_python_function(self):
        """"""
        return 'Hello there!!!'


    #----------------------------------------------------------------------
    def open_url(self, url):
        """"""
        try:
            context = autoclass('org.kivy.android.PythonActivity').mActivity
            Uri = autoclass('android.net.Uri')
            Intent = autoclass('android.content.Intent')
            intent = Intent()
            intent.setAction(Intent.ACTION_VIEW)
            intent.setData(Uri.parse(url))
            currentActivity = cast('android.app.Activity', context)
            currentActivity.startActivity(intent)

            return JsonResponse({'success': True,})

        except:

            return JsonResponse({'success': False,})


    #----------------------------------------------------------------------
    def save_rest(self, filename, content):
        """"""
        if os.getenv('TEMPLATE_DEBUG', False) == 'False':
            return

        if not os.path.exists('docs'):
            os.mkdir('docs')

        file = open(os.path.join('docs', filename), 'w')
        file.write('\n'.join(content))
        file.close()
