import os
import datetime
import tempfile
import lz4.frame
import glob
import tqdm
import logging
logger = logging.getLogger(__name__)

try:
    import cPickle as pickle
except ImportError:
    import pickle

class WorkingArea(object):
    def __init__(self, path, resume=False):
        self.task_paths = None

        if resume:
            self.path = path
            self.get_areas()
        else:
            prefix = 'tpd_{:%Y%m%d_%H%M%S}_'.format(datetime.datetime.now())
            self.path = tempfile.mkdtemp(prefix=prefix, dir=os.path.abspath(path))
            if not os.path.exists(self.path):
                os.makedirs(self.path)

    def create_areas(self, tasks, quiet=False):
        task_paths = []
        logger.info('Creating paths in {}'.format(self.path))
        for idx, task in tqdm.tqdm(
            enumerate(tasks), total=len(tasks), dynamic_ncols=True,
            disable=quiet,
        ):
            package_name = 'task_{:05d}'.format(idx)
            path = os.path.join(self.path, package_name)
            if not os.path.exists(path):
                os.makedirs(path)
            file_path = os.path.join(os.path.join(path, "task.p.lz4"))
            with lz4.frame.open(file_path, 'wb') as f:
                pickle.dump(task, f)
            task_paths.append(path)
        self.task_paths = task_paths

    def get_areas(self):
        self.task_paths = list(glob.glob(os.path.join(self.path, "task_*")))
