"""Explore example user views
"""
import json

from django.core.urlresolvers import reverse_lazy
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import View

import core_explore_example_app.components.persistent_query_example.api as persistent_query_example_api
import core_explore_example_app.permissions.rights as rights
import core_main_app.components.template_version_manager.api as template_version_manager_api
import core_main_app.utils.decorators as decorators
from core_explore_common_app.components.query import api as query_api
from core_explore_common_app.utils.query.query import create_default_query
from core_explore_common_app.views.user.views import ResultQueryRedirectView
from core_explore_example_app.components.explore_data_structure import api as explore_data_structure_api
from core_explore_example_app.components.saved_query import api as saved_query_api
from core_explore_example_app.settings import INSTALLED_APPS
from core_explore_example_app.utils.parser import render_form
from core_main_app.commons import exceptions as exceptions
from core_main_app.components.template import api as template_api
from core_main_app.utils.rendering import render


class IndexView(View):
    api = template_version_manager_api
    get_redirect = 'core_explore_example_app/user/index.html'
    select_object_redirect = "core_explore_example_select_fields"
    build_query_redirect = "core_explore_example_build_query"
    object_name = "template"

    @method_decorator(decorators.
                      permission_required(content_type=rights.explore_example_content_type,
                                          permission=rights.explore_example_access,
                                          login_url=reverse_lazy("core_main_app_login")))
    def get(self, request, *args, **kwargs):
        """ Page that allows to select a template to start exploring data

        Args:
            request:

        Returns:

        """
        assets = {
            "css": ['core_explore_example_app/user/css/style.css']
        }

        global_active_template_list = self.get_global_active_list()
        user_active_template_list = self.get_user_active_list(request.user.id)

        context = {
            'global_objects': global_active_template_list,
            'user_objects': user_active_template_list,
            'object_name': self.object_name,
            'select_object_redirect': self.select_object_redirect,
            'build_query_redirect': self.build_query_redirect,
        }

        return render(request, self.get_redirect, assets=assets, context=context)

    def get_global_active_list(self):
        """ Get all global version managers.

        Args:

        Returns:
            List of all global version managers

        """
        return self.api.get_active_global_version_manager()

    def get_user_active_list(self, user_id):
        """ Get all active version managers with given user id.

        Args:
            user_id:

        Returns:
            List of all global version managers with given user.

        """
        return self.api.get_active_version_manager_by_user_id(user_id)


class SelectFieldsView(View):
    build_query_url = 'core_explore_example_build_query'
    load_form_url = 'core_explore_example_load_form'
    generate_element_url = 'core_explore_example_generate_element'
    remove_element_url = 'core_explore_example_remove_element'
    generate_choice_url = 'core_explore_example_generate_choice'

    @method_decorator(decorators.
                      permission_required(content_type=rights.explore_example_content_type,
                                          permission=rights.explore_example_access,
                                          login_url=reverse_lazy("core_main_app_login")))
    def get(self, request, template_id, *args, **kwargs):
        """Loads view to customize exploration tree

        Args:
            request:
            template_id:

        Returns:

        """
        try:
            # Set the assets
            assets = {
                "js": [
                    {
                        "path": 'core_main_app/common/js/XMLTree.js',
                        "is_raw": False
                    },
                    {
                        "path": "core_parser_app/js/autosave.js",
                        "is_raw": False
                    },
                    {
                        "path": "core_parser_app/js/autosave_checkbox.js",
                        "is_raw": False
                    },
                    {
                        "path": "core_parser_app/js/autosave.raw.js",
                        "is_raw": True
                    },
                    {
                        "path": "core_parser_app/js/buttons.js",
                        "is_raw": False
                    },
                    {
                        "path": "core_explore_example_app/user/js/buttons.raw.js",
                        "is_raw": True
                    },
                    {
                        "path": "core_parser_app/js/modules.js",
                        "is_raw": False
                    },
                    {
                        "path": "core_parser_app/js/choice.js",
                        "is_raw": False
                    },
                    {
                        "path": "core_explore_example_app/user/js/choice.raw.js",
                        "is_raw": True
                    },
                    {
                        "path": "core_explore_example_app/user/js/select_fields.js",
                        "is_raw": False
                    },
                    {
                        "path": "core_explore_example_app/user/js/select_fields.raw.js",
                        "is_raw": True
                    },
                ],
                "css": ['core_explore_example_app/user/css/xsd_form.css',
                        'core_explore_example_app/user/css/style.css']
            }

            template = template_api.get(template_id)
            # get data structure
            data_structure = explore_data_structure_api.create_and_get_explore_data_structure(template,
                                                                                              request.user.id)
            root_element = data_structure.data_structure_element_root

            # renders the form
            xsd_form = render_form(request, root_element)

            # Set the context
            context = {
                "template_id": template_id,
                "build_query_url": self.build_query_url,
                "load_form_url": self.load_form_url,
                "generate_element_url": self.generate_element_url,
                "remove_element_url": self.remove_element_url,
                "generate_choice_url": self.generate_choice_url,
                "data_structure_id": str(data_structure.id),
                "xsd_form": xsd_form
            }

            return render(request,
                          'core_explore_example_app/user/select_fields.html',
                          assets=assets,
                          context=context)
        except Exception, e:
            return render(request,
                          'core_explore_example_app/user/errors.html',
                          assets={},
                          context={'errors': e.message})


