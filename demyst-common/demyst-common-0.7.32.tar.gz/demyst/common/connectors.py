import os
import sys
from functools import wraps
import json
import simplejson
import requests
from glom import glom, T
import urllib.parse

NKEY  = "__NO_API_KEY__"
NTXID = "__NO_TRANSACTION_ID__"
NATTR = "__DEMYST_ATTRIBUTE_NOT_FOUND__"

MOCK_PRODUCT_RESPONSE = {
    "output": {
        "mock_product": {
            "data": {
                "success": True
            }
        }
    }
}

MOCK_PRODUCT_ERROR = {
    "output": {
        "mock_product": {
            "error": {
                "message": "We had an error"
            }
        }
    }
}

DEFAULT_PRODUCT_ERROR = {
    "error": {
        "message": "Error detected"
    }
}

class DemystConnectorError(Exception):
    pass

class Connectors(object):

    def __init__(self, config, inputs=None, sample_mode=False):
        if inputs is None:
            inputs = {}
        self.C = config
        self.key = config.get('API_KEY')
        self.inputs = inputs
        self.sample_mode = sample_mode
        self.providers_cache = {}
        self.providers_errors = {}

    # XXX Hash by Inputs+BKF Options+Maybe Sample Mode
    def cache_key(self, provider_name, inputs=None):
        inputs = self.inputs if inputs == None else inputs
        inputs_hash = hash(frozenset(inputs.items()))
        key = provider_name + '.' + str(inputs_hash)
        return key

    def cache_add(self, provider_name, provider_payload, inputs=None):
        inputs = self.inputs if inputs == None else inputs
        key = self.cache_key(provider_name, inputs)

        if provider_payload.get('error'):
            # XXX Log error
            self.providers_cache[key] = provider_payload
            return False
        elif provider_payload.get('data') or provider_payload.get('flattened_data'):
            self.providers_cache[key] = provider_payload
            return True

    def fetch(self, provider_names, inputs=None, sample_mode=False):
        inputs = self.inputs if inputs == None else inputs

        api_key = None
        if self.key:
            api_key = self.key
        elif self.C.has_jwt_token():
            api_key = self.C.get_jwt_token()
        else:
            api_key = self.C.prompt_for_jwt_token_and_cache_it()

        # XXX be able to set BKF Options
        params = {
            "providers": provider_names,
            "api_key": api_key,
            "inputs": inputs,
            "config": {}
        }

        if (self.sample_mode or sample_mode):
            params['config']['mode'] = 'sample'

        params['config']['return_flattened_data'] = True
        params['config']['return_raw_data'] = True
        params['config']['return_meta_fields'] = True

        blackfin_url = "https://blackfin.us.mt.p.demystdata.com:443/"
        if self.C.get("BLACKFIN_URL"):
            blackfin_url = self.C.get("BLACKFIN_URL")
        url = urllib.parse.urljoin(blackfin_url, "v2/execute")

        resp = requests.post(url, data=simplejson.dumps(params, ignore_nan=True))
        if resp.status_code != 200:
            raise DemystConnectorError({
                'transaction_id': "Unknown",
                'message': resp.text
            })
            return False
        jresp = json.loads(resp.text)
        # Transactional failure
        if jresp.get('error'):
            raise DemystConnectorError({
                'transaction_id': jresp.get('transaction_id'),
                'message': jresp.get('error').get('message')
            })
            return False

        else:
            # Connector failures
            no_errors = True
            input_errors = jresp.get('input_errors')
            for provider in jresp.get('output').keys():
                payload = jresp.get('output').get(provider)
                # Add input errors to error message
                if input_errors:
                    provider_input_errors = input_errors.get(provider)
                    if provider_input_errors:
                        # Normally, payload should have error object, but create one if not
                        error = payload.get('error')
                        if not error:
                            error = {}
                            payload['error'] = error
                        msg = error.get('message') or ''
                        msg += self.format_input_errors(provider_input_errors)
                        error['message'] = msg
                r = self.cache_add(provider, payload, inputs)
                if not r:
                    no_errors = False
            return no_errors

    def format_input_errors(self, errors):
        result = ''
        for col, col_error in errors.items():
            result += ('\n* ' + col + ': ' + col_error['error']['message'])
        return result

    def cache_get_error(self, provider_name, inputs=None):
        inputs = self.inputs if inputs == None else inputs
        key = self.cache_key(provider_name, inputs)

        if self.providers_cache.get(key).get('error'):
            return self.providers_cache.get(key).get('error')
        else:
            return None

    def cache_get(self, provider_name, inputs=None, shape=None):
        inputs = self.inputs if inputs == None else inputs
        key = self.cache_key(provider_name, inputs)

        if (not self.providers_cache.get(key)):
            self.fetch([provider_name], inputs=inputs)

        if self.providers_cache.get(key).get('error'):
            return None
        else:
            if shape == "raw":
                return self.providers_cache.get(key).get('raw_data').get('body')
            if shape == "table":
                return self.providers_cache.get(key).get('flattened_data')
            else:
                return self.providers_cache.get(key).get('data')

    def raw(self, provider_name, inputs=None):
        return self.cache_get(provider_name, inputs=inputs, shape="raw")

    def get(self, provider_name, query, default=None, inputs=None, shape="nested", prefix=False):
        # XXX if Check fails log the miss on the cache
        # er = glom.Check(dict, query)
        # df.log(uuid, warn, er)
        if os.getenv("DEMYST_DF_PROVIDER_ERROR"):
            provider_data = DEFAULT_PRODUCT_ERROR
        elif provider_name == 'pass_through':
            # Ignore inputs parameter if pass_through is selected
            provider_data = self.inputs
        else:
            provider_data = self.cache_get(provider_name, inputs=inputs, shape=shape)
        if query == '':
            query = T
        elif shape == "table":
            query = T[query]

        res = glom(provider_data, query, default=None) or default
        if prefix and (shape == "table") and (type(res) is dict):
            keys = list(res).copy()
            for key in keys:
                res[provider_name+'.'+key] = res.pop(key)

        return res

    # full: include catalog
    def products(self, full=False):
        if full:
            return self.C.all_providers()
        else:
            results = []
            # remove catalog from each provider
            for p in self.C.all_providers():
                copy = p.copy()
                del copy["version"]
                results.append(copy)
            return results
            
    def product_catalog(self, provider_name):
        p = self.C.lookup_provider(provider_name)
        if p:
            return self.product_catalog_of_provider(p)
        else:
            return None

    def product_catalog_of_provider(self, p):
        if "version" in p:
            version = p["version"]
            if version and ("schema" in version):
                return version["schema"]
        return None
