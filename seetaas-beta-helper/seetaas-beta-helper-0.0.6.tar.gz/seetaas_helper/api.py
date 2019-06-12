from seetaas_helper.config import get_metric_api, get_dataset_api, get_metric_token, get_dataset_token
import requests
import logging
from requests.adapters import HTTPAdapter

logger = logging.getLogger("seetaas-helper")

session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=3))
session.mount('https://', HTTPAdapter(max_retries=3))


def send_metrics(**metrics):
    metric_api = get_metric_api()
    try:
        resp = session.post('{}/uploadTaskMetrics'.format(metric_api),
                            json={
                                "token": get_metric_token(),
                                "items": [
                                    {"subject": k, "value": v} for k, v in metrics.items()
                                ]
                            },
                            timeout=5)
        if resp.status_code != 200:
            logger.error("send metrics http code: {}".format(resp.status_code))
    except requests.RequestException as e:
        logger.error('Could not reach metric api. detail: {}'.format(e))


def send_data_attribute(output_index=1, **attr):
    dataset_api = get_dataset_api()
    for k, v in attr.items():
        try:
            resp = session.post('{}/uploadTaskMetrics'.format(dataset_api),
                                json={
                                    "token": get_dataset_token(),
                                    "output": str(output_index),
                                    "name": k,
                                    "value": v
                                },
                                timeout=5)
            if resp.status_code != 200:
                logger.error("send data attribute http code: {}".format(resp.status_code))
        except requests.RequestException as e:
            logger.error('Could not reach dataset api. detail: {}'.format(e))
