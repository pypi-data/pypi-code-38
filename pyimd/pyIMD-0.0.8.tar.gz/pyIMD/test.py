from pyIMD.imd import InertialMassDetermination

# Create the inertial mass determination object
imd = InertialMassDetermination()

file_path1 = "C:\\Users\\localadmin\\ownCloud\\Projects\\Collaborations\\David_Gotthold\\Showcase data\\Showcase data\\mass data\\20190110_ShowCase_PLL_B.txt"
file_path2 = "C:\\Users\\localadmin\\ownCloud\\Projects\\Collaborations\\David_Gotthold\\Showcase data\\Showcase data\\mass data\\20190110_ShowCase_PLL_A.txt"
file_path3 = "C:\\Users\\localadmin\\ownCloud\\Projects\\Collaborations\\David_Gotthold\\Showcase data\\Showcase data\\mass data\\20190110_ShowCase_PLL_LongTerm.txt"
imd.create_pyimd_project(file_path1, file_path2, file_path3, '\t', 23, 'PLL', figure_width=16.5, figure_height=20,
                         initial_parameter_guess=[60.0, 2.0, 0.0, 0.0], cell_position=9.5, figure_format='pdf')

# Print the config file to the console to check if all parameters are set correctly before starting the calculation.
imd.print_pyimd_project()

#imd.show_settings_dialog()
