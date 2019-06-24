"""Work with batches of jobs. Batches are modeled on git repos; state is maintained via hidden file in current folder.

"""
import os
from pathlib import Path

import yaml

from anonapi.objects import RemoteAnonServer


class YamlSavable:

    def to_dict(self):
        """
        Returns
        -------
        Dict
        """
        raise NotImplemented()

    def save(self, f):
        """

        Parameters
        ----------
        f: FileHandle

        """
        yaml.dump(self.to_dict(), f, default_flow_style=False)

    @staticmethod
    def from_dict(dict_in):
        """

        Parameters
        ----------
        dict_in: Dict

        Returns
        -------
        Instance of this class

        """
        raise NotImplemented()

    @classmethod
    def load(cls, f):
        """Load an instance of this class

        Parameters
        ----------
        f: FileHandle

        Returns
        -------

        """
        flat_dict = yaml.safe_load(f)
        return cls.from_dict(dict_in=flat_dict)


class JobBatch(YamlSavable):
    """A collection of anonymisation jobs

    """

    def __init__(self, job_ids, server):
        """

        Parameters
        ----------
        job_ids: List(str)
            All job ids in this batch
        server: RemoteAnonServer
            Server these jobs were created in
        """
        self.job_ids = job_ids
        self.server = server

    def to_dict(self):
        """

        Returns
        -------
        str

        """
        return {'server': self.server.to_dict(),
                'job_ids': self.job_ids}

    def to_string(self):
        """This batch as string

        Returns
        -------
        str:
            String with newlines representing this batch
        """
        return yaml.dump(self.to_dict())

    @classmethod
    def from_dict(cls, dict_in):
        return cls(job_ids=dict_in['job_ids'], server=RemoteAnonServer.from_dict(dict_in['server']))


class BatchFolder:
    """A folder in which a batch might be defined

    """

    BATCH_FILE_NAME = '.anonbatch'

    def __init__(self, path):
        """

        Parameters
        ----------
        path: Pathlike
            path to this folder
        """
        self.path = Path(path)

    @property
    def batch_file_path(self):
        return self.path / self.BATCH_FILE_NAME

    def has_batch(self):
        return self.batch_file_path.exists()

    def load(self):
        """Load batch from the current folder

        Returns
        -------
        JobBatch:
            If there is a batch defined in this folder

        None:
            If not
        """
        if not self.has_batch():
            return None
        else:
            with open(self.batch_file_path, 'r') as f:
                return JobBatch.load(f)

    def save(self, batch):
        """Save the given batch to this folder

        Parameters
        ----------
        batch: JobBatch
            job batch to save in this folder


        """
        with open(self.batch_file_path, 'w') as f:
            batch.save(f)

    def delete_batch(self):
        """Delete the batch file in this folder

        Raises
        ------
        BatchFolderException:
            if remove does not work for some reason

        """

        os.remove(self.batch_file_path)


class BatchFolderException(Exception):
    pass




