from tkinter import *
import tkinter as Tk
import tkinter.ttk as ttk
import time
from amarettopy.gui.util  import *
from amarettopy import *

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import logging

logger = logging.getLogger("amarettopy")

class GraphTab(Tk.Frame):

    def __init__(self, amaretto, master=None):

        Tk.Frame.__init__(self, master)
        self.amaretto = amaretto

        self.t0 = None
        self.fig = None

        global tickListener

        tickListener.append(self)
        
        self.refVal = None
        self.state = STATE_UNKNOWN


    def onTick(self, servoStatus):

        if servoStatus is None:
            self.t0 = None
            self.refVal = None
            
            return

        if self.amaretto.has_reference():
            self.refVal = servoStatus[3]
            s = self.amaretto.state()
            d = dict([(STATE_CURRENT_SERVO, 0),
              (STATE_VELOCITY_SERVO, 1),
              (STATE_POSITION_SERVO, 2),
              ])
            self.servoIdx = d[s]

        else:
            self.refVal = None


        t   = time.time()
        if self.t0 is None:
            self.t0  = t
            self.ts   = []
            self.poss = []
            self.vels = []
            self.curs = []
            if self.fig is not None:
                plt.close(self.fig)
            self.fig, self.ax = plt.subplots(3, 1)

        t0 = self.t0

        cur = servoStatus[2]
        rawvel = servoStatus[1]
        vel = toRPM(rawvel)
        rawpos = servoStatus[0]
        pos = toDegree(rawpos)
        
        ref = servoStatus[3]
        ref = self.ToRef(ref)
        temp = servoStatus[4]
        fault = servoStatus[5] 

        self.ts.append(t-t0)
        self.curs.append(cur)
        self.vels.append(vel)
        self.poss.append(pos)

        XRANGE =  5 # [sec]

        if t - t0 >= XRANGE:
            for x in self.ts[:]:
                if x < t-t0-XRANGE:
                    del(self.ts[0])
                    del(self.curs[0])
                    del(self.vels[0])
                    del(self.poss[0])
                else:
                    break

        lastsens = [cur, vel, pos]
        lastraw = [cur, rawvel, rawpos]
        sens = [self.curs, self.vels, self.poss]
        labels = ['cur', 'vel', 'pos']
        units = [' ', ' rpm', ' deg']
        self.ax[0].tick_params(labelbottom=False)
        self.ax[1].tick_params(labelbottom=False)


        for i in range(3):
            self.ax[i].clear()
            YRANGE2 = 10

            if t - t0 >= XRANGE:
                self.ax[i].set_xlim(t - self.t0 - XRANGE, t-self.t0)
            else:
                self.ax[i].set_xlim(0, XRANGE)

            if self.refVal is not None and self.servoIdx == i:

                yrange = max(YRANGE2, abs(max(sens[i]) - self.ToRef(self.refVal)), abs(min(sens[i]) - self.ToRef(self.refVal)))
                self.ax[i].set_ylim(self.ToRef(self.refVal)-yrange-10, self.ToRef(self.refVal)+yrange+10)
                

                self.ax[i].plot(self.ts, sens[i], 'b', self.ts, [self.ToRef(self.refVal)]*len(self.ts), 'r')
                if labels[i] == 'cur':
                    self.ax[i].set_title( labels[i] + ' {:6}, ref({:6})'.format(lastsens[i], self.ToRef(self.refVal), color='r', fontsize=1) + units[i])
                else:
                    self.ax[i].set_title( labels[i] + ' {0:.2f}[{3}] ({1}), ref({2:.2f})'.format(lastsens[i], lastraw[i], self.ToRef(self.refVal), units[i], color='r', fontsize=1))
            else:
                self.ax[0].set_ylim(-5000,5000)
                self.ax[1].set_ylim(-60,60)
                yrange = max(YRANGE2, abs(max(sens[2]) - pos), abs(min(sens[2]) - pos))
                self.ax[2].set_ylim(pos-yrange, pos+yrange)
                self.ax[i].plot(self.ts, sens[i], 'b')
                if labels[i] == 'cur':
                    self.ax[i].set_title( labels[i] + ' {}'.format(lastsens[i], color='r', fontsize=1) + units[i])
                else:
                    self.ax[i].set_title( labels[i] + ' {0:.2f}[{2}] ({1})'.format(lastsens[i], lastraw[i],  units[i], color='r', fontsize=1))

        self.ax[2].set_xlabel("Time [sec]", fontsize=10)
        
        logger.info("Servo values: cur:%s vel:%s pos:%s ref:%s temp:%s fault:%s " % (cur, vel, pos, ref, temp, fault))
        
        plt.pause(0.01)   

    def ToRef(self, ref):
        state= self.amaretto.state()
        
        if state == STATE_VELOCITY_SERVO:
            return toRPM(ref)
            
        if state == STATE_POSITION_SERVO:  
            return toDegree(ref)

        else: 
            return ref    



