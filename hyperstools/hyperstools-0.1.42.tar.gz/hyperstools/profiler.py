import functools
import builtins

try:
    from line_profiler import LineProfiler
except ImportError:
    print(
        """py3安装line_profiler
git clone https://github.com/rkern/line_profiler.git
cd line_profiler
python setup.py install
"""
    )
    raise


class Line_Profiler(object):
    """
    py3安装line_profiler
    git clone https://github.com/rkern/line_profiler.git
    cd line_profiler
    python setup.py install
 
    用法
    @profile()
    def func():
        pass
    """

    def __init__(self, follow=None):
        self.follow = follow or []

    def __call__(self, func):
        from line_profiler import LineProfiler

        def profiled_func(*args, **kwargs):

            line_profiler = LineProfiler()
            line_profiler.add_function(func)
            [line_profiler.add_function(x) for x in self.follow]
            line_profiler.enable_by_count()
            result = func(*args, **kwargs)
            line_profiler.disable_by_count()
            line_profiler.print_stats(stripzeros=True)
            return result

        return functools.wraps(func)(profiled_func)


builtins.profile = Line_Profiler
