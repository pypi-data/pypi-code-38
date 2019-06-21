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

import os
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.misc import imread
import matplotlib.pyplot as plt
from pyIMD.plotting.figures import create_montage_array

image_file_path = "/pyIMD/examples/data/show_case/images"
data_path = "/pyIMD/examples/data/show_case/CalculatedCellMass.csv"
figure_rows = 1
rows_to_plot = 10  # 1 := all data
images_to_plot = 6

# Create list of all image files
files = []
for file in os.listdir(image_file_path):
    if file.endswith(".tif"):
        files.append(os.path.join(image_file_path, file))

# Read images to image stack
image_array = []
for iFile in files:
    a = imread(iFile, flatten=1)
    image_array.append(a)
image_stack = np.array(image_array)

size = np.array([figure_rows, np.nan])
montage = create_montage_array(image_stack[0:images_to_plot, :, :], size)

# Read the calculated mass data from csv
p = Path(data_path)
mass_data = pd.read_csv(data_path, sep=',')
mass_data['Mean mass [ng]'] = mass_data['Mass [ng]'].rolling(window=1000).mean()

# Plot data
fig = plt.figure(figsize=(4.74, 4.74))
ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212)
ax1.plot(mass_data.iloc[0::rows_to_plot, 0]*60, mass_data.iloc[0::rows_to_plot, 1], 'ko', alpha=0.07, markersize=3)
ax1.plot(mass_data.iloc[0::rows_to_plot, 0]*60, mass_data.iloc[0::rows_to_plot, 2], 'r-', linewidth=0.8)
ax1.set_xlabel('Time [min]')
ax1.set_ylabel('Mass [ng]')
ax1.legend(['Measured data', 'Rolling mean', 'Bud event'], frameon=False)

# Plot images
ax2.imshow(montage, cmap='gray', vmin=0, vmax=256)
# Set proper figure labels
ticks_x = np.arange(0, montage.shape[1], step=image_stack.shape[2]/2)
x_names = []
x_ticks = []
for i in range(1, ticks_x.shape[0], 2):
    x_names.append(i)
    x_ticks.append(ticks_x[i])
x_names = np.array(x_names)
x_ticks = np.array(x_ticks)

x_tick_names = np.arange(0, x_names.shape[0]) * 3
plt.xticks(x_ticks, x_tick_names)
ticks_y = np.arange(0, montage.shape[0], step=image_stack.shape[1]/2)
y_names = []
for i in range(1, int(montage.shape[0]/image_stack.shape[1])*int(montage.shape[1]/image_stack.shape[2]),
               int(montage.shape[1]/image_stack.shape[2])):
    y_names.append(i)

y_ticks = []
for i in range(1, ticks_y.shape[0], 2):
    y_ticks.append(ticks_y[i])

y_names = np.array(y_names)
y_ticks = np.array(y_ticks)
y_tick_names = np.arange(y_names.shape[0])

plt.yticks(y_ticks, y_names)
plt.xlabel('Time [min]')
ax1.spines['right'].set_visible(False)
ax1.spines['top'].set_visible(False)
ax1.xaxis.set_ticks_position('bottom')
ax1.yaxis.set_ticks_position('left')
plt.savefig(str(Path(p.parent, 'ResultFigureMontage.png')), dpi=300)




