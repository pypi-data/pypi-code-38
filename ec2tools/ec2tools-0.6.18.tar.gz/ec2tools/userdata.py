"""
Summary.

    Userdata module: displays userdata script files found
    on the local filesystem from which user can choose

"""

import os
import sys
import inspect
import time
from veryprettytable import VeryPrettyTable
from pyaws.utils import userchoice_mapping
from pyaws import Colors
from ec2tools.statics import local_config
from ec2tools import logd, __version__
from ec2tools.user_selection import choose_resource

try:
    from pyaws.core.oscodes_unix import exit_codes
except Exception:
    from pyaws.core.oscodes_win import exit_codes    # non-specific os-safe codes


# globals
module = os.path.basename(__file__)
_scriptdir = local_config['CONFIG']['USERDATA_DIR']
logger = logd.getLogger(__version__)
act = Colors.ORANGE
yl = Colors.YELLOW
bd = Colors.BOLD + Colors.WHITE
frame = Colors.BOLD + Colors.BRIGHT_GREEN
rst = Colors.RESET
PACKAGE = 'runmachine'


def display_table(table, tabspaces=4):
    """Print Table Object offset from left by tabspaces"""
    indent = ('\t').expandtabs(tabspaces)
    table_str = table.get_string()
    for e in table_str.split('\n'):
        print(indent + frame + e)
    sys.stdout.write(Colors.RESET)
    return True


def source_local_userdata(paths=False):
    """
    Summary.

        returns userdata scripts found locally in configuration dir

    Returns:
        userdata scripts (full path), TYPE:  str

    """
    if paths is False:
        return os.listdir(_scriptdir)
    return [os.path.join(_scriptdir, x) for x in os.listdir(_scriptdir)]


def userdata_lookup(debug):
    """
    Summary.

        Instance Profile role user selection

    Returns:
        iam instance profile role ARN (str) or None
    """
    # setup table
    x = VeryPrettyTable(border=True, header=True, padding_width=2)
    field_max_width = 70

    x.field_names = [
        bd + '#' + frame,
        bd + 'Filename' + frame,
        bd + 'Path' + frame,
        bd + 'CreateDate' + frame,
        bd + 'LastModified' + frame
    ]

    # cell alignment
    x.align[bd + '#' + frame] = 'c'
    x.align[bd + 'Filename' + frame] = 'c'
    x.align[bd + 'Path' + frame] = 'l'
    x.align[bd + 'CreateDate' + frame] = 'c'
    x.align[bd + 'LastModified' + frame] = 'c'

    filenames = source_local_userdata()
    paths = source_local_userdata(paths=True)
    ctimes = [time.ctime(os.path.getctime(x)) for x in paths]
    mtimes = [time.ctime(os.path.getmtime(x)) for x in paths]

    # populate table
    lookup = {}

    for index, path in enumerate(paths):

            lookup[index] = paths[index]

            x.add_row(
                [
                    rst + userchoice_mapping(index) + '.' + frame,
                    rst + filenames[index] + frame,
                    rst + path + frame,
                    rst + ctimes[index] + frame,
                    rst + mtimes[index] + frame
                ]
            )

    # Table showing selections
    print(f'\n\tUserdata Scripts (local filesystem: ~/.config/ec2tools/userdata)\n'.expandtabs(26))
    display_table(x, tabspaces=4)
    return choose_resource(lookup)
