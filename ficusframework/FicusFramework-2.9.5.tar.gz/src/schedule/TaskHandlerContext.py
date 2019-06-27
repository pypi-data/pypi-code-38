from api.annotation import annotation


def registry_task_handler(name: str, job_handler):
    annotation.TASK_HANDLERS[name] = job_handler
    return job_handler


def load_task_handler(name: str):
    return annotation.TASK_HANDLERS.get(name)