class BuildQueryView(View):
    build_query_url = 'core_explore_example_build_query'
    get_query_url = 'core_explore_example_get_query'
    save_query_url = 'core_explore_example_save_query'
    results_url = 'core_explore_example_results'
    select_fields_url = 'core_explore_example_select_fields'
    object_name = "template"
    data_sources_selector_template = 'core_explore_common_app/user/selector/data_sources_selector' \
                                     '.html'
    query_builder_interface = 'core_explore_example_app/user/query_builder/initial_form.html'

    @method_decorator(decorators.
                      permission_required(content_type=rights.explore_example_content_type,
                                          permission=rights.explore_example_access,
                                          login_url=reverse_lazy("core_main_app_login")))
    def get(self, request, template_id, query_id=None):
        """Page that allows to build and submit queries

        Args:
            request:
            template_id:
            query_id:

        Returns:

        """
        try:
            template = template_api.get(template_id)
            if template is None:
                return render(request,
                              'core_explore_example_app/user/errors.html',
                              assets={},
                              context={'errors': "The selected {0} does not exist".
                                       format(self.object_name)})

            # Init variables
            saved_query_form = ""

            try:
                explore_data_structure = explore_data_structure_api.get_by_user_id_and_template_id(str(request.user.id),
                                                                                                   template_id)
                # If custom fields form present, set it
                custom_form = explore_data_structure.selected_fields_html_tree
            except exceptions.DoesNotExist:
                custom_form = None

            # If new form
            if query_id is None:
                # empty session variables
                request.session['mapCriteriaExplore'] = dict()
                request.session['savedQueryFormExplore'] = ""
                # create new query object
                query = self._create_new_query(request, template)
            else:
                # if not a new form and a query form is present in session
                if 'savedQueryFormExplore' in request.session:
                    saved_query_form = request.session['savedQueryFormExplore']
                query = query_api.get_by_id(query_id)

            # Get saved queries of a user
            if '_auth_user_id' in request.session:
                user_id = request.session['_auth_user_id']
                user_queries = saved_query_api.get_all_by_user_and_template(user_id=user_id,
                                                                            template_id=template_id)
            else:
                user_queries = []

            assets = {
                "js": self._get_js(),
                "css": self._get_css()
            }

            context = {
                'queries': user_queries,
                'template_id': template_id,
                'description': self.get_description(),
                'title': self.get_title(),

                'custom_form': custom_form,
                'query_form': saved_query_form,
                'query_id': str(query.id),

                "build_query_url": self.build_query_url,
                "results_url": self.results_url,
                "get_query_url": self.get_query_url,
                "save_query_url": self.save_query_url,
                "select_fields_url": self.select_fields_url,

                "data_sources_selector_template": self.data_sources_selector_template,
                "query_builder_interface": self.query_builder_interface
            }

            modals = [
                "core_explore_example_app/user/modals/custom_tree.html",
                "core_explore_example_app/user/modals/sub_elements_query_builder.html",
                "core_main_app/common/modals/error_page_modal.html",
                "core_explore_example_app/user/modals/delete_all_queries.html",
                "core_explore_example_app/user/modals/delete_query.html"
            ]

            return render(request,
                          'core_explore_example_app/user/build_query.html',
                          assets=assets,
                          context=context,
                          modals=modals)
        except Exception, e:
            return render(request,
                          'core_explore_example_app/user/errors.html',
                          assets={},
                          context={'errors': e.message})

    @staticmethod
    def _create_new_query(request, template):
        """ Create a new query
        Args:
            request:
            template:

        """
        # from the template, we get the version manager
        template_version_manager = template_version_manager_api.get_by_version_id(str(template.id))
        # from the version manager, we get all the version
        template_ids = template_api.get_all_by_id_list(template_version_manager.versions)
        # create query
        query = create_default_query(request, template_ids)
        # then upsert
        return query_api.upsert(query)

    @staticmethod
    def _get_js():
        return [
            {
                "path": 'core_explore_example_app/user/js/build_query.js',
                "is_raw": False
            },
            {
                "path": 'core_explore_example_app/user/js/build_query.raw.js',
                "is_raw": True
            },
            {
                "path": 'core_parser_app/js/autosave.raw.js',
                "is_raw": True
            },
            {
                "path": "core_parser_app/js/choice.js",
                "is_raw": False
            },
            {
                "path": 'core_main_app/common/js/modals/error_page_modal.js',
                "is_raw": True
            }]

    @staticmethod
    def _get_css():
        return [
            "core_explore_example_app/user/css/query_builder.css",
            "core_explore_example_app/user/css/xsd_form.css"
        ]

    @staticmethod
    def get_description():
        return "Click on a field of the Query Builder to add an element to your query. "\
               "The elements selected in the previous step will appear and you will be able to insert "\
               "them in the query builder. Click on plus/minus icons to add/remove criteria. "\
               "You can save queries to build more complex queries and you will retrieve them on your next connection."\
               " When your query is done, please click on Submit Query to get XML documents that match the criteria."

    @staticmethod
    def get_title():
        return "Query Builder"


