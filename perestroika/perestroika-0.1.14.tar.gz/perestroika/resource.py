import json
from typing import Dict, Union, Optional

from perestroika.exceptions import RestException
from perestroika.methods import Method


class Resource:
    methods: Optional[Dict[str, Method]] = None

    def handler(self, request, **kwargs):
        raise NotImplementedError()

    def get_method_handler(self, **kwargs):
        raise NotImplementedError()

    def method_not_permitted(self):
        raise NotImplementedError()


class DjangoResource(Resource):
    from django.views.decorators.csrf import csrf_exempt

    cache_control: Dict[str, Union[bool, int]] = None

    def get_method_handler(self, **kwargs):
        request = kwargs['request']

        if self.methods:
            return self.methods.get(request.method.lower())

    def method_not_permitted(self):
        from django.http import HttpResponseNotAllowed

        permitted_methods = list(self.methods.keys()) if self.methods else []
        return HttpResponseNotAllowed(permitted_methods=permitted_methods)

    @csrf_exempt
    def handler(self, request, **kwargs):
        from django.utils.cache import patch_cache_control

        method_handler = self.get_method_handler(request=request)

        if method_handler:
            response = method_handler.handle(request)

            if self.cache_control:
                patch_cache_control(response, **self.cache_control)

            return response

        return self.method_not_permitted()

    def schema(self, request):
        from django.http import JsonResponse
        _schema = {
            k: v.schema() for k, v in self.methods.items()
        }

        return JsonResponse(_schema)


class JSONResource(Resource):
    def get_method_handler(self, **kwargs):
        if self.methods:
            return self.methods.get(kwargs.get('method'))

    def method_not_permitted(self):
        permitted_methods = list(self.methods.keys()) if self.methods else []

        return json.dumps(
            {
                'status': 'error',
                'status_code': 405,
                'message': f'Permitted methods: {permitted_methods}'
            }
        )

    def handler(self, request, **kwargs):
        method_handler = self.get_method_handler(**kwargs)

        if method_handler:
            try:
                response = method_handler.handle(
                    request,
                    json_data=kwargs.get('json_data'),
                    method=kwargs.get('method')
                )
            except RestException as e:
                return json.dumps(
                    {
                        'status': 'error',
                        'status_code': e.status_code,
                        'message': e.message
                    }
                )

            return response

        return self.method_not_permitted()
