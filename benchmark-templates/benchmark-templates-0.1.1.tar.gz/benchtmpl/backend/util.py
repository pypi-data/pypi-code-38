"""Utilities for workflow templates. Provides methods and classes to copy
and upload files for workflow runs.
"""

import errno
import os
import shutil

import benchtmpl.error as err
import benchtmpl.workflow.template.base as tmpl



# ------------------------------------------------------------------------------
# Helper Classes
# ------------------------------------------------------------------------------

class FileCopy(object):
    """File upload function that copies files to a local directory instead of
    uploading them to a remote server. This class is used as argument for the
    REANA upload function that prepares a workflow run.
    """
    def __init__(self, destination_dir):
        """Initialize the destination directory into which all files are copied.

        Parameters
        ----------
        destination_dir: string
            Path to local directory
        """
        self.destination_dir = destination_dir

    def __call__(self, source, target):
        """Copy the local source file to the relative target location in the
        destination directory.

        Parameters
        ----------
        source: string
            Path to file on disk
        target: string
            Relative target path for file in destination directory
        """
        dst = os.path.join(self.destination_dir, target)
        # If the source references a directory the whole directory tree is
        # copied
        if os.path.isdir(source):
            shutil.copytree(src=source, dst=dst)
        else:
            # Based on https://stackoverflow.com/questions/2793789/create-destination-path-for-shutil-copy-files/3284204
            try:
                shutil.copy(src=source, dst=dst)
            except IOError as e:
                # ENOENT(2): file does not exist, raised also on missing dest
                # parent dir
                if e.errno != errno.ENOENT or not os.path.isfile(source):
                    raise
                # try creating parent directories
                os.makedirs(os.path.dirname(dst))
                shutil.copy(src=source, dst=dst)


# ------------------------------------------------------------------------------
# Helper Methods
# ------------------------------------------------------------------------------

def upload_files(template, files, arguments, loader):
    """Upload all references to local files in a given list of file names of
    parameter references. THe list of files, for example corresponds to the
    entries in the 'inputs.files' section of a REANA workflow specification.

    Uses a loader function to allow use of this method in cases where the
    workflow is executed locally or remote using a REANA cluster instance.

    Raises errors if (i) an unknown parameter is referenced or (ii) if the type
    of a referenced parameter in the input files section is not of type file.

    Parameters
    ----------
    template: benchtmpl.workflow.template.base.TemplateHandle
        Workflow template containing the parameterized specification and the
        parameter declarations
    files: list(string)
        List of file references
    arguments: dict(benchtmpl.workflow.parameter.value.TemplateArgument)
        Dictionary of argument values for parameters in the template
    loader: func
        File (up)load function that takes a filepath as the first argument and
        a (remote) target path as the second argument

    Raises
    ------
    benchtmpl.error.InvalidTemplateError
    benchtmpl.error.MissingArgumentError
    benchtmpl.error.UnknownParameterError
    """
    for val in files:
        # Set source and target values depending on whether the list
        # entry references a template parameter or not
        if tmpl.is_parameter(val):
            var = tmpl.get_parameter_name(val)
            # Raise error if the type of the referenced parameter is
            # not file
            para = template.get_parameter(var)
            if not para.is_file():
                raise err.InvalidTemplateError('expected file parameter for \'{}\''.format(var))
            arg = arguments.get(var)
            if arg is None:
                if para.default_value is None:
                    raise err.MissingArgumentError(var)
                else:
                    # Set source path to default value (assuming that
                    # the default points to a file in the template
                    # base directory)
                    source = os.path.join(
                        template.base_dir,
                        para.default_value
                    )
            else:
                # Get path to source file from file handle
                source = arg.value.filepath
            if para.has_constant():
                target = para.get_constant()
            else:
                target = arg.value.name
        else:
            source = os.path.join(template.base_dir, val)
            target = val
        # Upload source file
        loader(source, target)
