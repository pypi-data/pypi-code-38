# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""The template repository maintains workflow templates together with any static
files that are required to run a parameterized workflow.

The default repository implementation stores all template information in files
that are organized under a given base directory.
"""

import git
import os
import shutil

from benchtmpl.workflow.template.base import TemplateHandle
from benchtmpl.workflow.template.loader import DefaultTemplateLoader

import benchtmpl.error as err
import benchtmpl.util.core as util


"""Names for files and folders that are used to maintain template information."""
STATIC_FILES_DIR = 'static'
TEMPLATE_FILE = 'template.json'


""" "Default value for max. attempts parameters."""
DEFAULT_MAX_ATTEMPTS = 100


class TemplateRepository(object):
    """The template repository maintains a set of workflow templates. Each
    template is stored in a folder on the file system. The folder contains all
    static files that are provided when adding a new workflow template to the
    repository (i.e., files that are required to run the workflow).

    The repository can be used to store template handles of different types. It
    is the responsibility of the provided template loader to read and write
    template specification files to/from disk.
    """
    def __init__(
        self, base_dir,  loader=None, filenames=None, suffixes=None,
        id_func=None, max_attempts=DEFAULT_MAX_ATTEMPTS
    ):
        """Initialize the base directory where templates are maintained. The
        optional identifier function is used to generate unique template
        identifier. By default, short identifier are used.

        Uses the cross product of file names and suffixes to look for a
        template specification file when adding a new template.

        Parameters
        ----------
        base_dir: string
            Base directory for templates
        loader: benchtmpl.workflow.template.loader.TemplateLoader, optional
            Loader for reading and writing template specification files
        filenames: list(string)
            List of file names for templates files
        suffixes: list(string)
            List of recognized file suffies for template files
        id_func: func, optional
            Function to generate template folder identifier
        max_attempts: int, optional
            Maximum number of attempts to create a unique folder for a new
            workflow template
        """
        self.base_dir = os.path.abspath(base_dir)
        self.loader = loader if not loader is None else DefaultTemplateLoader()
        self.filenames = filenames if not filenames is None else ['template', 'workflow']
        self.suffixes = suffixes if not suffixes is None else ['.yml', '.yaml', '.json']
        self.id_func = id_func if not id_func is None else util.get_short_identifier
        self.max_attempts = max_attempts
        # Create the base directory if it does not exist
        util.create_dir(self.base_dir)

    def add_template(self, src_dir=None, src_repo_url=None, template_spec_file=None):
        """Create file and folder structure for a new workflow template. Assumes
        that either a workflow source directory or the Url of a remote Git
        repository is given.

        Creates a new folder with unique name in the base directory of the
        template store. The created folder will contain a copy of the source
        folder or the git repository.

        The source folder is expected to contain the template specification
        file. If the template_spec file is not given the method will look for a
        file using the entries in the file name and file suffix lists.

        If no template file is found in the source folder a ValueError is
        raised. The contents of the source directory will be copied to the
        new template directory (as subfolder named 'workflow'). The template
        directory may also contain other subfolders, e.g., subfolders for
        individual runs containing downloaded result files.

        Parameters
        ----------
        src_dir: string, optional
            Directory containing the workflow components, i.e., the fixed
            files and the template specification (optional).
        src_repo_url: string, optional
            Git repository that contains the the workflow components
        template_spec_file: string, optional
            Path to the workflow template specification file (absolute or
            relative to the workflow directory)

        Returns
        -------
        benchtmpl.workflow.template.TemplateHandle

        Raises
        ------
        benchtmpl.error.InvalidParameterError
        benchtmpl.error.InvalidTemplateError
        ValueError
        """
        # Exactly one of src_dir and src_repo_url has to be not None. If both
        # are None (or not None) a ValueError is raised.
        if src_dir is None and src_repo_url is None:
            raise ValueError('both \'src_dir\' and \'src_repo_url\' are missing')
        elif not src_dir is None and not src_repo_url is None:
            raise ValueError('cannot have both \'src_dir\' and \'src_repo_url\'')
        # Create a new unique folder for the template resources
        identifier = None
        template_dir = None
        attempt = 0
        while identifier is None or template_dir is None:
            identifier = self.id_func()
            template_dir = os.path.join(self.base_dir, identifier)
            if os.path.isdir(template_dir):
                identifier = None
                template_dir = None
                attempt += 1
                if attempt > self.max_attempts:
                    raise RuntimeError('could not create unique directory')
        # Create the new folder (this should be unique now)
        os.makedirs(template_dir)
        try:
            # Copy either the given workflow directory into the created template
            # folder or clone the Git repository.
            static_dir = os.path.join(template_dir, STATIC_FILES_DIR)
            if not src_dir is None:
                shutil.copytree(src=src_dir, dst=static_dir)
            else:
                git.Repo.clone_from(src_repo_url, static_dir)
            # Find template specification file in the template workflow folder.
            # If the file is not found the template directory is removed and a
            # ValueError is raised.
            candidates = list()
            for name in self.filenames:
                for suffix in self.suffixes:
                    candidates.append(os.path.join(static_dir, name + suffix))
            if not template_spec_file is None:
                candidates = [template_spec_file] + candidates
            for filename in candidates:
                if os.path.isfile(filename):
                    # Read template from file. If no error occurs the folder
                    # contains a valid template.
                    template = self.loader.load(
                        filename=filename,
                        identifier=identifier,
                        base_dir=static_dir,
                        validate=True
                    )
                    # Store serialized template handle on disk
                    self.loader.write(
                        template=template,
                        filename=os.path.join(template_dir, TEMPLATE_FILE)
                    )
                    return template
        except (IOError, OSError, ValueError, err.TemplateError) as ex:
            # Make sure to cleanup by removing the created template folder
            shutil.rmtree(template_dir)
            raise err.InvalidTemplateError(str(ex))
        # No template file found. Cleanup and raise error
        shutil.rmtree(template_dir)
        raise err.InvalidTemplateError('no template file found')

    def delete_template(self, identifier):
        """Delete all resources that are associated with the given template.
        This will delete the directory on disk that contains the template
        resources.

        The result is True if the template existed and False otherwise.

        Parameters
        ----------
        identifier: string
            Unique template identifier

        Returns
        -------
        bool

        Raises
        ------
        IOError
        OSError
        """
        # Drop the template directory if it exists
        template_dir = os.path.join(self.base_dir, identifier)
        if os.path.isdir(template_dir):
            shutil.rmtree(template_dir)
            return True
        return False

    def get_template(self, identifier):
        """Get handle for the template with the given identifier.

        Parameters
        ----------
        identifier: string
            Unique template identifier

        Returns
        -------
        benchtmpl.workflow.template.base.TemplateHandle

        Raises
        ------
        benchtmpl.error.InvalidTemplateError
        benchtmpl.error.UnknownTemplateError
        """
        # Raise exception if the template directory does not exist
        template_dir = os.path.join(self.base_dir, identifier)
        if not os.path.isdir(template_dir):
            raise err.UnknownTemplateError(identifier)
        return self.loader.load(
            filename=os.path.join(template_dir, TEMPLATE_FILE),
            base_dir=os.path.join(template_dir, STATIC_FILES_DIR)
        )
