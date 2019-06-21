from pyIMD.imd import InertialMassDetermination
from pyIMD.scratch_space.testSettingsinit import S
from PyQt5.QtWidgets import QApplication
# Create the inertial mass determination object
#imd = InertialMassDetermination()
#imd.show_settings_dialog()
#app = QApplication([])
#ss = S()
#ss.show_settings_dialog()
imd = InertialMassDetermination()
imd.show_settings_dialog()
#app.exec_()

# # Create a config file for the project / experiment to analyze using default values. Note non default parameters can be
# # added as optional arguments for e.g. cell_position = 9.5.
# no_cell_path = "C:\\Users\\localadmin\\Projects\\PyIMD Showcase\\20190110_ShowCase_PLL_B.txt"
# with_cell_path = "C:\\Users\\localadmin\\Projects\\PyIMD Showcase\\20190110_ShowCase_PLL_A.txt"
# long_term_measurement_path = "C:\\Users\\localadmin\\Projects\\PyIMD Showcase\\20190110_ShowCase_PLL_LongTerm.txt"
# imd.create_pyimd_project(no_cell_path, with_cell_path, long_term_measurement_path, '\t', 23, 'PLL', figure_width=16.5,
#                          figure_height=20, initial_parameter_guess=[60.0, 2.0, 0.0, 0.0], cell_position=9.5,
#                          figure_format='pdf')
#
# # Print the config file to the console to check if all parameters are set correctly before starting the calculation.
# imd.print_pyimd_project()
#
# # Run the inertial mass determination
# imd.run_intertial_mass_determination()
#
# # Save the config file for the project / experiment for documentation purpose or to re-run with different /
# # same parameter later
# imd.save_pyimd_project("C:\\Users\\localadmin\\Projects\\PyIMD Showcase\\pyIMDShowCaseProject.xml")
#
