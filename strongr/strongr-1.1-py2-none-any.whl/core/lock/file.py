import filelock
import os

class FileLock(filelock.FileLock):
    def __init__(self, name, path, *args, **kwargs):
        if not os.path.isdir(path):
            os.makedirs(path)

        super(FileLock, self).__init__(lock_file=os.path.join(path, name), *args, **kwargs)

    def exists(self):
        # unfortunately there is no proper function in the filelock lib to check this
        try:
            self.acquire(timeout=0.001,poll_intervall=0.001)
            self.release()
        except:
            return True
        return False

    def __enter__(self):
        self.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
