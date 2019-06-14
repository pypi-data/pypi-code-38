from seetaas_helper.api import send_metrics, send_data_attribute, MetricFigure, PLOT_LINE
from seetaas_helper.config import get_data_attribute
import unittest


class TestHelper(unittest.TestCase):
    def test_dataset_api(self):
        send_data_attribute(classNum=100, recordNum=1000, className=["class1", "class2", "class3"])

    def test_metric_api(self):
        send_metrics(loss=1.0, acc=0.98)

    def test_get_dataset_attribute(self):
        print("dataset attribute: ", get_data_attribute())


class TestMetricFigure(unittest.TestCase):
    def test_multi_metric(self):
        figure = MetricFigure("loss&acc", "loss", PLOT_LINE, "acc", PLOT_LINE)
        for i in range(100):
            figure.push_metric(i, i * 9, i * 11)

    def test_a_metric(self):
        figure = MetricFigure("loss&acc", "loss", PLOT_LINE)
        for i in range(100):
            figure.push_metric(i, i * 9.9, 10000)


class TestDeployAPI(unittest.TestCase):
    def test_pass_image(self):
        import requests
        import base64
        data = {
            "base64_image": base64.b64encode(open("/tmp/test.jpg", 'rb').read()).decode()
        }
        resp = requests.post(url="http://localhost:5050/", json=data)
        print("STATUS: ", resp.status_code, " Content: ", resp.content)


if __name__ == '__main__':
    unittest.main()

