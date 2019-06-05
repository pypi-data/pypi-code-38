#!/usr/bin/env python3
import time
from shutil import get_terminal_size
"""
Very simple implementation of a time prognosis objekt for iterables.

"""
class EnumeraTIME:
    REDU = 37
    def __init__(self, iterator):
        self.iterator=iterator
        try:
            self.l=len(iterator)
        except:
            raise Exception("Your Object has no length, EnumeraTIME needs one")
        if self.l>1000:
            self.t=self.l//1000 #Timer
        elif self.l>100:
            self.t=self.l//100
        elif self.l>10:
            self.t=self.l//10
        else:
            self.t=1
        self.PLEN = 60
        try:
            twidth, tlen = get_terminal_size()
            self.PLEN = twidth - self.REDU
        except:
            pass
        self.laststamp = time.time()
    def __iter__(self):
        self.t1=time.time()
        self.n=0
        self.i=self.iterator.__iter__()
        return self
    def __next__(self):
        self.n+=1
        no=self.i.__next__()
        if self.n%self.t==self.t-1:
            percent=self.n/self.l
            tstamp = time.time()
            if self.laststamp+1>tstamp:
                #This corrects the terminal width one time a second
                try:
                    twidth, tlen = get_terminal_size()
                    self.PLEN = twidth - self.REDU
                except:
                    pass
                self.laststamp = tstamp
            tmt=tstamp-self.t1
            now=time.localtime(self.t1+tmt*(1/(self.n/self.l)))
            now = time.strftime("%H:%M \033[0m%d.%m.%Y",now)
            #print("="*5)
            print(" \033[34m{:.1%}\033[0m".format(percent), end=" ")
            print("ETA: %5.1fs\033[0m"%(tmt*(1/(self.n/self.l))-tmt), end=" ",sep="")
            print("\033[32m",now,"\033[0m",end="",sep="")
            print("\033[33m","="*int(percent*self.PLEN) +"\033[36m" + "_"*(self.PLEN-int(percent*self.PLEN)),"\033[0m ",end="\r",sep="")
        return (self.n, no)
    
    def __len__(self):
        return self.l
    
    def __str__(self):
        return str(self.iterator)
