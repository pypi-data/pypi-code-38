from seetaas_helper.base import _ResultType, _send_result, logger, Config


def send_progress(progress):
    """
    :param progress: 百分比进度，值范围：0.0 ~ 1.0
    :return:
    """
    if not Config.OPEN:
        return
    if not (0.0 <= progress <= 1.0):
        logger.error("progress value error. should in range [0.0: 1.0]. but get {}".format(progress))
        return
    _send_result(_ResultType.PROGRESS, "progress", progress)


if __name__ == '__main__':
    for i in range(100):
        print("send progress")
        send_progress(i * 0.01)
