from IPython.core.magic import Magics
from IPython.core.magic import magics_class
from IPython.core.magic import line_cell_magic
from IPython.core.magic_arguments import argument
from IPython.core.magic_arguments import magic_arguments
from IPython.core.magic_arguments import parse_argstring
from IPython.display import display
from IPython.display import IFrame
from IPython.utils.py3compat import unicode_to_str

from . import driver


def get_arg(arg, cast):
    """
    Helper function that returns an input argument `arg` and uses the
    callable `cast` to cast the argument to the desired type. if `arg` is
    list return and cast only the first element of the list.

    :param arg: input argument return by IPython.core.magic_arguments.parse_argstring
    :param cast: function
    :return: argument
    """
    return cast(arg[0] if isinstance(arg, list) else arg)


@magics_class
class PProfileMagics(Magics):

    @magic_arguments()
    @argument('-n', '--name', default='pprofile_output', nargs=1,
              help='Name of the directory relative to the current notebook in which to store the '
                   'profile output and the html version of the profile output; If the directory '
                   'does not exist it will be created. If the directory does exist a new directory '
                   'will be created that has a running integer suffix _x. The default name is '
                   'pprofile_output.')
    @argument('-w', '--width', default=980, nargs=1,
              help='Width in pixels of the iframe displaying the pprofile output; default 980 '
                   '(used only in cell mode)')
    @argument('-h', '--height', default=400, nargs=1,
              help='Height in pixels of the iframe displaying the pprofile output; default 400 '
                   '(used only in cell mode)')
    @argument('code', nargs='*')
    @line_cell_magic
    def pprofile(self, line, cell=''):
        """PProfile IPython extension"""

        args = parse_argstring(self.pprofile, line)

        # set the output directory in which to store the profile output and create it
        output_dir = get_arg(args.name, unicode_to_str)
        output_dir = driver.create_output_dir(output_dir)

        # get the width and height
        width = get_arg(args.width, int)
        height = get_arg(args.height, int)

        # get the code
        command_line_code = ' '.join(args.code) + '\n' if len(args.code) > 0 else ''
        code = unicode_to_str(command_line_code + cell)

        # compile the code block and execute the code block
        ccode = driver.compile_code(code, output_dir)
        status = self.shell.run_code(ccode)
        # as of ipython 7.5.0 the run_code was wrapped in a coroutine.
        #   https://github.com/ipython/ipython/commit/f384e255144b97194cff1de9cb57a7dfca6f2547
        # so check type of status and if it is not a bool "list" the generator that is returned
        #   by run_code
        if not isinstance(status, bool):
            status = list(status)

        # process the profile output and return an IFrame to display the profile information in
        uri = driver.process_profile(output_dir)
        display(IFrame(uri, width=width, height=height))


# Register the class, not need to instantiate it. IPython will call the default constructor on it.
def load_ipython_extension(ipython):
    """Load the extension in IPython."""
    ipython.register_magics(PProfileMagics)


def unload_ipython_extension(ipython):
    """Any actions required to 'unload' the extension go here"""
    pass
