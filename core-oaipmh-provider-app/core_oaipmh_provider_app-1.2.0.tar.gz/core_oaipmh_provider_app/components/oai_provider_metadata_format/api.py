"""
OaiProviderMetadataFormat API
"""
from urlparse import urljoin

from core_main_app.utils.requests_utils.requests_utils import send_get_request
from core_oaipmh_common_app.commons import exceptions as oai_pmh_exceptions
from core_oaipmh_common_app.commons.messages import OaiPmhMessage
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.response import Response

import xml_utils.commons.exceptions as exceptions
from core_main_app.commons.exceptions import DoesNotExist
from core_main_app.commons.exceptions import XSDError
from core_main_app.components.template import api as template_api
from core_main_app.components.version_manager import api as version_manager_api
from core_main_app.utils.xml import is_schema_valid
from core_oaipmh_provider_app import settings
from core_oaipmh_provider_app.components.oai_provider_metadata_format.models import  \
    OaiProviderMetadataFormat
from xml_utils.xsd_tree.xsd_tree import XSDTree


def upsert(oai_provider_metadata_format):
    """ Create or update an OaiProviderMetadataFormat.

    Args:
        oai_provider_metadata_format: OaiProviderMetadataFormat to create or update.

    Returns:
        OaiProviderMetadataFormat instance.


    """
    is_schema_valid(oai_provider_metadata_format.xml_schema)
    return oai_provider_metadata_format.save_object()


def delete(oai_provider_metadata_format):
    """ Delete an OaiProviderMetadataFormat.

    Args:
        oai_provider_metadata_format: OaiProviderMetadataFormat to delete.

    """
    oai_provider_metadata_format.delete()


def get_by_id(oai_provider_metadata_format_id):
    """ Get an OaiProviderMetadataFormat by its id.

    Args:
        oai_provider_metadata_format_id: Id of the OaiProviderMetadataFormat.

    Returns:
        OaiProviderMetadataFormat instance.

    """
    return OaiProviderMetadataFormat.\
        get_by_id(oai_metadata_format_id=oai_provider_metadata_format_id)


def get_by_metadata_prefix(metadata_prefix):
    """ Get an OaiProviderMetadataFormat by its metadata prefix.

    Args:
        metadata_prefix: metadata_prefix of the OaiProviderMetadataFormat.

    Returns:
        OaiProviderMetadataFormat instance.

    """
    return OaiProviderMetadataFormat.get_by_metadata_prefix(metadata_prefix=metadata_prefix)


def get_all():
    """ Get all OaiProviderMetadataFormat.

    Returns:
        List of OaiProviderMetadataFormat.

    """
    return OaiProviderMetadataFormat.get_all()


def get_all_custom_metadata_format(order_by_field=None):
    """ Get all custom OaiProviderMetadataFormat.

    Args:
        order_by_field: Order by field.

    Returns:
        List of metadata format.

    """
    return OaiProviderMetadataFormat.get_all_custom_metadata_format(order_by_field)


def get_all_default_metadata_format(order_by_field=None):
    """ Get all default OaiProviderMetadataFormat.

    Args:
        order_by_field: Order by field.

    Returns:
        List of metadata format.

    """
    return OaiProviderMetadataFormat.get_all_default_metadata_format(order_by_field)


def get_all_template_metadata_format(order_by_field=None):
    """ Get all OaiProviderMetadataFormat based on a template.

    Args:
        order_by_field: Order by field.

    Returns:
        List of metadata format.

    """
    return OaiProviderMetadataFormat.get_all_template_metadata_format(order_by_field)


def get_all_no_template_metadata_format():
    """ Get all OaiProviderMetadataFormat except the metadata formats based on a template.

     Returns:
         List of metadata format.

     """
    return OaiProviderMetadataFormat.get_all_no_template_metadata_format()


def get_all_by_templates(templates):
    """ Get all OaiProviderMetadataFormat used by a list of templates.

    Returns:
        List of metadata format.

    """
    return OaiProviderMetadataFormat.get_all_by_templates(templates)


