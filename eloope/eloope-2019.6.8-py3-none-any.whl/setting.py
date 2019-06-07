from . import logger


def _connection_interrupt_callback(engine, repeat_count):
    """
    Engine 连接中断回调函数,
    :param engine: Engine 实例
    :param repeat_count: 重复连接次数
    :return: True: 重新连接, False: 断开连接退出程序
    """
    logger.system(f'Connection interrupt (repeat_count: {repeat_count}) ')
    return True if repeat_count < 5 else False


connection_interrupt_callback = _connection_interrupt_callback
send_interval = 1
log_path = None
log_filter = ('info', 'debug', 'result', 'warning', 'error', 'system')
