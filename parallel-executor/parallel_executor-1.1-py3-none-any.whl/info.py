from datetime import datetime
from .task import Task

class Info:

    @classmethod
    def _get_tasks_count(cls, tasks):
        return len(tasks)

    @classmethod
    def _get_completed_tasks(cls, tasks):
        return [task for task in tasks if task.getStatus() == Task.Status.COMPLETED]

    @classmethod
    def _get_succeeded_tasks(cls, tasks):
        return [task for task in tasks if task.getCompletedStatus() == Task.Completed_Status.SUCCESS]

    @classmethod
    def _get_failed_tasks(cls, tasks):
        return [task for task in tasks if task.getCompletedStatus() == Task.Completed_Status.FAIL]

    @classmethod
    def _get_elapsed_time(cls, started_timestamp, current_timestamp):
        if started_timestamp is not None:
            elapsed_time = (current_timestamp - started_timestamp).total_seconds()
        else:
            elapsed_time = "N/A"

        return elapsed_time

    @classmethod
    def _get_estimated_time_till_completion(cls, elapsed_time, task_count, completed_task_count):
        if completed_task_count > 0:
            estimated_time = (elapsed_time / completed_task_count) * (task_count - completed_task_count)
        else:
            estimated_time = "N/A"

        return estimated_time
    
    @classmethod
    def getInfo(cls, tasks, started_timestamp):

        current_timestamp = datetime.now()
        tasks_count = cls._get_tasks_count(tasks)
        completed_tasks = cls._get_completed_tasks(tasks)
        completed_tasks_count = len(completed_tasks)
        succeeded_tasks = cls._get_succeeded_tasks(completed_tasks)
        succeeded_tasks_count = len(succeeded_tasks)
        failed_tasks = cls._get_failed_tasks(completed_tasks)
        failed_tasks_count = len(failed_tasks)
        elapsed_time = cls._get_elapsed_time(started_timestamp, current_timestamp)
        estimated_time = cls._get_estimated_time_till_completion(elapsed_time, tasks_count, completed_tasks_count)
        
        info = {
            "tasks_count": tasks_count,
            "completed_tasks": completed_tasks,
            "completed_tasks_count": completed_tasks_count,
            "succeeded_tasks": succeeded_tasks,
            "succeeded_tasks_count": succeeded_tasks_count,
            "failed_tasks": failed_tasks,
            "failed_tasks_count": failed_tasks_count,
            "elapsed_time": elapsed_time,
            "estimated_time": estimated_time
            }

        return info
    
