from autolens.data.array.util import array_util

import matplotlib.pyplot as plt
import numpy as np

import os

path = '{}/'.format(os.path.dirname(os.path.realpath(__file__)))

profile_name = 'power_law'
# profile_name = 'ltm2_aligned'
profile_name = 'ltm2_offset'
# profile_name = 'ltm2_rad_grad'
# profile_name = 'ltm2_black_hole'
# profile_name = 'uv_ltm_offset'
# profile_name = 'uv_ltm_black_hole'
# profile_name = 'uv_power_law'

file_path = path+'/rj_lens_plots/data_original/'+profile_name+'/ML_RJLens2_All_Image_FgSub.dat'
output_path = path+'/rj_lens_plots/data_fits/'+profile_name+'/lens_subtracted_image.fits'

# file_path = path+'/rj_lens_plots/data_original/'+profile_name+'/ML_RJLens_All_Recon_Src.dat'
# output_path = path+'/rj_lens_plots/data_fits/'+profile_name+'/source_model_image.fits'
#
# file_path = path+'/rj_lens_plots/data_original/'+profile_name+'/ML_RJLens_All_Recon_FgSrc.dat'
# output_path = path+'/rj_lens_plots/data_fits/'+profile_name+'/model_image.fits'
#
# file_path = path+'/rj_lens_plots/data_original/'+profile_name+'/ML_RJLens_All_Residuals.dat'
# output_path = path+'/rj_lens_plots/data_fits/'+profile_name+'/residual_map.fits'
#
# file_path = path+'/rj_lens_plots/data_original/'+profile_name+'/ML_RJLens_All_Chi_Sq_Scaled_Noise.dat'
# output_path = path+'/rj_lens_plots/data_fits/'+profile_name+'/chi_squared_map.fits'

# file_path = path+'/rj_lens_plots/data_original/'+profile_name+'/ML_RJLens_All_Scaled_Noise.dat'
# output_path = path+'/rj_lens_plots/data_fits/'+profile_name+'/noise_map.fits'

file = open(file_path, 'r')

fileread = file.readlines()

image = np.zeros((422,422))

with open(file_path, "r") as f:
    for i, lineread in enumerate(fileread):
        line = str(round(float(fileread[i][0:13]), 2))
        line += ' ' * (8 - len(line))
        line += str(round(float(fileread[i][13:25]), 2))
        line += ' ' * (16 - len(line))
        line += str(float(fileread[i][25:80])) + '\n'
        image[int(fileread[i][0:13]), int(fileread[i][13:25])] = float(fileread[i][25:80])
       # print(int(fileread[i][0:13]), int(fileread[i][13:25]), float(fileread[i][25:80]))
       # f.write(line)

image = image.T
# image = np.fliplr(image)
image = np.flipud(image)

plt.imshow(image)
plt.show()



array_util.numpy_array_2d_to_fits(array_2d=image, file_path=output_path, overwrite=True)