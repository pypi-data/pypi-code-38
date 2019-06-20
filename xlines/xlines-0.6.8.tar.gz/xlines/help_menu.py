"""

Help Menu
    Help menu object containing body of help content.
    For printing with formatting

"""

from xlines.statics import PACKAGE
from xlines import Colors


PKG_ACCENT = Colors.ORANGE
PARAM_ACCENT = Colors.WHITE


synopsis_cmd = (
    Colors.RESET + PKG_ACCENT + PACKAGE +
    PARAM_ACCENT + ' --sum ' + Colors.RESET + ' <dir1> <dir2> <fname1> ... '
    )

url_doc = Colors.URL + 'http://xlines.readthedocs.io' + Colors.RESET
url_sc = Colors.URL + 'https://github.com/fstab50/xlines' + Colors.RESET

menu_body = Colors.BOLD + """
  DESCRIPTION""" + Colors.RESET + """

            Count lines of text. Utility for code projects
            Source Code:  """ + url_sc + """
    """ + Colors.BOLD + """
  SYNOPSIS""" + Colors.RESET + """

            """ + synopsis_cmd + """

                        -s, --sum <value1>...
                       [-e, --exclusions ]
                       [-c, --configure  ]
                       [-d, --debug    ]
                       [-h, --help     ]
                       [-m, --multiprocess  ]
                       [-w, --whitespace  ]
                       [-V, --version  ]
    """ + Colors.BOLD + """
  OPTIONS
        -s, --sum""" + Colors.RESET + """ (string): Sum the counts of all lines contained
            in filesystem objects referenced in the sum parameter
    """ + Colors.BOLD + """
        -c, --configure""" + Colors.RESET + """:  Configure runtime parameter via the cli
            menu. Change display format, color scheme, etc values
    """ + Colors.BOLD + """
        -e, --exclusions""" + Colors.RESET + """:  Print out list of file type extensions
            and directories excluded from line count calculations
    """ + Colors.BOLD + """
        -d, --debug""" + Colors.RESET + """: Print out additional debugging information
    """ + Colors.BOLD + """
        -h, --help""" + Colors.RESET + """: Show this help message and exit
    """ + Colors.BOLD + """
        -V, --version""" + Colors.RESET + """: Print package version and copyright info

    """
