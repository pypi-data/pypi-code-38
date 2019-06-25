# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Class for automl picklers."""

from abc import ABC, abstractmethod
from io import BytesIO
import os
import pickle
import time

from automl.client.core.common.exceptions import ClientException

# This is the highest protocol number for 3.6.
DEFAULT_PICKLE_PROTOCOL_VERSION = 4

# Chunk meta file extension
CHUNK_META_FILE_EXTN = '.partition'

# No of retries
DEFAULT_NO_OF_RETRIES = 3


class Pickler(ABC):
    """Pickler abstract class."""

    def __init__(self):
        """Pickler class constructor."""
        pass

    @abstractmethod
    def dump(self, obj, path):
        """
        Dump the object to file.

        :param obj: object to pickle
        :param path: pickler path
        :return: path of pickler
        """
        pass

    @abstractmethod
    def load(self, path):
        """
        Load the object from path.

        :param path: Path for loading.
        """
        pass

    @abstractmethod
    def get_pickle_files(self, path):
        """
        Get file names of the given pickle file with path.

        :param path: The path of the pickled file(s).
        :return: The chunked file(s).
        """
        pass

    def get_meta_file(self, path):
        """
        Get the meta file if available.

        :param path: The path of the pickled file.
        :return: The meta file path.
        """
        return path

    def is_meta_file(self, path):
        """
        Check if path is the meta file.

        Default is true, chunking, etc.. overrides

        :param path: The path of the pickled file.
        :return: Whether or not the file is the meta file.
        """
        return True

    def get_name_without_extn(self, path):
        """
        Get the key without extension.

        :param path: The path of the file.
        :return: The key without extension.
        """
        return os.path.splitext(path)[0]


