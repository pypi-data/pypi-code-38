# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Safe resource limits class for early termination.

Implementation of resource limits with fallback for systems
which do not support the python resource module.
"""
from typing import Any, Callable, Dict, Optional, Tuple
import logging
import sys
import time
import warnings
from automl.client.core.common.types import T

SIMPLE_PLATFORMS = {
    'linux': 'linux',
    'linux2': 'linux',
    'darwin': 'osx',
    'win32': 'win'
}

simple_platform = SIMPLE_PLATFORMS.get(sys.platform, 'unknown')

TIME_CONSTRAINT = 'wall_time_in_s'
TOTAL_TIME_CONSTRAINT = 'total_wall_time_in_s'
MEM_CONSTRAINT = 'mem_in_mb'
_ONE_WEEK_IN_SECONDS = 60 * 60 * 24 * 7
_TOTAL_TIME_MULTIPLIER = 52

DEFAULT_RESOURCE_LIMITS = {
    # note that this is approximate
    MEM_CONSTRAINT: None,
    # Use 1 week time out so that we dont interfere with user specified timeout
    # and dont cause errors for being too big
    TIME_CONSTRAINT: _ONE_WEEK_IN_SECONDS,
    # Use 1 year time out so that we dont interfere with user specified timeout.
    TOTAL_TIME_CONSTRAINT: _ONE_WEEK_IN_SECONDS * _TOTAL_TIME_MULTIPLIER,
    'cpu_time_in_s': None,
    'num_processes': None,
    'grace_period_in_s': None,
    'logger': None
}


# use this for module functions
class SafeEnforceLimits:
    """Class to allow for early termination of an execution."""

    try:
        import resource
        # see https://github.com/sfalkner/pynisher
        from automl.client.core.common import limit_function_call_spawn as pynisher_spawn
        from automl.client.core.common import limit_function_call as pynisher_sub
        ok = True
    except ImportError as e:
        # this is the error we're expecting
        assert str(e) == "No module named 'resource'"
        ok = False

    def get_param_str(self, params: Dict[str, Any]) -> str:
        """
        Combine the key-value in kwargs as a string.

        :param params:
        :return: str.
        """
        s = ""
        for k, v in params.items():
            s += k + "=" + str(v) + ", "
        return s

    def __init__(self,
                 *args: Any,
                 enable_limiting: bool = True,
                 run_as_spawn: bool = True,
                 **kwargs: Any):
        """
        Init the class.

        :param args:
        :param kwargs:
        """
        self.log = logging.getLogger(__name__)

        if SafeEnforceLimits.ok and enable_limiting:
            if run_as_spawn:
                pynisher_module = self.pynisher_spawn
            else:
                pynisher_module = self.pynisher_sub
            self.limiter = pynisher_module.EnforceLimits(*args, **kwargs)   # type: ignore
            self.log.info("Limits set to %s" % self.get_param_str(kwargs))
        else:
            # TODO Add the windows resource limit in core sdk
            # change the code to use the libray's resource enforcement.
            if not enable_limiting:
                self.log.info('Limiting disabled.')
            elif simple_platform != "win":
                self.log.warning("Unable to enforce resource limits.")
                warnings.warn("Unable to enforce resource limits.")
            self.limiter = None

        self.exit_status = None     # type: Optional[BaseException]
        self.wall_clock_time = 0    # type: float
        self.result = None          # type: Optional[Any]

    def wrap(self, func: 'Callable[..., Optional[Any]]') -> 'Callable[..., Optional[Any]]':
        """
        Wrap a function to limit its resource usage.

        :param func:
        :return:
        """
        if self.limiter is not None:
            def wrapped_limited(*args, **kwargs):
                # capture and log stdout, stderr
                # out, err = sys.stdout, sys.stderr
                # out_str, err_str = StringIO(), StringIO()
                # sys.stdout, sys.stderr = out_str, err_str

                self.result, self.exit_status, self.wall_clock_time = self.limiter.execute(func, *args, **kwargs)

                # out_str, err_str = out_str.getvalue(), err_str.getvalue()
                # if err_str != "": self.log.error(err_str)
                # if out_str != "": self.log.info(out_str)
                # sys.stdout, sys.stderr = out, err

                return self.result
            return wrapped_limited
        else:
            def wrapped(*args, **kwargs):
                start = time.time()
                try:
                    self.result = func(*args, **kwargs)
                except Exception as e:
                    self.exit_status = e
                finally:
                    self.wall_clock_time = time.time() - start
                return self.result
            return wrapped

    def __call__(self, func: 'Callable[..., Optional[Any]]') -> 'Callable[..., Optional[Any]]':
        """
        Decorate a function to limit its resource usage.

        :param func:
        :return:
        """
        return self.wrap(func)

    def execute(self,
                func: 'Callable[..., Optional[Any]]',
                *args: Any,
                **kwargs: Any) -> Tuple[Optional[T], Optional[BaseException], float]:
        """
        Execute function with limits.

        :param func:
        :param args:
        :param kwargs:
        :return:
        """
        wrapped_func = self.wrap(func)
        wrapped_func(*args, **kwargs)
        return self.result, self.exit_status, self.wall_clock_time
