"""
Brython Framework: Static HTML exporter
========================================

"""

from django.shortcuts import render
from django.conf import settings


# import socket
# if socket.gethostname() == 'arch':
from radiant.framework.brython.views import BrythonView as PostHandler
# else:
    # from radiant.framework.brython.wsgi_handler import BrythonPostHandler as\
         # PostHandler

# import json
import os
# import socket

# This file is interpreted by a real Python in interpreter not Python


########################################################################
class BrythonExporter(PostHandler):
    """"""


    #----------------------------------------------------------------------
    def export(self, name, code):
        """"""
        template_name = "radiant/brythonframework/export.html"

        contex = {}
        contex['code'] = code.replace('\\\\n', '\n')


        path = os.path.join(settings.BASE_DIR, 'static_html')
        if not os.path.exists(path):
            os.mkdir(path)

        file = open(os.path.join(path, name), 'wb')


        content = render(self.request, template_name, contex).content


        content = content.decode().replace('/static/', 'static/')

        file.write(content.encode())
        file.close()

        return True



    # #----------------------------------------------------------------------
    # def local_ip(self):
        # """"""
        # try:
            # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # s.connect(('google.com', 0))
            # return s.getsockname()[0]
        # except:
            # return None


    # #----------------------------------------------------------------------
    # def my_python_function(self):
        # """"""
        # return 'Hello there!!!'
