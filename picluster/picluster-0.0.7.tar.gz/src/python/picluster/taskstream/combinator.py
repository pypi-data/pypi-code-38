import typing

# from .primitive import func
from functools import reduce

import rx
import datetime
from rx import merge
from rx import operators as ops


def func(fn):
    """
    Turn a function to Observable.
    """
    return rx.create(fn)


def parallel(tasks: typing.Sequence[func]):
    """
    wrap of rx operators merge
    Usage: parallel([task_1, task_2...])
    """
    return merge(*tasks)


def sequential(seq: "List[submit]"):
    """
    usage:
    sequential([submit_task_1, submit_task_2])
    """
    return reduce(lambda prev, nxt: prev.pipe(ops.flat_map(nxt)), seq)


# def concate(l: "List[Observable]"):
#     """
#     Convert list of observables to a sequential task queue.
#
#     :param l: List of Observables.
#     :return: Observable that chains input together.
#     """
#     if len(l) == 1:
#         return l[0]
#     elif len(l) > 1:
#         result = l[0]
#         for obs in l[1:]:
#             result = result.pipe(ops.last(), ops.flat_map(lambda _: obs))
#         return result
#     else:
#         raise ValueError("Input of concate is supposed to be a list of observables.")


def parallel_with_error_detect(tasks, rate_of_tolerance=3):
    """
    Throw timeout if one or more observed tasks runs for a ratio * mean_time_of(80% tasks)
    """

    num_tasks = len(tasks)

    def _get_time_used(
        task_tuple: "(Datetime(start), Timestamp(value=[], timestamp=current))"
    ):
        return tuple((task_tuple[1].value, task_tuple[1].timestamp - task_tuple[0]))

    def _tuple_acc(acc, x):
        t_0 = acc[0] + x[0]
        acc[1].append(x[1])
        return tuple((t_0, acc[1]))

    def _task_with_avg_time_with_tolerance(
        task_tuple: "(List[Output], List[datetime.timedelta])"
    ):
        outputs = task_tuple[0]
        time_consumed = task_tuple[1]

        sum_task_tuple = reduce(lambda x, y: x + y, time_consumed)
        num_of_tasks = len(time_consumed)
        avg_time_with_tolerance = (sum_task_tuple / num_of_tasks) * rate_of_tolerance
        return tuple((outputs, avg_time_with_tolerance))

    start_time = rx.from_callable(datetime.datetime.now)
    tasks_with_time_stamp = rx.merge(*[t.pipe(ops.timestamp()) for t in tasks])

    output_with_time = rx.combine_latest(start_time, tasks_with_time_stamp).pipe(
        ops.map(_get_time_used), ops.scan(_tuple_acc, ([], []))
    )

    _outputs_with_time_of_tolerance_on_majority_completed = output_with_time.pipe(
        ops.filter(lambda t: len(t[1]) > num_tasks * 0.8),
        ops.map(_task_with_avg_time_with_tolerance),
    ).pipe(ops.share())

    _time_of_tolerance_on_majority_completed = _outputs_with_time_of_tolerance_on_majority_completed.pipe(
        ops.map(lambda t: t[1]),
        ops.take(1),
        ops.flat_map(
            lambda time_of_tolerance: rx.Observable().pipe(
                ops.timeout(time_of_tolerance)
            )
        ),
    )

    _outputs_of_tolerance_on_majority_completed = _outputs_with_time_of_tolerance_on_majority_completed.pipe(
        ops.map(lambda t: t[0]), ops.last()
    )

    _outputs_with_timeout = rx.amb(
        _time_of_tolerance_on_majority_completed,
        _outputs_of_tolerance_on_majority_completed,
    )

    return _outputs_with_timeout