class DefaultPickler(Pickler):
    """Default pickler based on python cPickler."""

    def __init__(self, protocol=DEFAULT_PICKLE_PROTOCOL_VERSION):
        """Create a default pickler."""
        super(DefaultPickler, self).__init__()
        self.protocol = protocol

    def dump(self, obj, path):
        """
        Dump the object to a file.

        :param obj: The object to pickle.
        :param path: The path the pickler will use.
        :return: The path.
        """
        try:
            with open(path, "wb") as f:
                pickle.dump(obj, f, protocol=self.protocol)
        except Exception as e:
            raise Exception("Pickle error {}".format(e))

        return path

    def load(self, path):
        """
        Unpickle the file.

        :param path: The file path used by the pickler.
        :return: The unpickled object.
        """
        try:
            with open(path, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            raise Exception("UnPickle error {}".format(e))

    def get_pickle_files(self, path):
        """
        Get the pickle files.

        default behavior return passed path.

        :param path: The path of pickle file.
        :return: The path of pickle file.
        """
        return [path]


class ChunkPickler(Pickler):
    """Chunk pickler based on python cPickler."""

    def __init__(self, chunk_size=100000000, retries=DEFAULT_NO_OF_RETRIES, protocol=DEFAULT_PICKLE_PROTOCOL_VERSION):
        """
        Create a Chunk Pickler.

        :param chunk_size: The chunk size.
        :param retries: The number of retries.
        """
        self.chunk_size = chunk_size
        self._retries = retries
        self.protocol = protocol
        super(ChunkPickler, self).__init__()

    def dump(self, obj, path):
        """
        Dump the object to a file.

        :param obj: The object to pickle.
        :param path: The path the pickler will use.
        :return: The path.
        """
        try:
            base_dir = os.path.dirname(path)
            pickle_file = os.path.basename(path)
            meta_file_name = self.get_meta_file(path)

            with BytesIO() as bio:
                pickle.dump(obj, bio, protocol=self.protocol)
                bio.seek(0)
                chunk_content = bio.read(self.chunk_size)
                with self._try_open_file(meta_file_name, 'wt') as mf:
                    self._try_write_chunks(base_dir, bio, chunk_content, mf, pickle_file)
        except Exception as e:
            raise AutoMLPickleException("Pickle error {}".format(e))

        return path

    def _try_open_file(self, file_name, mode):
        exception_thrown = None
        for i in range(0, self._retries):
            try:
                return open(file_name, mode)
            except Exception as e:
                exception_thrown = e
                time.sleep(1)

        if exception_thrown:
            raise exception_thrown

    def _try_write_chunks(self, base_dir, bio, chunk_content, meta_file, pickle_file_name):
        """
        Write chunks into file and update the metadata file.

        :param base_dir: The base directory to use.
        :param bio: BytesIO object to write to file.
        :param chunk_content: The chunks to write to file.
        :param meta_file: The metadata file.
        :param pickle_file_name: The file name.
        :return:
        """
        exception_thrown = None
        p = 0
        while len(chunk_content) > 0:
            file = os.path.join(base_dir, "{}.{}".format(pickle_file_name, str(p)))
            for i in range(0, self._retries):
                try:
                    with open(file, 'wb') as uc:
                        uc.write(chunk_content)
                    break
                except Exception as e:
                    exception_thrown = e
                    time.sleep(1)

            if exception_thrown:
                raise exception_thrown

            chunk_content = bio.read(self.chunk_size)
            p += 1
            meta_file.write(file)
            meta_file.write('\n')

    def load(self, path):
        """
        Unpickle the file.

        :param path: The path to the file to unpickle.
        :return: The unpickled object.
        """
        exception_thrown = None

        try:
            chunk_files = self._get_chunk_files(path)

            with BytesIO() as content:
                for chunk_file in chunk_files:
                    for i in range(0, self._retries):
                        try:
                            with open(chunk_file, 'rb') as uc:
                                uc_content = uc.read()
                            break
                        except Exception as e:
                            exception_thrown = e
                            time.sleep(1)
                    if exception_thrown:
                        raise exception_thrown
                    content.write(uc_content)
                content.seek(0)
                return pickle.load(content)
        except Exception as e:
            raise AutoMLPickleException("UnPickle error {}".format(e))

    def get_pickle_files(self, path):
        """
        Get the pickled file(s) with the meta file.

        :param path: The path of pickle file(s).
        :return: The pickle file(s) with meta file.
        """
        meta_file = self.get_meta_file(path)
        chunked_files = self._get_chunk_files(path)
        chunked_files.append(meta_file)
        return chunked_files

    def get_meta_file(self, path):
        """
        Get the meta file from path.

        :param path: The path of pickle file.
        :return: The pickle meta file name.
        """
        base_dir = os.path.dirname(path)
        pickle_file = os.path.basename(path)
        return os.path.join(base_dir, "{}{}".format(pickle_file, CHUNK_META_FILE_EXTN))

    def is_meta_file(self, path):
        """
        Check if the file is a  meta file based on extension.

        :param path: The path of pickle file.
        :return: True if meta file otherwise False
        """
        return path.endswith(CHUNK_META_FILE_EXTN)

    def _get_chunk_files(self, path):
        chunked_files = []
        meta_file = self.get_meta_file(path)
        exception_thrown = None

        for i in range(0, self._retries):
            try:
                with open(meta_file, 'r') as mf:
                    file = mf.readline()
                    file = file.replace('\n', '')
                    while len(file) > 0:
                        chunked_files.append(file)
                        file = mf.readline()
                        file = file.replace('\n', '')

                return chunked_files
            except Exception as e:
                exception_thrown = e
                time.sleep(1)

        if exception_thrown:
            raise AutoMLPickleException("Failed to get chunk files {}".format(exception_thrown))


class NoOpPickler(Pickler):
    """No operation pickler for memory based."""

    def __init__(self):
        """Create a no operation pickler."""
        super(NoOpPickler, self).__init__()
        pass

    def dump(self, obj, path):
        """
        No Operation.

        :param obj: The object to pickle.
        :param path: The path the pickler will use.
        :return:
        """
        pass

    def load(self, path):
        """
        No Operation.

        :param path: The path to the file to unpickle.
        :return: The unpickled object.
        """
        return path

    def get_pickle_files(self, path):
        """
        Get the pickle files based on chunking.

        :param path: The path of pickle file(s).
        :return: The pickle file(s) with meta file.
        """
        return [path]


class AutoMLPickleException(ClientException):
    """Automl pickle exceptions."""

    def __init__(self, *args, **kwargs):
        """Create an automl pickle exception."""
        super(AutoMLPickleException, self).__init__(*args, **kwargs)
