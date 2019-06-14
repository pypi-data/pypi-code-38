from django.conf import settings
from django.templatetags.static import static

import urllib.parse


VUE_DEFAULTS = {
    "vuejs": {
        "development": "https://cdn.jsdelivr.net/npm/vue/dist/vue.js",
        "production": "https://cdn.jsdelivr.net/npm/vue",
    },
    "defer_scripts": False,
    "scripts": {},
    "css": {},
}

VUE_SETTINGS = {}
VUE_SETTINGS.update(VUE_DEFAULTS)
VUE_SETTINGS.update(getattr(settings, "DJANGO_VUE", {}))


def get_vue_setting(name: str):
    """Helper function to get a setting from the VUE_SETTINGS dict.

    Args:
        name: The name of the item to be retrieved

    Returns:
        An item from the DJANGO_VUE settings dict.
    """

    return VUE_SETTINGS.get(name, None)


def resource_is_from_cdn(resource: str) -> bool:
    """Parses the resource and checks if it has a valid scheme.

    If the resource has a scheme the function will return true.

    Args:
        resource:

    Returns:
        True if the parsed url has a valid scheme.
    """

    return urllib.parse.urlparse(resource).scheme != ""


def get_resource_path(resource: str) -> str:
    """Helper function which checks if the given resource has a valid
    scheme. If the resource has a valid scheme it will be returned, if
    not the resource path will be generated using the django static template
    tag.

    Args:
        resource: A javascript or stylesheet resource.

    Returns:
        The resource path.
    """

    if resource_is_from_cdn(resource):
        return resource
    else:
        return static(resource)


def wrap_script_src(src: str):
    """Helper function to wrap a src link within a script tag.

    Args:
        src: A link to a javascript file

    Returns:
        A script tag which should be santitised.
    """

    if VUE_SETTINGS["defer_scripts"]:
        return f'<script src="{src}" defer></script>'
    else:
        return f'<script src="{src}"></script>'


def wrap_link_href(href: str):
    """Helper function to wrap a href link within a link tag.

    Args:
        href: A link to a stylesheet.

    Returns:
        A link tag which should be santitised.
    """

    return f'<link rel="stylesheet" href="{href}"></link>'


def get_custom_script_tag(name: str):
    """Helper function to retrieve an unsanitised script tag containing the specified javascript
    file from the DJANGO_VUE settings.

    Args:
        name: The dict key for the stylesheet to be generated

    Returns:
        An unsantised script tag.
    """

    scripts = get_vue_setting("scripts")
    resource = get_resource_path(scripts[name])
    return wrap_script_src(src=resource)


def get_custom_link_tag(name: str):
    """Helper function to retrieve an unsanitised link tag containing the specified stylesheet
    from the DJANGO_VUE settings.

    Args:
        name: The dict key for the stylesheet to be generated

    Returns:
        An unsantised stylesheet link tag.
    """

    css = get_vue_setting("css")
    resource = get_resource_path(css[name])
    return wrap_link_href(href=resource)


def get_vuejs_script_tag() -> str:
    """Helper function to retrieve vue from the official CDN.

    The django DEBUG setting is used to determine if the development or production
    version of vue should be used.

    Returns:
        An unsanitsed script tag containing the vue js library.
    """

    vuejs = get_vue_setting("vuejs")

    if settings.DEBUG:
        src = vuejs["development"]
    else:
        src = vuejs["production"]

    resource = get_resource_path(src)
    return wrap_script_src(src=resource)


def get_djangovue_script_tag() -> str:
    """Helper function to retrieve the djangovue Vue plugin.

    Returns:
        The djangovue Vue plugin.
    """

    resource = get_resource_path("djangovue/djangovue.js")
    return wrap_script_src(src=resource)
