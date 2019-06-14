from seetaas_helper.config import get_metric_api, get_dataset_api, get_metric_token, get_dataset_token
import requests
import logging
from requests.adapters import HTTPAdapter

logger = logging.getLogger("seetaas-helper")

session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=3))
session.mount('https://', HTTPAdapter(max_retries=3))

PLOT_LINE = 'line'


class _MsgType:
    NewMetric = "NewMetric"
    MetricData = "MetricData"
    Progress = "Progress"


_metric_api = get_metric_api()
_token = get_metric_token()


def _send(*bodys):
    for b in bodys:
        if len(_metric_api) == 0 or len(_token) == 0:
            raise Exception("You should run your algorithm inner SeeTaaS or AutoDL platform")
        try:
            resp = session.post('{}/uploadTaskMetrics'.format(_metric_api),
                                json=b,
                                timeout=5)
            if resp.status_code != 200:
                logger.error("send metrics http code: {}".format(resp.status_code))
        except requests.RequestException as e:
            logger.error('Could not reach metric api. detail: {}'.format(e))


class MetricFigure:
    def __init__(self, title, y1_name, y1_type=PLOT_LINE, y2_name=None, y2_type=None):
        """
        :param title:      图表的名称(最多两个纵轴)
        :param y1_name:    metric纵轴1名称, 如 Accuracy
        :param y1_type:    metric纵轴1类型, 如 PLOT_LINE为折线图
        :param y2_name:    metric纵轴2名称, 如 Softmax_Loss
        :param y2_type:    metric纵轴2类型, 如 PLOT_LINE为折线图
        """
        self.y1_name = y1_name
        self.y2_name = y2_name
        self.title = title
        if not isinstance(title, str) and len(title) == 0:
            raise ValueError("title must be string")
        if not isinstance(y1_name, str) and len(y1_name) == 0:
            raise ValueError("y1 must be string")
        if y1_type not in (PLOT_LINE,):
            raise KeyError("y1_type not exists")
        series = [{
            "name": y1_name,
            "type": y1_type,
        }]
        if y2_name:
            if not isinstance(y2_name, str) and len(y2_name) == 0:
                raise ValueError("y2 must be string")
            if y2_type not in (PLOT_LINE,):
                raise KeyError("y2_type not exists")
            series.append({
                "name": y2_name,
                "type": y2_type,
            })
        body = {
            "msgType": _MsgType.NewMetric,
            "title": title,
            "series": series
        }
        _send(body)

    def push_metric(self, x, y1, y2=None):
        """
        :param x:   横坐标，一般为迭代次数
        :param y1:  x对应的y1的值
        :param y2:  x对应的y2的值
        :return:
        """
        items = [{
            "msgType": _MsgType.MetricData,
            "title": self.title,
            "seriesName": self.y1_name,
            "value": [x, y1]
        }]
        if y2 and self.y2_name:
            items.append({
                "msgType": _MsgType.MetricData,
                "title": self.title,
                "seriesName": self.y2_name,
                "value": [x, y2]
            })
        _send(items)


def send_progress(progress):
    """
    :param progress: 百分比进度，值范围：0.0 ~ 1.0
    :return:
    """
    if not (0.0 < progress < 1.0):
        logger.error("progress value error. should in range [0.0: 1.0]. but get {}".format(progress))
        return
    body = {
        "msgType": _MsgType.Progress,
        "value": progress
    }
    _send(body)


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


if __name__ == '__main__':
    figure = MetricFigure("loss&acc", "loss", PLOT_LINE, "acc", PLOT_LINE)
    import time
    import random
    while True:
        for i in range(10):
            figure.push_metric(i, random.randint(1, 10), random.randint(5, 15))
        time.sleep(60)
