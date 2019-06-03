""" Exporter Serializers
"""
from rest_framework.serializers import ListField
from rest_framework_mongoengine.serializers import DocumentSerializer

import core_exporters_app.components.exporter.api as exporter_api
import core_exporters_app.exporters.xsl.api as xsl_api
from core_exporters_app.commons.constants import XSL_URL
from core_exporters_app.components.exported_compressed_file.models import ExportedCompressedFile
from core_exporters_app.components.exporter.models import Exporter
from core_exporters_app.exporters.xsl.models import ExporterXsl
from core_main_app.commons.serializers import BasicSerializer


class ExporterSerializer(DocumentSerializer):
    """ Exporter serializer
    """
    class Meta:
        """ Meta
        """
        model = Exporter
        fields = "__all__"

    def create(self, validated_data):
        return exporter_api.upsert(Exporter(**validated_data))

    def update(self, instance, validated_data):
        # The only field we can actually update is the name of the instance
        instance.name = validated_data.get('name', instance.name)
        return exporter_api.upsert(instance)


class ExporterXslSerializer(DocumentSerializer):
    """ Xsl Exporter serializer
    """

    class Meta:
        """ Meta
        """
        model = ExporterXsl
        fields = "__all__"
        read_only_fields = ('enable_by_default', 'url')

    def create(self, validated_data):
        exporter = ExporterXsl(**validated_data)
        # set default values for XSL exporters
        exporter.enable_by_default = False
        exporter.url = XSL_URL
        return xsl_api.upsert(exporter)


class ExporterToZipSerializer(BasicSerializer):
    """ Serializer used for entered data validation
    """
    exporter_id_list = ListField(required=True)
    data_id_list = ListField(required=True)


class ExporterExportedCompressedFileSerializer(DocumentSerializer):
    """ Compressed File serializer
    """

    class Meta:
        """ Meta
        """
        model = ExportedCompressedFile
        fields = ("id",)
