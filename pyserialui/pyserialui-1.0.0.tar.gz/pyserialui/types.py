'''
types

@summary: Python version of SerialUI types, and utility classes.

@author: Pat Deegan
@copyright: Copyright (C) 2019 Pat Deegan, https://psychogenic.com

'''

from enum import Enum
import datetime

import logging

log = logging.getLogger(__name__)

class Item(Enum):
    Menu = 0x01
    Command = 0x02
    Input = 0x03
    
    Group = 0x07
    List = 0x08
    
    TrackedState = 0xff

class Input(Enum):
    Character = 0x01
    Boolean = 0x02
    Toggle = 0x03
    Integer = 0x04
    UnsignedInteger = 0x05
    BoundedInteger = 0x06
    OptionsList = 0x07
    Float = 0x08
    String = 0x09
    DateTime = 0x0A
    Time = 0x0B
    Event = 0x0C
    WeeklySchedule = 0x0D 
    Passphrase = 0x0E
    Color = 0x0F
    
    
class TrackedState(Enum):
    Char = 0x01
    Bool = 0x02
    Toggle = 0x03
    Integer = 0x04
    UnsignedInteger = 0x05
    BoundedInteger = 0x06
    OptionsList = 0x07
    Float = 0x08
    String = 0x09
    DateTime = 0x0A
    Time = 0x0B
    Event = 0x0C
    
class AccessLevel(Enum):
    NoAccess = 0
    Guest = 1
    User = 2
    Admin = 3


class DayOfWeek(Enum):
    Any = 0
    Sunday = 1
    Monday = 2
    Tuesday = 3
    Wednesday = 4
    Thursday = 5
    Friday = 6
    Saturday = 7
    

    
class TimeDetails:
    def __init__(self, val:int = 0):
        self._val = val
        self.second = 0
        self.minute = 0
        self.hour = 0
    
    
class EventDetails:
    '''
        EventDetails
        @summary: encapsulation for Event input item data.
        
        Event requests store their state as a fat 32-bit int.  Efficient, 
        in terms of memory, but no fun to use.
        
        This class is used to translate these into something more manageable,
        with utility methods such as isCurrentNow() and isCurrentOn(DATETIME)
    '''
    def __init__(self, val:int=0):
        self._val = val
        self._startTime = None
        self._endTime = None
        self._day = DayOfWeek.Any
        self._allday = True
        
        self._parseValue(val)
        
    def isCurrentNow(self):
        return self.isCurrentOn(datetime.datetime.now())
    
    def isCurrentOn(self, dt:datetime.datetime):
        pyDateDays = [
            #py datetime.date -- 0 == monday, 6 == sunday
            DayOfWeek.Monday,
            DayOfWeek.Tuesday,
            DayOfWeek.Wednesday,
            DayOfWeek.Thursday,
            DayOfWeek.Friday,
            DayOfWeek.Saturday,
            DayOfWeek.Sunday
        ]

        #log.debug("checking if event current on %s" % str(dt))
        
        if self.day() != DayOfWeek.Any:
            if pyDateDays[dt.date().weekday()] != self.day():
                #log.debug("Not today")
                return False
            
        if self.isAllDay():
            return True
        
        # any day, or this day, check times
        tmVal = dt.time()
        
        if tmVal >= self.startTime() and tmVal <= self.endTime():
            return True
        
        return False       
    
    def startTime(self) -> datetime.time:
        return self._startTime
    
    def endTime(self) -> datetime.time:
        return self._endTime
    
    def day(self) -> DayOfWeek:
        return self._day
    
    def isAllDay(self) -> bool:
        return self._allday
        
    def _mask(self, numbits:int, bitShift):
        bitMasks = {
            3: 0x7,
            6: 0x3f,
            5:0x1f
        }
        if numbits in bitMasks:
            return (bitMasks[numbits] << bitShift)
        
    def _select(self, fromVal:int, numbits:int, bitShift:int):
        return ((self._mask(numbits, bitShift) & fromVal) >> bitShift)
    
    
    
    def _parseValue(self, val):
        st = TimeDetails()
        et = TimeDetails()
        st.second = self._select(val, 6, 0)
        st.minute = self._select(val, 6, 6)
        st.hour = self._select(val, 5, 12)
        et.minute = self._select(val, 6, 17)
        et.hour = self._select(val, 5, 23)
        
        self._startTime = datetime.time(st.hour, st.minute, st.second)
        self._endTime = datetime.time(et.hour, et.minute, 0)
        
        self._day = DayOfWeek(self._select(val, 3, 28))
        if (val & (1<<31)):
            self._allday = True
        else:
            self._allday = False

