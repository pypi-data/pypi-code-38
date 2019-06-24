import abc
import hashlib
import json
import os
from abc import ABC, abstractmethod
from .utils import run_shell, cd
from .command_result import CommandResult, CommandException

# We generate checksums for small files according to what is used by git annex,
# This ensures that all files in a data set have the same checksum type.

def get_checksum_generator(checksum_type, data_path, metadata_path, default=None):
    if checksum_type == "SHA256":
        return ChecksumGeneratorSha256(data_path, metadata_path)
    elif checksum_type == "MD5":
        return ChecksumGeneratorMd5(data_path, metadata_path)
    elif checksum_type == "WORM":
        return ChecksumGeneratorWORM(data_path, metadata_path)
    elif default is not None:
        return default
    else:
        return None


def validate_checksum(openbis, files, data_set_id, data_path, metadata_path):
    invalid_files = []
    dataset_files = openbis.search_files(data_set_id)['objects']
    dataset_files_by_path = {}
    for dataset_file in dataset_files:
        dataset_files_by_path[dataset_file['path']] = dataset_file
    for filename in files:
        dataset_file = dataset_files_by_path[filename]
        checksum_generator = None
        # data set files have either checksumCRC32 or checksumType and checksum.
        if dataset_file['checksumCRC32'] is not None and dataset_file['checksumCRC32'] > 0:
            checksum_generator = ChecksumGeneratorCrc32(data_path, metadata_path)
            expected_checksum = dataset_file['checksumCRC32']
        elif dataset_file['checksumType'] is not None:
            checksum_generator = get_checksum_generator(dataset_file['checksumType'], data_path, metadata_path)
            expected_checksum = dataset_file['checksum']
        if checksum_generator is not None:
            checksum = checksum_generator.get_checksum(filename)['checksum']
            if checksum != expected_checksum:
                invalid_files.append(filename)
    return invalid_files


class ChecksumGenerator(metaclass=abc.ABCMeta):

    def __init__(self, data_path, metadata_path=None):
        self.data_path = data_path
        self.metadata_path = metadata_path

    def get_checksum(self, file):
        with cd(self.data_path):
            return self._get_checksum(file)

    @abc.abstractmethod
    def _get_checksum(self, file):
        return

class ChecksumGeneratorCrc32(ChecksumGenerator):
    def _get_checksum(self, file):
        result = run_shell(['cksum', file])
        if result.failure():
            raise CommandException(result)
        fields = result.output.split(" ")
        return {
            'crc32': int(fields[0]),
            'fileLength': int(fields[1]),
            'path': file
        }


class ChecksumGeneratorHashlib(ChecksumGenerator):

    def hash_function(self):
        """ Implemented in subclass. """
        pass

    def hash_type(self):
        """ Implemented in subclass. """
        pass

    def _get_checksum(self, file):
        return {
            'checksum': self._checksum(file),
            'checksumType': self.hash_type(),
            'fileLength': os.path.getsize(file),
            'path': file
        }

    def _checksum(self, file):
        hash_function = self.hash_function()
        with open(file, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_function.update(chunk)
        return hash_function.hexdigest()


class ChecksumGeneratorSha256(ChecksumGeneratorHashlib):
    def hash_function(self):
        return hashlib.sha256()
    def hash_type(self):
        return 'SHA256'


class ChecksumGeneratorMd5(ChecksumGeneratorHashlib):
    def hash_function(self):
        return hashlib.md5()
    def hash_type(self):
        return "MD5"


class ChecksumGeneratorWORM(ChecksumGenerator):
    def _get_checksum(self, file):
        return {
            'checksum': self.worm(file),
            'checksumType': 'WORM',
            'fileLength': os.path.getsize(file),
            'path': file
        }        
    def worm(self, file):
        modification_time = int(os.path.getmtime(file))
        size = os.path.getsize(file)
        return "s{}-m{}--{}".format(size, modification_time, file)


class ChecksumGeneratorGitAnnex(ChecksumGenerator):
    """ This class generates checksums according to the git annex backend configuration. """

    def __init__(self, data_path, metadata_path):
        self.data_path = data_path
        self.metadata_path = metadata_path
        self.backend = self._get_annex_backend()
        self.checksum_generator_replacement = None
        if self.backend is None:
            self.checksum_generator_replacement = ChecksumGeneratorCrc32(self.data_path, self.metadata_path)
        # define which generator to use for files which are not handled by annex
        self.checksum_generator_supplement = get_checksum_generator(
            self.backend, self.data_path, self.metadata_path, 
            default=ChecksumGeneratorCrc32(self.data_path, self.metadata_path))

    def _get_checksum(self, file):
        if self.checksum_generator_replacement is not None:
            return self.checksum_generator_replacement.get_checksum(file)
        return self.__get_checksum(file)

    def __get_checksum(self, file):
        git_dir = os.path.join(self.metadata_path, '.git')
        annex_result = run_shell(['git', '--work-tree', self.data_path, '--git-dir', git_dir, 'annex', 'info', '-j', file], raise_exception_on_failure=True)
        if 'Not a valid object name' in annex_result.output:
            return self.checksum_generator_supplement.get_checksum(file)
        annex_info = json.loads(annex_result.output)
        # TODO annex_info will not have 'present' if there is a git repository within the obis repository
        if annex_info['present'] != True:
            return self.checksum_generator_supplement.get_checksum(file)
        return {
            'checksum': self._get_checksum_from_annex_info(annex_info),
            'checksumType': self.backend,
            'fileLength': os.path.getsize(file),
            'path': file
        }

    def _get_checksum_from_annex_info(self, annex_info):
        if self.backend in ['MD5', 'SHA256']:
            return annex_info['key'].split('--')[1].split('.')[0]
        elif self.backend == 'WORM':
            return annex_info['key'][5:]
        else:
            raise ValueError("Git annex backend not supported: " + self.backend)

    def _get_annex_backend(self):
        with cd(self.metadata_path):
            with open('.git/info/attributes') as gitattributes:
                for line in gitattributes.readlines():
                    if 'annex.backend' in line:
                        backend = line.split('=')[1].strip()
                        if backend == 'SHA256E':
                            backend = 'SHA256'
                        return backend
        return None
