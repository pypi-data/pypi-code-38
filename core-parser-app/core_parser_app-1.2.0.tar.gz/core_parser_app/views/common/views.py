"""
    Common views
"""
from django.urls import reverse, NoReverseMatch
from django.views.generic import View

from core_main_app.components.template import api as template_api
from core_main_app.components.version_manager import api as version_manager_api
from core_main_app.utils.rendering import render
from core_parser_app.components.module import api as module_api
from core_parser_app.utils.xml import transform_xsd_to_html_with_modules


class ManageModulesUserView(View):
    back_to_previous_url = None
    read_only = False
    title = "Modules Manager"

    def get(self, request, pk):
        """ View that allows module management

        Args:
            request:
            pk:

        Returns:

        """
        assets = {
            "js": [
                {
                    "path": 'core_main_app/common/js/XMLTree.js',
                    "is_raw": True
                },

            ],
            "css": ['core_main_app/common/css/XMLTree.css',
                    'core_parser_app/common/css/modules.css']
        }

        modals = []
        if not self.read_only:
            modals = ["core_parser_app/common/modals/add_module.html"]
            assets["js"].append({
                                    "path": 'core_parser_app/common/js/module_manager.js',
                                    "is_raw": False
                                })

        try:
            return render(request,
                          'core_parser_app/common/module_manager.html',
                          modals=modals,
                          assets=assets,
                          context=get_context(pk, self.back_to_previous_url, self.read_only, self.title))
        except Exception, e:
            return render(request,
                          'core_main_app/common/commons/error.html',
                          context={'error': e.message})


def get_context(template_id, url_previous_button, read_only, title):
    """ Get the context to manage the template modules

    Args: template_id:
    Returns:
    """

    # get the template
    template = template_api.get(template_id)

    # get template content as HTML
    xsd_tree_html = transform_xsd_to_html_with_modules(template.content)

    # get list of modules
    modules = module_api.get_all()

    # get version manager
    version_manager = version_manager_api.get_from_version(template)

    # reverse url
    try:
        url_back_to = reverse(url_previous_button, kwargs={'version_manager_id': version_manager.id})
    except NoReverseMatch:
        url_back_to = reverse(url_previous_button)

    context = {
        'xsdTree': xsd_tree_html,
        'modules': modules,
        'object': template,
        'version_manager': version_manager,
        'url_back_to': url_back_to,
        'read_only': read_only,
        'title': title
    }
    return context
