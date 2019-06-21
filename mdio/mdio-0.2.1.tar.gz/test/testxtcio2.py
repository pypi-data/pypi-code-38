from mdio.xtcio import xtc_open
import time

xtcfile = 'examples/test.xtc'

frames = []
f = xtc_open(xtcfile, 'r')
time0 = time.time()
frame = f.read_frame()
while frame is not None:
    frame = f.read_frame()
    frames.append(frame)
f.close()
time1 = time.time()

fout = xtc_open('tmp.xtc', 'w')
time2 = time.time()
for frame in frames[:-1]:
    fout.write_frame(frame)
fout.close()
time3 = time.time()

print('time to read:', time1-time0)
print('time to write:', time3-time2)

frames = []
f = xtc_open(xtcfile, 'r', selection=range(50))
time0 = time.time()
frame = f.read_frame()
while frame is not None:
    frame = f.read_frame()
    frames.append(frame)
f.close()
time1 = time.time()

fout = xtc_open('tmp.xtc', 'w')
time2 = time.time()
for frame in frames[:-1]:
    fout.write_frame(frame)
fout.close()
time3 = time.time()

print('time to read 50 atoms:', time1-time0)
print('time to write 50 atoms:', time3-time2)
