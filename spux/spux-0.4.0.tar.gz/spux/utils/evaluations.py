def construct (instance, tasks):
    """Recursively construct model evaluations report."""

    if hasattr (instance, 'task'):
        taskevals = instance.task.evaluations
        evaluations = {'Component' : instance.component, 'Class' : instance.name, 'tasks' : tasks, 'sizes' : taskevals [0] ['cumulative'], 'cumulative' : tasks * taskevals [0] ['cumulative']}
        return [evaluations] + taskevals
    else:
        evaluations = {'Component' : instance.component, 'Class' : instance.name, 'tasks' : tasks, 'sizes' : 1, 'cumulative' : tasks}
        return [evaluations]