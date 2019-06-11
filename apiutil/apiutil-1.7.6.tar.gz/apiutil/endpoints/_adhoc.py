# encoding: utf-8

from configurationutil import configuration
configuration.DEV_FORCE_REWRITE_CONFIG = True

import logging_helper
from logging_helper import multi_line_logger
from future.utils import iteritems
from apiutil.endpoints import APIConfig
from apiutil.endpoints.gui.window.config import APIEndpointsConfigRootWindow

logging = logging_helper.setup_logging(level=logging_helper.INFO)


api_config = APIConfig()

hosts = api_config.hosts
endpoints = api_config.endpoints
apis = api_config.apis
envs = api_config.environments


def host_adhoc():
    logging.info(u'---*---')
    logging.info(u'Hosts')

    def run_host(host):
        logging.info(u'===')
        logging.info(host.name)
        logging.info(u'---')
        multi_line_logger.LogLines(log_lines=str(host))

    logging.info(hosts.keys)  # Hosts

    for h in hosts.get_items():
        run_host(h)

    logging.info(u'---^---')


def endpoint_adhoc():
    logging.info(u'---*---')
    logging.info(u'Endpoints')

    def run_endpoint(endpoint):
        logging.info(u'===')
        logging.info(endpoint.name)
        logging.info(u'---')
        multi_line_logger.LogLines(log_lines=str(endpoint))

    logging.info(endpoints.keys)  # Endpoints

    for h in endpoints.get_items():
        run_endpoint(h)

    logging.info(u'---^---')


def api_adhoc():
    logging.info(u'---*---')
    logging.info(u'APIs')

    def run_api(api):
        logging.info(u'===')
        logging.info(api.name)
        logging.info(u'---')
        multi_line_logger.LogLines(log_lines=str(api))
        for ep in api.endpoints:
            multi_line_logger.LogLines(log_lines=str(ep))

    logging.info(apis.keys())  # APIs

    for ak, a in iteritems(apis):
        run_api(a)
        logging.info([k for k, e in iteritems(envs) if a.key in [a.key for a in e.apis]])  # Envs for API

    logging.info(u'---^---')


def env_adhoc():
    logging.info(u'---*---')
    logging.info(u'Environments')

    def run_env(env):
        logging.info(u'===')
        logging.info(env.name)
        logging.info(u'---')
        multi_line_logger.LogLines(log_lines=str(env))
        for api in env.apis:
            multi_line_logger.LogLines(log_lines=str(api))

    logging.info(envs.keys())  # Environments

    for ek, e in iteritems(envs):
        run_env(e)
        logging.info([a.key for a in e.apis])  # APIs for Env

    logging.info(u'---^---')


#host_adhoc()
#endpoint_adhoc()
#api_adhoc()
#env_adhoc()

logging.info(u'---*---')

#first_api = envs.production.apis.first_api
#multi_line_logger.LogLines(log_lines=str(first_api.host))
#multi_line_logger.LogLines(log_lines=str(first_api.params))
#multi_line_logger.LogLines(log_lines=str(first_api.endpoints))
#multi_line_logger.LogLines(log_lines=str(first_api.endpoints.ep_1))
#for ep in first_api.endpoints:
#    multi_line_logger.LogLines(log_lines=str(first_api.endpoints[ep]))

APIEndpointsConfigRootWindow()
