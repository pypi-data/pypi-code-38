# verbosity level
# 0: error
# 1: warning
# 2: info
# 3: debug

class worker_logger(object):
    pid = None
    worker_id = None
    worker_type = None
    resource_id = None
    conn = None

    def __init__(self,
                 pid,
                 worker_id="<none>",
                 worker_type="<none>",
                 resource_id=-1):

        self.pid = pid
        self.worker_id = worker_id
        self.worker_type = worker_type
        self.resource_id = resource_id

    def commit_log(self, event, message, task_id, level):
        pass

    def log_error(self, event, message, task_id=None):
        self.print_console(event, message, "error")
        self.commit_log(event, message, task_id, 0)

    def log_warning(self, event, message, task_id=None):
        self.print_console(event, message, "warning")
        self.commit_log(event, message, task_id, 1)

    def log_info(self, event, message, task_id=None):
        self.print_console(event, message, "info")
        self.commit_log(event, message, task_id, 2)

    def log_debug(self, event, message, task_id=None):
        self.print_console(event, message, "debug")
        self.commit_log(event, message, task_id, 3)

    def print_console(self, event, message, error_type):
        msg = "[{}][ {}:{} :: {}] {}".format(error_type, self.worker_id[:12], self.worker_type, event, message)
        print(msg)
