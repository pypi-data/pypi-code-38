"""Curate registry app user views
"""
from django.core.urlresolvers import reverse_lazy

import core_curate_app.permissions.rights as rights
import core_main_app.utils.decorators as decorators
from core_curate_app.views.user.views import EnterDataView
from core_explore_keyword_registry_app.settings import REGISTRY_XSD_FILENAME
from core_main_app.components.version_manager import api as version_manager_api
from core_main_app.utils.rendering import render


@decorators.permission_required(content_type=rights.curate_content_type,
                                permission=rights.curate_access, login_url=reverse_lazy("core_main_app_login"))
def index(request):
    """ Curate homepage for the registry.

    Args:
        request:

    Returns:

    """

    assets = {
        "css": ['core_curate_registry_app/user/css/index.css'],
    }

    return render(request,
                  'core_curate_registry_app/user/index.html',
                  assets=assets,
                  context={})


@decorators.permission_required(content_type=rights.curate_content_type,
                                permission=rights.curate_access, login_url=reverse_lazy("core_main_app_login"))
def start_curate(request, role):
    """ Start curate with role parameter.

    Args:
        request:
        role:

    Returns:

    """
    assets = {
        "js": [
            {
                "path": 'core_curate_app/user/js/select_template.js',
                "is_raw": False
            },
            {
                "path": 'core_curate_registry_app/user/js/start_curate.js',
                "is_raw": False
            },

        ],
        "css": ['core_curate_app/user/css/style.css']
    }

    context = {
        'template_id': version_manager_api.get_active_global_version_manager_by_title(REGISTRY_XSD_FILENAME).current,
        'role': role,
    }
    return render(request,
                  'core_curate_app/user/curate.html',
                  assets=assets,
                  context=context)


class EnterDataRegistryView(EnterDataView):

    def __init__(self):
        super(EnterDataRegistryView, self).__init__()
        self.assets['js'].append(
            {
                "path": 'core_curate_registry_app/user/js/role.js',
                "is_raw": False
            }
        )

    def build_context(self, request, curate_data_structure, reload_unsaved_changes):
        # get the role before module initialization
        role = request.GET.get('role', None)
        # build context
        context = super(EnterDataRegistryView, self).build_context(request,
                                                                   curate_data_structure,
                                                                   reload_unsaved_changes)
        # don't give a role to select, if editing a form
        if not curate_data_structure.form_string:
            # update context with role
            context['role'] = role

        # return context
        return context
