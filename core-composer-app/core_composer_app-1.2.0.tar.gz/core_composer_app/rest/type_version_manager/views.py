""" REST views for the type version manager API
"""
from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAuthenticated

from core_composer_app.components.type_version_manager import api as type_version_manager_api
from core_composer_app.rest.type_version_manager.abstract_views import AbstractTypeList
from core_main_app.rest.template_version_manager.views import AbstractTemplateVersionManagerList
from core_main_app.utils.decorators import api_staff_member_required


class GlobalTypeVersionManagerList(AbstractTemplateVersionManagerList):
    """ List all global type version managers
    """

    def get_template_version_managers(self):
        """ Get global type version managers

        Returns:

            TypeVersionManager
        """
        return type_version_manager_api.get_global_version_managers()


class UserTypeVersionManagerList(AbstractTemplateVersionManagerList):
    """ List all user type version managers
    """

    permission_classes = (IsAuthenticated, )

    def get_template_version_managers(self):
        """ Get all user type version managers

        Returns:

            TypeVersionManager
        """
        return type_version_manager_api.get_version_managers_by_user(user_id=self.request.user.id)


class UserTypeList(AbstractTypeList):
    """ Create a user type
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """ Create a user type & type version manager

        Parameters:

            {
                "title": "title",
                "filename": "filename",
                "content": "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'><xs:simpleType name='root'/></xs:schema>"
            }

        Note:

            "dependencies_dict": json.dumps({"schemaLocation1": "id1" ,"schemaLocation2":"id2"})

        Args:

            request: HTTP request

        Returns:

            - code: 201
              content: Type
            - code: 400
              content: Validation error / bad request
            - code: 500
              content: Internal server error
        """
        return super(UserTypeList, self).post(request)

    def get_user(self):
        """ Retrieve user from the request
        """
        return str(self.request.user.id)


class GlobalTypeList(AbstractTypeList):
    """ Create a global type
    """

    @method_decorator(api_staff_member_required())
    def post(self, request):
        """ Create a global type & type version manager

        Parameters:

            {
                "title": "title",
                "filename": "filename",
                "content": "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'><xs:simpleType name='root'/></xs:schema>"
            }

        Note:

            "dependencies_dict": json.dumps({"schemaLocation1": "id1" ,"schemaLocation2":"id2"})

        Args:

            request: HTTP request

        Returns:

            - code: 201
              content: Type
            - code: 400
              content: Validation error / bad request
            - code: 500
              content: Internal server error
        """
        return super(GlobalTypeList, self).post(request)

    def get_user(self):
        """ None for global type
        """
        return None
