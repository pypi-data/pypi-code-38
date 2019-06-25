# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from abc import abstractmethod, ABCMeta
import hashlib
import os
import tempfile
from shutil import make_archive
from azureml._project.ignore_file import get_project_ignore_file


class _ModuleBuilder(object):
    """
    Encapsulates logic to build a module by interacting with a workflow_provider
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_fingerprint(self):
        """
        Calculate and return a deterministic unique fingerprint for the module
        :return: fingerprint
        :rtype str
        """
        pass

    @abstractmethod
    def build(self):
        """
        Build the module and register it with the provider
        :return: module_id
        :rtype str
        """
        pass

    @property
    @abstractmethod
    def module_def(self):
        pass

    @staticmethod
    def _is_file_included(file_path, exclude_function=None):
        return (not exclude_function or
                (exclude_function and not exclude_function(os.path.normpath(file_path))))

    @staticmethod
    def _default_content_hash_calculator(hash_paths, exclude_function=None):
        hash_src = []
        for hash_path in hash_paths:
            if os.path.isfile(hash_path):
                if _ModuleBuilder._is_file_included(hash_path, exclude_function):
                    hash_src.append(hash_path)
            elif os.path.isdir(hash_path):
                for root, dirs, files in os.walk(hash_path, topdown=True):
                    hash_src.extend([os.path.join(root, name)
                                     for name in files
                                     if _ModuleBuilder._is_file_included(os.path.join(root, name),
                                                                         exclude_function)])
            else:
                raise ValueError("path not found %s" % hash_path)

        if len(hash_src) == 0:
            hash = "00000000000000000000000000000000"
        else:
            hasher = hashlib.md5()
            for f in hash_src:
                with open(str(f), 'rb') as afile:
                    buf = afile.read()
                    hasher.update(buf)
            hash = hasher.hexdigest()
        return hash

    @staticmethod
    def calculate_hash(module_def, hash_paths=None, exclude_function=None):
        module_hash = module_def.calculate_hash()
        if hash_paths is not None:
            content_hash = _ModuleBuilder._default_content_hash_calculator(hash_paths, exclude_function)
            module_hash = module_hash + "_" + content_hash
        return module_hash


class _FolderModuleBuilder(_ModuleBuilder):
    """Create a _FolderModuleBuilder

    :param context: context object
    :type context: _GraphContext
    :param module_def: module def object
    :type module_def: ModuleDef
    :param content_root: content root
    :type content_root: str
    :param hash_paths: hash_paths
    :type hash_paths: list
    """

    def __init__(self, context, module_def, content_root, hash_paths):
        """Initializes _FolderModuleBuilder."""
        self._content_path = content_root
        self._hash_paths = hash_paths
        self._module_provider = context.workflow_provider.module_provider
        self._module_def = module_def

    def get_fingerprint(self):
        exclude_function = None
        if self._content_path is not None:
            ignore_file = get_project_ignore_file(self._content_path)
            exclude_function = ignore_file.is_file_excluded
        module_hash = _ModuleBuilder.calculate_hash(self._module_def, self._hash_paths, exclude_function)
        return module_hash

    def build(self):
        fingerprint = self.get_fingerprint()
        module_id = self._module_provider.create_module(
            module_def=self._module_def, content_path=self._content_path, fingerprint=fingerprint)
        return module_id

    @property
    def module_def(self):
        return self._module_def


class _ZipFolderModuleBuilder(_FolderModuleBuilder):
    """Create a _ZipFolderModuleBuilder

    :param context: context object
    :type context: _GraphContext
    :param module_def: module def object
    :type module_def: ModuleDef
    :param content_root: content root
    :type content_root: str
    :param hash_paths: hash_paths
    :type hash_paths: list
    """

    def __init__(self, context, module_def, content_root, hash_paths):
        """Initializes _ZipFolderModuleBuilder."""
        super().__init__(context, module_def, content_root, hash_paths)

    def build(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_file_zip = os.path.join(temp_dir, 'project')
            make_archive(base_name=project_file_zip, format='zip', root_dir=self._content_path)
            module_id = self._module_provider.create_module(module_def=self._module_def,
                                                            content_path=project_file_zip + '.zip')
        return module_id


class _InterfaceModuleBuilder(_ModuleBuilder):
    """Create a _InterfaceModuleBuilder

    :param context: context object
    :type context: _GraphContext
    :param module_def: module def object
    :type module_def: ModuleDef
    """

    # enable interface only modules by supplying default values for root and hash paths
    def __init__(self, context, module_def):
        """Initializes _InterfaceModuleBuilder."""
        self._module_provider = context.workflow_provider.module_provider
        self._module_def = module_def

    def get_fingerprint(self):
        module_hash = _ModuleBuilder.calculate_hash(module_def=self._module_def)
        return module_hash

    def build(self):
        fingerprint = self.get_fingerprint()
        module_id = self._module_provider.create_module(module_def=self._module_def, fingerprint=fingerprint)
        return module_id

    @property
    def module_def(self):
        return self._module_def
