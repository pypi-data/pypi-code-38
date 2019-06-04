#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
from _thread import start_new_thread

from Homevee.Helper import Logger


class Cronjob():
    '''
        task_name => the name of the task
    '''

    def __init__(self, task_name):
        self.task_name = task_name

        start_new_thread(self.start_task, ())

    def start_task(self):
        """
        Start the task to do
        :return:
        """
        while (True):
            start_time = time.time()
            self.task_to_do()
            end_time = time.time()
            execution_time = end_time - start_time
            seconds_to_wait = self.get_seconds_to_wait(execution_time)
            Logger.log("Running Cronjob: " + self.task_name +" in "+str(int(seconds_to_wait))+" seconds")
            time.sleep(seconds_to_wait)

    def task_to_do(self, *args):
        """
        Executes the task to do
        :param args: additional arguments
        :return:
        """
        raise NotImplementedError("This Method has to be overridden")

    def get_seconds_to_wait(self, execution_time=None) -> int:
        """
        Compute the number of seconds the cronjob has to wait before starting again
        :param execution_time: the time since the last execution
        :return: the number of seconds to wait
        """
        raise NotImplementedError("This Method has to be overridden")


class IntervalCronjob(Cronjob):
    '''
        interval_seconds => time in seconds to wait
        task_name => the name of the task
        wait_full_interval => waits the given time AFTER the task if true,
                                    subtracts the tasks execution time if false
    '''
    def __init__(self, task_name, interval_seconds, wait_full_interval=False):
        super(IntervalCronjob, self).__init__(task_name)
        self.interval_seconds = interval_seconds
        self.wait_full_interval = wait_full_interval

    def get_seconds_to_wait(self, execution_time=None):
        seconds_to_wait = self.interval_seconds

        if (not self.wait_full_interval):
            seconds_to_wait = seconds_to_wait - execution_time

        return seconds_to_wait


class FixedTimeCronjob(Cronjob):
    def __init__(self, task_name):
        super(FixedTimeCronjob, self).__init__(task_name)

    def start_task(self):
        while (True):
            seconds_to_wait = self.get_seconds_to_wait()

            Logger.log("Running Cronjob: " + self.task_name +" in "+str(int(seconds_to_wait))+" seconds")

            time.sleep(seconds_to_wait)

            self.task_to_do()

    def get_seconds_to_wait(self, execution_time=None):
        raise NotImplementedError("This Method has to be overridden")