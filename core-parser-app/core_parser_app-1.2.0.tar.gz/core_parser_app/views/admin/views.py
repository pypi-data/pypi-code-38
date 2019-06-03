"""Core parser app admin views
"""
from django.views.generic import View

from core_main_app.utils.rendering import admin_render
from core_parser_app.views.common.views import get_context


class ManageModulesAdminView(View):
    back_to_previous_url = None

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
                {
                    "path": 'core_parser_app/common/js/module_manager.js',
                    "is_raw": False
                }
            ],
            "css": ['core_main_app/common/css/XMLTree.css',
                    'core_parser_app/common/css/modules.css']
        }

        modals = ["core_parser_app/common/modals/add_module.html"]

        try:
            return admin_render(request,
                                'core_parser_app/common/module_manager.html',
                                modals=modals,
                                assets=assets,
                                context=get_context(pk, self.back_to_previous_url,
                                                    False,
                                                    "Modules Manager"))
        except Exception, e:
            return admin_render(request,
                                'core_main_app/common/commons/error.html',
                                context={'error': e.message})
