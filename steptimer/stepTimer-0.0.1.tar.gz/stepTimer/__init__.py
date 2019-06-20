import time
from functools import reduce

class Timer:
    def __init__(self, nsteps = None):
        self.nsteps = nsteps
        self.prevStep = None
        self.start = time.time()
        self.prev = self.start
        self.laps = []

    def elapsed(self, step = None, round=True):
        # get eleapsed        
        end = time.time()
        prev = self.prev
        self.prev = end
        lap = end - prev
        
        self.laps.append(lap)
        self.prevStep = step if step else None

        output = "{0:.2f}".format(lap) if round else lap
        return output

    def printTime(self, timeDetail):
        try:
            timeString = time.strftime("%H:%M:%S",  time.gmtime(timeDetail))
        except Exception as e:
            print(e)
        return timeString
    
    def elapsedTot(self):
        return self.printTime(time.time() - self.start)

    def left(self, step = None):
        self.elapsed(step = step) if step else None

        avLap = reduce((lambda x, y: x + y), self.laps, 0)/self.prevStep
        remainininTime = avLap * (self.nsteps - self.prevStep)
        return self.printTime(remainininTime)