import requests

from ioflow.performance_reporter.performance import Performance
from ioflow.performance_reporter.performance_reporter_base import \
    PerformanceReporterBase


class DbPerformanceReporter(PerformanceReporterBase):
    def send_performances(self, metrics):
        for k, v in metrics.items():
            self.log_performance(k, v)

    def log_performance(self, key, value):
        metric = Performance(key, value)
        self.post_performance(metric)

    def post_performance(self, metric):
        data = {
            'id': self.config['task_id'],
            'key': metric.key,
            'value': metric.value,
        }
        r = requests.post(self.config['performance_report_url'],
                          json=data)
        assert r.ok


if __name__ == "__main__":
    config = {'task_id': '5d005b6cb775fa16367a2f74', 'performance_report_url': 'http://10.43.10.22:25005/savedrawingdata'}
    dpr = DbPerformanceReporter(config)
    dpr.send_performances(
        {"trainLoss": "2",
         "trainAccuray": "3",
         "testLoss": "4",
         "testAccuray": "66"}
    )
