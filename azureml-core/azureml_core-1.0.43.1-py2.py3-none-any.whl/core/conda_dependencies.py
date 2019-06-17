# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Module for managing conda environment dependencies.

Load existing Conda environment files, configure, or manipulate new environments where the experiment executes.
For more information visit the CondaDependencies class.
"""
import os
import ruamel.yaml
import re
from azureml._base_sdk_common.common import get_run_config_dir_name
from azureml._base_sdk_common.common import normalize_windows_paths
from azureml._base_sdk_common import __version__ as VERSION
from pkg_resources import resource_stream
from azureml.exceptions import UserErrorException
from io import StringIO

BASE_PROJECT_MODULE = 'azureml._project'
BASE_PROJECT_FILE_RELATIVE_PATH = 'base_project_files/conda_dependencies.yml'
DEFAULT_SDK_ORIGIN = 'https://pypi.python.org/simple'
CONDA_FILE_NAME = 'auto_conda_dependencies.yml'
CHANNELS = 'channels'
PACKAGES = 'dependencies'
PIP = 'pip'
PYTHON_PREFIX = 'python'
VERSION_REGEX = re.compile(r'(\d+)\.(\d+)(\.(\d+))?([ab](\d+))?$')
CNTK_DEFAULT_VERSION = '2.5.1'
PYTHON_DEFAULT_VERSION = '3.6.2'
LINUX_PLATFORM = 'linux'
WINDOWS_PLATFORM = 'win32'
TENSORFLOW_DEFAULT_VERSION = '1.10.0'
PYTORCH_DEFAULT_VERSION = '1.0.0'
TORCHVISION_DEFAULT_VERSION = '0.2.1'
HOROVOD_DEFAULT_VERSION = '0.15.2'
DEFAULT_CHAINER_VERSION = "5.1.0"
CUPY_DEFAULT_VERSION = "cupy-cuda90"
CPU = 'cpu'
GPU = 'gpu'
CNTK_PACKAGE_PREFIX = 'cntk'
TENSORFLOW_PACKAGE_PREFIX = 'tensorflow'
PYTORCH_PACKAGE_PREFIX = 'torch'
TORCHVISION_PACKAGE_PREFIX = 'torchvision'
CHAINER_PACKAGE_PREFIX = "chainer"
INVALID_PATHON_MESSAGE = "Invalid python version {0}," + \
    "only accept '3.5 and '3.6'"


class CondaDependencies(object):
    """The class used to manage application dependencies.

    .. remarks::

        Users can load an existing Conda environment file or they may choose to configure and manipulate
        the application dependencies in memory. During experiment submission a preparation step is executed
        which creates and caches a Conda environment within which the experiment executes.

    The object only contains the Azure Machine Learning packages by default, if conda_dependencies_file_path is
    not used.

    :param conda_dependencies_file_path: A local path to a conda configuration file. Using this parameters
        allows for loading and editing of an existing Conda environment file.
    :type conda_dependencies_file_path: str
    :param _underlying_structure:
    :type _underlying_structure: str
    """

    DEFAULT_NUMBER_OF_CONDA_PACKAGES = 0
    DEFAULT_NUMBER_OF_PIP_PACKAGES = 0

    def __init__(self, conda_dependencies_file_path=None, _underlying_structure=None):
        """Initialize a new object to manage dependencies."""
        if conda_dependencies_file_path:
            with open(conda_dependencies_file_path, "r") as input:
                self._conda_dependencies = ruamel.yaml.round_trip_load(input)
        elif _underlying_structure:
            self._conda_dependencies = _underlying_structure
        else:
            with resource_stream(
                BASE_PROJECT_MODULE,
                BASE_PROJECT_FILE_RELATIVE_PATH
            ) as base_stream:
                self._conda_dependencies = ruamel.yaml.round_trip_load(base_stream)
                base_stream.close()

        self._python_version = self.get_python_version()

    @staticmethod
    def create(pip_indexurl=None, pip_packages=None, conda_packages=None,
               python_version=PYTHON_DEFAULT_VERSION, pin_sdk_version=True):
        """Initialize a new CondaDependencies object.

        :param pip_indexurl: pip index url if not specified sdk origin index url will be used.
        :type pip_indexurl: str
        :param pip_packages: list of pip packages.
        :type pip_packages: :class:`list[str]`
        :param conda_packages: list of conda packages.
        :type conda_packages: :class:`list[str]`
        :param python_version: python version.
        :type python_version: str
        :param pin_sdk_version: pin sdk packages to the installed version.
        :type pin_sdk_version: bool
        :return: conda dependency object
        :rtype: CondaDependencies
        """
        cd = CondaDependencies()
        _sdk_origin_url = CondaDependencies.sdk_origin_url().rstrip('/')

        # set index url to sdk origin pypi index if not specified
        if pip_indexurl or _sdk_origin_url != DEFAULT_SDK_ORIGIN:
            cd.set_pip_index_url(
                "--index-url {}".format(pip_indexurl if pip_indexurl else _sdk_origin_url))
            cd.set_pip_option("--extra-index-url {}".format(DEFAULT_SDK_ORIGIN))

        cd.set_python_version(python_version)

        if pip_packages is None:
            pip_packages = ['azureml-defaults']
        else:
            # clear defaults if pip packages were specified
            for package in cd.pip_packages:
                cd.remove_pip_package(package)

        scope = CondaDependencies._sdk_scope()
        # adding specified pip packages
        for package in pip_packages:
            # pin current sdk version assuming all azureml-* are a part of sdk
            if pin_sdk_version and cd._get_package_name(package) in scope:
                cd.add_pip_package("{}=={}.*".format(cd._get_package_name_with_extras(package), VERSION))
            else:
                cd.add_pip_package(package)

        if conda_packages:
            # clear defaults if conda packages were specified
            for conda_package in conda_packages:
                cd.remove_conda_package(conda_package)
            # adding specified conda packages
            for conda_package in conda_packages:
                cd.add_conda_package(conda_package)

        return cd

    @staticmethod
    def merge_requirements(requirements):
        """Merge requirements.

        :param requirements:
        :type requirements: :class:`list`
        :return: newpackages
        :rtype: :class:`list`
        """
        packages = {}
        for req in requirements:
            package = CondaDependencies._get_package_name(req)
            if packages.get(package, None):
                packages[package].append(req[len(package):].strip())
            else:
                packages[package] = [req[len(package):].strip()]
        newpackages = []
        for pack, req in packages.items():
            newpackages.append("{}{}".format(pack, ",".join([x for x in req if x])))
        return newpackages

    @staticmethod
    def _sdk_scope():
        """Return list of SDK packages.

        :return: list of SDK packages
        :rtype: list
        """
        from azureml._project.project_manager import _sdk_scope
        return _sdk_scope()

    @staticmethod
    def sdk_origin_url():
        """Return SDK origin index url.

        :return: Returns index
        :rtype: str
        """
        from azureml._project.project_manager import _current_index
        index = _current_index()
        if index:
            return index
        else:
            return "https://pypi.python.org/simple"

    def _merge_dependencies(self, conda_dependencies):
        if not conda_dependencies:
            return

        # merge channels, conda dependencies, pip packages
        for channel in conda_dependencies.conda_channels:
            self.add_channel(channel)

        for package in conda_dependencies.conda_packages:
            self.add_conda_package(package)

        for package in conda_dependencies.pip_packages:
            self.add_pip_package(package)

    def set_pip_index_url(self, index_url):
        """Set pip --index-url option.

        :param index_url: index url.
        :type index_url: str
        """
        self.set_pip_option(index_url)

    @property
    def conda_channels(self):
        """Return conda channels.

        :return: Returns the channel dependencies. The returned dependencies are a copy, and any changes to the
            returned channels won't update the conda channels in this object.
        :rtype: iter
        """
        conda_channels = []
        # We are returning a copy because self._conda_dependencies[CHANNELS] is of CommentedSeq ruamel.yaml
        # type, which extends from list. But, self._conda_dependencies[CHANNELS] contains the
        # comments and list elements, so in case user removes some element then it would mess up the
        # self._conda_dependencies[CHANNELS] and conda file completely.
        # Any edits to self._conda_dependencies[CHANNELS] should be done using the provided public
        # methods in this class.
        if CHANNELS in self._conda_dependencies:
            for ditem in self._conda_dependencies[CHANNELS]:
                conda_channels.append(ditem)
        return iter(conda_channels)

    @property
    def conda_packages(self):
        """Return conda packages.

        :return: Returns the package dependencies. Returns a copy of conda packages, and any edits to
            the returned list won't be reflected in the conda packages of this object.
        :rtype: iter
        """
        conda_dependencies = []
        if PACKAGES in self._conda_dependencies:
            for ditem in self._conda_dependencies[PACKAGES]:
                if PIP not in ditem:
                    conda_dependencies.append(ditem)
        return iter(conda_dependencies)

    def _is_option(self, item, startswith='-'):
        """Check if parameter is option.

        :param item:
        :type item: str
        :param startswith:
        :type startswith: char
        :return: Returns if item starts with '-'
        :rtype: bool
        """
        return item.startswith('-')

    def _filter_options(self, items, startswith='-', keep=True):
        """Filter options.

        :param items:
        :type items: :class:`list`
        :param startswith:
        :type startswith: char
        :param keep:
        :type keep: bool
        :return: Returns the filtered options
        :rtype: :class:`list`
        """
        if keep:
            return [x for x in items if self._is_option(x, startswith)]
        else:
            return [x for x in items if not self._is_option(x, startswith)]

    @property
    def pip_packages(self):
        """Return pip dependencies.

        :return: Returns the pip dependencies. Returns a copy of pip packages, and any edits to
            the returned list won't be reflected in the pip packages of this object.
        :rtype: iter
        """
        pip_dependencies = []
        if PACKAGES in self._conda_dependencies:
            for ditem in self._conda_dependencies[PACKAGES]:
                if PIP in ditem:
                    pip_dependencies = self._filter_options(ditem[PIP], keep=False)

        return iter(pip_dependencies)

    @property
    def pip_options(self):
        """Return pip options.

        :return: Returns the pip options. Returns a copy of pip options, and any edits to
            the returned list won't be reflected in the pip options of this object.
        :rtype: iter
        """
        pip_options = []
        if PACKAGES in self._conda_dependencies:
            for ditem in self._conda_dependencies[PACKAGES]:
                if PIP in ditem:
                    pip_options = self._filter_options(ditem[PIP])

        return iter(pip_options)

    def get_default_number_of_packages(self):
        """Return default number of packages.

        :return: Gets the default number of conda and pip packages
        :rtype: :class:`list`
        """
        if self.DEFAULT_NUMBER_OF_CONDA_PACKAGES == 0 and \
                self.DEFAULT_NUMBER_OF_PIP_PACKAGES == 0:
            conda_packages = 0
            pip_packages = 0
            with resource_stream(
                    BASE_PROJECT_MODULE,
                    BASE_PROJECT_FILE_RELATIVE_PATH
            ) as base_stream:
                conda_dependencies = ruamel.yaml.round_trip_load(base_stream)
                if PACKAGES in conda_dependencies:
                    for ditem in conda_dependencies[PACKAGES]:
                        if PIP not in ditem:
                            conda_packages += 1
                        else:
                            pip_packages = len(self._filter_options(ditem[PIP], keep=False))
                base_stream.close()
            self.DEFAULT_NUMBER_OF_CONDA_PACKAGES = conda_packages
            self.DEFAULT_NUMBER_OF_PIP_PACKAGES = pip_packages

        return self.DEFAULT_NUMBER_OF_CONDA_PACKAGES, self.DEFAULT_NUMBER_OF_PIP_PACKAGES

    def get_python_version(self):
        """Return python version.

        :return: Returns the python version.
        :rtype: str
        """
        if PACKAGES in self._conda_dependencies:
            for ditem in self._conda_dependencies[PACKAGES]:
                if isinstance(ditem, str) and ditem.startswith(PYTHON_PREFIX):
                    return self._get_version(ditem)
        return None

    def set_python_version(self, version):
        """Set the python version.

        :param version: the version to be added.
        :type version: str
        :rtype: None
        """
        if PACKAGES in self._conda_dependencies:
            has_python, index = self._has_python_package()
            if has_python:
                # TODO: update the cntk url if exists
                # and update the python package dependency
                if self._python_version != version:
                    # Doing an inplace update to preserve the comment above this field in the file.
                    self._conda_dependencies[PACKAGES][index] = PYTHON_PREFIX + '=' + version
            else:
                self._conda_dependencies[PACKAGES].append(PYTHON_PREFIX + '=' + version)
        else:
            self._conda_dependencies[PACKAGES] = [PYTHON_PREFIX + '=' + version]
        self._python_version = version
        return None

    def add_channel(self, channel):
        """Add a conda channel.

        A list of channels can be found at https://docs.anaconda.com/anaconda/user-guide/tasks/using-repositories/

        :param channel: the channel to be added.
        :type channel: str
        :rtype: None
        """
        if CHANNELS in self._conda_dependencies:
            if channel not in self._conda_dependencies[CHANNELS]:
                self._conda_dependencies[CHANNELS].append(channel)
        else:
            self._conda_dependencies[CHANNELS] = [channel]

    def remove_channel(self, channel):
        """Remove a channel.

        :param channel: the channel to be removed.
        :type channel: str
        """
        if CHANNELS in self._conda_dependencies and \
                channel in self._conda_dependencies[CHANNELS]:
            self._remove_from_list(self._conda_dependencies[CHANNELS], channel)

    def add_conda_package(self, conda_package):
        """Add a conda package.

        :param conda_package: the conda package to be added.
        :type conda_package: str
        """
        if PACKAGES in self._conda_dependencies:
            if conda_package not in self._conda_dependencies[PACKAGES]:
                if conda_package.startswith(PYTHON_PREFIX):
                    python_version = self._get_version(conda_package)
                    self.set_python_version(python_version)
                else:
                    self._conda_dependencies[PACKAGES].append(conda_package)
        else:
            self._conda_dependencies[PACKAGES] = [conda_package]

    def remove_conda_package(self, conda_package):
        """Remove a conda package.

        :param conda_package: the conda package to be removed.
        :type conda_package: str
        """
        if PACKAGES in self._conda_dependencies and \
                conda_package in self._conda_dependencies[PACKAGES]:
            if conda_package.startswith(PYTHON_PREFIX):
                raise UserErrorException(
                    "python must not be removed from conda dependencies")

            self._remove_from_list(self._conda_dependencies[PACKAGES], conda_package)

    def add_pip_package(self, pip_package):
        """Add a pip package.

        :param pip_package: the pip package to be added.
        :type pip_package: str
        """
        if self._is_option(pip_package):
            raise UserErrorException(
                "Invalid package name {}".format(
                    pip_package
                ))

        self.remove_pip_package(pip_package)

        if not self._has_pip_package():
            pip_obj = {PIP: [pip_package]}
            if PACKAGES in self._conda_dependencies:
                self._conda_dependencies[PACKAGES].append(pip_obj)
            else:
                self._conda_dependencies[PACKAGES] = [pip_obj]
        elif pip_package not in self.pip_packages:
            for pitem in self._conda_dependencies[PACKAGES]:
                if PIP in pitem:
                    pitem[PIP].append(pip_package)

    def set_pip_option(self, pip_option):
        """Add a pip option.

        :param pip_option: the pip option to be added.
        :type pip_option: str
        """
        if not self._is_option(pip_option):
            raise UserErrorException(
                "Invalid pip option {}".format(
                    pip_option
                ))

        if not self._has_pip_package():
            pip_obj = {PIP: [pip_option]}
            if PACKAGES in self._conda_dependencies:
                self._conda_dependencies[PACKAGES].append(pip_obj)
            else:
                self._conda_dependencies[PACKAGES] = [pip_obj]

        else:
            options = [x.split()[0] for x in self.pip_options]
            option_to_add = pip_option.split()[0]
            for pitem in self._conda_dependencies[PACKAGES]:
                if PIP in pitem:
                    if option_to_add not in options:
                        pitem[PIP].append(pip_option)
                    else:
                        for i in range(len(pitem[PIP])):
                            if pitem[PIP][i].split()[0] == option_to_add:
                                pitem[PIP][i] = pip_option

    def remove_pip_option(self, pip_option):
        """Add a pip option.

        :param pip_option: the pip option to be added.
        :type pip_option: str
        """
        if not self._is_option(pip_option):
            raise UserErrorException(
                "Invalid pip option {}".format(
                    pip_option
                ))

        if self._has_pip_package():
            options = [x.split()[0] for x in self.pip_options]
            option_to_remove = pip_option.split()[0]
            if option_to_remove in options:
                for pitem in self._conda_dependencies[PACKAGES]:
                    if PIP in pitem:
                        to_remove = None
                        for i in range(len(pitem[PIP])):
                            if pitem[PIP][i].split()[0] == option_to_remove:
                                to_remove = pitem[PIP][i]
                        if to_remove:
                            self._remove_from_list(pitem[PIP], to_remove)

    @staticmethod
    def _get_package_name(value):
        """Return package name.

        :param value:
        :type value: str
        :return: Returns the package name
        :rtype: str
        """
        # If it is whl file get package name by parsing the whl file pattern
        # https://www.python.org/dev/peps/pep-0427/#file-name-convention
        if value.endswith(".whl"):
            # whl file can be a URL, so add split based on /
            return re.split("-", re.split("/", value)[-1])[0]
        else:
            pattern = "[\[=|<|>|~|!]"
            return re.split(pattern, value)[0]

    @staticmethod
    def _get_package_name_with_extras(value):
        """Return package name with extras.

        :param value:
        :type value: str
        :return: Returns the package name with extras
        :rtype: str
        """
        pattern = "[=|<|>|~|!]"
        return re.split(pattern, value)[0]

    def remove_pip_package(self, pip_package):
        """Remove a pip package.

        :param pip_package: the pip package to be removed.
        :type pip_package: str
        """
        if self._is_option(pip_package):
            raise UserErrorException(
                "Invalid package name {}".format(
                    pip_package
                ))

        # strip version and extras
        packages = [CondaDependencies._get_package_name(x) for x in self.pip_packages]
        package_to_remove = CondaDependencies._get_package_name(pip_package)
        if pip_package in self.pip_packages or package_to_remove in packages:
            for pitem in self._conda_dependencies[PACKAGES]:
                if PIP in pitem:
                    to_remove = None
                    for i in range(len(pitem[PIP])):
                        if CondaDependencies._get_package_name(pitem[PIP][i]) == package_to_remove:
                            to_remove = pitem[PIP][i]
                    if to_remove:
                        self._remove_from_list(pitem[PIP], to_remove)

    def add_cntk_package(self, core_type=CPU):
        """Add a cntk package.

        :param core_type: 'cpu' or 'gpu'.
        :type core_type: str
        """
        self._validate_core_type(core_type)
        self._remove_pip_package_with_prefix(CNTK_PACKAGE_PREFIX)
        self.add_pip_package(self._get_cntk_package(core_type))

    def add_tensorflow_pip_package(self, core_type=CPU, version=None):
        """Add a tensorflow package.

        :param core_type: 'cpu' or 'gpu'.
        :type core_type: str
        :param version:
        :type version: str
        """
        self._validate_core_type(core_type)
        self._remove_pip_package_with_prefix(TENSORFLOW_PACKAGE_PREFIX)
        self.add_pip_package(self._get_tensorflow_pip_package(core_type, version))

    def add_tensorflow_conda_package(self, core_type=CPU, version=None):
        """Add a tensorflow package.

        :param core_type: 'cpu' or 'gpu'.
        :type core_type: str
        :param version:
        :type version: str
        """
        self._validate_core_type(core_type)
        self._remove_conda_package_with_prefix(TENSORFLOW_PACKAGE_PREFIX)
        self.add_conda_package(self._get_tensorflow_conda_package(core_type, version))

    def save_to_file(self, base_directory, conda_file_path=None):
        """Save the conda dependencies object to file.

        :param base_directory: the base directory to save the file.
        :type base_directory: str
        :param conda_file_path: the file name.
        :type conda_file_path: str
        :return: returns the normalized conda path
        :rtype: str
        """
        run_config_dir_name = get_run_config_dir_name(base_directory)
        if not conda_file_path:
            conda_file_path = "{}/{}".format(run_config_dir_name, CONDA_FILE_NAME)

        # currently we need to return the relative path of the conda file
        # with the linux path style
        # the full_path is the full path of the conda file which might
        # be the window path style. That's why we have two separate path here
        normalized_conda_path = normalize_windows_paths(conda_file_path)
        full_path = os.path.join(
            os.path.abspath(base_directory), normalized_conda_path)
        self._validate()

        with open(full_path, 'w') as outfile:
            ruamel.yaml.round_trip_dump(self._conda_dependencies, outfile)
        return normalized_conda_path

    def serialize_to_string(self):
        """Serialize conda dependencies object into a string.

        :return: Returns the conda dependencies object serialized into a string
        :rtype: str
        """
        with StringIO() as output:
            ruamel.yaml.round_trip_dump(self._conda_dependencies, output)
            content = output.getvalue()
            output.close()
            return content

    def _remove_from_list(self, element_list, element):
        """Remove element from list.

        Remove element from element_list considering both cases if type(element_list)=
        =ruamel.yaml.comments.CommentedSeq or type(element_list)==list.

        :param element_list: The list of elements.
        :type element_list: ruamel.yaml.comments.CommentedSeq or list
        :param element: The element to remove.
        :type element: str
        :return:
        :rtype: None
        """
        if type(element_list) == ruamel.yaml.comments.CommentedSeq:
            # We need to delete the element, and any associated comment, so we need to
            # ruamel.yaml methods.
            count = 0
            for litem in element_list:
                if litem == element:
                    element_list.pop(count)
                count = count + 1
        else:
            element_list.remove(element)

    def _validate_core_type(self, core_type):
        if core_type != CPU and core_type != GPU:
            raise UserErrorException(
                "Invalid core type {0}. Only accept 'cpu' or 'gpu'".format(
                    core_type
                ))

    def _has_pip_package(self):
        """Check if object has pip packages.

        :return: Returns if conda dependencies have pip packages
        :rtype: bool
        """
        has_pip = False
        if PACKAGES in self._conda_dependencies:
            for ditem in self._conda_dependencies[PACKAGES]:
                if PIP in ditem:
                    return True
        return has_pip

    def _has_python_package(self):
        """Check if the conda file, dict, hsa python package or not.

        :return: Returns bool and index of the python package.
        :rtype: :class:`list`
        """
        has_python = False
        index = -1
        count = 0
        if PACKAGES in self._conda_dependencies:
            for ditem in self._conda_dependencies[PACKAGES]:
                if isinstance(ditem, str) and ditem.startswith(PYTHON_PREFIX):
                    index = count
                    return True, index
                count = count + 1
        return has_python, index

    def _validate(self):
        has_python, index = self._has_python_package()
        if not has_python:
            raise UserErrorException("Python package is missing.")

    def _get_version_major_minor(self, version):
        """Return version groups.

        :param version:
        :type version: str
        :return: Returns group of matched items
        :rtype: :class:`list`
        """
        match = VERSION_REGEX.match(version)
        if not match:
            raise UserErrorException(
                "invalid version number '{0}'".format(version))
        return match.group(1) + '.' + match.group(2)

    def _get_version(self, version):
        """Return version.

        :param version:
        :type version: str
        :return: Returns group of matched items
        :rtype: :class:`list`
        """
        matched_group = VERSION_REGEX.search(version)
        if matched_group:
            return matched_group.group()

    def _remove_pip_package_with_prefix(self, prefix):
        """Remove pip package that starts with prefix.

        :param prefix:
        :type prefix: str
        """
        items_to_remove = self._get_pip_package_with_prefix(prefix)
        if items_to_remove:
            for item in items_to_remove:
                self.remove_pip_package(item)

    def _get_pip_package_with_prefix(self, prefix):
        """Return list of pip packages with prefix.

        :param prefix:
        :type prefix: str
        :return: Returns the list of items to remove
        :rtype: :class:`list`
        """
        items_to_remove = []
        if PACKAGES in self._conda_dependencies:
            for ditem in self._conda_dependencies[PACKAGES]:
                if PIP in ditem:
                    for pitem in ditem[PIP]:
                        if isinstance(pitem, str) and pitem.startswith(prefix):
                            items_to_remove.append(pitem)
        return items_to_remove

    def _get_conda_package_with_prefix(self, prefix):
        """Return list of conda packages with prefix.

        :param prefix:
        :type prefix: str
        :return: Returns the list of items to remove
        :rtype: :class:`list`
        """
        items_to_remove = []
        if PACKAGES in self._conda_dependencies:
            for ditem in self._conda_dependencies[PACKAGES]:
                if isinstance(ditem, str) and ditem.startswith(prefix):
                    items_to_remove.append(ditem)
        return items_to_remove

    def _remove_conda_package_with_prefix(self, prefix):
        """Remove conda package that starts with prefix.

        :param prefix:
        :type prefix: str
        """
        items_to_remove = []
        if PACKAGES in self._conda_dependencies:
            for ditem in self._conda_dependencies[PACKAGES]:
                if isinstance(ditem, str) and ditem.startswith(prefix):
                    items_to_remove.append(ditem)
        if items_to_remove:
            for item in items_to_remove:
                self.remove_conda_package(item)

    def _get_cntk_package(self, core_type):
        """Return cntk package.

        :param core_type:
        :type core_type: str
        :return: Returns cntk package
        :rtype: str
        """
        cntk_version_suffix = "==" + CNTK_DEFAULT_VERSION
        if core_type.lower() == GPU:
            return CNTK_PACKAGE_PREFIX + '-gpu' + cntk_version_suffix
        return CNTK_PACKAGE_PREFIX + cntk_version_suffix

    def _get_tensorflow_pip_package(self, core_type, version=None):
        """Return tensoflow pip package.

        :param core_type:
        :type core_type: str
        :param version:
        :type version: str
        :return: Returns tensorflow pip package
        :rtype: str
        """
        tf_version_suffix = "==" + (version if version else TENSORFLOW_DEFAULT_VERSION)
        if core_type.lower() == GPU:
            return TENSORFLOW_PACKAGE_PREFIX + '-gpu' + tf_version_suffix
        return TENSORFLOW_PACKAGE_PREFIX + tf_version_suffix

    def _get_tensorflow_conda_package(self, core_type, version=None):
        """Return tensorflow conda package.

        :param core_type:
        :type core_type: str
        :param version:
        :type version: str
        :return: Returns tensorflow conda package
        :rtype: str
        """
        tf_version_suffix = "=" + (version if version else TENSORFLOW_DEFAULT_VERSION)
        if core_type.lower() == GPU:
            return TENSORFLOW_PACKAGE_PREFIX + '-gpu' + tf_version_suffix
        return TENSORFLOW_PACKAGE_PREFIX + tf_version_suffix

    @staticmethod
    def _register_private_pip_wheel_to_blob(workspace, file_path, container_name=None, blob_name=None):
        """Register the private pip package wheel file on disk to the Azure storage blob attached to the workspace.

        :param workspace: Workspace object to use to register the private pip package wheel.
        :type workspace: azureml.core.workspace.Workspace
        :param file_path: Path to the local pip wheel file on disk, including the file extension.
        :type file_path: str
        :param container_name: Container name to use to store the pip wheel. Defaults to private-packages.
        :type container_name: str
        :param blob_name: Full path to use to store the pip wheel on the blob container.
        :type blob_name: str
        :return: Returns the full URI to the uploaded pip wheel on Azure blob storage to use in conda dependencies.
        :rtype: str
        """
        if not os.path.isfile(file_path):
            raise UserErrorException("Please make sure the wheel file exists at: {}".format(file_path))

        workspace_details = workspace.get_details()
        storage_account_name = workspace_details["storageAccount"].split('/')[-1]

        from azureml._base_sdk_common.common import storage_client_factory
        storage_client = storage_client_factory(workspace._auth_object, workspace._subscription_id)
        storage_keys = storage_client.storage_accounts.list_keys(workspace._resource_group, storage_account_name)
        storage_keys = {v.key_name: v.value for v in storage_keys.keys}

        from azureml._vendor.azure_storage.blob import BlockBlobService
        blob_service = BlockBlobService(account_name=storage_account_name, account_key=storage_keys['key1'])

        # since we're guaranteeing that the file_path points to a file, os.path.basename should return the file name.
        blob_name = blob_name if blob_name is not None else os.path.basename(file_path)
        container_name = container_name if container_name is not None else "private-packages"

        if not blob_service.exists(container_name):
            blob_service.create_container(container_name)

        blob_service.create_blob_from_path(container_name, blob_name, file_path)
        return blob_service.make_blob_url(container_name, blob_name)
