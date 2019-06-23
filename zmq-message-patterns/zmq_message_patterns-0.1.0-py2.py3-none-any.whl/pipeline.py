# -*- coding: utf-8 -*-

# TODO: module description
# TODO: copyright notice

import zmq

from .zmessage import ZMessage
from .znode import ZNode


try:
    from typing import Any, Dict, Iterator, List, Optional, Type, TypeVar
    VentilatorWorkerMessageType = TypeVar('VentilatorWorkerMessageType', bound='VentilatorToWorkerMessage')
    WorkerSinkMessageType = TypeVar('WorkerSinkMessageType', bound='WorkerToSinkMessage')
except ImportError:
    pass


class SinkToWorkerMessage(ZMessage):
    types = ('shutdown',)


class VentilatorToWorkerMessage(ZMessage):
    pass


class VentilatorToSinkMessage(ZMessage):
    types = ('ventilator job', 'finished')
    required_data = ('request_id',)


class WorkerToSinkMessage(ZMessage):
    types = ('job done',)
    required_data = ('ventilator_request_id',)


class Sink(ZNode):
    """
    Receive messages from workers and job IDs from ventilator:

    Subclass and implement :py:meth:`handle_result()`.
    """
    def __init__(self, worker_results_addr, worker_control_addr, job_ids_to_sink_addr):  # type: (str, str, str) -> None
        super(Sink, self).__init__()
        self.unfinished_request_ids = []  # type: List[str]
        self.unknown_ventilator_request_ids = []  # type: List[str]
        self.add_socket('worker_results', 'bind', 'PULL', worker_results_addr)
        self.add_socket('worker_control', 'bind', 'PUB', worker_control_addr)
        self.add_socket('job_ids_to_sink', 'connect', 'PULL', job_ids_to_sink_addr)
        self.poller = None  # type: zmq.Poller

    def init(self, install_sig_handler=True):  # type: (Optional[bool]) -> None
        super(Sink, self).init(install_sig_handler)
        self.poller = zmq.Poller()
        self.poller.register(self.sockets['worker_results'], zmq.POLLIN)
        self.poller.register(self.sockets['job_ids_to_sink'], zmq.POLLIN)

    def cleanup(self):
        if self.unknown_ventilator_request_ids:
            self.logger.warning(
                'Received %f results from workers that could not be matched to requests sent by ventilator: %r',
                len(self.unknown_ventilator_request_ids),
                self.unknown_ventilator_request_ids
            )
        if self.unfinished_request_ids:
            self.logger.error('Missing %d results: %r', len(self.unfinished_request_ids), self.unfinished_request_ids)
        super(Sink, self).cleanup()

    def handle_result(self, request):  # type: (WorkerSinkMessageType) -> None
        raise NotImplemented()

    def run(self, *args, **kwargs):  # type: (*Any, **Any) -> Any
        ventilator_finished = False
        while True:
            polled = self.poller.poll()
            socks = dict(polled)

            if self.sockets['job_ids_to_sink'] in socks:
                request_v = self.receive('job_ids_to_sink', VentilatorToSinkMessage)  # type: VentilatorToSinkMessage
                if request_v.type == 'ventilator job':
                    request_id = request_v['request_id']
                    try:
                        # worker finished before ventilator message was received by sink
                        self.unknown_ventilator_request_ids.remove(request_id)
                    except ValueError:
                        self.unfinished_request_ids.append(request_id)
                elif request_v.type == 'finished':
                    ventilator_finished = True

            if self.sockets['worker_results'] in socks:
                request_w = self.receive('worker_results', WorkerToSinkMessage)  # type: WorkerSinkMessageType
                try:
                    self.unfinished_request_ids.remove(request_w['ventilator_request_id'])
                    self.handle_result(request_w)
                except ValueError:
                    self.unknown_ventilator_request_ids.append(request_w['ventilator_request_id'])

                if ventilator_finished and not self.unfinished_request_ids:
                    if self.unknown_ventilator_request_ids:
                        self.logger.error(
                            '[%s] Received worker message(s) with unknown ventilator_request_id: %r.',
                            self.name, request_w['ventilator_request_id']
                        )

                    self.logger.debug('[%s] Workers finished all jobs, telling them to shut down.', self.name)
                    # self.send('worker_control', SinkToWorkerMessage('shutdown'))
                    self.sockets['worker_control'].send_string('shutdown')
                    self.messages_sent_count['shutdown'] += 1
                    break


