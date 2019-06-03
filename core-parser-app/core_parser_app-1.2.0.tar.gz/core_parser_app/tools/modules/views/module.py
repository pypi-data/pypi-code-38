"""Abstract Class Module
"""
import importlib
import json
from abc import ABCMeta, abstractmethod

from django.http import HttpResponse
from django.http.response import HttpResponseBadRequest
from django.template.loader import get_template
from django.views.generic import View
from rest_framework.status import HTTP_200_OK

from core_parser_app.components.data_structure_element import api as data_structure_element_api
from core_parser_app.components.module import api as module_api
from core_parser_app.tools.modules.exceptions import ModuleError


class AbstractModule(View):
    """Abstract module class
    """
    __metaclass__ = ABCMeta

    # Is the module managing occurrences by its own? (False by default)
    # NOTE: needs to be redefined in subclasses
    is_managing_occurrences = False

    def __init__(self, scripts=list(), styles=list()):
        """Initializes the module

        :param scripts:
        :param styles:
        """
        # JS scripts
        self.scripts = scripts
        # CSS spreadsheets
        self.styles = styles

        # Skeleton of the modules
        self.template_name = 'core_parser_app/module.html'

        # initialize data
        self.data = None

    def get(self, request, *args, **kwargs):
        """ Manage the GET requests

        Args:
            request:
            *args:
            **kwargs:

        Returns:

        """
        if 'resources' in request.GET:
            return self._get_resources()
        elif 'managing_occurrences' in request.GET:
            return HttpResponse(json.dumps(self.is_managing_occurrences), HTTP_200_OK)
        else:
            return self._get(request)

    def _get(self, request):
        """ Manage the GET requests

        Args:
            request:

        Returns:

        """
        module_id = request.GET['module_id']
        url = request.GET['url'] if 'url' in request.GET else \
            data_structure_element_api.get_by_id(module_id) .options['url']
        template_data = {
            'module_id': module_id,
            'module': '',
            'display': '',
            'url': url
        }

        try:
            # retrieve module's data
            self.data = self._retrieve_data(request)
            # get module's rendering
            template_data['module'] = self._render_module(request)
            # get nodule's data rendering
            template_data['display'] = self._render_data(request)

            # get module element
            module_element = data_structure_element_api.get_by_id(module_id)
            # get its options
            options = module_element.options
            # update module element data
            options['data'] = self.data
            # set updated options
            module_element.options = options
            # save module element
            data_structure_element_api.upsert(module_element)
        except Exception, e:
            raise ModuleError('Something went wrong during module initialization: ' + e.message)

        # Check that values are not None
        for key, val in template_data.items():
            if val is None:
                raise ModuleError('Variable '+key+' cannot be None. Module initialization cannot be completed.')

        # TODO Add additional checks

        # Apply tags to the template
        html_string = AbstractModule.render_template(self.template_name, template_data)
        return HttpResponse(html_string, status=HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """ Manage POST requests

        Args:
            request:
            *args:
            **kwargs:

        Returns:

        """
        template_data = {
            'display': '',
            'url': ''
        }

        try:
            if 'module_id' not in request.POST:
                return HttpResponseBadRequest({'error': 'No "module_id" parameter provided'})

            module_element = data_structure_element_api.get_by_id(request.POST['module_id'])
            # retrieve module's data
            self.data = self._retrieve_data(request)
            template_data['display'] = self._render_data(request)
            options = module_element.options

            # TODO: needs to be updated
            if type(self.data) == dict:
                options['data'] = self.data['data']
                options['attributes'] = self.data['attributes']
            else:
                options['data'] = self.data

            # TODO Implement this system instead
            # options['content'] = self._get_content(request)
            # options['attributes'] = self._get_attributes(request)

            module_element.options = options
            data_structure_element_api.upsert(module_element)
        except Exception, e:
            raise ModuleError('Something went wrong during module update: ' + e.message)

        html_code = AbstractModule.render_template(self.template_name, template_data)

        response_dict = dict()
        response_dict['html'] = html_code

        if hasattr(self, "get_XpathAccessor"):
            response_dict.update(self.get_XpathAccessor())

        return HttpResponse(json.dumps(response_dict))

    def _get_resources(self):
        """Returns HTTP response containing module resources
        """
        response = {
            'scripts': self.scripts,
            'styles': self.styles
        }

        return HttpResponse(json.dumps(response), status=HTTP_200_OK)

    @abstractmethod
    def _render_module(self, request):
        """ Render the module content

        Args:
            request:

        Returns:

        """
        raise NotImplementedError("_render_module method is not implemented.")

    @abstractmethod
    def _retrieve_data(self, request):
        """ Retrieve module's data

        Args:
            request:

        Returns:

        """
        raise NotImplementedError("_retrieve_data method is not implemented.")

    @abstractmethod
    def _render_data(self, request):
        """ Return the module's data representation

        Args:
            request:

        Returns:

        """
        raise NotImplementedError("_render_data method is not implemented.")

    @staticmethod
    def get_module_view(url):
        """Returns module view from an url

        :param url:
        :return:
        """
        module = module_api.get_by_url(url)
        return AbstractModule.get_view_from_view_path(module.view).as_view()

    @staticmethod
    def get_view_from_view_path(view):
        """Returns module view from its view string

        :param view:
        :return:
        """
        # module = module_api.get_by_url(url)
        pkglist = view.split('.')

        pkgs = '.'.join(pkglist[:-1])
        func = pkglist[-1:][0]

        imported_pkgs = importlib.import_module(pkgs)
        return getattr(imported_pkgs, func)

    @staticmethod
    def render_template(template_name, context=None):
        """ Renders the module in HTML using django template

        Args:
            template_name:
            context:

        Returns:

        """
        if context is None:
            context = {}

        template = get_template(template_name)
        return template.render(context)

