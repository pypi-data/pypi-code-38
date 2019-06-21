# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Simple file store that is used to maintain files that are uploaded by a user
(e.g., via an API). The file store assigns each uploaded file an unique
identifier while also maintaining the original file name.

When creating an instance for a parameterized workflow the user will pass the
identifier of an uploaded file as the argument for template parameters of the
respective data type for input files. These identifier will be replaces with
references to the actual files on disk managed by the file store.
"""

import os
import shutil

from benchtmpl.io.files.base import FileHandle
import benchtmpl.util.core as util


class Filestore(object):
    """The simple file store maintains a list of uploaded files. Each file is
    assigned a unique identifier that can later be used as argument value when
    creating a workflow instance for a workflow template.

    All files are maintained in sub-folders under a given base directory.
    """
    def __init__(self, directory):
        """Initialize the base directory where files are stored.

        Parameters
        ----------
        directory : string
            Path to the base directory.
        """
        self.directory = os.path.abspath(directory)
        # Create directory if it does not exist
        util.create_dir(self.directory)

    def delete_file(self, identifier):
        """Delete file with given identifier. Returns True if file was deleted
        or False if no such file existed.

        Parameters
        ----------
        identifier: string
            Unique file identifier

        Returns
        -------
        bool
        """
        file_dir =self.get_file_dir(identifier)
        if os.path.isdir(file_dir):
            shutil.rmtree(file_dir, ignore_errors=True)
            return True
        return False

    def get_file(self, identifier):
        """Get handle for file with given identifier. Returns None if no file
        with given identifier exists.

        Parameters
        ----------
        identifier: string
            Unique file identifier

        Returns
        -------
        benchtmpl.io.files.base.FileHandle
        """
        file_dir = self.get_file_dir(identifier)
        if os.path.isdir(file_dir):
            # The uploaded file is the only file in the directory
            file_name = os.listdir(file_dir)[0]
            return FileHandle(
                identifier=identifier,
                filepath=os.path.join(file_dir, file_name),
                file_name=file_name
            )
        return None

    def get_file_dir(self, identifier, create=False):
        """Get path to the directory for the file with the given identifier. If
        the directory does not exist it will be created if the create flag is
        True.

        Parameters
        ----------
        identifier: string
            Unique file identifier
        create: bool, optional
            File directory will be created if it does not exist and the flag
            is True

        Returns
        -------
        string
        """
        file_dir = os.path.join(os.path.abspath(self.directory), identifier)
        if create and not os.path.isdir(file_dir):
            os.makedirs(file_dir)
        return file_dir

    def list_files(self):
        """Get list of file handles for all uploaded files.

        Returns
        -------
        list(benchtmpl.io.files.base.FileHandle)
        """
        result = list()
        for f_name in os.listdir(self.directory):
            dir_name = os.path.join(self.directory, f_name)
            if os.path.isdir(dir_name):
                file_name = os.listdir(dir_name)[0]
                f_handle = FileHandle(
                    identifier=f_name,
                    filepath=os.path.join(dir_name, file_name),
                    file_name=file_name
                )
                result.append(f_handle)
        return result

    def upload_file(self, filename):
        """Create a new entry from a given local file. Will make a copy of the
        given file.

        Raises ValueError if the given file does not exist.

        Parameters
        ----------
        filename: string
            Path to file on disk

        Returns
        -------
        benchtmpl.io.files.base.FileHandle
        """
        # Ensure that the given file exists
        if not os.path.isfile(filename):
            raise ValueError('invalid file path \'' + str(filename) + '\'')
        file_name = os.path.basename(filename)
        # Create a new unique identifier for the file.
        identifier = util.get_unique_identifier()
        file_dir = self.get_file_dir(identifier, create=True)
        output_file = os.path.join(file_dir, file_name)
        # Copy the uploaded file
        shutil.copyfile(filename, output_file)
        # Add file to file index
        f_handle = FileHandle(
            identifier=identifier,
            filepath=output_file,
            file_name=file_name
        )
        return f_handle

    def upload_stream(self, file, file_name):
        """Create a new entry from a given file stream. Will copy the given
        file to a file in the base directory.

        Parameters
        ----------
        file: werkzeug.datastructures.FileStorage
            File object (e.g., uploaded via HTTP request)
        file_name: string
            Name of the file

        Returns
        -------
        benchtmpl.io.files.base.FileHandle
        """
        # Create a new unique identifier for the file.
        identifier = util.get_unique_identifier()
        file_dir = self.get_file_dir(identifier, create=True)
        output_file = os.path.join(file_dir, file_name)
        # Save the file object to the new file path
        file.save(output_file)
        f_handle = FileHandle(
            identifier=identifier,
            filepath=output_file,
            file_name=file_name
        )
        return f_handle
