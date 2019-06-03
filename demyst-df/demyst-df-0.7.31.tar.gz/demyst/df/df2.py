import os
import sys
import datetime
from functools import wraps
import json
import requests
from glom import glom, T

from demyst.common import load_config
from demyst.common import Connectors

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

class DataFunction(object):

    def __init__(self, txid=NTXID, inputs=None, config_file=None, sample_mode=False, region=None, env=None, key=None):
        if inputs is None:
            inputs = {}
        self.C = load_config(config_file=config_file, region=region, env=env, key=key)
        if(key):
            self.key = key
        else:
            self.key = self.C.get("API_KEY")

        self.txid = txid
        self.inputs = inputs
        self.sample_mode = sample_mode
        self.providers_cache = {}
        self.connectors = Connectors(inputs=self.inputs,
                                     config=self.C,
                                     sample_mode=self.sample_mode)

    # XXX Need to rethink this
    def provider(self, name, inputs=None):
        if (inputs == None):
            inputs = self.inputs

        if os.getenv("DEMYST_DF_PROVIDER_ERROR"):
            return MOCK_PRODUCT_ERROR
        else:
            return MOCK_PRODUCT_RESPONSE

    # See https://www.notion.so/demystdata/Data-Function-Logging-c50ecfd139a54988a8e3781a567ae3c4
    def record(self, table, data, f=sys.stdout):
        data_function_name = self.C.get('DATA_FUNCTION_NAME')
        data_str = "\t".join(str(d) for d in data)
        now = datetime.datetime.utcnow()
        # https://prestodb.io/docs/current/language/types.html#timestamp
        # TIMESTAMP '2001-08-22 03:04:05.321
        athena_ts = now.strftime('%Y-%m-%d %H:%M:%S.%f')
        iso_ts = now.isoformat()
        # _df_record DF_NAME TABLE ISOTS ATHTS DATA
        print('_df_record\t{}\t{}\t{}\t{}\t{}'.format(data_function_name, table, iso_ts, athena_ts, data_str), file=f)


def df2(f):

    @wraps(f)
    def wrapper(*args, **kwargs):

        event = {}
        if type(args[0]) is dict:
            event = args[0]
        elif type(args[1]) is dict:
            event = args[1]
        else:
            raise "Bad arguments in df2 decorator"

        inputs = {}
        if event.get('input') and event['input'].get("pass_through") and event['input']['pass_through'].get('data'):
            inputs = event['input']['pass_through']['data']

        if inputs == {} and event.get('input'): # this is the case when blackfin batches are run against df providers
            inputs = event['input']

        if inputs == None:
            inputs = {}

        key = event.get('api_token')

        df = DataFunction(txid=NTXID, inputs=inputs, key=key)
        return f(df)

    return wrapper

if __name__ == '__main__':
    @df2
    def fun(e):
        print(e)
    fun({"inputs": True})
