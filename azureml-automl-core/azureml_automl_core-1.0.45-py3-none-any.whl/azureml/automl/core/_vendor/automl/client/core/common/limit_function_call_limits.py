"""Functionality to enforce limits on a process.

Adapted from https://github.com/sfalkner/pynisher
"""
from . import limit_function_call_exceptions as lfce


def set_limits(logger, mem_in_mb, num_procs, wall_time_limit_in_s,
               cpu_time_limit_in_s, grace_period_in_s):
    """Set the limits on the child process to enforce."""
    import resource
    import signal

    # TODO: Better error messages

    # simple signal handler to catch the signals for time limits
    def handler(signum, frame):
        # logs message with level debug on this logger
        logger.debug("signal handler: %i" % signum)
        if signum == signal.SIGXCPU:
            # when process reaches soft limit --> a SIGXCPU signal is
            # sent (it
            # normally terminats the process)
            raise lfce.CpuTimeoutException()
        elif signum == signal.SIGALRM:
            # SIGALRM is sent to process when the specified time limit to
            # an alarm function elapses (when real or clock time elapses)
            logger.debug("timeout")
            raise lfce.TimeoutException()
        raise lfce.SubprocessException('Uncaught signal: {} ({})'.format(signum, signal.Signals(signum).name))

    # catching all signals at this point turned out to interfere with the
    # subprocess (e.g. using ROS)
    signal.signal(signal.SIGALRM, handler)
    signal.signal(signal.SIGXCPU, handler)
    signal.signal(signal.SIGQUIT, handler)

    # code to catch EVERY catchable signal (even X11 related ones ... )
    # only use for debugging/testing as this seems to be too intrusive.
    """
    for i in [x for x in dir(signal) if x.startswith("SIG")]:
        try:
            signum = getattr(signal,i)
            print("register {}, {}".format(signum, i))
            signal.signal(signum, handler)
        except:
            print("Skipping %s"%i)
    """

    # set the memory limit
    if mem_in_mb is not None:
        # byte --> megabyte
        mem_in_b = mem_in_mb * 1024 * 1024
        # the maximum area (in bytes) of address space which may be taken
        # by the process.
        resource.setrlimit(resource.RLIMIT_AS, (mem_in_b, mem_in_b))

    # for now: don't allow the function to spawn subprocesses itself.
    # resource.setrlimit(resource.RLIMIT_NPROC, (1, 1)) Turns out, this is
    # quite restrictive, so we don't use this option by default
    if num_procs is not None:
        resource.setrlimit(resource.RLIMIT_NPROC, (num_procs, num_procs))

    # schedule an alarm in specified number of seconds
    if wall_time_limit_in_s is not None:
        signal.alarm(wall_time_limit_in_s)

    if cpu_time_limit_in_s is not None:
        # From the Linux man page: When the process reaches the soft
        # limit, it is sent a SIGXCPU signal. The default action for this
        # signal is to  terminate the process. However, the signal can
        # be caught, and the handler can return control to the main
        # program. If the process continues to consume CPU time, it will
        # be sent SIGXCPU once per second until the hard limit is
        # reached, at which time it is sent SIGKILL.
        resource.setrlimit(
            resource.RLIMIT_CPU, (cpu_time_limit_in_s,
                                  cpu_time_limit_in_s + grace_period_in_s))
