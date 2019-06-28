"""
    Static assignments for universally used colors and variables

"""
from xlines.statics import local_config
from xlines.colors import Colors

c = Colors()

try:

    from xlines.oscodes_unix import exit_codes
    os_type = 'Linux'

    # special colors - linux
    acct = c.ORANGE
    text = c.BRIGHT_PURPLE
    TITLE = c.WHITE + c.BOLD

except Exception:
    from xlines.oscodes_win import exit_codes    # non-specific os-safe codes
    os_type = 'Windows'

    # special colors - windows
    acct = c.CYAN
    text = c.LT2GRAY
    TITLE = c.WHITE + c.BOLD


# universal colors
rd = c.RED + c.BOLD
yl = c.YELLOW + c.BOLD
fs = c.GOLD3
bd = c.BOLD
gn = c.BRIGHT_GREEN
title = c.BRIGHT_WHITE + c.BOLD
bcy = c.BRIGHT_CYAN
bbc = bd + c.BRIGHT_CYAN
bbl = bd + c.BRIGHT_BLUE
highlight = bd + c.BRIGHT_BLUE
frame = gn + bd
btext = text + c.BOLD
bwt = c.BRIGHT_WHITE
bdwt = c.BOLD + c.BRIGHT_WHITE
ub = c.UNBOLD
rst = c.RESET

# globals
expath = local_config['EXCLUSIONS']['EX_EXT_PATH']
exdirpath = local_config['EXCLUSIONS']['EX_DIR_PATH']
config_dir = local_config['CONFIG']['CONFIG_PATH']
div = text + bd + '/' + rst
div_len = 2
horiz = text + '-' + rst
arrow = bwt + '-> ' + rst
BUFFER = local_config['OUTPUT']['BUFFER']
