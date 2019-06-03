""" OaiXslTransformation API calls
"""
from core_oaipmh_provider_app.components.oai_xsl_template.models import OaiXslTemplate


def get_by_id(oai_xslt_template_id):
    """ Returns the object with the given id

    Args:
        oai_xslt_template_id: Object id.

    Returns:
        OaiXslTemplate (obj): OaiXslTemplate object with the given id.


    """

    return OaiXslTemplate.get_by_id(oai_xslt_template_id)


def delete(oai_xsl_template):
    """ Deletes an OaiXslTemplate.

    Args:
        oai_xsl_template: OaiXslTemplate to delete.

    """
    oai_xsl_template.delete()


def get_all_by_templates(templates):
    """ Returns all OaiXslTemplate used by a list of templates.

       Args:
           templates: List of templates.

       Returns:
           List of OaiXslTemplate.

       """
    return OaiXslTemplate.get_all_by_templates(templates)


def get_all_by_metadata_format(metadata_format):
    """ Returns all OaiXslTemplate used by a metadata format.

       Args:
           metadata_format: OaiProviderMetadataFormat.

       Returns:
           List of OaiXslTemplate.

       """
    return OaiXslTemplate.get_all_by_metadata_format(metadata_format)


def upsert(oai_xsl_template):
    """ Upsert an OaiXslTemplate.
    Args:
        oai_xsl_template:

    Returns:

    """
    return oai_xsl_template.save_object()


def get_by_template_id_and_metadata_format_id(template_id, metadata_format_id):
    """ Returns an OaiXslTemplate by its template and metadata_format.
    Args:
        template_id: Template id.
        metadata_format_id: Metadata format id.

    Returns:
        OaiXslTemplate instance.

    """
    return OaiXslTemplate.get_by_template_id_and_metadata_format_id(template_id, metadata_format_id)


def get_template_ids_by_metadata_format(metadata_format):
    """ Returns all template ids using the given metadata_format.
    Args:
        metadata_format: Metadata format.

    Returns:
        List of template ids.

    """
    templates_id = []
    oai_xslt_templates = get_all_by_metadata_format(metadata_format)
    for elt in oai_xslt_templates:
        templates_id.append(elt.template.id)

    return templates_id


def get_metadata_formats_by_templates(templates):
    """ Returns all metadata formats using the given list of templates.
    Args:
        templates: List of templates.

    Returns:
        List of metadata formats.

    """
    metadata_formats = []
    oai_xslt_templates = get_all_by_templates(templates)
    for elt in oai_xslt_templates:
        metadata_formats.append(elt.oai_metadata_format)

    return metadata_formats

