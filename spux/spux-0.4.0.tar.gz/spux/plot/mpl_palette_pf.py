# # # # # # # # # # # # # # # # # # # # # # # # # #
# Palette for the Particle Filter performance plots in MatPlotLib plotter
# For color meanings, see 'mpl_palette_colors.png'.
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

# === container for palette components

palette = {}

# === custom colors

palette ['colors'] = {}
palette ['colors'] ["spux_orange"] = (251 / 256.0, 124 / 256.0, 42 / 256.0)
palette ['colors'] ["spux_blue"] = (38 / 256.0, 135 / 256.0, 203 / 256.0)
palette ['colors'] ["spux_green"] = (182 / 256.0, 212 / 256.0, 43 / 256.0)

# === list of colors for consistent color selection accross spaghetti plots

import numpy
import matplotlib

# randomly pre-ordered list of all available built-in colors
colorlist = [ color for index, color in matplotlib.colors.cnames.items () ]
colorlist = sorted (colorlist)
rng = numpy.random.RandomState (seed=1)
rng.shuffle (colorlist)

palette ['spaghetti'] = colorlist

# === likelihoods plot palette

palette ['likelihoods'] = { 'likelihood' : 'darkorchid', 'posterior' : 'orangered', 'fitscore' : 'gray' }

# === accuracies plot palette

palette ['accuracies'] = 'mediumorchid'

# === particles plot palette

palette ['particles'] = 'tan'

# === acceptances plot palette

palette ['acceptances'] = 'darkgreen'

# === Available timing (manager and its owner) and timings (workers) for different executors and SPUX components

# Serial executor:
#  - timing: task, init, resample

# Pool executor:
#  - timing: wait
#  - timings: task, sync

# Ensemble executor:
#  - timing: wait, routings
#  - timings: tasks scatter, init, init sync, instruction,
#             <method> & <method>-sync & <method>-gather - 'as in call (<method>, ...)',
#             routings scatter, resample, kill, stash, fetch, replicate, resample sync

# Direct likelihood:
#  - timing: all from executor.report ()
#  - timings: all from executor.call/disconnect (...) - with <method> in {run, errors, advance}

# Replicates likelihood:
#  - timing: all from executor.report ()
#  - timings: all from executor.map (...)

# PF likelihood:
#  - timing: evaluate, all from executor.report ()
#  - timings: all from executor.call/resample/disconnect (...) - with <method> in {run, errors, advance}

# EMCEE sampler:
#  - timing: all from executor.report ()
#  - timings: all from executor.map (...)

# === runtimes plot palette

palette ['runtimes'] = { 'colors' : {}, 'communications' : [], 'order' : [] }

# timing (manager and its owner)

palette ['runtimes'] ['colors'] ["evaluate"] = "lightgray"
palette ['runtimes'] ['colors'] ["wait"] = "y"
palette ['runtimes'] ['colors'] ["routings"] = "darkturquoise"

# timings (workers)

palette ['runtimes'] ['colors'] ["tasks scatter"] = "r"
palette ['runtimes'] ['colors'] ["instruction"] = "crimson"
palette ['runtimes'] ['colors'] ["init"] = "green"
palette ['runtimes'] ['colors'] ["init sync"] = "lightgreen"

palette ['runtimes'] ['colors'] ["run"] = "spux_orange"
palette ['runtimes'] ['colors'] ["run gather"] = "sandybrown"
palette ['runtimes'] ['colors'] ["run sync"] = "sandybrown"
palette ['runtimes'] ['colors'] ["errors"] = "chocolate"
palette ['runtimes'] ['colors'] ["errors gather"] = "goldenrod"
palette ['runtimes'] ['colors'] ["errors sync"] = "goldenrod"
palette ['runtimes'] ['colors'] ["advance"] = "darkgray"
palette ['runtimes'] ['colors'] ["advance sync"] = "lightgray"

palette ['runtimes'] ['colors'] ["routings scatter"] = "teal"
palette ['runtimes'] ['colors'] ["resample"] = "steelblue"
palette ['runtimes'] ['colors'] ["resample sync"] = "lightskyblue"

palette ['runtimes'] ['colors'] ["kill"] = "k"
palette ['runtimes'] ['colors'] ["replicate"] = "mediumorchid"
palette ['runtimes'] ['colors'] ["stash"] = "c"
palette ['runtimes'] ['colors'] ["fetch"] = "aqua"

# preset order of the legend entries

palette ['runtimes'] ['order'] += ["evaluate"]
palette ['runtimes'] ['order'] += ["wait"]

palette ['runtimes'] ['order'] += ["tasks scatter"]
palette ['runtimes'] ['order'] += ["instruction"]
palette ['runtimes'] ['order'] += ["init"]
palette ['runtimes'] ['order'] += ["init sync"]

palette ['runtimes'] ['order'] += ["run"]
palette ['runtimes'] ['order'] += ["run gather"]
palette ['runtimes'] ['order'] += ["run sync"]
palette ['runtimes'] ['order'] += ["errors"]
palette ['runtimes'] ['order'] += ["errors gather"]
palette ['runtimes'] ['order'] += ["errors sync"]
palette ['runtimes'] ['order'] += ["advance"]
palette ['runtimes'] ['order'] += ["advance sync"]

palette ['runtimes'] ['order'] += ["routings"]
palette ['runtimes'] ['order'] += ["routings scatter"]
palette ['runtimes'] ['order'] += ["resample"]
palette ['runtimes'] ['order'] += ["kill"]
palette ['runtimes'] ['order'] += ["stash"]
palette ['runtimes'] ['order'] += ["fetch"]
palette ['runtimes'] ['order'] += ["replicate"]
palette ['runtimes'] ['order'] += ["resample sync"]

# ==== traffic plot palette

palette ['traffic'] = {}
palette ['traffic'] ['keys'] = ["init", "move", "cost", "copy", "kill"]
palette ['traffic'] ['colors'] = dict (zip (["init", "move", "cost", "copy", "kill"], ["g", "spux_orange", "magenta", "spux_blue", "k"]))

# === efficiency plot palette

palette ['efficiency'] = 'saddlebrown'

# === scaling plot palette

palette ['scaling'] = {}
palette ['scaling'] ['runtime'] = "forestgreen"
palette ['scaling'] ['linear'] = "forestgreen"
palette ['scaling'] ['efficiency'] = "saddlebrown"
