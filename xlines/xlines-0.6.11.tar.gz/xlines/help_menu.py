"""

Help Menu
    Help menu object containing body of help content.
    For printing with formatting

"""

from xlines.statics import PACKAGE
from xlines import Colors
from xlines.variables import *

c = Colors()

ACCENT = c.ORANGE               # orange accent highlight color
bdacct = c.ORANGE + c.BOLD      # bold orange
bdcy = c.CYAN + c.BOLD          # bold blue
lbrct = bbc + ' [ ' + rst        # left bracket
rbrct = bbc + ' ]' + rst        # right bracket
vdiv = bbc + ' | ' + rst
tab = '\t'.expandtabs(24)

menu_title = '\n' + c.BOLD + tab + PACKAGE + rst + ' help contents'

synopsis_cmd = (
    rst + ACCENT + PACKAGE +
    lbrct + '--sum <values>' + vdiv + '--whitespace' + vdiv +
    '--configure' + rbrct
    )

url_doc = c.URL + 'http://xlines.readthedocs.io' + rst
url_sc = c.URL + 'https://github.com/fstab50/xlines' + rst

menu_body = menu_title + c.BOLD + """

  DESCRIPTION""" + rst + """

            Count lines of text: A utility for all code projects
            Source Code Repo:  """ + url_sc + """
    """ + c.BOLD + """
  SYNOPSIS""" + rst + """

        $ """ + synopsis_cmd + """

                        -s, --sum
                       [-e, --exclusions ]
                       [-c, --configure  ]
                       [-d, --debug  ]
                       [-h, --help   ]
                       [-m, --multiprocess  ]
                       [-w, --whitespace  ]
                       [-V, --version  ]
    """ + c.BOLD + """
  OPTIONS
        -s, --sum""" + rst + """ (string): Sum the counts of all lines contained
            in filesystem objects referenced in the sum parameter
    """ + c.BOLD + """
        -c, --configure""" + rst + """:  Configure runtime parameter via the cli
            menu. Change display format, color scheme, etc values
    """ + c.BOLD + """
        -d, --debug""" + rst + """: Print out additional debugging information
    """ + c.BOLD + """
        -e, --exclusions""" + rst + """:  Print out list of file type extensions
            and directories excluded from line count calculations
    """ + c.BOLD + """
        -h, --help""" + rst + """: Show this help message and exit
    """ + c.BOLD + """
        -m, --multiprocess""" + rst + """:  Use multiple cpu cores for counting
            lines of text in expansive filesystem directories
    """ + c.BOLD + """
        -w, --whitespace""" + rst + """:  Perform line counts of all filesystem
            objects,  but omit lines containing only whitespace
    """ + c.BOLD + """
        -V, --version""" + rst + """: Print package version and copyright info
    """ + c.BOLD + """
  LEGEND""" + rst + """

           """ + bbl + 'o' + rst + """  |  Filesystem object counted (""" + bcy + 'cyan' + rst + """)
        --------------------------------------------------------
           """ + bdacct + 'o' + rst + """  |  Line count above high ct threshold (""" + acct + 'orange' + rst + """)
        --------------------------------------------------------
          """ + bwt + '->' + rst + """  |  Truncated (shortened) file path (""" + bwt + 'white' + rst + """)

    """
