#from .config_exception import ConfigException
import json
import os
from ..client.configuration import Configuration
from ..client.api_client import ApiClient

MODELARTS_CONFIG = os.getenv("MODELARTS_CONFIG", "~/.modelmaker/config.json")

def create_client(config_file=None, context=None, credential=None, access_key=None, secret_key=None, username=None, password=None, token=None, host=None, verify_ssl=False):
	"""
    create apiclient by context config
    :param config_file: config file
    :param context: context name
    :param credential: user token
    :return:

    Examples:
       from modelarts import config
       client = config.create_client(context="normal_user")
	"""
	client_config = Configuration(host,verify_ssl,username,password)
#    _load_config(config_file=config_file, context=context,
#                 client_configuration=client_config, credential=credential,
#                 access_key=access_key, secret_key=secret_key, username=username, password=password, account=account)
	api_client = ApiClient(configuration=client_config,header_name="Auth-Token",header_value=token)
    #Dynamic add context property
	ApiClient.context = None
	api_client.context = context
	return api_client


