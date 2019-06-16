"""
    Static assignments for universally used colors and variables

"""
from xlines.statics import local_config
from xlines.colors import Colors

try:

    from xlines.oscodes_unix import exit_codes
    os_type = 'Linux'

    # special colors - linux
    acct = Colors.ORANGE
    text = Colors.BRIGHT_PURPLE
    TITLE = Colors.WHITE + Colors.BOLD

except Exception:
    from xlines.oscodes_win import exit_codes    # non-specific os-safe codes
    os_type = 'Windows'

    # special colors - windows
    acct = Colors.CYAN
    text = Colors.LT2GRAY
    TITLE = Colors.WHITE + Colors.BOLD


# universal colors
rd = Colors.RED + Colors.BOLD
yl = Colors.YELLOW + Colors.BOLD
fs = Colors.GOLD3
bd = Colors.BOLD
gn = Colors.BRIGHT_GREEN
title = Colors.BRIGHT_WHITE + Colors.BOLD
bbc = bd + Colors.BRIGHT_CYAN
highlight = bd + Colors.BRIGHT_YELLOW2
frame = gn + bd
btext = text + Colors.BOLD
bwt = Colors.BRIGHT_WHITE
bdwt = Colors.BOLD + Colors.BRIGHT_WHITE
ub = Colors.UNBOLD
rst = Colors.RESET

# globals
expath = local_config['EXCLUSIONS']['EX_EXT_PATH']
config_dir = local_config['CONFIG']['CONFIG_PATH']
div = text + '/' + rst
div_len = 2
horiz = text + '-' + rst
arrow = bwt + '-> ' + rst
BUFFER = local_config['OUTPUT']['BUFFER']
