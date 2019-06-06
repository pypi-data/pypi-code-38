import os
from tqdm import tqdm
from .area import WorkingArea
from .submitter import SGETaskSubmitter, MPTaskSubmitter
from .monitor import JobMonitor

def validate_tasks(tasks):
    for task in tasks:
        if any(key not in task for key in ("task", "args", "kwargs")):
            return False
        if not callable(task["task"]):
            return False
    return True

def sge_submit(
    name, path, tasks=[], options="-q hep.q", dryrun=False, quiet=False,
    sleep=5, request_resubmission_options=True,
):
    if not validate_tasks(tasks):
        logger.error(
            "Invalid tasks. Ensure tasks=[{'task': .., 'args': [..], "
            "'kwargs': {..}}, ...], where 'task' is callable."
        )
        return []
    area = WorkingArea(os.path.abspath(path))
    submitter = SGETaskSubmitter(" ".join(['-N {}'.format(name), options]))
    monitor = JobMonitor(submitter)

    results = []
    area.create_areas(tasks, quiet=quiet)
    try:
        submitter.submit_tasks(area.task_paths, dryrun=dryrun, quiet=quiet)
        if not dryrun:
            results = monitor.monitor_jobs(
                sleep=sleep, request_user_input=request_resubmission_options,
            )
    except KeyboardInterrupt as e:
        submitter.killall()
    return results

def sge_submit_yield(
    name, path, tasks=[], options="-q hep.q", quiet=False, sleep=5,
    request_resubmission_options=True,
):
    if not validate_tasks(tasks):
        logger.error(
            "Invalid tasks. Ensure tasks=[{'task': .., 'args': [..], "
            "'kwargs': {..}}, ...], where 'task' is callable."
        )
        return []
    area = WorkingArea(os.path.abspath(path))
    submitter = SGETaskSubmitter(" ".join(['-N {}'.format(name), options]))
    monitor = JobMonitor(submitter)

    area.create_areas(tasks, quiet=quiet)
    submitter.submit_tasks(area.task_paths, quiet=quiet)
    return monitor.request_jobs(
        sleep=sleep, request_user_input=request_resubmission_options,
    )

def sge_resume(
    name, path, options="-q hep.q", quiet=False, sleep=5,
    request_resubmission_options=True,
):
    area = WorkingArea(os.path.abspath(path), resume=True)
    submitter = SGETaskSubmitter(" ".join(['-N {}'.format(name), options]))
    for idx in range(len(area.task_paths)):
        submitter.jobid_tasks['{}'.format(idx)] = area.task_paths[idx]
    monitor = JobMonitor(submitter)

    results = []
    try:
        results = monitor.monitor_jobs(
            sleep=sleep, request_user_input=request_resubmission_options,
        )
    except KeyboardInterrupt as e:
        submitter.killall()
    return results

def mp_submit(tasks, ncores=4, quiet=False):
    if not validate_tasks(tasks):
        logger.error(
            "Invalid tasks. Ensure tasks=[{'task': .., 'args': [..], "
            "'kwargs': {..}}, ...], where 'task' is callable."
        )
        return []
    submitter = MPTaskSubmitter()
    return submitter.submit_tasks(tasks, ncores=ncores, quiet=quiet)

def local_submit(tasks, quiet=False):
    if not validate_tasks(tasks):
        logger.error(
            "Invalid tasks. Ensure tasks=[{'task': .., 'args': [..], "
            "'kwargs': {..}}, ...], where 'task' is callable."
        )
        return []

    results = []
    pbar = tqdm(total=len(tasks), desc="Finished", dynamic_ncols=True, disable=quiet)

    try:
        for t in tasks:
            results.append(t["task"](*t["args"], **t["kwargs"]))
            pbar.update()
    except KeyboardInterrupt:
        results = []

    pbar.close()
    return results
