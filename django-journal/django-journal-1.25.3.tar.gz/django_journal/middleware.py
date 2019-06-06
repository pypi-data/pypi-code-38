import django_journal

class JournalMiddleware(object):
    '''Add record and error_record methods to the request object to log
       current user and current REMOTE_ADRESS.

       It must be setup after the auth middleware.
    '''

    def process_request(self, request):
        user = getattr(request, 'user', None)
        ip = request.META.get('REMOTE_ADDR', None)
        def record(tag, template, using=None, **kwargs):
            if 'user' not in kwargs:
                kwargs['user'] = user
            if 'ip' not in kwargs:
                kwargs['ip'] = ip
            django_journal.record(tag, template, using=using,**kwargs)
        def error_record(tag, template, using=None, **kwargs):
            if 'user' not in kwargs:
                kwargs['user'] = user
            if 'ip' not in kwargs:
                kwargs['ip'] = ip
            django_journal.error_record(tag, template, using=using, **kwargs)
        request.record = record
        request.error_record = error_record
        return None

    def process_response(self, request, response):
        if hasattr(request, 'record'):
            del request.record
        if hasattr(request, 'error_record'):
            del request.error_record
        return response
