class EnvelopeMiddleware(object):

    def __init__(self, get_response):
        # One-time configuration and initialization.
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        return response

    @staticmethod
    def process_template_response(request, response):
        params = getattr(request, 'query_params', getattr(request, 'GET', None))
        if params:
            envelope = params.get('envelope', None)
            if envelope and envelope in ('t', 1, '1', 'true'):
                data = {'code': response.status_code, 'message': response.status_text}
                if 'data' in response.data:
                    data_interno = response.data.pop('data')
                    data.update(response.data)
                    data['data'] = data_interno
                else:
                    data['data'] = response.data
                response.data = data
        return response
