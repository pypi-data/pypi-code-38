# -*- coding: utf-8 -*-
import requests
from urllib.parse import urljoin
from chaoslib.types import Secrets, Configuration
from logzero import logger
import os
import json
from chaosk8s_wix.slack.logger_handler import SlackHanlder

__all__ = ["check_no_alert_for_dashboard", "check_service_uppness"]

slack_handler = SlackHanlder()
slack_handler.attach(logger)


def check_no_alert_for_dashboard(
        dashboard_id: int,
        configuration: Configuration = None,
        secrets: Secrets = None) -> bool:
    """
    Check alert for dashboard in grafana
    :param panel_id: panel id in grafana
    :param dashboard_id: dashboard id in grafana
    :return: true if no alerts exist for specified dashboard, false otherwise
    """
    env = os.environ

    grafana_host = configuration.get('grafana_host')

    secrets = secrets or {}

    def lookup(k: str, d: str = None) -> str:
        return secrets.get(k, env.get(k, d))

    grafana_token = lookup("GRAFANA_TOKEN", "")

    headers = {"Authorization": "Bearer %s" % grafana_token}

    parameters = {"dashboardId": dashboard_id, "state": "alerting"}

    endpoint = urljoin(grafana_host, "/api/alerts")

    alerts = requests.get(endpoint, headers=headers, params=parameters).json()
    retval = len(alerts) == 0

    for alert in alerts:
        for match in alert['evalData']['evalMatches']:
            logger.debug("Alert for node {n}' ".format(
                n=match))

    return retval


def metrics_have_spikes(metrics: [], allowed_results: []) -> bool:
    '''
    Checks that metrics list has only allowed values in results field of metric
    :param metrics: list of metrics to check
    :param allowed_results: list of good values for metrics
    :return: true if there are results that are not allowed, true otherwise
    '''
    bad_metrics = [metric for metric in metrics if metric[0]
                   not in allowed_results]
    retval = len(bad_metrics) > 0

    return retval


def check_service_uppness(service: str,
                          allowed_results: [],
                          time_interval_seconds: int = 300,
                          configuration: Configuration = None,
                          secrets: Secrets = None) -> bool:
    """
       Check alert for dashboard in grafana
       :param panel_id: panel id in grafana
       :param dashboard_id: dashboard id in grafana
       :param alowed_results: whitelist of values that can be in dashboard metrics results
       :return: true if no alerts exist for specified dashboard, false otherwise
       """
    retval = False
    env = os.environ

    grafana_host = configuration.get('grafana_host')

    secrets = secrets or {}

    def lookup(k: str, d: str = None) -> str:
        return secrets.get(k, env.get(k, d))

    grafana_token = lookup("GRAFANA_TOKEN", "")

    headers = {"Content-Type": 'application/json',
               "Authorization": "Bearer %s" % grafana_token}
    # tmpl = 'minSeries(root_is_sensu.type_is_app-router.dispatcher_is_*.dc_is_*.app_is_{s}.metric_is_response)'
    tmpl = 'movingMedian(minSeries' \
           '(root_is_sensu.type_is_app-router.dispatcher_is_*.dc_is_*.app_is_{s}.metric_is_response), \'1min\')'

    query = tmpl.format(
        s=service)
    time_interval_string = "-{sec}seconds".format(sec=time_interval_seconds)
    parameters = {
        "target": query,
        "format": "json",
                  "from": time_interval_string
    }
    endpoint = urljoin(grafana_host, "api/datasources/proxy/1/render")

    resp = requests.get(endpoint, headers=headers, params=parameters)
    if resp.text != '':
        data = json.loads(resp.text)
        metrics = data[0]['datapoints']
        have_spikes = metrics_have_spikes(metrics, allowed_results)

    return not have_spikes
