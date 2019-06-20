import os
import datetime
import logging


class TaskHandlerInterface():

    def __init__(self, frequancy, timeout=None, *args, **kwargs):
        logging.basicConfig(format="[%(asctime)s] "
                                   "%(levelname)-8s:"
                                   "%(message)s")
        logging.getLogger().setLevel(logging.INFO)
        self.timeout = timeout
        self._get_or_create_metadata_file()
        self.frequancy = frequancy
        if kwargs.get('dry_run', None):
            self.dry_run = kwargs['dry_run']
        else:
            self.dry_run = False
        if kwargs.get('admin_override', None):
            self.override = True
        else:
            self.override = False

    def _get_or_create_metadata_file(self):
        name = self.__class__.__name__
        var_path = os.path.join(os.environ["HOME"], 'var')
        if not os.path.exists(var_path):
            os.makedirs(var_path)
        self.meta_filename = os.path.join(var_path, name)

    def should_run(self):
        if self.override:
            logging.warn("Execution override by admin")
            return True
        try:
            with open(self.meta_filename, 'r') as f:
                data = ''.join(f.readlines())
                try:
                    last_run = datetime.datetime.strptime(
                        data,
                        "%Y-%m-%d %H:%M:%S")
                except Exception as e:
                    return True
                now = datetime.datetime.now()
                d = now - last_run
                if d.total_seconds() < self.frequancy:
                    logging.warn("Skipping execution due to frequency!")
                    return False
        except IOError:
            pass
        return True

    def update_last_run(self):
        with open(self.meta_filename, 'w') as f:
            f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def get_list_of_tasks(self):
        raise NotImplementedError()

    def preTransaction(self):
        pass

    def postTransaction(self, success=False):
        pass

    def perform_task(self, task):
        raise NotImplementedError()

    def configure(self):
        raise NotImplementedError()
