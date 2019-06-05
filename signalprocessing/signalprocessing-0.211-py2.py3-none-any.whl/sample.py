from signalprocessing import basicdspalgorithm
from signalprocessing import fir
a=[1,2,3]
b=[1,2,3]
c=basicdspalgorithm()
print(c.conv(a,b))
print(c.circonv(a,b))
print(c.fft(a))
print(c.auto(a))
print(c.cross(a,b))
flt=fir()
flt.lpf(71,1.5,'hamm') #lowpass filter order=71
                       #cut off freq=1.5rad/sec
					   #window=hamming
flt.bpf(71,1.5,2.5,'hamm') #bandpass filter order=71
                       #low cut off freq=1.5rad/sec high cut off freq=2.5 rad/sec
					   #window=hamming

