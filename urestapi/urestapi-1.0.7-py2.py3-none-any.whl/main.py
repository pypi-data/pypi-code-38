from __future__ import unicode_literals
from __future__ import print_function

import click
import json
import os
import sys

from .uptycs_rest_api import uptycs_rest_call as urest_call
from .__init__ import __version__


click.disable_unicode_literals_warning = True

class UptycsRest(object):

    def __init__(self,
                 api_json_key=None,
                 verify_ssl=True,
                 suffix=None,
                 api=None,
                 method=None,
                 post_data_file=None,
                 post_data=None):

        self.api_json_key_data = json.load(open(api_json_key))
        self.verify_ssl = verify_ssl
        self.suffix = ".uptycs.io"
        if suffix:
            self.suffix = suffix

        self.domain = self.api_json_key_data['domain']
        self.key = self.api_json_key_data['key']
        self.secret = self.api_json_key_data['secret']
        self.verify_ssl = verify_ssl
        self.customer_id = self.api_json_key_data['customerId']
        self.url = "https://" + self.domain + self.suffix
        self.method = method
        if post_data:
            self.post_data = json.loads(post_data)
        else:
            self.post_data = post_data
        self.post_data_file = post_data_file
        if post_data_file:
            self.post_data = json.load(open(post_data_file))

        self.api = api

    def call_api(self):
        urest = urest_call(url=self.url,
                           customer_id=self.customer_id,
                           key=self.key,
                           secret=self.secret,
                           api=self.api,
                           method=self.method,
                           post_data=self.post_data,
                           verify_ssl=self.verify_ssl)
        urest.rest_api_call()
            
        if urest.response_content:
            if urest.is_response_json:
                print(json.dumps(json.loads(urest.response_content), 
                                 indent=4,
                                 sort_keys=True))
            else:
                print(urest.response_content)


@click.command()
@click.option("-V", "--version", is_flag=True, help="Output urestapi's version.")
@click.option("-k", "--keyfile", "keyfile", help="Uptycs json key file.")
@click.option("--domainsuffix","domainsuffix",help="Uptycs Domain Suffix like"
                                                       " .uptycs.io")
@click.option("--enable-ssl/--disable-ssl", default=False,
                help="verify ssl certificate")
@click.option("-m", "--method", type=str, help="restAPI method")
@click.option("-a", "--api", type=str, help="API name [GET|POST|PUT|DELETE]")
@click.option("-d", "--postdata", type=str, help="post json data")
@click.option("-D", "--postdatafile", type=str, help="post json data file")

def cli(
    version,
    keyfile,
    domainsuffix,
    enable_ssl,
    method,
    api,
    postdata,
    postdatafile,
):
    if version:
        print("Version:", __version__)
        sys.exit(0)

    if not keyfile:
        print("Keyfile is required to continue\nPlease check --help option")
        sys.exit(1)

    if (not os.path.isfile(keyfile)):
        print("ERROR: Key file doesnt exists.")
        sys.exit(1)

    if not api:
        print("API is required to continue\nPlease check --help option")
        sys.exit(1)

    if not method:
        print("method is required to continue\nPlease check --help option")
        sys.exit(1)

    if enable_ssl:
        verify_ssl = True
    else:
        verify_ssl = False

    if method.lower() in ['post','put']:
        if not postdata and not postdatafile:
            print("method post data json continue\nPlease check --help option")

    api_call = UptycsRest(api_json_key=keyfile,
                      verify_ssl=verify_ssl,
                      suffix=domainsuffix,
                      api=api,
                      method=method,
                      post_data=postdata,
                      post_data_file=postdatafile)

    api_call.call_api()

if __name__ == "__main__":                                                      
    cli()
