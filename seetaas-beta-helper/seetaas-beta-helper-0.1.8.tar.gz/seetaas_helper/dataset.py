from seetaas_helper.base import session
import requests
from seetaas_helper.config import get_dataset_api, get_dataset_token
import logging
logger = logging.getLogger("seetaas-helper")


def send_data_attribute(output_index=1, **attr):
    dataset_api = get_dataset_api()
    for k, v in attr.items():
        try:
            resp = session.post('{}/updateDatasetAttribute'.format(dataset_api),
                                json={
                                    "token": get_dataset_token(),
                                    "output": str(output_index),
                                    "name": k,
                                    "value": v
                                },
                                timeout=5)
            if resp.status_code != 200:
                logger.error("send data attribute http code: {}. content: {}".format(resp.status_code, resp.content))
        except requests.RequestException as e:
            logger.error('Could not reach dataset api. detail: {}'.format(e))
