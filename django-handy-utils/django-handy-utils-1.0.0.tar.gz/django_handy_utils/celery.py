import os


def detect_periodic_tasks(project_root):
    tasks = {}
    file_path = os.path.join(project_root)
    for root, dirs, files in os.walk(file_path):
        for filename in files:
            if os.path.basename(root) == 'tasks':
                if filename.startswith('periodic_tasks'):
                    full_path = os.path.join(root, filename)
                    ldict = locals()
                    exec(open(full_path).read(), globals(), ldict)
                    try:
                        tasks.update(ldict['periodic_tasks'])
                    except NameError:
                        pass
    return tasks
