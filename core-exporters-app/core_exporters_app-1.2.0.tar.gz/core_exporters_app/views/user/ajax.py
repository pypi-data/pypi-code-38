""" Ajax Exporter user
"""
import json

from celery.exceptions import TimeoutError, SoftTimeLimitExceeded
from django.core.urlresolvers import reverse
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.template import loader

import core_exporters_app.components.exported_compressed_file.api as exported_compressed_file_api
import core_exporters_app.components.exported_compressed_file.api as exported_file_api
import core_exporters_app.tasks as exporter_tasks
from core_exporters_app.components.exported_compressed_file.models import ExportedCompressedFile
from core_exporters_app.views.user.forms import ExportForm


def exporters_selection(request):
    """ exporters selection modal POST / GET

    Args:
        request:

    Returns:

    """
    try:
        if request.method == 'POST':
            return _exporters_selection_post(request)
        else:
            raise Exception("request method should be POST")
    except Exception as e:
        return HttpResponseBadRequest(e.message)


def open_form(request):
    """ open form to selection exporters

    Args:
        request:

    Returns:

    """
    try:
        context_params = dict()

        # Template form base
        templates_selector = \
            loader.get_template('core_exporters_app/user/exporters/list/list_exporters_selector_base.html')

        # Getting the template ID list and data selected URL because the Export Form need it
        template_id_list = request.POST.getlist('template_id_list[]')
        template_hash_list = request.POST.getlist('template_hash_list[]')
        data_url_list = request.POST.getlist('data_url_list[]')

        # Generating the Export form
        exporters_selection_form = ExportForm(template_id_list=template_id_list,
                                              template_hash_list=template_hash_list,
                                              data_url_list=data_url_list)
        context_params['exporters_selector_form'] = exporters_selection_form

        # Generates and returns the context
        context = {}
        context.update(request.COOKIES)
        context.update(request.POST)
        context.update(context_params)
        return HttpResponse(json.dumps({'template': templates_selector.render(context)}),
                            content_type='application/javascript')
    except Exception as e:
        raise Exception('Error occurred during the form display')


def check_download_status(request):
    """ Checks if a file is ready for download, Id is expected on the request

    Args:
        request:

    Returns:

    """
    file_id = request.GET.get('file_id', None)

    if file_id is not None:
        try:
            # Get the exported file with the given id
            exported_file = exported_file_api.get_by_id(file_id)
        except:
            return HttpResponseBadRequest("File with the given id does not exist")

        return HttpResponse(json.dumps({'is_ready': exported_file.is_ready,
                                        'message': "The file is now ready for download"}),
                            content_type='application/javascript')
    else:
        return HttpResponseBadRequest("File id is missing in parameters")


def _exporters_selection_post(request):
    """ exporters selection modal POST

    Args:
        request:

    Returns:

    """
    try:
        if request.method == 'POST':
            # gets all parameters
            templates_id = request.POST['template_id_list'].split(',')
            templates_hash = request.POST['template_hash_list'].split(',')
            data_url_list = request.POST['data_url_list'].split(',')
            form = ExportForm(request.POST,
                              template_id_list=templates_id,
                              template_hash_list=templates_hash,
                              data_url_list=data_url_list)
            url_base = request.build_absolute_uri('/')[:-1]
            if form.is_valid():
                exporters = request.POST.getlist('my_exporters', None)
                if exporters is not None:
                    # Creation of the compressed file with is_ready to false
                    exported_file = ExportedCompressedFile(file_name='Query_Results.zip',
                                                           is_ready=False,
                                                           mime_type="application/zip")

                    # Save in database to generate an Id and be accessible via url
                    exported_compressed_file_api.upsert(exported_file)

                    try:
                        # start asynchronous task
                        exporter_tasks.export_files.delay(str(exported_file.id),
                                                          exporters,
                                                          url_base,
                                                          data_url_list,
                                                          request.session.session_key)
                    except (TimeoutError, SoftTimeLimitExceeded, exporter_tasks.export_files.OperationalError) as ex:
                        # Raised when a transport connection error occurs while sending a message
                        exporter_tasks.export_files(str(exported_file.id),
                                                    exporters,
                                                    url_base,
                                                    data_url_list,
                                                    request.session.session_key)

                    # redirecting
                    url_download = reverse("core_exporters_app_exporters_download")
                    url_to_redirect = "{0}{1}?id={2}".format(url_base, url_download, str(exported_file.id))
                    return HttpResponse(json.dumps({'url_to_redirect': url_to_redirect}),
                                        content_type='application/json')
            else:
                return HttpResponseBadRequest('Bad entries. Please check your entries')
        else:
            return HttpResponseBadRequest('Bad entries. Please check your entries')
    except Exception, e:
        return HttpResponseBadRequest(e.message, content_type='application/javascript')




