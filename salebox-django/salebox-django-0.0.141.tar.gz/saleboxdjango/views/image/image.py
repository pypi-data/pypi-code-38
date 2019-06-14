from opposablethumbs.opposablethumbs import OpposableThumbs

from django.conf import settings
from django.http import Http404


def salebox_image_view(request, imgtype, dir, id, hash, suffix):
    try:
        f = '%s/salebox/%s/%s.%s.%s' % (
            settings.MEDIA_ROOT,
            dir,
            id,
            hash,
            suffix
        )
        params = 'file=%s&%s' % (f, settings.SALEBOX['IMG'][imgtype])
        ot = OpposableThumbs(params)
        return ot.response()
    except:
        raise Http404()
