'''
 - Matplotlib - very slow, and likely to crash, so only 1 out of every 100
                points are plotted.
              - Also, data looks VERY distorted due to auto scaling along
                each axis. (this could potentially be edited)
 - Mayavi     - Much faster, and looks nicer.
              - Preserves actual scale along each axes so items look
                recognizable
'''

import pathlib
import pykitti

VISLIB = "mayavi"
# VISLIB = "matplotlib"

basedir = pathlib.Path.home() / 'Data' / 'Datasets' / 'Vision' / 'Kitti'
date = '2011_09_26'
drive = '0005'

# Optionally, specify the frame range to load
# since we are only visualizing one frame, we will restrict what we load
# Set to None to use all the data
frame_range = range(150, 151, 1)

dataset = pykitti.raw(basedir, date, drive, frames=frame_range)

i = 0
velo = dataset.get_velo(i)

if VISLIB == "mayavi":
  xs = velo[:, 0]
  ys = velo[:, 1]
  zs = velo[:, 2]
  rs = velo[:, 3]  # reflectance values

  import mayavi.mlab

  fig = mayavi.mlab.figure(bgcolor=(0, 0, 0), size=(640, 360))

  mayavi.mlab.points3d(xs,
                       ys,
                       zs,
                       zs,
                       mode="point",  # How to render each point {'point', 'sphere' , 'cube' }
                       colormap='spectral',  # 'bone', 'copper',
                       # color=(0, 1, 0),     # Used a fixed (r,g,b) color instead of colormap
                       scale_factor=100,  # scale of the points
                       line_width=10,  # Scale of the line, if any
                       figure=fig,
                       )
  mayavi.mlab.show()

else:
  import matplotlib.pyplot as plt

  skip = 100  # plot one in every `skip` points

  fig = plt.figure()
  ax = fig.add_subplot(111, projection='3d')
  velo_range = range(0, velo.shape[0], skip)  # skip points to prevent crash
  ax.scatter(velo[velo_range, 0],  # x
             velo[velo_range, 1],  # y
             velo[velo_range, 2],  # z
             c=velo[velo_range, 3],  # reflectance
             cmap='gray')
  ax.set_title('Lidar scan (subsampled)')
  plt.show()
