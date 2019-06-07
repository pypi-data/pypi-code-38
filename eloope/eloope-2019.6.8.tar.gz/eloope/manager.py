from . import service_pb2, service_pb2_grpc
from multiprocessing import Process
from types import MethodType
from .engine import Engine
from . import setting
from . import logger
import pickle
import gevent
import grpc
import time


class Manager:
    def __init__(self, engine_names=None, host='localhost', port=6991):
        if engine_names is None:
            engine_names = []
        self._tasks = []
        self._engines = []
        self._is_run = False
        self._host = host
        self._port = port
        self.create_engines(engine_names)

    def create_engines(self, engine_names, size=50):
        assert not self._is_run, 'Manager object is already running.'
        for name in engine_names:
            engine = Engine(name, size)
            engine.add_task(_send_status, engine)
            self._engines.append(engine)

    def add_task(self, fn, *params):
        assert not self._is_run, 'Manager object is already running.'
        self._tasks.append((fn, *params))

    def add_tasks(self, fn, param_groups):
        for param in param_groups:
            self.add_task(fn, *param if isinstance(param, (tuple, list)) else param)

    def run(self):
        assert not self._is_run, 'Manager object is already running.'
        assert self._engines, 'No Engine object added.'
        channel = grpc.insecure_channel(f'{self._host}:{self._port}')
        stub = service_pb2_grpc.ControllerStub(channel)
        # Push initial tasks
        try:
            tasks = pickle.dumps([pickle.dumps(t) for t in self._tasks])
            stub.SendStatus(service_pb2.SendStatusRequest(tasks=tasks, free_count=0, completed_tasks=pickle.dumps([]),
                                                          logs=pickle.dumps([])))
            self._tasks = []
        except grpc.RpcError:
            raise ConnectionError('Connect Failed.')
        # Create process
        for engine in self._engines:
            Process(target=_create_process, args=(engine, self._host, self._port)).start()


def _add_task(self, fn, *params, is_put=True):
    self.task_queue.append((fn, *params)) if is_put else self._task_pool.spawn(fn, *params)


def _create_process(engine, host, port):
    channel = grpc.insecure_channel(f'{host}:{port}')
    logger._is_client = True
    engine.stub = service_pb2_grpc.ControllerStub(channel)
    engine.task_queue = []
    engine.completed_tasks = []
    engine.add_task = MethodType(_add_task, engine)
    logger.system('Create process', engine.name)
    engine.run()


def _package_task(engine, code, fn, *params):
    fn(*params)
    engine.completed_tasks.append(code)


def _send_status(engine):
    repeat_count = 0
    while True:
        # Upload tasks
        try:
            logger.info(f'task_count= {engine.task_count - 1}')
            tasks = pickle.dumps([pickle.dumps(t) for t in engine.task_queue])
            logs = pickle.dumps(logger.log_list)
            resp = engine.stub.SendStatus(service_pb2.SendStatusRequest(
                tasks=tasks, free_count=engine.free_count, logs=logs,
                completed_tasks=pickle.dumps(engine.completed_tasks)))
            engine.task_queue = []
            logger.log_list = []
            engine.completed_tasks = []
            if resp.command == 'add':
                # Download tasks
                for code, task in pickle.loads(resp.tasks):
                    engine.add_task(_package_task, engine, code, *pickle.loads(task), is_put=False)
            elif resp.command == 'quit':
                gevent.killall(engine.task_pool)
                break
        except grpc.RpcError:
            # Connection interrupt
            if engine.task_count == 1:
                if setting.connection_interrupt_callback(engine, repeat_count): repeat_count += 1
                else: break
        # Request_interval
        time.sleep(setting.send_interval) if engine.task_count == 1 else gevent.sleep(setting.send_interval)
