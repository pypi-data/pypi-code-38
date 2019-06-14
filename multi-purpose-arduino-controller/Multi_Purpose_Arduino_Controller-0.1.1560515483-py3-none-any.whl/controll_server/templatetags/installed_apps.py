from django.apps import apps


APPS = None
CONTEXTAPPS = None


def reset():
    global APPS, CONTEXTAPPS
    APPS = None
    CONTEXTAPPS = None


def get_apps():
    global APPS
    if APPS is None:
        APPS = [app for app in apps.get_app_configs()]
    return APPS


def get_apps_context(request):
    global CONTEXTAPPS
    if CONTEXTAPPS is None:
        CONTEXTAPPS = []
        for app in get_apps():
            if hasattr(app, "to_context"):
                if app.to_context:
                    CONTEXTAPPS.append(
                        {
                            "indexurl": (
                                app.indexurl
                                if hasattr(app, "indexurl")
                                else app.label + ":index"
                            ),
                            "in_nav_bar": (
                                app.in_nav_bar if hasattr(app, "in_nav_bar") else False
                            ),
                            "navbarhtml":(app.in_nav_bar_html if hasattr(app, "in_nav_bar_html") else False),
                            "verbose_name": app.verbose_name,
                        }
                    )
    apps_in_nav = False
    for app in CONTEXTAPPS:
        if app["in_nav_bar"]:
            apps_in_nav = True
            break

    return {"apps": CONTEXTAPPS,
            'apps_in_nav':apps_in_nav
            }
