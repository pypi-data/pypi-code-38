from django.http import HttpResponse
from django.utils.encoding import escape_uri_path
from django.views.generic import View

from .client import cmis_client


class CmisDownloadView(View):
    def get(self, request, *args, **kwargs):
        cmis_doc = cmis_client.get_cmis_document(kwargs.get("uuid"))
        response = HttpResponse(content=cmis_doc.getContentStream(), content_type="application/force-download")
        response["Content-Disposition"] = f"attachment; filename={escape_uri_path(cmis_doc.properties.get('cmis:name'))}.bin"
        return response
