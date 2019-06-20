from django.conf import settings

import importlib


def navbar(request):
    """Add the navbar specified in the settings to the context."""

    if settings.BOOTSTRAP_NAVBAR:
        module_path, class_name = settings.BOOTSTRAP_NAVBAR.split(":")
        navbar_module = importlib.import_module(module_path)

        NavBar = getattr(navbar_module, class_name, None)

        if NavBar is not None:
            navbar = NavBar(extra_context={"request": request})
            navbar.set_active_navitem()
        else:
            navbar = None

        return {"navbar": navbar}

    return {}