def add_metadata_format(metadata_prefix, schema_url):
    """ Add a new metadata format.
    Args:
        metadata_prefix: Metadata Prefix.
        schema_url: URL of the schema.

    Returns: Response.

    """
    try:
        http_response = send_get_request(schema_url)
        if http_response.status_code == status.HTTP_200_OK:
            xml_schema = http_response.text
            target_namespace = _get_target_namespace(xml_schema)
            obj = OaiProviderMetadataFormat(metadata_prefix=metadata_prefix, schema=schema_url,
                                            xml_schema=xml_schema, is_default=False,
                                            metadata_namespace=target_namespace, is_template=False)
            upsert(obj)
            content = OaiPmhMessage.get_message_labelled('Metadata format added with success.')

            return Response(content, status=status.HTTP_201_CREATED)
        else:
            raise oai_pmh_exceptions.\
                OAIAPILabelledException(message='Unable to add the new metadata format. Impossible'
                                                ' to retrieve the schema at the given URL',
                                        status_code=status.HTTP_400_BAD_REQUEST)
    except oai_pmh_exceptions.OAIAPILabelledException as e:
        raise e
    except (exceptions.XMLError, XSDError) as e:
        raise oai_pmh_exceptions.\
            OAIAPILabelledException(message='Unable to add the new metadata format. %s' % e.message,
                                    status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        raise oai_pmh_exceptions.\
            OAIAPILabelledException(message='Unable to add the new metadata format.%s' % e.message,
                                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


def add_template_metadata_format(metadata_prefix, template_id):
    """ Add a new template metadata format.
    Args:
        metadata_prefix: Metadata Prefix.
        template_id: Id of the template.

    Returns: Response.

    """
    try:
        template = template_api.get(template_id)
        version_manager = version_manager_api.get_from_version(template)
        xml_schema = template.content
        target_namespace = _get_target_namespace(xml_schema)
        version_number = version_manager_api.get_version_number(version_manager, template_id)
        schema_url = _get_simple_template_metadata_format_schema_url(version_manager.title,
                                                                     version_number)
        obj = OaiProviderMetadataFormat(metadata_prefix=metadata_prefix, schema=schema_url,
                                        xml_schema=xml_schema, is_default=False, is_template=True,
                                        metadata_namespace=target_namespace, template=template)
        upsert(obj)
        content = OaiPmhMessage.get_message_labelled('Metadata format added with success.')

        return Response(content, status=status.HTTP_201_CREATED)
    except oai_pmh_exceptions.OAIAPILabelledException as e:
        raise e
    except DoesNotExist:
        raise oai_pmh_exceptions.\
            OAIAPILabelledException(message='Unable to add the new metadata format. '
                                            'Impossible to retrieve the template with the '
                                            'given template',
                                    status_code=status.HTTP_404_NOT_FOUND)
    except exceptions.XMLError as e:
        raise oai_pmh_exceptions.\
            OAIAPILabelledException(message='Unable to add the new metadata format.%s' % e.message,
                                    status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        raise oai_pmh_exceptions.\
            OAIAPILabelledException(message='Unable to add the new metadata format.%s' % e.message,
                                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_metadata_format_schema_url(metadata_format, host_uri=None):
    """ Get the Schema URL.
    Args:
        metadata_format: OaiProviderMetadataFormat.
        host_uri: Host URI.

    Returns:
        Schema URL.

    """
    if metadata_format.is_template:
        split_url = metadata_format.schema.split("/")
        title = split_url[0]
        version_number = split_url[1]
        return _get_absolute_uri(title, version_number, host_uri)
    else:
        return metadata_format.schema


def _get_absolute_uri(title, version_number, host_uri=None):
    """ Get the absolute URI. Use the host_uri in parameter, otherwise use settings.
    Args:
        title: Metadata Format title.
        version_number: Metadata Format version.
        host_uri: Host URI.

    Returns:

    """
    reverse_get_xsd = reverse('core_oaipmh_provider_app_get_xsd', args=[title, version_number])
    absolute_uri_from_settings = urljoin(settings.OAI_HOST_URI, reverse_get_xsd)
    try:
        if host_uri:
            absolute_uri = urljoin(host_uri, reverse_get_xsd)
        else:
            absolute_uri = absolute_uri_from_settings
    except:
        absolute_uri = absolute_uri_from_settings

    return absolute_uri


def _get_simple_template_metadata_format_schema_url(title, version_number):
    """ Get the simple Schema URL for a template metadata format.
    Args:
        title: Title of the template.
        version_number: Version of the template

    Returns:
        Simple Schema URL.

    """
    return "{0}/{1}".format(title, version_number)


def _get_target_namespace(xml_schema):
    """ Get the target namespace.
    Args:
        xml_schema:  XML representation of the schema.

    Returns:
        The target namespace.

    """
    xsd_tree = XSDTree.fromstring(xml_schema.encode('utf-8'))
    root = xsd_tree.find(".")
    if 'targetNamespace' in root.attrib:
        target_namespace = root.attrib['targetNamespace']
        if target_namespace not in root.nsmap.values():
            message = "The use of a targetNamespace without an associated prefix is not supported."
            raise oai_pmh_exceptions.OAIAPILabelledException(message=message,
                                                             status_code=status.HTTP_400_BAD_REQUEST)
    else:
        target_namespace = "http://www.w3.org/2001/XMLSchema"

    return target_namespace
