"""
WSGI config for snowland_astardownload project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

try:
    from django.core.handlers.wsgi import WSGIHandler
    application = WSGIHandler()
    print("use uwsgi")
except:
    import os
    from django.core.wsgi import get_wsgi_application
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "snowland_astardownload.settings")
    application = get_wsgi_application()
    print("use wsgi")
