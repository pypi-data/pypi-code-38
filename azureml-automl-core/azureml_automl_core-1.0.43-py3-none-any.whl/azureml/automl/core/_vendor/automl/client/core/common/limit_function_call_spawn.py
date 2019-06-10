"""
Limit function calls using spawn.

Limit function calls to specified resource constraints, but guarantees
the use of "spawn" instead of "fork" in order to be compatible with
libraries that aren't fork-safe (e.g. LightGBM).

Adapted from https://github.com/sfalkner/pynisher
"""
from typing import Any, Callable, Optional, Tuple
import logging
import subprocess
import time

from automl.client.core.common import limit_function_call_base as lfcb
from automl.client.core.common import limit_function_call_exceptions as lfce
from automl.client.core.common import limit_function_call_limits as lfcl
from automl.client.core.common import spawn_client
from automl.client.core.common.types import T
from automl.client.core.common import logging_utilities


class EnforceLimits(lfcb.EnforceLimitsBase):
    """Class to enforce resource limits using subprocess.Popen."""

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

        if self.log_function_parameters:
            self.logger.debug("Function called with argument: {}, {}".format(args, kwargs))

        # determine timeout
        timeout = None
        if self.wall_time_in_s:
            timeout = self.wall_time_in_s + self.grace_period_in_s

        # create and start the process
        start = time.time()
        try:
            res = spawn_client.run_in_proc(
                timeout,
                EnforceLimits.subprocess_func,
                args=(func,
                      self.mem_in_mb,
                      self.cpu_time_in_s,
                      self.wall_time_in_s,
                      self.num_processes,
                      self.grace_period_in_s) + args,
                **kwargs)

            # read the return value
            result, exit_status = res
        except subprocess.TimeoutExpired:
            exit_status = lfce.TimeoutException()
        except Exception as e:
            logging_utilities.log_traceback(
                e,
                self.logger
            )
            exit_status = e
        finally:
            wall_clock_time = time.time() - start

        return result, exit_status, wall_clock_time

    @staticmethod
    def subprocess_func(func, mem_in_mb, cpu_time_limit_in_s,
                        wall_time_limit_in_s, num_procs,
                        grace_period_in_s, *args, **kwargs):
        """
        Create the function the subprocess can execute.

        :param func: the function to enforce limit on
        :param mem_in_mb:
        :param cpu_time_limit_in_s:
        :param wall_time_limit_in_s:
        :param num_procs:
        :param grace_period_in_s:
        :param args: the args for the function
        :param kwargs: the kwargs for function
        :return:
        """
        logger = logging.Logger("spawn")

        lfcl.set_limits(logger, mem_in_mb, num_procs, wall_time_limit_in_s,
                        cpu_time_limit_in_s, grace_period_in_s)

        return lfcb.EnforceLimitsBase.call(func, logger, *args, **kwargs)
