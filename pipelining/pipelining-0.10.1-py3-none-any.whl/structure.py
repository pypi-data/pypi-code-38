from typing import Union
import signal
import logging
from threading import Thread
from multiprocessing import managers, Manager, Process, Event
from multiprocessing.queues import JoinableQueue
from time import time, sleep
import abc

DEFAULT_TICK_SLEEP = 1

class WorkUnit():
    def __init__(self, id: str=None, payload=None, type: str = None):
        self.id = id
        self.payload = payload
        self.type = type
        self.creation_ts = time()


class PipeStage(Process):
    def __init__(self, name: str, work_threads=1, tick_sleep=None):
        super().__init__(name=name)
        self._shared_state: dict = None
        self._stopped_event: Event = None
        self._tick_sleep = tick_sleep or DEFAULT_TICK_SLEEP
        self.__work_threads = work_threads
        self.__work_counter = 0

    def __tick(self):
        self._will_tick()
        wps = self.__work_counter / self._tick_sleep
        self._shared_state[f'{self.name}_wps'] = wps
        self.__work_counter = 0

    def __tick_until_stopped(self):
        while not self._stopped_event.is_set():
            self.__tick()    
            sleep(self._tick_sleep)

    def __start_work(self):
        for _ in range(self.__work_threads):
            thread = Thread(target=self._work)
            thread.daemon = True
            thread.start()

    def join_pipeline(self, state: managers.DictProxy, stopped: Event):
        self._shared_state = state
        self._stopped_event = stopped

    @abc.abstractmethod
    def _will_tick(self):
        pass

    @abc.abstractmethod
    def _will_start(self):
        pass

    @abc.abstractmethod
    def _will_stop(self):
        pass

    @abc.abstractmethod
    def _work(self):
        pass

    def _work_done(self):
        self.__work_counter += 1

    def _should_work(self):
        return not self._stopped_event.is_set()

    @abc.abstractmethod
    def ports(self):
        pass

    def run(self):
        try:
            self._will_start()
            self.__start_work()
            self.__tick_until_stopped()
            self._will_stop()
        except KeyboardInterrupt:
            self._will_stop()    

class OutputPort():
    def __init__(self, name: str, owner: PipeStage):
        self.name = name
        self.direction = "OUTPUT"
        self.owner = owner
        self.__queue = None

    def connect_to(self, queue: 'PipeQueue'):
        if self.__queue:
            raise Exception("port already connected")
        self.__queue = queue
        queue.track_producer(self)

    def put(self, work: WorkUnit):
        if not self.__queue:
            raise Exception("port not connected")
        self.__queue.put(work)

class InputPort():
    def __init__(self, name: str, owner: PipeStage):
        self.name = name
        self.direction = "INPUT"
        self.owner = owner
        self.queue = None

    def __safe_get_queue(self):
        if not self.queue:
            raise Exception("port not connected")
        return self.queue

    def connect_to(self, queue: 'PipeQueue'):
        if self.queue:
            raise Exception("port already connected")
        self.queue = queue
        queue.track_consumer(self)

    def get(self, block: bool=True, timeout: int=None):
        queue = self.__safe_get_queue()
        return queue.get(block=block, timeout=timeout)

    def get_or_continue(self):
        queue = self.__safe_get_queue()
        if not queue.empty():
            return queue.get_nowait()
        return None

    def yield_until_empty(self):
        queue = self.__safe_get_queue()
        while not queue.empty():
            yield queue.get_nowait()

    def drop_all_but_last(self):
        queue = self.__safe_get_queue()
        while queue.qsize() > 1:
            queue.get(timeout=.1)
            queue.task_done()
        return queue.get()

    def qsize(self):
        queue = self.__safe_get_queue()
        return queue.qsize()

    def task_done(self):
        queue = self.__safe_get_queue()
        queue.task_done()

AnyPort = Union[InputPort, OutputPort]

class PipeQueue(JoinableQueue):
    def __init__(self, name: str, ctx, maxsize: int=None):
        super().__init__(ctx=ctx, maxsize=maxsize)
        self.name = name
        self.producers = []
        self.consumers = []
    
    def track_producer(self, port: OutputPort):
        self.producers.append(port)

    def track_consumer(self, port: InputPort):
        self.consumers.append(port)


class Pipeline():
    def __init__(self):
        self.__ctx = managers.get_context()
        self.__manager = Manager()
        self.__stopped = Event()
        self.shared_state = self.__manager.dict()
        self.stages = {}
        self.queues = {}
        self.start_ts = None

    def add_stage(self, stage: PipeStage):
        stage.join_pipeline(self.shared_state, self.__stopped)
        self.stages[stage.name] = stage

    def add_pipe(self, name: str, maxsize=10000):
        queue = PipeQueue(name=name, ctx=self.__ctx, maxsize=maxsize)
        self.queues[name] = queue
        return queue

    def start(self):
        self.start_ts = time()
        for name, stage in self.stages.items():
            logging.debug(f"starting stage {name}")
            stage.start()

    def stop(self):
        self.__stopped.set()

    def join(self):
        for name, stage in self.stages.items():
            logging.debug(f"joining stage {name}")
            stage.join()

    def terminate(self):
        for name, stage in self.stages.items():
            logging.debug(f"terminating stage {name}")
            stage.terminate()
