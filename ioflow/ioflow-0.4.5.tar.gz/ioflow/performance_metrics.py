import requests

from ioflow.performance_reporter.metric import Metric

task_status_registry = {}


def get_performance_metrics_class(config):
    return task_status_registry[config.get('performance_metrics_schema', 'raw')]


def registry_performance_metrics_class(schema, class_):
    task_status_registry[schema] = class_


class BasePerformanceMetrics(object):
    def __init__(self, config):
        self.config = config

    def send_metrics(self, metrics, step=None):
        timestamp = int(time.time())
        for k, v in metrics.items():
            self.log_metric(k, v, timestamp=timestamp, step=step)

    def log_metric(self, key, value, timestamp=None, step=None):
        """ learned from MLflow log_metrics"""
        timestamp = timestamp if timestamp is not None else int(time.time())
        step = step if step is not None else 0

        metric = Metric(key, value, timestamp, step)
        self.post_metric(metric)

    def post_metric(self, metric):
        raise NotImplementedError


class RawPerformanceMetrics(BasePerformanceMetrics):
    def post_metric(self, metric):
        print('[{}]{}: {} => {}'.format(
            self.config['task_id'],
            metric.timestamp, metric.key, metric.value))


registry_performance_metrics_class('raw', RawPerformanceMetrics)


class HttpPerformanceMetrics(BasePerformanceMetrics):
    def post_metric(self, metric):
        data = {
            'id': self.config['task_id'],
            'key': metric.key,
            'value': metric.value,
            'step': metric.step,
            'timestamp': metric.timestamp
        }

        r = requests.post(self.config['metrics_report_url'], json=data)
        assert r.ok


registry_performance_metrics_class('http', HttpPerformanceMetrics)
