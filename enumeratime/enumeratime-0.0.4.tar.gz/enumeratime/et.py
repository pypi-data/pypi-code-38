#!/usr/bin/env python3
import time
"""
Very simple implementation of a time prognosis objekt for iterables.

"""
class EnumeraTIME:
    PLEN = 60
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
            tmt=time.time()-self.t1
            #print("="*5)
            print(" Percent: {:.1%}".format(percent), end=" ")
            print("ETA: %f s"%(tmt*(1/(self.n/self.l))-tmt), end=" ")
            print(time.ctime(self.t1+tmt*(1/(self.n/self.l))),end=" ")
            print("="*int(percent*self.PLEN) + "_"*(self.PLEN-int(percent*self.PLEN)),end="\r")
        #if self.n%(self.t*10)==(self.t*10)-1:
            #print(time.ctime(self.t1+tmt*(1/(self.n/self.l))))
        return (self.n, no)
    
    def __len__(self):
        return self.l
    
    def __str__(self):
        return str(self.iterator)
