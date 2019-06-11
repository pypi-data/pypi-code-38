import stspy
import matplotlib.pyplot as plt

filename = 'A181025.181345.VERT'
#filename = 'C160929.102937.VERT'
#filename = 'A181112.193218.specgrid'

spec = stspy.load_VERT_file(filename)

print spec

plt.figure()
plt.plot(spec.V, spec.dIdV, label = spec.label)
plt.show()
