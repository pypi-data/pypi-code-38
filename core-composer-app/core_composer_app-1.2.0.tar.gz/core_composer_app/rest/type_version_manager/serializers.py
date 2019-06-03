"""Serializers used throughout the Rest API
"""
from core_composer_app.components.type.models import Type
from core_composer_app.components.type_version_manager import api as type_version_manager_api
from core_composer_app.components.type_version_manager.models import TypeVersionManager
from core_main_app.components.template.api import init_template_with_dependencies
from core_main_app.rest.template.serializers import TemplateSerializer
from core_main_app.rest.template_version_manager.serializers import TemplateVersionManagerSerializer
from core_main_app.rest.template_version_manager.utils import load_dependencies


class TypeVersionManagerSerializer(TemplateVersionManagerSerializer):
    """
        Type Version Manager serializer
    """

    def create(self, validated_data):
        """ Create.

        Args:
            validated_data:

        Returns:

        """
        return TypeVersionManager(**validated_data)


class CreateTypeSerializer(TemplateSerializer):
    """
        Create Type Version Manager serializer
    """
    def create(self, validated_data):
        """
        Create and return a new `Type` instance, given the validated data.
        """
        type_object = Type(filename=validated_data['filename'],
                           content=validated_data['content'])
        type_version_manager_object = validated_data['type_version_manager']

        # load dependencies
        dependencies_dict = load_dependencies(validated_data)

        # Update the content of the template with dependencies
        init_template_with_dependencies(type_object, dependencies_dict)

        # Create the template and its template version manager
        type_version_manager_api.insert(type_version_manager_object, type_object)

        return type_object

    def update(self, instance, validated_data):
        raise NotImplementedError("Type Version Manager should only be updated using specialized APIs.")