class ResultQueryView(View):
    back_to_query_redirect = 'core_explore_example_build_query'

    @method_decorator(decorators.
                      permission_required(content_type=rights.explore_example_content_type,
                                          permission=rights.explore_example_access,
                                          login_url=reverse_lazy("core_main_app_login")))
    def get(self, request, template_id, query_id):
        """Query results view

        Args:
            request:
            template_id:
            query_id:

        Returns:

        """
        context = {
            'template_id': template_id,
            'query_id': query_id,
            'exporter_app': False,
            'back_to_query_redirect': self.back_to_query_redirect,
            'get_shareable_link_url': reverse("core_explore_example_get_persistent_query_url")
        }

        assets = {
            "js": [
                {
                    "path": 'core_explore_common_app/user/js/results.js',
                    "is_raw": False
                },
                {
                    "path": 'core_explore_common_app/user/js/results.raw.js',
                    "is_raw": True
                },
                {
                    "path": 'core_main_app/common/js/XMLTree.js',
                    "is_raw": False
                },
                {
                    "path": 'core_main_app/common/js/modals/error_page_modal.js',
                    "is_raw": True
                },
                {
                    "path": 'core_explore_common_app/user/js/button_persistent_query.js',
                    "is_raw": False
                },
            ],
            "css": ["core_explore_common_app/user/css/query_result.css",
                    "core_main_app/common/css/XMLTree.css",
                    "core_explore_common_app/user/css/results.css"],
        }

        modals = [
            "core_main_app/common/modals/error_page_modal.html",
            "core_explore_common_app/user/persistent_query/modals/persistent_query_modal.html"
        ]

        if 'core_exporters_app' in INSTALLED_APPS:
            # add all assets needed
            assets['js'].extend([{
                    "path": 'core_exporters_app/user/js/exporters/list/modals/list_exporters_selector.js',
                    "is_raw": False
                }])
            # add the modal
            modals.extend([
                "core_exporters_app/user/exporters/list/modals/list_exporters_selector.html"
            ])
            # the modal need all selected template
            query = query_api.get_by_id(query_id)

            context['exporter_app'] = True
            context['templates_list'] = json.dumps([str(template.id) for template in query.templates])

        if "core_file_preview_app" in INSTALLED_APPS:
            assets["js"].extend([
                {
                    "path": 'core_file_preview_app/user/js/file_preview.js',
                    "is_raw": False
                }
            ])
            assets["css"].append("core_file_preview_app/user/css/file_preview.css")
            modals.append("core_file_preview_app/user/file_preview_modal.html")

        return render(request,
                      'core_explore_example_app/user/results.html',
                      assets=assets,
                      modals=modals,
                      context=context)


class ResultQueryExampleRedirectView(ResultQueryRedirectView):

    @staticmethod
    def _get_persistent_query(persistent_query_id):
        return persistent_query_example_api.get_by_id(persistent_query_id)

    @staticmethod
    def _get_reversed_url(query):
        return reverse("core_explore_example_results", kwargs={'template_id': query.templates[0].id,
                                                               'query_id': query.id})

    @staticmethod
    def _get_reversed_url_if_failed():
        return reverse("core_explore_example_index")
