"""
Limit function calls to specified resource constraints.

Limit function calls to specified resource constraints, but guarantees
the use of "spawn" instead of "fork" in order to be compatible with
libraries that aren't fork-safe (e.g. LightGBM).

Adapted from https://github.com/sfalkner/pynisher
"""
from typing import Any, Callable, Optional, Tuple
from abc import abstractmethod
import errno
import logging
import multiprocessing
import os

from . import limit_function_call_exceptions as lfce
from . import logging_utilities
from .exceptions import AutoMLException
from .types import T


class EnforceLimitsBase:
    """Base class to enforce resource limits on Linux."""

    def __init__(self,
                 mem_in_mb: Optional[int] = None,
                 cpu_time_in_s: Optional[int] = None,
                 wall_time_in_s: Optional[int] = None,
                 num_processes: Optional[int] = None,
                 grace_period_in_s: Optional[int] = None,
                 logger: Optional[logging.Logger] = None,
                 log_function_parameters: bool = False,
                 total_wall_time_in_s: Optional[int] = None) -> None:
        """
        Resource limit to be enforced.

        :param mem_in_mb:
        :param cpu_time_in_s:
        :param wall_time_in_s:
        :param num_processes:
        :param grace_period_in_s:
        :param logger:
        :param log_function_parameters:
        :param total_wall_time_in_s: unused now but used to limit the entire run
        """
        self.mem_in_mb = mem_in_mb
        self.cpu_time_in_s = cpu_time_in_s
        self.num_processes = num_processes

        if total_wall_time_in_s is None:
            self.wall_time_in_s = wall_time_in_s
        elif wall_time_in_s is None:
            self.wall_time_in_s = total_wall_time_in_s
        else:
            self.wall_time_in_s = min(wall_time_in_s, total_wall_time_in_s)

        self.grace_period_in_s = (0 if grace_period_in_s is None else grace_period_in_s)
        self.logger = (
            logger if logger is not None else multiprocessing.get_logger())
        self.log_function_parameters = log_function_parameters

        if self.mem_in_mb is not None:
            self.logger.debug(
                "Restricting your function to {} mb memory."
                .format(self.mem_in_mb))
        if self.cpu_time_in_s is not None:
            self.logger.debug(
                "Restricting your function to {} seconds cpu time."
                .format(self.cpu_time_in_s))
        if self.wall_time_in_s is not None:
            self.logger.debug(
                "Restricting your function to {} seconds wall time."
                .format(self.wall_time_in_s))
        if self.num_processes is not None:
            self.logger.debug(
                "Restricting your function to {} threads/processes."
                .format(self.num_processes))
        if self.grace_period_in_s is not None:
            self.logger.debug(
                "Allowing a grace period of {} seconds."
                .format(self.grace_period_in_s))

    @abstractmethod
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
        raise NotImplementedError

    @staticmethod
    def call(func: 'Callable[..., Optional[Any]]',
             logger: logging.Logger,
             *args: Any,
             **kwargs: Any) -> Tuple[Optional[Any], Optional[BaseException]]:
        """
        Execute the function with the supplied arguments.

        :param func: the function to execute
        :param logger: the logger to log debug information
        :param args: list of positional args to pass to the function
        :param kwargs: list of keyword args to pass to the function
        :return: a value/error tuple
        """
        try:
            logger.debug("call function")
            res = (func(*args, **kwargs), None)     # type: Tuple[Optional[Any], Optional[BaseException]]
            logger.debug("function returned properly: {}".format(res))
        except lfce.CpuTimeoutException as e:
            res = (None, e)
        except lfce.TimeoutException as e:
            res = (None, e)
        except MemoryError:
            res = (None, lfce.MemorylimitException())
        except OSError as e:
            msg = '[OSError {} ({})] {}'.format(e.errno,
                                                errno.errorcode.get(e.errno, 'Unknown'),
                                                os.strerror(e.errno))
            res = (None, lfce.SubprocessException(msg))
        except Exception as e:
            res = (None, e)
            logging_utilities.log_traceback(
                e,
                logger
            )

        return res
