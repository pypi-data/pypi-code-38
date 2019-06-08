from django.conf import settings

class WebFactionFixes(object):
    """Sets 'REMOTE_ADDR' based on 'HTTP_X_FORWARDED_FOR', if the latter is
    set.

    Based on http://djangosnippets.org/snippets/1706/
    """
    def process_request(self, request):
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            ip = request.META['HTTP_X_FORWARDED_FOR'].split(",")[0].strip()
            request.META['REMOTE_ADDR'] = ip


class DisableCSRFMiddleware(object):

    def process_request(self, req):
        attr = '_dont_enforce_csrf_checks'
        if settings.DEBUG and not getattr(req, attr, False):
            setattr(req, attr, True)
