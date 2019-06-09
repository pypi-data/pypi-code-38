#Generated with django-for-android

""" Start Django in multithreaded mode

It allows for debugging Django while serving multiple requests at once in
multi-threaded mode.

"""

import sys
import os


#BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append('Lib')


try:
    from jnius import autoclass
    JNIUS = True
except:
    JNIUS = False
    pass

#if not '--nodebug' in sys.argv:
    #log_path = os.path.abspath("{{APP_LOGS}}")

    #if not os.path.exists(log_path):
        #os.mkdir(log_path)
        ##os.makedirs(log_path, exist_ok=True)

    #print("Logs in {}".format(log_path))
    #sys.stdout = open(os.path.join(log_path, "stdout.log"), "w")
    #sys.stderr = open(os.path.join(log_path, "stderr.log"), "w")

    #os.environ['STDOUT'] = os.path.join(log_path, "stdout.log")
    #os.environ['STDERR'] = os.path.join(log_path, "stderr.log")


from wsgiref import simple_server

sys.path.append(os.path.join(os.path.dirname(__file__), "{{NAME}}"))

if JNIUS:

    # Create INTENT_FILTERS in environ
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    activity = PythonActivity.mActivity
    intent = activity.getIntent()
    intent_data = intent.getData()
    try:
        file_uri = intent_data.toString()
        os.environ["INTENT_FILTERS"] = file_uri
    except AttributeError:
        pass

    #permissions

    #import time
    #import functools
    #import jnius

    ##----------------------------------------------------------------------
    #def acquire_permissions(permissions, timeout=30):
        #"""
        #blocking function for acquiring storage permission

        #:param permissions: list of permission strings , e.g. ["android.permission.READ_EXTERNAL_STORAGE",]
        #:param timeout: timeout in seconds
        #:return: True if all permissions are granted
        #"""

        #PythonActivity = jnius.autoclass('org.kivy.android.PythonActivity')
        #Compat = jnius.autoclass('android.support.v4.content.ContextCompat')
        #currentActivity = jnius.cast('android.app.Activity', PythonActivity.mActivity)

        #checkperm = functools.partial(Compat.checkSelfPermission, currentActivity)

        #def allgranted(permissions):
            #"""
            #helper function checks permissions
            #:param permissions: list of permission strings
            #:return: True if all permissions are granted otherwise False
            #"""
            #return reduce(lambda a, b: a and b,
                          #[True if p == 0 else False for p in map(checkperm, permissions)]
                          #)

        #haveperms = allgranted(permissions)
        #if haveperms:
            ## we have the permission and are ready
            #return True

        ## invoke the permissions dialog
        #currentActivity.requestPermissions(permissions, 0)

        ## now poll for the permission (UGLY but we cant use android Activity's onRequestPermissionsResult)
        #t0 = time.time()
        #while time.time() - t0 < timeout and not haveperms:
            ## in the poll loop we could add a short sleep for performance issues?
            #haveperms = allgranted(permissions)

        #return haveperms

    #perms = ["android.permission.READ_EXTERNAL_STORAGE",
             #"android.permission.WRITE_EXTERNAL_STORAGE",
             #"android.permission.CAMERA"]

    #haveperms = acquire_permissions(perms)


#----------------------------------------------------------------------
def django_wsgi_application():
    """"""
    from django.core.wsgi import get_wsgi_application
    print("Creating WSGI application...")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{{NAME}}.settings")
    os.environ.setdefault("FRAMEWORK", "django")
    application = get_wsgi_application()
    return application


#----------------------------------------------------------------------
def brython_wsgi_application():
    """"""
    import static
    print("Creating WSGI application...")
    os.environ.setdefault("FRAMEWORK", "brython")
    from brython_app.{{BRYTHON_MODULE}}.main import {{BRYTHON_CLASS}}
    application = static.Cling(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'brython_app'), index_file='index.html', method_not_allowed={{BRYTHON_CLASS}})
    return application


if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'brython_app')):
    wsgi_application = brython_wsgi_application
else:
    wsgi_application = django_wsgi_application


if {{APP_MULTITHREAD}}:
    import socketserver

    class ThreadedWSGIServer(socketserver.ThreadingMixIn, simple_server.WSGIServer):
        pass
    httpd = simple_server.make_server('{{IP}}', {{PORT}}, wsgi_application(), server_class=ThreadedWSGIServer)
else:
    httpd = simple_server.make_server('{{IP}}', {{PORT}}, wsgi_application())

httpd.serve_forever()
print("Radiant serving on {}:{}".format(*httpd.server_address))



