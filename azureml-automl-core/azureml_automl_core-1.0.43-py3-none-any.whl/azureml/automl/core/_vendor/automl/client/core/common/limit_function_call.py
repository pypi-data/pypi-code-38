"""
Limit function calls to specified resource constraints.

Adapted from:
 https://github.com/sfalkner/pynisher
"""
from typing import Any, Callable, Optional, Tuple
import multiprocessing
import os
import sys
import time

from automl.client.core.common import killable_subprocess
from automl.client.core.common import limit_function_call_base as lfcb
from automl.client.core.common import limit_function_call_exceptions as lfce
from automl.client.core.common import limit_function_call_limits as lfcl
from automl.client.core.common.types import T
from automl.client.core.common import logging_utilities
from automl.client.core.common.exceptions import AutoMLException


class EnforceLimits(lfcb.EnforceLimitsBase):
    """Class to enforce resource limits using multiprocessing.Process."""

    def execute(self,
                func: 'Callable[..., Optional[Any]]',
                *args: Any,
                **kwargs: Any) -> Tuple[Optional[T], Optional[BaseException], float]:
        """
        Execute the function with the resource constraints applied.

        :param func: the function to execute
        :param args: list of positional args to pass to the function
        :param kwargs: list of keyword args to pass to the function
        :return: a value/error/execution time tuple
        """
        result = None

        # create a pipe to retrieve the return value
        parent_conn, child_conn = multiprocessing.Pipe()

        # create and start the process
        subproc = multiprocessing.Process(
            target=EnforceLimits.subprocess_func,
            name="pynisher function call",
            args=(func,
                  child_conn,
                  self.logger,
                  self.mem_in_mb,
                  self.cpu_time_in_s,
                  self.wall_time_in_s,
                  self.num_processes,
                  self.grace_period_in_s) + args,
            kwargs=kwargs)

        if self.log_function_parameters:
            self.logger.debug(
                "Function called with argument: {}, {}".format(
                    args, kwargs))

        # start the process

        start = time.time()
        subproc.start()
        child_conn.close()

        try:
            # read the return value
            if self.wall_time_in_s is not None:
                if parent_conn.poll(
                        self.wall_time_in_s +
                        self.grace_period_in_s):
                    result, exit_status = parent_conn.recv()
                else:
                    subproc.terminate()
                    exit_status = lfce.TimeoutException()

            else:
                result, exit_status = parent_conn.recv()

        except EOFError as e:
            # Don't see that in the unit tests :(
            error_msg = ("Your function call closed the pipe prematurely ->"
                         " Subprocess probably got an uncatchable signal.")
            exit_status = lfce.SubprocessException.from_exception(e, error_msg)
            logging_utilities.log_traceback(
                exit_status,
                self.logger
            )

        except Exception as e:
            logging_utilities.log_traceback(
                e,
                self.logger
            )
            exit_status = e
        finally:
            wall_clock_time = time.time() - start
            # don't leave zombies behind

            # subproc.join hangs in mac, due to empty queue
            # deadlock join with timeout doesn't work either,
            # so forcing terminate. finally is called only after
            # the timeout period
            if subproc.is_alive() and sys.platform == 'darwin':
                subproc.terminate()
            else:
                subproc.join()

        return result, exit_status, wall_clock_time

    @staticmethod
    def subprocess_func(func, pipe, logger, mem_in_mb, cpu_time_limit_in_s,
                        wall_time_limit_in_s, num_procs,
                        grace_period_in_s, *args, **kwargs):
        """
        Create the function the subprocess can execute.

        :param func: the function to enforce limit on
        :param pipe: the pipe to communicate the result
        :param logger:
        :param mem_in_mb:
        :param cpu_time_limit_in_s:
        :param wall_time_limit_in_s:
        :param num_procs:
        :param grace_period_in_s:
        :param args: the args fot the functiom
        :param kwargs: the kwargs for function
        :return:
        """
        lfcl.set_limits(logger, mem_in_mb, num_procs, wall_time_limit_in_s,
                        cpu_time_limit_in_s, grace_period_in_s)

        try:
            res = lfcb.EnforceLimitsBase.call(func, logger, *args, **kwargs)
            return res
        finally:
            try:
                logger.debug("return value: {}".format(res))

                pipe.send(res)
                pipe.close()

            except Exception:
                # this part should only fail if the parent process is already
                # dead, so there is not much to do anymore :)
                pass
            finally:
                # recursively kill all children
                pid = os.getpid()
                killable_subprocess.kill_process_tree_in_linux(pid)
