# Put a function on the active plot and adjust it's parameters with mouse buttons
# Derek Fujimoto
# April 2019

import bdata as bd
import matplotlib.pyplot as plt
import numpy as np
from bfit.fitting.functions import lorentzian # freq, peak, width, amp
from bfit.fitting.functions import pulsed_exp # time, lambda_s, amp
from bfit.fitting.functions import pulsed_strexp # time, lambda_s, beta, amp

class FunctionPlacer(object):
    
    npts = 500  # number of points used to draw line
    tau = bd.life.Li8   # lifetime of probe 
    
    # ======================================================================= #
    def __init__(self,fig,data,fn,p0,endfn,base=0):
        """
            fig:    pointer to matplotlib figure object to draw in
            data:   bdata object 
            fn:     function to draw and get the parameters for
            p0:     dictionary of StringVar corresponding to input parameters
            endfn:  function pointer to function to call at end of sequence. 
                        Called with no inputs
            base:   value of the baseline when we're not altering it
        
            fn needs input parameters with keys: 
            
                1F
                    peak, width, amp, base (optional)
                20/2H
                    amp, lam, beta (optional)
        """
        # save input
        self.fig = fig
        self.fn = fn
        self.p0_variable = p0
        self.p0 = {k:float(p0[k].get()) for k in p0.keys()}
        self.endfn = endfn
        self.base = base
        
        self.mode = data.mode
        x = data.asym('c')[0]
        self.x = np.linspace(min(x),max(x),self.npts)
        
        # get axes for drawing
        self.ax = fig.axes
        if len(self.ax) == 0:
            self.ax = fig.add_subplot(111)
        else:
            self.ax = self.ax[0]
        
        # get ylims
        ylims = self.ax.get_ylim()
        
        # draw line with initial parameters
        self.line = self.ax.plot(self.x,fn(self.x,**self.p0),zorder=20)[0]
        
        # reset ylims
        self.ax.set_ylim(ylims)
        
        # start step
        self.step = 0
        
        # inital connect
        if self.mode in ('20','2h'):    self.connect_motion_20()
        elif self.mode in ('1f',):      self.connect_motion_1f()
        self.connect_click()
    
    # ======================================================================= #
    def connect_click(self):
        """Connect the mouse release events"""
        
        if self.mode in ('1f',):
            self.cidrelease = self.line.figure.canvas.mpl_connect(
                'button_release_event',self.connect_motion_1f)
        elif self.mode in ('20','2h'):
            self.cidrelease = self.line.figure.canvas.mpl_connect(
                'button_release_event',self.connect_motion_20)
        else:
            pass
            
    # ======================================================================= #
    def connect_motion_20(self,*args):
        """Connect the needed mouse motion events"""
        
        if self.step == 0:
            
            titlestr = ''
                    
            # do T1
            self.cidmotion_x = self.line.figure.canvas.mpl_connect(
                'motion_notify_event', self.on_motion_20lam)
            titlestr += '1/T1 (xmove)'
            
            # do initial asymmetry
            self.cidmotion_y = self.line.figure.canvas.mpl_connect(
                    'motion_notify_event', self.on_motion_20amp)
            titlestr += ', amp (ymove)'
            
            # do beta
            if 'beta' in self.p0.keys():
                self.cidscroll = self.line.figure.canvas.mpl_connect(
                    'scroll_event', self.on_scroll_20beta)
                titlestr += ', beta (scroll)'
            
            self.ax.set_title(titlestr,fontsize='small')
            
        # END: disconnect
        else:
            
            if hasattr(self,'cidmotion_x'):   
                self.line.figure.canvas.mpl_disconnect(self.cidmotion_x)
            if hasattr(self,'cidmotion_y'):   
                self.line.figure.canvas.mpl_disconnect(self.cidmotion_y)
            if hasattr(self,'cidscroll'):   
                self.line.figure.canvas.mpl_disconnect(self.cidscroll)
            if hasattr(self,'cidkey'):   
                self.line.figure.canvas.mpl_disconnect(self.cidkey)
            self.line.figure.canvas.mpl_disconnect(self.cidrelease)
            
            self.ax.set_title('')
            
            # display new parameters
            for k in self.p0.keys():
                self.p0_variable[k].set(str(self.p0[k]))
                
            # end the sequence
            self.endfn()
            
        self.step += 1
        self.fig.show()
    
    # ======================================================================= #
    def connect_motion_1f(self,*args):
        """Connect the needed mouse motion events"""
        
        # connect motion to setting the peak
        if self.step == 0:

            self.ax.set_title('Click to set peak position (x and y)',fontsize='small')
            self.cidmotion = self.line.figure.canvas.mpl_connect(
                'motion_notify_event', self.on_motion_1fpeak)
        
        # connect motion to setting the base
        elif self.step == 1:
            
            if 'base' in self.p0.keys():
                self.ax.set_title('Click to set baseline',fontsize='small')
                self.line.figure.canvas.mpl_disconnect(self.cidmotion)
                self.cidmotion = self.line.figure.canvas.mpl_connect(
                    'motion_notify_event', self.on_motion_1fbase)
            else:
                self.step += 1
                self.connect_motion_1f()
                
         # connect motion to setting the width
        elif self.step == 2:
            
            self.ax.set_title('Click to set width',fontsize='small')
            
            if hasattr(self,'cidmotion'):
                self.line.figure.canvas.mpl_disconnect(self.cidmotion)
            self.cidmotion = self.line.figure.canvas.mpl_connect(
                'motion_notify_event', self.on_motion_1fwidth)
            
        # END: disconnect
        else:
            self.ax.set_title('')
            self.line.figure.canvas.mpl_disconnect(self.cidmotion)
            self.line.figure.canvas.mpl_disconnect(self.cidrelease)
            
            # display new parameters
            for k in self.p0.keys():
                self.p0_variable[k].set(str(self.p0[k]))
            
            # end the sequence
            self.endfn()
        
        self.step += 1
        self.fig.show()
    
    # ======================================================================= #
    def on_motion_20amp(self,event):
        """Updated the initial asymmetry on mouse movement"""
     
        # check event data
        if event.ydata is not None:
            
            self.p0['amp'] = max(0,event.ydata)
            self.line.set_ydata(self.fn(self.x,**self.p0))
            self.line.figure.canvas.draw()
 
    # ======================================================================= #
    def on_scroll_20beta(self,event):
        """Updated the initial asymmetry on mouse scroll"""
     
        if event.step is not None:
            beta = self.p0['beta']
            beta += beta*0.05*event.step
            self.p0['beta'] = min(max(beta,0),1)
            self.line.set_ydata(self.fn(self.x,**self.p0))
            self.line.figure.canvas.draw()
        
    # ======================================================================= #
    def on_motion_20lam(self,event):
        """Updated 1/T1 on mouse movement"""
        
        # set lambda
        if event.xdata is not None:
            self.p0['lam'] = max(0,1/(event.xdata*2))
            self.line.set_ydata(self.fn(self.x,**self.p0))
            self.line.figure.canvas.draw()
                
    # ======================================================================= #
    def on_motion_1fpeak(self,event):
        """Updated the peak position on mouse movement"""
    
        # check event data
        if event.xdata is not None and event.ydata is not None:
            
            self.p0['peak'] = event.xdata
            
            if 'base' in self.p0.keys():
                self.p0['base'] = event.ydata+self.p0['amp']
            else:
                self.p0['amp'] = self.base-event.ydata
            
            self.line.set_ydata(self.fn(self.x,**self.p0))
            self.line.figure.canvas.draw()
        
    # ======================================================================= #
    def on_motion_1fbase(self,event):
        """Updated the baseline position on mouse movement"""
        
        # check event data
        if event.xdata is not None and event.ydata is not None:
            
            self.p0['amp'] -= self.p0['base']-event.ydata
            self.p0['base'] = event.ydata
            
            self.line.set_ydata(self.fn(self.x,**self.p0))
            self.line.figure.canvas.draw()
    
    # ======================================================================= #
    def on_motion_1fwidth(self,event):
        """Updated the width on mouse movement"""
        
        # check event data
        if event.xdata is not None and event.ydata is not None:
            
            self.p0['width'] = abs(self.p0['peak']-event.xdata)
            self.line.set_ydata(self.fn(self.x,**self.p0))
            self.line.figure.canvas.draw()
