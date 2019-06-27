class WifiError(Exception):
    'a wifi error was found or raised'
    pass
class NoResponseError(WifiError):
    'no response from server site or somting'
import time
import sys

def tool():
    print('''toolbar_width = 40

# setup toolbar
sys.stdout.write("[%s]" % (" " * toolbar_width))
sys.stdout.flush()
sys.stdout.write("\b" * (toolbar_width+1)) # return to start of line, after '['

for i in range(toolbar_width):
    time.sleep(0.1) # do real work here
    # update the bar
    sys.stdout.write("-")
    sys.stdout.flush()

sys.stdout.write("
")''')
import sys, time
from numpy import linspace
import sys


def ProgressBar(iterObj, refreshTime=10):
  #refreshTime=10: refresh the time estimate at least every 10 sec.
  def SecToStr(sec):
    m, s = divmod(sec, 60)
    h, m = divmod(m,   60)
    return u'%d:%02d:%02d'%(h,m,s)
  L       = len(iterObj)
  steps   = {int(x):y for x,y in zip(linspace(0,L,  min(100,L),endpoint=False), 
                                     linspace(0,100,min(100,L),endpoint=False))}
  qSteps  = ['', u'\u258E',u'\u258C',u'\u258A'] # quarter and half block chars
  startT  = endT = time.time()
  timeStr = ' [0:00:00, -:--:--]'
  for nn,item in enumerate(iterObj):
    if nn in steps:
      done    = u'\u2588'*int(steps[nn]/4.0)+qSteps[int(steps[nn]%4)]
      todo    = ' '*(25-len(done))
      barStr  = u'%4d%% |%s%s|'%(steps[nn], done, todo)
      if nn>0:
        endT    = time.time()
        timeStr = ' [%s, %s]'%(SecToStr(endT-startT), SecToStr((endT-startT)*(L/float(nn)-1)))
      sys.stdout.write('\r'+barStr+timeStr); sys.stdout.flush()
    elif time.time()-endT > refreshTime:
      endT    = time.time()
      timeStr = ' [%s, %s]'%(SecToStr(endT-startT), SecToStr((endT-startT)*(L/float(nn)-1)))
      sys.stdout.write('\r'+barStr+timeStr); sys.stdout.flush()
    yield item
  barStr  = u'%4d%% |%s|'%(100, u'\u2588'*25)
  timeStr = ' [%s, 0:00:00]'%(SecToStr(time.time()-startT))
  sys.stdout.write('\r'+barStr+timeStr + '\n'); sys.stdout.flush()
  

# Example

qSteps  = ['', u'\u258E',u'\u258C',u'\u258A']


