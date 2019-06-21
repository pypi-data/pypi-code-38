# /********************************************************************************
# * Copyright © 2018-2019, ETH Zurich, D-BSSE, Andreas P. Cuny & Gotthold Fläschner
# * All rights reserved. This program and the accompanying materials
# * are made available under the terms of the GNU Public License v3.0
# * which accompanies this distribution, and is available at
# * http://www.gnu.org/licenses/gpl
# *
# * Contributors:
# *     Andreas P. Cuny - initial API and implementation
# *******************************************************************************/

from pyIMD.imd import InertialMassDetermination

# Create the inertial mass determination object
imd = InertialMassDetermination()

# Create a config file for the project / experiment to analyze using default values. Note non default parameters can be
# added as optional arguments for e.g. spring_constant = 5.
file_path1 = "/pyIMD/examples/data/nanonis_long_term/20190510_LC_05_B001.dat"
file_path2 = "/pyIMD/examples/data/nanonis_long_term/20190510_LC_05_A001.dat"
file_path3 = "/pyIMD/examples/data/nanonis_long_term/20190510_LC_05_Longterm001.dat"
imd.create_pyimd_project(file_path1, file_path2, file_path3, '\t', 23, 'PLL', figure_width=5.4, figure_height=9.35,
                         initial_parameter_guess=[73.0, 5.2, 0.0, 0.0], upper_parameter_bounds=[100.0, 8.0, 3.0, 3.0],
                         spring_constant=8.0, cell_position=10, cantilever_length=100.0)

# Print the config file to the console to check if all parameters are set correctly before starting the calculation.
imd.print_pyimd_project()

# Save the config file for the project / experiment for documentation purpose or to re-run with different /
# same parameter later
imd.save_pyimd_project("/pyIMD/examples/data/nanonis_long_term/pyIMDProjectName.xml")

# Run the inertial mass determination
imd.run_intertial_mass_determination()

