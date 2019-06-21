'''
:File: _zmq_pair.py
:Author: Jayesh Joshi
:Email: jayeshjo1@utexas.edu

Wrapper around the ZMQ class used by client and server to communicate.

Built on the principle of ISRs -- IO requests should be handled in the
background when the main thread is not busy. Main thread can then poll the
background thread to check to see if there are any updates. This allows the main
thread to run foreground activities and check the connection whenever desired
for any updates.
'''

import zmq
import time
from threading import Thread, local, main_thread
from queue import Queue

from ._msg import MSG, MSGType
from ._decorators import timeout
from ._general import logger
from .exceptions import ZMQPairTimeout


_ctx = local()


class ZMQPair(object):
    def __init__(self, dest_ip=None, port=9922):
        self._context = _get_context()
        self._socket = self._context.socket(zmq.PAIR)
        self._socket.setsockopt(zmq.LINGER, 0)
        self._dest_ip = dest_ip
        self._port = port
        self._connected = False
        self.__queue = Queue()
        self.__msg_backlog = {}
        self.__bg_worker = Thread(target=ZMQPair.__bg_receiver, args=(self.__queue, self._socket))
        self.__bg_worker.start()

    @property
    def context(self):
        return self._context

    @property
    def socket(self):
        return self._socket

    @property
    def dest_ip(self):
        return self._dest_ip

    @property
    def port(self):
        return self._port

    @property
    def connected(self):
        return self._connected

    def close(self):
        if(self._connected and self._dest_ip):
            self.disconnect()
        self._socket.close()

    def bind(self):
        self._connected = self.__heartbeat(0.1)
        if(not(self._connected)):
            self._socket.bind("tcp://*:{}".format(self._port))
            self._connected = True

    def unbind(self):
        if(self._connected):
            self._socket.unbind()
            self._connected = False

    def connect(self):
        self._connected = self.__heartbeat(0.1)
        if(not(self._connected)):
            self._socket.connect("tcp://{}:{}".format(self._dest_ip, self._port))
            self._connected = True
            logger.debug("Main:: Connected: {}:{}".format(self._dest_ip, self._port))

    def disconnect(self):
        self._socket.disconnect("tcp://{}:{}".format(self._dest_ip, self._port))
        self._connected = False
        logger.debug("Main:: Disconnect: {}:{}".format(self._dest_ip, self._port))
        self.__msg_backlog.clear()

    def send_msg(self, msg, timeout=None):
        assert type(msg) == MSG, "ZMQPair only communicates through MSG class"
        if(self._connected):
            logger.debug("Main:: Sending Message {}".format(str(msg)))
            self.__send_process(msg, timeout=timeout, exception=ZMQPairTimeout)
            return True
        else:
            return False

    def recv_msg(self, timeout=None, msg_id=None):
        if(msg_id is not None and msg_id in self.__msg_backlog and self.__msg_backlog[msg_id]):
            return self.__msg_backlog[msg_id].pop(0)
        self.__check_mail(timeout=timeout, exception=ZMQPairTimeout)
        mail = self.__queue.get(timeout=10)
        logger.debug("Main:: Retrieved Message: {}".format(str(mail)))
        return mail

    def requeue_msg(self, msg):
        if(not(msg.type == MSGType.ACKNOWLEDGE) and msg.has_request_id()):
            self.__msg_backlog.setdefault(msg.request_id, list()).append(msg)
            logger.debug("Putting MSG to backlog {}".format(msg))
        else:
            self.__queue.put(msg)

    def pulse(self, timeout=None):
        return self.__heartbeat(timeout=timeout)

    @timeout(name="Trasmitter")
    def __send_process(self, msg, **kwargs):
        tracker = self._socket.send_pyobj(msg, flags=zmq.NOBLOCK, track=True, copy=False)
        while(not(tracker.done)):
            yield None

    @timeout(name="Receiver")
    def __check_mail(self, **kwargs):
        if(self.__bg_worker.is_alive()):
            while(self.__queue.empty()):
                yield None
        else:
            raise RuntimeError("Recv thread died?")

    def __heartbeat(self, timeout):
        if(self._connected):
            self.send_msg(MSG(MSGType.HEARTBEAT, request=True), timeout=timeout)
            try:
                while(True):
                    msg = self.recv_msg(timeout=timeout)
                    if(msg.type == MSGType.HEARTBEAT):
                        return True
                    else:
                        self.requeue_msg(msg)
                    time.sleep(0)
            except ZMQPairTimeout:
                return False
        else:
            return False

    def __bg_receiver(queue, socket):
        logger.debug("Thread:: Starting")
        try:
            while(True):
                while(not(socket.poll(timeout=0.001, flags=zmq.POLLIN))):
                    time.sleep(0)
                    if(not(main_thread().is_alive())):
                        return
                msg = socket.recv_pyobj()
                if(msg.type == MSGType.ACKNOWLEDGE and msg.request_id == 0):  # if server reset, clear out older msgs
                    queue_return = []
                    while(not(queue.empty())):
                        msg = queue.get()
                        if(msg.type == MSGType.HEARTBEAT or msg.type == MSGType.SYNC):
                            queue_return.append(msg)
                    while(queue_return):
                        queue.put(queue_return.pop(0))
                logger.debug("Thread:: {}".format(str(msg)))
                if(msg.request and msg.type == MSGType.HEARTBEAT):
                    socket.send_pyobj(MSG(MSGType.HEARTBEAT, request=False))
                else:
                    queue.put(msg)
                time.sleep(0)
        except (zmq.ZMQError, zmq.Again):
            pass


def _get_context():
    try:
        return getattr(_ctx, "zmq_context")
    except (AttributeError, IndexError):
        _ctx.__dict__["zmq_context"] = zmq.Context()
        return _ctx.zmq_context


def _close_context():
    try:
        getattr(_ctx, "zmq_context").term()
    except (AttributeError, IndexError):
        pass  # No need to close context?
