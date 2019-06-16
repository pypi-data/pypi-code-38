from scipy.interpolate import interpn
import numpy as np
points = np.zeros((2, 2))
points[0, 1] = 1
points[1, 1] = 1
values = np.array(([5.222, 6.916], [6.499, 4.102]))
xi = np.array((0.108, 0.88))

vals = interpn(points, values, xi)

print(vals)  # Gives: 6.462


# 3D
p2 = np.array(([0, 1], [0, 1], [0, 1]))

v2 = np.array([[[5.222, 4.852],
                [6.916, 4.377]],
               [[6.499, 6.076],
                [4.102, 5.729]]])

x2 = np.array(([0.108, 2.3], [0.88, 0.9], [1, 1.1]))

vals2 = interpn(p2, v2, x2)

print(vals2)