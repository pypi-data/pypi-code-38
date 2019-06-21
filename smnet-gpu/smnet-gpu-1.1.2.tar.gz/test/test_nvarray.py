# --------------------------------------------------------
# SMNet test
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

import numpy as np
#from smnet import nvarray as na
from smnet import nvarray as na

print(na)
print(na.empty)
print(na.NvArray)
print(na.array)

a = np.random.randn(32, 2, 1, 3)
b = na.array(a)
c = b.to_array()

print(a.reshape(-1)[:10])
print(c.reshape(-1)[:10])
