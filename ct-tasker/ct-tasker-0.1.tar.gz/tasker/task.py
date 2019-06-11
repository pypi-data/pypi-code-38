from functools import reduce

class CyclicDependencyError(Exception):
    pass


def parse(task_spec):
    try:
        name, command, dependencies = task_spec.split('\n')[:3]
        return (name, command, dependencies.split(',') if dependencies else [])
    except ValueError:
        name, command = task_spec.split('\n')
        return (name, command, [])

def by_name(tasks):
    return {t[0]: t for t in tasks}

def todo(tasks_by_name, task_name):
    try:
        return deduplicate(reversed(_todo(tasks_by_name, task_name, [])))
    except RecursionError:
        # This is not _guaranteed_ to be because of a cyclic dependencey
        raise CyclicDependencyError

def _todo(tasks_by_name, task_name, tasks_todo):
    task = tasks_by_name[task_name]
    tasks_todo_ = tasks_todo + [task_name]
    for dependecency in task[2]:
        tasks_todo_ = _todo(tasks_by_name, dependecency, tasks_todo_)
    return tasks_todo_

def deduplicate(l):
    return reduce(lambda acc, n: acc if n in acc else acc + [n], l, [])
