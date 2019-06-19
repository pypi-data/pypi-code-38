import time
from geocelery import MapReduce

def ndvi(pos):
    import dboxio
    ds = dboxio.DBoxDataset("/dboxstorage/c0/p3/GS_LT51300341992300BJC00_B30.DBOX")
    pts = ds.ReadPoints(pos)
    return pts.tolist()[0]


def g(results):
    return sum(results)

beg = time.time()

taskid = MapReduce.start([[104, 37]]*1000, ndvi, g)

rst = MapReduce.result(taskid)

print(time.time()-beg, rst)


# def task():
#     taskid = Function.start(ndvi)
#     rst = Function.result(taskid)
#     return rst
#
# beg = time.time()
#
# futures = []
# with ThreadPoolExecutor(max_workers=100) as exec:
#     for idx in range(50):
#         future_rst = exec.submit(task)
#         futures.append(future_rst)
#
# for ft in futures:
#     print(ft.result())
#
# print(time.time()-beg)





