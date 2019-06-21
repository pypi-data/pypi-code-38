from datetime import datetime
from time import sleep
from pprint import pprint as pp

class Scheduler(object):

    waitTime = 60

    # activatee -> function
    def __init__(self, activatee, hours:[int], mins:[int]):
        self.activatee = activatee
        if len(hours) != len(mins):
            raise ValueError
        
        self.hours = hours
        self.mins =  mins 
        self.times = list(zip(hours, mins))
    
    def __checkTime(self):
        (h, m) = self.__getCurrentTime()

        if h in self.hours and m in self.mins:
            self.__activate()

    def __getCurrentTime(self):
        now = datetime.now()
        return (now.hour, now.minute)

    def __activate(self):
        print("Activating Function")
        self.activatee()

    def scheduleStart(self):
        print("Activation Hours: ")
        pp(self.times)
        print("Starting Scheduling ...")
        while True:
            self.__checkTime()
            sleep(self.waitTime)
        