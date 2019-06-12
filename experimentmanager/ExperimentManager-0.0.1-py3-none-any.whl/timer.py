from time import time
from threading import Lock

'''
#Description
A Timer class that automatically prints (or logs using a provided logger) and returns relative and absolute times since last and first call.
Implements empty laps and hierarchichal timings. 
Time-steps can easily be named by adding a string to the timer call : timer('a step name') (the behavior is the same of for print: multilple args will be seperated by a space).
get_timer works like the python logging class : it will create a new Timer or get one that already exists based on the required name.
get_timer is also safe for concurrency.
#Usage
    
```
from time import sleep
from timer import get_timer
def demo_function():
    timer = get_timer('Doing Something', remember=True)
    #...doing something 1
    sleep(1)
    timer('doing something 1')
    for i in range(2):
        #...doing some sub process
        sleep(0.5)
        timer.sub('doing subprocess',i)
    sleep(2)
    #... doing some background process
    timer.empty_lap() # next relative measurement will be measured from here on out
    #...doing something 2
    sleep(1)
    timer('doing all things')
    timer.summary()
if __name__ == '__main__':
    demo_function()
```
Demo function will output :
Timer - Doing Something --- doing something 1 took 1.0012 seconds (1.0012).
Timer - Doing Something --- doing subprocess 0 took 0.5009 seconds (1.502).
Timer - Doing Something --- doing subprocess 1 took 0.5008 seconds (2.0028).
Timer - Doing Something --- doing all things took 1.0011 seconds (5.0058).
Timer summary:
-- origin: 1560152644.2148
-- doing something 1: 1560152645.216
-- doing all things: 1560152649.2207   
'''

class TimerManager():

    def __init__(self):
        self.timers = {}
        self.lock = Lock()

manager = TimerManager()

def get_timer(name, verbose = 1, logger = None, remember = False):
    try :
        manager.lock.acquire()
        if name in manager.timers:
            return manager.timers[name]
        else:
            timer = Timer(name,verbose,logger,remember)
            manager.timers[name] = timer
            return timer
    except Exception as err:
        print('WARNING : get_timer lock acquisition raised {}. Timer may be overwritten...'.format(err))
        timer = Timer(name,verbose,logger,remember)
        manager.timers[name] = timer
        return timer
    finally:
        manager.lock.release()

class Timer():
    ''' A handy all-round Timer class.
    
    # Args:
        - name (optionnal) : the timer name, if provided, will be prefixed to all messages
        - verbose (default = 1). If set to 0, timer will never print messages but only return relative and absolute time measurements. 
        - logger (optionnal) : a logger to redirect prints
        - remember (default = False) : if set to True, all timesteps will be kept in a list.
        - round (default True) : if True, times will be rounded upon display for prettier prints
    
    Not safe for concurrency.
    '''

    def __init__(self, name  = None, verbose = 1, logger = None, remember = False, round_off = True):

        self.origin = time()
        
        self.current = self.origin
        
        self.sub_current = self.current
        
        self.ouput = logger.info if logger else print
        
        self.verbose = verbose

        self.name = name
        self.prefix = '' if name is None else '{} --- '.format(name)

        self.round = ( lambda x : round(x,4) ) if round_off else lambda x : x
        
        self.remember = remember
        if self.remember:
            self.steps = [ ('origin',self.origin) ]
            
    def step(self,*args):
        current = time()
        
        message = ' '.join([str(arg) for arg in args])

        delta = current - self.current        
        absolute = current - self.origin
        
        if self.verbose > 0 :
            self.ouput('Timer - {}{} took {} seconds ({}).'.format(self.prefix, message,self.round(delta), self.round(absolute)))
            
        self.current = current
        self.sub_current = current
        
        if self.remember:
            self.steps.append((message,current))
        
        return delta,absolute

    def lap(self):
        self.current = time()

    def empty_lap(self):
        self.lap()

    def sublap(self):
        self.sub_current = time()

    def sub(self,*args):
        current = time()
        message = ' '.join([str(arg) for arg in args])
        delta = current - self.sub_current
        absolute = current - self.origin
        if self.verbose > 0:
            self.ouput('Timer - {}{} took {} seconds ({}).'.format(self.prefix, message,self.round(delta), self.round(absolute)))
        self.sub_current = current
        return delta,absolute

    def summary(self):
        if self.remember:
            if self.verbose>0:
                print('\n'.join(['Timer summary:']+['-- {}: {}'.format(s,self.round(t)) for s,t in self.steps]))
            return self.steps
        return None

    def __call__(self,*args):
        self.step(*args)