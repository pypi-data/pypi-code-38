"""Views for the module system
"""
import json

from django.contrib.staticfiles import finders
from django.http.response import HttpResponseBadRequest, HttpResponse

from core_main_app.utils.rendering import render
from core_parser_app.components.module import api as module_api
from core_parser_app.tools.modules.sanitize import sanitize
from core_parser_app.tools.modules.views.module import AbstractModule


def index(request):
    """Modules index

    Args:
        request:

    Returns:

    """
    # get list of modules
    list_modules = module_api.get_all()
    # set context
    context = {'modules': list_modules}
    # render template
    return render(request,
                  'core_parser_app/common/modules.html',
                  context=context)


def load_resources_view(request):
    """ Load resources for a given list of modules

    :param request:
    :return:
    """
    if not request.method == 'GET':
        return HttpResponseBadRequest({})

    if 'urlsToLoad' not in request.GET or 'urlsLoaded' not in request.GET:
        return HttpResponseBadRequest({})

    # URLs of the modules to load
    mod_urls_qs = sanitize(request.GET['urlsToLoad'])
    mod_urls = json.loads(mod_urls_qs)

    # URLs of the loaded modules
    mod_urls_loaded_qs = sanitize(request.GET['urlsLoaded'])
    mod_urls_loaded = json.loads(mod_urls_loaded_qs)

    # Request hack to get module resources
    request.GET = {
        'resources': True
    }

    # List of resources
    resources = {
        'scripts': [],
        'styles': []
    }

    # Add all resources from requested modules
    for url in mod_urls:
        module = module_api.get_by_url(url)
        module_view = AbstractModule.get_view_from_view_path(module.view).as_view()
        mod_resources = module_view(request).content

        mod_resources = sanitize(mod_resources)
        mod_resources = json.loads(mod_resources)

        # Append resource to the list
        for key in resources.keys():
            if mod_resources[key] is None:
                continue

            for resource in mod_resources[key]:
                if resource not in resources[key]:
                    resources[key].append(resource)

    # Remove possible dependencies form already loaded modules
    for url in mod_urls_loaded:
        module_view = AbstractModule.get_module_view(url)
        mod_resources = module_view(request).content

        mod_resources = sanitize(mod_resources)
        mod_resources = json.loads(mod_resources)

        # Remove resources already loaded
        for key in resources.keys():
            if mod_resources[key] is None:
                continue

            for resource in mod_resources[key]:
                if resource in resources[key]:
                    i = resources[key].index(resource)
                    del resources[key][i]

    # Build response content
    response = {
        'scripts': "",
        'styles': ""
    }

    # Aggregate scripts
    for script in resources['scripts']:
        if script.startswith('http://') or script.startswith('https://'):
            script_tag = '<script class="module" src="' + script + '"></script>'
        else:
            with open(finders.find(script), 'r') as script_file:
                script_tag = '<script class="module">' + script_file.read() + '</script>'

        response['scripts'] += script_tag

    # Aggregate styles
    for style in resources['styles']:
        if style.startswith('http://') or style.startswith('https://'):
            script_tag = '<link class="module" rel="stylesheet" type="text/css" href="' + style + '"></link>'
        else:
            with open(finders.find(style), 'r') as script_file:
                script_tag = '<style class="module">' + script_file.read() + '</style>'

        response['styles'] += script_tag

    # Send response
    return HttpResponse(json.dumps(response))

