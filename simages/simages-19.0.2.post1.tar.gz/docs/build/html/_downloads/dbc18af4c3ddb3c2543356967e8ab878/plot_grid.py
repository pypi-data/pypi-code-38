"""
Plotting trajectories on a grid
-------------------------------
simages allows comparing trajectories using various methods.
"""
import simages

df = simages.generate()

###############################################################################
# Plot a heat map of the trajectory
# =================================
# A heat map can be generated using :func:`~simages.trajectory.trip_grid`.
df.simages.trip_grid()

###############################################################################
# Increase the grid resolution
# ============================
# Number of bins can be specified with the `bins` parameter.
df.simages.trip_grid(bins=40)

###############################################################################
# Convert coordinates to grid indices
# ===================================
# Number of x and y bins can be specified with the `bins` parameter.

from simages.trajectory import grid_coordinates

grid_coords = grid_coordinates(df, bins=32)
print(grid_coords.head())

###############################################################################
# Transitions as Markov first-order Markov model
# ==============================================
# Probability of transitioning between cells is computed using :func:`simages.trajectory.transitions`.

transitions_matrix = simages.trajectory.transitions(df, bins=32)
print(transitions_matrix[:10])
