"""
Plotting with simages
-------------------
`simages  <https://simages.readthedocs.io>`_ is a Python
library providing a selection of easy-to-use spatial visualizations. It is
built on top of pandas and is designed to work with a range of libraries.
For more details on the library refer to its documentation.
First we'll load in data using simages.
"""
import simages

df = simages.TrajaDataFrame({"x": [0, 1, 2, 3, 4], "y": [1, 3, 2, 4, 5]})

###############################################################################
# Plotting with Traja
# ===================
#
# We start out by plotting a basic sime series trajectory using the ``simages``
# accessor and :meth:`~simages.main.TrajaAccessor.plot`` method.
df.simages.plot()

###############################################################################
# Generate Random Walks
# =====================
#
# Also, random walks can be generated using :meth:`~simages.utils.generate`.
df = simages.generate(n=1000, fps=30)
df.simages.plot()

###############################################################################
# Traja can re-scale data with any units

df.simages.scale(100)
df.spatial_units = "cm"
df.simages.plot()

###############################################################################
# Rediscretize step lengths
# =========================
#
# :meth:`~simages.utils.rediscretize` method allows resampling the trajectory
# into an arbitrary step length ``R``.
# .. note::
#
#   This can also be achieved using `simages.utils.rediscretize(trj, step_length)`
rt = df.simages.rediscretize(R=5000)
rt.simages.plot()

###############################################################################
# Resample step time
# =========================
#
# :meth:`~simages.utils.resample_time` method allows resampling the trajectory by
# time into `step_time`.
# .. note::
#
#   This can also be achieved using `simages.utils.resample_time(trj, step_time)`
resampled = df.simages.resample_time(step_time="2s")
resampled.simages.plot()

###############################################################################
# Calculate derivatives
# =====================
#
# Derivatives can be calculated with ``derivatives`` and histograms can be
# plotted using pandas built-in :meth:`~pandas.DataFrame.hist>` method.
derivs = df.simages.get_derivatives()
speed = derivs["speed"]
speed.hist()

###############################################################################
# Again, these are just some of the plots you can make with Traja. There are
# several other possibilities not covered in this brief introduction. For more
# examples, refer to the
# `Gallery <https://simages.readthedocs.io/en/latest/gallery/index.html>`_ in the
# simages  documentation.
