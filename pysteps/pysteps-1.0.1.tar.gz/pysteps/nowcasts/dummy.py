import dask
import numpy as np
import time

M = np.random.uniform(size=(20000, 20000))

res = []


def worker(j):
    X = M + M


# with dask
print("WITH DASK:")
n = 8
t0 = time.time()
dask.config.set(scheduler="threading")
for j in range(n):
    res.append(dask.delayed(worker)(j))
R_f_ = dask.compute(*res)
print("--- %s seconds ---" % (time.time() - t0))

# without dask
print("WITHOUT DASK:")
n = 8
t0 = time.time()
for j in range(n):
    worker(j)
print("--- %s seconds ---" % (time.time() - t0))
