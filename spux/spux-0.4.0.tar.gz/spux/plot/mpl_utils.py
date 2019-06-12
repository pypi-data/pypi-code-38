# # # # # # # # # # # # # # # # # # # # # # # # # #
# Utils for MatPlotLib plotting class
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

import matplotlib

# does not need $DISPLAY - must be called before import pylab
matplotlib.use ('Agg')

# figure configuration
matplotlib.rcParams ["figure.max_open_warning"] = 100
matplotlib.rcParams ["savefig.dpi"] = 300

# font configuration
matplotlib.rcParams ["font.size"] = 16
matplotlib.rcParams ["legend.fontsize"] = 14

# === helper routines

import os

# create a new solid color which is slighly brighter
def brighten (color, factor=0.7):
    """Create a new solid color which is slighly brighter."""

    if color is None:
        return None
    rgb = list (matplotlib.colors.ColorConverter().to_rgb (color))
    brighter = rgb
    for channel, value in enumerate (rgb):
        brighter [channel] += factor * (1.0 - value)
    return tuple (brighter)

# generate figure name using the format 'figpath/pwd_suffix.extension'
def figname (save, figpath="fig", suffix="", extension="pdf"):
    """Generate figure name using the format 'figpath/pwd_suffix.extension'."""

    if save is not None:
        return save

    if not os.path.exists (figpath):
        os.mkdir (figpath)
    runpath, rundir = os.path.split (os.getcwd ())
    if suffix == "":
        return os.path.join (figpath, rundir + "_" + "." + extension)
    else:
        return os.path.join (figpath, rundir + "_" + suffix + "." + extension)

# # compute parameters needed for the generation of the TexTable
# def getTexTableConfig ():

#     # config

#     keys     =  ['grid_size', 'cores', 'runtime', 'cluster']
#     captions =  ['grid size', 'cores', 'runtime', 'cluster']

#     # aggregation of information

#     import time

#     values               = {}
#     #if isinstance (self.mlmc.config.discretizations [self.mlmc.config.L], dict):
#     #  grid = 'x'.join ( [ str(parameter) for parameter in self.mlmc.config.discretizations [self.mlmc.config.L] .values() ] )
#     #else:
#     grid = str ( self.mlmc.config.discretizations [self.mlmc.config.L] )
#     values ['grid_size'] = grid
#     values ['cores']     = self.mlmc.status.list ['parallelization']
#     values ['cluster']   = self.mlmc.status.list ['cluster']

#     if self.mlmc.finished:
#       runtime = self.mlmc.mcs [self.mlmc.config.L] .timer (batch=1) ['max']
#       values ['runtime'] = time.strftime ( '%H:%M:%S', time.gmtime (runtime) )
#     else:
#       values ['runtime'] = self.mlmc.status.list ['walltimes'] [-1] [0]

#     # number of levels

#     if self.mlmc.config.L != 0:
#       keys = ['L'] + keys
#       captions = [r'$L$'] + captions
#       values ['L'] = self.mlmc.config.L

#     return [keys, captions, values]

# # generate TeX code with the table including information about the simulation
# def generateTexTable (base):

#     # get the config

#     [keys, captions, opts] = self.getTexTableConfig ()

#     # TeX code generation

#     columns =  '|' + 'c|' * len(keys)

#     text =  '\n'
#     text += r'\begin{tabular}{%s}' % columns + '\n'

#     text += r'\hline' + '\n'
#     text += (r'%s & ' * len(captions))[0:-2] % tuple(captions) + r'\\' + '\n'
#     text += r'\hline' + '\n'
#     text += (r'%s & ' * len(keys))[0:-2] % tuple([opts[key] for key in keys]) + r'\\' + '\n'
#     text += r'\hline' + '\n'

#     text += r'\end{tabular}' + '\n'

#     # saving
#     f = open (base + '.tex', 'w')
#     f.write (text)
#     f.close ()

