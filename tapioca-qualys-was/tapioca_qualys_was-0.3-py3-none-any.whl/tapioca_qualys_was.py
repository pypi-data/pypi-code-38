# coding: utf-8

from tapioca import (
    TapiocaAdapter, generate_wrapper_from_adapter, JSONAdapterMixin)

from requests.auth import HTTPBasicAuth


from .resource_mapping import RESOURCE_MAPPING


class Qualys_wasClientAdapter(JSONAdapterMixin, TapiocaAdapter):
    api_root = 'https://qualysapi.qg3.apps.qualys.com'
    resource_mapping = RESOURCE_MAPPING

    def get_request_kwargs(self, api_params, *args, **kwargs):
        params = super(Qualys_wasClientAdapter, self).get_request_kwargs(
            api_params, *args, **kwargs)

        params['auth'] = HTTPBasicAuth(
            api_params.get('user'), api_params.get('password'))

        if 'headers' not in params:
            params['headers'] = {}

        params['headers'].update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'})

        return params

    def get_iterator_list(self, response_data):
        return response_data

    def get_iterator_next_request_kwargs(self, iterator_request_kwargs,
                                         response_data, response):
        pass


Qualys_was = generate_wrapper_from_adapter(Qualys_wasClientAdapter)
