"""
tCell Agent

This agent communicates with the tCell service and instruments your
application.
"""


def init():
    """
    Entrypoint for the TCellAgent when it gets called from wsgi.py
    as an SDK.

    Sample wsgi.py for django app:

        import os
        from django.core.wsgi import get_wsgi_application

        import tcell_agent
        tcell_agent.init()

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_waitlist.settings")
        application = get_wsgi_application()
    """
    from tcell_agent.instrumentation.startup import instrument
    instrument()
