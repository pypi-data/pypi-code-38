"""Global index view."""
import pkg_resources

from django.shortcuts import render


def index(request):
    """Basic view."""
    plugins = \
        [plugin.load() for plugin in
         pkg_resources.iter_entry_points(group='elrados.plugins')]
    return render(request, "index.html", {
        "plugins": plugins
    })
