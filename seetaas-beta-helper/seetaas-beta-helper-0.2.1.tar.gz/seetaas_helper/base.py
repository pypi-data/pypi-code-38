import requests
from requests.adapters import HTTPAdapter
from seetaas_helper.config import get_metric_api, get_metric_token
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("seetaas-helper")

session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=3))
session.mount('https://', HTTPAdapter(max_retries=3))


class Config:
    OPEN = True


def TURN_OFF():
    Config.OPEN = False


class _MsgType:
    NewMetric = "NewMetric"
    MetricData = "MetricData"


class _ResultType:
    SCALAR_RESULT = 'scalar_result'  # 用于如Rank1，Rank5，LFW，MegaFace测试协议输出的单精度值测试结果
    CURVE_RESULT = 'curve_result'  # 用于如ROC测试协议输出的测试曲线
    PROGRESS = 'progress'


_metric_api = get_metric_api()
_metric_token = get_metric_token()


def _send_metric(body):
    if not Config.OPEN:
        return
    if len(_metric_api) == 0 or len(_metric_token) == 0:
        raise Exception("You should run your algorithm inner SeeTaaS or AutoDL platform")
    try:
        if not isinstance(body, list):
            body = [body]
        resp = session.post('{}/uploadTaskMetrics'.format(_metric_api),
                            json={
                                "token": _metric_token,
                                "items": body
                            },
                            timeout=5)
        if resp.status_code != 200:
            logger.error("send metrics http code: {}. content: {}".format(resp.status_code, resp.content))
    except requests.RequestException as e:
        logger.error('Could not reach metric api. detail: {}'.format(e))


def _send_result(result_type, name, value):
    if not Config.OPEN:
        return
    if len(_metric_api) == 0 or len(_metric_token) == 0:
        raise Exception("You should run your algorithm inner SeeTaaS or AutoDL platform")
    try:
        resp = session.post('{}/updateTaskAttribute'.format(_metric_api),
                            json={
                                "token": _metric_token,
                                "type": result_type,
                                "name": name,
                                "value": value
                            },
                            timeout=5)
        if resp.status_code != 200:
            logger.error("send evaluate result http code: {}. content: {}".format(resp.status_code, resp.content))
    except requests.RequestException as e:
        logger.error('Could not reach evaluate result api. detail: {}'.format(e))
