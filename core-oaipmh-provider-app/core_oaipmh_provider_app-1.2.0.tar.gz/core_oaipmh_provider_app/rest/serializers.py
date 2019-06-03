"""
    Serializers used throughout the Rest API
"""
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import CharField, ListField
from rest_framework_mongoengine.serializers import DocumentSerializer

import core_main_app.components.version_manager.api as version_manager_api
from core_main_app.commons import exceptions
from core_main_app.commons.serializers import BasicSerializer
from core_main_app.components.xsl_transformation import api as oai_xslt_api
from core_oaipmh_provider_app.components.oai_provider_metadata_format import api as \
    oai_provider_metadata_format_api
from core_oaipmh_provider_app.components.oai_provider_metadata_format.models import \
    OaiProviderMetadataFormat
from core_oaipmh_provider_app.components.oai_provider_set import api as oai_provider_set_api
from core_oaipmh_provider_app.components.oai_provider_set.models import OaiProviderSet
from core_oaipmh_provider_app.components.oai_settings import api as oai_settings_api
from core_oaipmh_provider_app.components.oai_settings.models import OaiSettings
from core_oaipmh_provider_app.components.oai_xsl_template import api as  oai_xsl_template_api
from core_oaipmh_provider_app.components.oai_xsl_template.models import OaiXslTemplate


class TemplateMetadataFormatSerializer(BasicSerializer):
    metadata_prefix = CharField(required=True)
    template_id = CharField(required=True)

    def create(self, validated_data):
        return oai_provider_metadata_format_api.add_template_metadata_format(**validated_data)


class OaiProviderMetadataFormatSerializer(DocumentSerializer):
    schema_url = CharField(required=True, write_only=True)

    class Meta:
        model = OaiProviderMetadataFormat
        fields = "__all__"
        depth = 1

        read_only_fields = ('id', 'is_default', 'is_template', 'template', 'schema', 'xml_schema',
                            'metadata_namespace')

    def create(self, validated_data):
        return oai_provider_metadata_format_api.add_metadata_format(**validated_data)


class UpdateMetadataFormatSerializer(BasicSerializer):
    def update(self, instance, validated_data):
        instance.metadata_prefix = validated_data.get('metadata_prefix')
        return oai_provider_metadata_format_api.upsert(instance)

    metadata_prefix = CharField(required=True)


class OaiProviderSetSerializer(DocumentSerializer):
    templates_manager = ListField(child=CharField(), required=True)

    class Meta:
        model = OaiProviderSet
        fields = ['id', 'set_spec', 'set_name', 'description', 'templates_manager']
        depth = 1

        read_only_fields = ('id',)

    def create(self, validated_data):
        return oai_provider_set_api.upsert(OaiProviderSet(**validated_data))

    def update(self, instance, validated_data):
        instance.set_spec = validated_data.get('set_spec', instance.set_spec)
        instance.set_name = validated_data.get('set_name', instance.set_name)
        templates_manager = validated_data.get('templates_manager', [])
        if len(templates_manager) > 0:
            templates_manager = [version_manager_api.get(id_) for id_ in templates_manager]
            instance.templates_manager = templates_manager
        instance.description = validated_data.get('description', instance.description)
        return oai_provider_set_api.upsert(instance)


class TemplateToMFMappingXSLTSerializer(DocumentSerializer):
    class Meta:
        model = OaiXslTemplate
        fields = '__all__'

    @staticmethod
    def validate_oai_metadata_format(oai_metadata_format):
        """ Validate oai_metadata_format field

        Args:
            oai_metadata_format:

        Returns:

        """
        oai_metadata_format_object = oai_provider_metadata_format_api.get_by_id(oai_metadata_format)

        if oai_metadata_format_object.is_template:
            raise ValidationError('Impossible to map a XSLT to a template metadata format')

        return oai_metadata_format

    def create(self, validated_data):
        return oai_xsl_template_api.upsert(OaiXslTemplate(**validated_data))

    def update(self, instance, validated_data):
        instance.xslt = oai_xslt_api.get_by_id(validated_data['xslt'])
        return oai_xsl_template_api.upsert(instance)

    def init_instance(self):
        try:
            oai_xsl_template = oai_xsl_template_api. \
                get_by_template_id_and_metadata_format_id(self.validated_data.get('template', ''),
                                                          self.validated_data.get(
                                                              'oai_metadata_format', ''))
            self.instance = oai_xsl_template
        except exceptions.DoesNotExist:
            pass

    template = CharField(required=True)
    oai_metadata_format = CharField(required=True)
    xslt = CharField(required=True)


class TemplateToMFUnMappingXSLTSerializer(BasicSerializer):
    template_id = CharField(required=True)
    metadata_format_id = CharField(required=True)


class SettingsSerializer(DocumentSerializer):
    class Meta:
        model = OaiSettings
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.repository_name = validated_data.get('repository_name', instance.repository_name)
        instance.repository_identifier = validated_data.get('repository_identifier',
                                                            instance.repository_identifier)
        instance.enable_harvesting = validated_data.get('enable_harvesting',
                                                        instance.enable_harvesting)
        return oai_settings_api.upsert(instance)
