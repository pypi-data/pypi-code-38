"""
Type Version Manager model
"""
from core_main_app.components.template_version_manager.models import TemplateVersionManager
from core_main_app.components.version_manager.models import VersionManager


class TypeVersionManager(TemplateVersionManager):
    """Manage versions of types.
    """

    # TODO: see if better way to find _cls
    class_name = 'VersionManager.TemplateVersionManager.TypeVersionManager'

    @staticmethod
    def get_global_version_managers(_cls=True):
        """Return all Type Version Managers with user set to None.

        Returns:

        """
        return TypeVersionManager.objects(user=None).all()

    @staticmethod
    def get_active_global_version_manager(_cls=True):
        """Return all active Type Version Managers with user set to None.

        Returns:

        """
        return TypeVersionManager.objects(is_disabled=False, user=None).all()

    @staticmethod
    def get_version_managers_by_user(user_id):
        """Return Type Version Managers with user set to user_id.

        Args:
            user_id:

        Returns:

        """
        return TypeVersionManager.objects(user=str(user_id)).all()

    @staticmethod
    def get_active_version_manager_by_user_id(user_id):
        """Return active Type Version Managers with user set to user_id.

        Args:
            user_id:

        Returns:

        """
        return TypeVersionManager.objects(is_disabled=False, user=str(user_id)).all()

    @staticmethod
    def get_all_type_version_manager_except_user_id(user_id):
        """ Return all Version Managers of all users except user with given user id.

        Args:
            user_id:

        Returns:

        """
        return VersionManager.objects(_cls=TypeVersionManager.class_name, user__nin=str(user_id)).all()

    @staticmethod
    def get_all_type_version_manager():
        """ Return all Version Managers of all users.

        Args:

        Returns:

        """
        return VersionManager.objects(_cls=TypeVersionManager.class_name).all()
