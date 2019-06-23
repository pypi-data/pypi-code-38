from autolens.data.array.util import array_util

import matplotlib.pyplot as plt
import numpy as np

import os

path = '{}/'.format(os.path.dirname(os.path.realpath(__file__)))

profile_name = 'data'

file_path = path+'/rj_lens_plots/data_original/'+profile_name+'/RJLens2.dat'
output_path = path+'/rj_lens_plots/data_fits/'+profile_name+'/rjlens2.fits'

file = open(file_path, 'r')

fileread = file.readlines()

image = np.zeros((422,422))

with open(file_path, "r") as f:
    for i, lineread in enumerate(fileread):
        line = str(round(float(fileread[i][0:8]), 2))
        line += ' ' * (8 - len(line))
        line += str(round(float(fileread[i][8:16]), 2))
        line += ' ' * (16 - len(line))
        line += str(float(fileread[i][16:80])) + '\n'
        image[int(float(fileread[i][0:8].strip())), int(float(fileread[i][8:16].strip()))] = float(fileread[i][16:80].strip())
       # print(int(fileread[i][0:13]), int(fileread[i][13:25]), float(fileread[i][25:80]))
       # f.write(line)

image = image.T
# image = np.fliplr(image)
image = np.flipud(image)

plt.imshow(image)
plt.show()



array_util.numpy_array_2d_to_fits(array_2d=image, file_path=output_path, overwrite=True)