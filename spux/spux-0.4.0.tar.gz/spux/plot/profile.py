# # # # # # # # # # # # # # # # # # # # # # # # # #
# Profile plotting class based on gprof2dot
# Based on pstasts output from the profile/cProfile modules
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

# === pycallgraph
# available tools: dot, neato, fdp, sfdp, twopi, circo
# pycallgraph --max-depth 8
# --exclude "cb" --exclude "_handle_fromlist" --exclude "_load_unlocked" --exclude "_find_and_load*"
# --exclude "*.__exit__" --exclude "*.__enter__" --exclude "*.<listcomp>" --exclude "copy.*"
# --exclude "_distn_intrastructure.*" --exclude "doccer.*" --exclude "*.__init__" --exclude "__main__"
# --no-groups --memory graphviz --tool "dot" --output-file "profile-serial.png" -- ./script_serial.py

import os
import pstats

# generate figure name using the format 'figpath/pwd_suffix.extension'
def figname (figpath="fig", suffix="", extension="pdf"):
    """Generate figure name using the format 'figpath/pwd_suffix.extension'."""

    if not os.path.exists(figpath):
        os.mkdir(figpath)
    runpath, rundir = os.path.split(os.getcwd())
    if suffix == "":
        return os.path.join(figpath, rundir + "_" + "." + extension)
    else:
        return os.path.join(figpath, rundir + "_" + suffix + "." + extension)

# export profile information into a text file
def report (pstatsfile, outputdir='fig'):
    """Export profile information into a text file."""

    filename = figname (suffix='profile-report', figpath=outputdir, extension='txt')
    print (' :: Generating profile report at: ', filename)
    with open (filename, 'w') as outputfile:
        stats = pstats.Stats (pstatsfile, stream=outputfile)
        stats.print_stats ()

# generate callgraph from profile stats using gprof2dot
def callgraph (pstatsfile, root=None, threshold=10, outputdir='fig'):
    """Generate callgraph from profile stats using gprof2dot."""

    filename = figname (suffix='profile-callgraph', figpath=outputdir, extension='png')
    print (' :: Generating profile call graph at: ', filename)
    print ('  : -> with root: ', root)
    cmd = 'python3 -m gprof2dot -f pstats ' + pstatsfile
    options = '--node-thres %f --colormap print' % threshold
    if root is not None:
        options += ' --root %s' % root
    dot = 'dot -Tpng -o ' + filename
    os.system (cmd + ' ' + options + ' | ' + dot)
