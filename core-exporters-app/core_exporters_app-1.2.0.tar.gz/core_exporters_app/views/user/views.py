""" Exporter User views
"""
from django.http.response import HttpResponse
from core_main_app.utils.rendering import render
import core_exporters_app.components.exported_compressed_file.api as exported_file_api


def download_exported_compressed_file(request):
    """ Download view, ID file expected in parameters

    Args:
        request:

    Returns:

    """
    exporter_file_id = request.GET['id']

    try:
        # Get the exported file with the given id
        exported_file = exported_file_api.get_by_id(exporter_file_id)
    except:
        # TODO: catch good exception, redirect to error page
        pass

    # The file is not ready yet
    if exported_file.is_ready is False:
        # Generate the context
        context = {
            'message': 'Please wait, the download will start automatically',
            'is_ready': False,
            'id_file': exporter_file_id
        }
        # Add assets
        assets = {
            "js": [
                {
                    "path": 'core_exporters_app/user/js/exporter_compressed_file/download.js',
                    "is_raw": False
                }
            ],
            "css": [],
        }
        # Render the page
        return render(request, 'core_exporters_app/user/exported_compressed_file/download.html',
                      context=context, assets=assets)
    # the file is ready to be downloaded
    else:
        response = HttpResponse(exported_file.file.read())
        response['Content-Disposition'] = "attachment; filename=" + exported_file.file_name
        response['Content-Type'] = exported_file.file.content_type
        return response
