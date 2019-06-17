# coding=utf8

__author__ = 'Alexander.Li'

import sys
import os
import signal
import multiprocessing
import threading
import logging
import time
from errorbuster import formatError


class SingletonMixin(object):
    __singleton_lock = threading.Lock()
    __singleton_instance = None

    @classmethod
    def instance(cls):
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls()

        return cls.__singleton_instance


class LogicHolder(SingletonMixin):
    def __init__(self):
        self.worker = None
        self.dont_quit = True

    def regist(self, worker_func):
        self.worker = worker_func

    def run(self, message):
        self.worker(message)


class PollerHolder(SingletonMixin):
    def __init__(self):
        self.poller = None

    def regist(self, poll_object):
        self.poller = poll_object

    def poll(self, queue_name):
        return self.poller.poll(queue_name)


class Message(object):
    QUIT = 1
    MESSAGE = 2

    def __init__(self, cmd, message):
        self.cmd = cmd
        self.message = message


def worker_process(pid, pipe):
    logging.basicConfig(level=logging.INFO)
    def handle_signal(signal_num, frame):
        LogicHolder.instance().dont_quit = False

    signal.signal(signal.SIGTERM, handle_signal)
    logging.info('Worker Process(%s) ready to work', pid)

    while LogicHolder.instance().dont_quit:
        try:
            message = pipe.recv()
            if message.cmd == Message.QUIT:
                logging.info('Process(%s) will quit', pid)
                LogicHolder.instance().dont_quit = False
                continue
            if message.cmd == Message.MESSAGE:
                try:
                    LogicHolder.instance().run(message.message)
                except Exception as e:
                    logging.error(formatError(e))
        except KeyboardInterrupt:
            sys.exit(0)


def kill_all(_, __):
    os.killpg(os.getpgid(os.getpid()), signal.SIGKILL)


def master_process(queue_name, worker_number, stopwaits):
    logging.basicConfig(level=logging.INFO)
    processes = []
    pipes = []
    for pid in range(worker_number):
        slave_pipe, master_pipe = multiprocessing.Pipe(duplex=False)
        proc = multiprocessing.Process(target=worker_process, args=(pid, slave_pipe))
        proc.start()
        processes.append(proc)
        pipes.append(master_pipe)

    def handle_quit(signal_number, frame):
        if stopwaits:
            signal.alarm(stopwaits)
            signal.signal(signal.SIGALRM, kill_all)
        for pipe in pipes:
            pipe.send(Message(Message.QUIT, None)) # dispatch quit command
        logging.info('Waiting for all subprocess exit')
        for proc in processes:
            proc.join()
        logging.info('Every subprocess quited')
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_quit)
    signal.signal(signal.SIGINT, handle_quit)
    signal.signal(signal.SIGQUIT, handle_quit)

    execute_counter = 0
    running = True
    try:
        while running:
            try:
                message = PollerHolder.instance().poll(queue_name)
                if message:
                    pipe_idx = execute_counter % worker_number
                    pipe = pipes[pipe_idx]
                    pipe.send(Message(Message.MESSAGE, message))
            except BrokenPipeError:
                running = False
                continue
    except KeyboardInterrupt:
        handle_quit(0, None)










