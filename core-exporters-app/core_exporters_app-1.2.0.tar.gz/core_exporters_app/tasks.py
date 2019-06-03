""" Exporters tasks
"""
from __future__ import absolute_import, unicode_literals

import json

from celery import shared_task

import core_exporters_app.commons.constants as exporter_constants
import core_exporters_app.components.exporter.api as exporter_api
from core_explore_common_app.components.result.models import Result
from core_explore_common_app.rest.result.serializers import ResultBaseSerializer
from core_exporters_app.exporters.exporter import get_exporter_module_from_url, AbstractExporter
from core_main_app.utils.requests_utils.requests_utils import send_get_request


@shared_task
def export_files(exported_file_id, exporters_list_url, url_base, data_url_list, session_key):
    """ Asynchronous tasks exporting files

    Args:
        exported_file_id:
        exporters_list_url:
        url_base:
        data_url_list:
        session_key:

    Returns:

    """
    # gets all data from the url list
    result_list = _get_results_list_from_url_list(url_base, data_url_list, session_key)

    transformed_result_list = []
    # Converts all data
    for exporter_id in exporters_list_url:
        # get the exporter with the given id
        exporter_object = exporter_api.get_by_id(exporter_id)
        # get the exporter module
        exporter_module = get_exporter_module_from_url(exporter_object.url)
        # if is a xslt transformation, we have to set the xslt
        if exporter_object.url == exporter_constants.XSL_URL:
            # set the xslt
            exporter_module.set_xslt(exporter_object.xsl_transformation.content)
        # transform the list of xml files
        transformed_result_list.extend(exporter_module.transform(result_list, session_key))

    # Export in Zip
    AbstractExporter.export(exported_file_id, transformed_result_list)


def _get_results_list_from_url_list(url_base, url_list, session_key):
    """ Gets all data from url

    Args:
        url_base: url of running server
        url_list: url list to request
        session_key: Session key used for requests.get
    Returns:

    """
    result_list = []
    for url in url_list:
        response = send_get_request(url_base + url, cookies={"sessionid": session_key})
        if response.status_code == 200:
            # Build serializer
            results_serializer = ResultBaseSerializer(data=json.loads(response.text))
            # Validate result
            results_serializer.is_valid(True)
            # Append the list returned
            result_list.append(Result(title=results_serializer.data['title'],
                                      xml_content=results_serializer.data['xml_content']))
    return result_list
