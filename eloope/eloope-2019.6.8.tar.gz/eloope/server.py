from .controller import Controller
from toolset import get_localhost
from concurrent import futures
from . import service_pb2_grpc
from pathlib import Path
from . import setting
from . import logger
import importlib
import pickle
import grpc
import time


def run_server(load_file=None, dump_path='.', log_path=None, host='localhost', port=6991):
    """
    启动服务
    :param load_file: 加载任务文件
    :param dump_path: 保存任务文件路径
    :param log_path: 日志保存路径
    :param host: 主机
    :param port: 端口
    """
    if not Path(dump_path).exists(): raise FileExistsError(dump_path)
    if setting.log_path and log_path:
        importlib.reload(logger)
        setting.log_path = log_path
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    controller = Controller(dump_path)
    if load_file:
        if not Path(load_file).exists(): raise FileExistsError(load_file)
        with open(load_file, 'rb') as f:
            controller.task_set = pickle.load(f)
            controller.task_list = list(controller.task_set.keys())
            controller.task_index = max(controller.task_list) + 1
        task_total = controller.task_index
        task_count = len(controller.task_list)
        logger.system(f'Load task file({load_file}) - task_total={task_total}  task_count={task_count}', 'Server')

    service_pb2_grpc.add_ControllerServicer_to_server(controller, server)
    if not server.add_insecure_port(f'{host}:{port}'):
        raise RuntimeError('Failed to add port to server.')
    logger.system(f'Start server({get_localhost()}:{port}) - dump_path={dump_path}  log_path={log_path}', 'Server')
    server.start()

    while not controller.is_quit:
        time.sleep(15)
    server.stop(0)
    logger.system('Server has logged out.', 'Server')