class Ventilator(ZNode):
    """
    Sends messages to workers and sink:

    * a VentilatorToWorkerMessage with a job to workers (socket `jobs_to_workers`)
    * a VentilatorToSinkMessage with the ID of the VentilatorToWorkerMessage to the sink (socket `job_ids_to_sink`)
    * a VentilatorToSinkMessage with type `finished` to the sink, once all jobs and job IDs have been sent

    Subclass and implement :py:meth:`requests()`.
    """
    def __init__(self, jobs_to_workers_addr, job_ids_to_sink_addr, jobs_in_hwm=None):
        # type: (str, str, Optional[bool]) -> None
        """
        :param str jobs_to_workers_addr: address to bind to, workers will connect to this (e.g. `tcp://*:5555`)
        :param str job_ids_to_sink_addr: address to bind to, sink will connect to this (e.g. `tcp://*:5556`)
        """
        super(Ventilator, self).__init__()
        if jobs_in_hwm:
            jobs_in_kwargs = dict(rcvhwm=jobs_in_hwm, sndhwm=jobs_in_hwm)
        else:
            jobs_in_kwargs = {}
        self.add_socket('jobs_to_workers', 'bind', 'PUSH', jobs_to_workers_addr, **jobs_in_kwargs)
        self.add_socket('job_ids_to_sink', 'bind', 'PUSH', job_ids_to_sink_addr)

    def requests(self):  # type: () -> Iterator[VentilatorWorkerMessageType]
        """Iterator that yields VentilatorToWorkerMessage objects"""
        raise NotImplemented()

    def run(self, *args, **kwargs):  # type: (*Any, **Any) -> None
        assert 'job_ids_to_sink' in self.sockets
        assert 'jobs_to_workers' in self.sockets

        for request in self.requests():
            self.send_job(request)
        self.send_finished()

    def send_job(self, request):
        request_s = VentilatorToSinkMessage('ventilator job', request_id=request.id)
        self.send('job_ids_to_sink', request_s)
        self.send('jobs_to_workers', request)

    def send_finished(self):
        request_s = VentilatorToSinkMessage('finished', request_id=0)
        self.send('job_ids_to_sink', request_s)


class Worker(ZNode):
    """
    Set VentilatorWorkerMessageCls to your subclass of VentilatorToWorkerMessage.
    """
    VentilatorWorkerMessageCls = VentilatorToWorkerMessage  # type: VentilatorWorkerMessageType

    def __init__(self, jobs_in_addr, worker_control_addr, results_out_addr, jobs_in_hwm=None):
        # type: (str, str, str, Optional[int]) -> None
        """HWM limiting is not stable."""
        super(Worker, self).__init__()
        if jobs_in_hwm:
            jobs_in_kwargs = dict(rcvhwm=jobs_in_hwm, sndhwm=jobs_in_hwm)
        else:
            jobs_in_kwargs = {}
        self.add_socket('jobs_in', 'connect', 'PULL', jobs_in_addr, **jobs_in_kwargs)
        self.add_socket('worker_control', 'connect', 'SUB', worker_control_addr)
        self.add_socket('results_out', 'connect', 'PUSH', results_out_addr)
        self.poller = None  # type: zmq.Poller

    def init(self, install_sig_handler=True):  # type: (Optional[bool]) -> None
        super(Worker, self).init(install_sig_handler)
        self.poller = zmq.Poller()
        self.poller.register(self.sockets['jobs_in'], zmq.POLLIN)
        self.poller.register(self.sockets['worker_control'], zmq.POLLIN)
        self.sockets['worker_control'].setsockopt_string(zmq.SUBSCRIBE, u'shutdown')

    def do_work(self, request):  # type: (VentilatorWorkerMessageType) -> WorkerSinkMessageType
        """
        Do the work.

        :param VentilatorToWorkerMessage request: the ventilators request
        :return: message to send to sink
        :rtype: WorkerToSinkMessage
        """
        raise NotImplemented()

    def run(self, *args, **kwargs):  # type: (*Any, **Any) -> None
        while True:
            polled = self.poller.poll()
            socks = dict(polled)

            if self.sockets['jobs_in'] in socks:
                request = self.receive('jobs_in', self.VentilatorWorkerMessageCls)  # type: VentilatorWorkerMessageType
                result = self.do_work(request)
                self.send('results_out', result)

            if self.sockets['worker_control'] in socks:
                worker_control_string = self.sockets['worker_control'].recv_string()
                if worker_control_string == 'shutdown':
                    break


if __name__ == "__main__":
    import doctest
    doctest.testmod()
