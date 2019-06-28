from django.http import Http404, HttpResponse, StreamingHttpResponse
from django.utils.encoding import escape_uri_path
from django.views.generic import View

from .client import cmis_client
from .client.exceptions import DocumentDoesNotExistError


class CmisDownloadView(View):
    def get(self, request, *args, **kwargs):
        try:
            cmis_doc = cmis_client.get_cmis_document(kwargs.get("uuid"))
        except DocumentDoesNotExistError:
            raise Http404
        else:
            content_type = cmis_doc.properties.get("formaat") or "application/octet-stream"
            file_name = escape_uri_path(cmis_doc.properties.get('cmis:name'))
            response = StreamingHttpResponse(streaming_content=cmis_doc.getContentStream(), content_type=content_type)
            response["Content-Disposition"] = f"attachment; filename={file_name}.bin"
            return response
