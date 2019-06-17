from seetaas_helper.base import _send_result, _ResultType


def send_scalar_result(**results):
    """
    发送单数值测试结果
    eg: send_scalar_result(top1=0.92, top2=0.98)
    """
    for k, v in results.items():
        _send_result(_ResultType.SCALAR_RESULT, k, v)


def send_curve_result(title, x_points, y_points):
    """
    发送测试协议输出为曲线的测试结果
    eg: send_curve_result("ROC", [0.0, 0.2, 0.4, 0.6, 0.8, 1.0], [0.0, 0.8, 0.89, 0.94, 0.96, 1.0])
    """
    _send_result(_ResultType.CURVE_RESULT, title, {"x": x_points, "y": y_points})


if __name__ == '__main__':
    send_scalar_result(top1=0.92, top2=0.98)
    send_curve_result("ROC", [0.0, 0.2, 0.4, 0.6, 0.8, 1.0], [0.0, 0.8, 0.89, 0.94, 0.96, 1.0])
