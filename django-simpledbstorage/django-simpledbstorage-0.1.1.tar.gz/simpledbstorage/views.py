from django.http.response import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse

from .models import DbFile

def download(request, filename):
    try:
        file = DbFile.objects.defer("data").get(name=filename)

        response = HttpResponse(content=file.data.tobytes(), content_type=file.media_type)
        response['Content-Disposition'] = 'inline; filename=%s' % file.name

        return response
    except ObjectDoesNotExist:
        raise Http404()
