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
file_path1 = "/pyIMD/examples/data/show_case/20170712_RSN_3_B"
file_path2 = "/pyIMD/examples/data/show_case/20170712_RSN_3_A"
file_path3 = "/pyIMD/examples/data/show_case/20170712_RSN_3_A_long_term.tdms"
imd.create_pyimd_project(file_path1, file_path2, file_path3, '\t', 23, 'PLL', figure_width=5.4, figure_height=9.35,
                         initial_parameter_guess=[73.0, 5.2, 0.0, 0.0], upper_parameter_bounds=[100.0, 7.0, 3.0, 3.0],
                         spring_constant=8.0, cell_position=9.5, cantilever_length=100.0, figure_format='pdf')

# Print the config file to the console to check if all parameters are set correctly before starting the calculation.
imd.print_pyimd_project()

# If one needs to change a parameter on the fly just type: imd.settings.<parameter_key> = value as eg.
# imd.settings.figure_resolution_dpi = 300. Note: Just hit imd.settings. + TAB to get automatically a list of all
# available <parameter_keys>

# To enter all the parameters one can also start the settings user interface and enter all the parameter values there.
# imd.show_settings_dialog()

# Run the inertial mass determination
imd.run_intertial_mass_determination()

# Save the config file for the project / experiment for documentation purpose or to re-run with different /
# same parameter later
imd.save_pyimd_project("/pyIMD/examples/data/show_case/pyIMDProjectName.xml")

# To load an existing project type
imd.load_pyimd_project("/pyIMD/examples/data/show_case/pyIMDProjectName.xml")
# change a parameter i.e
imd.settings.figure_format = 'png'
# and run again
imd.run_intertial_mass_determination()
