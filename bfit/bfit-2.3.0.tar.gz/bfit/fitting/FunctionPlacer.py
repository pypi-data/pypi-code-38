# Put a function on the active plot and adjust it's parameters with mouse buttons
# Derek Fujimoto
# April 2019

import bdata as bd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from bfit.fitting.functions import lorentzian # freq, peak, width, amp
from bfit.fitting.functions import gaussian # freq, peak, width, amp
from bfit.fitting.functions import bilorentzian # freq, peak, width, amp
from bfit.fitting.functions import pulsed_exp # time, lambda_s, amp
from bfit.fitting.functions import pulsed_strexp # time, lambda_s, beta, amp

class FunctionPlacer(object):
    
    npts = 1000  # number of points used to draw line
    
    # ======================================================================= #
    def __init__(self,fig,data,fn_single,ncomp,p0,fnname,endfn,base=0):
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
        self.ncomp = ncomp
        self.base = base
        self.fn = lambda x,**kwargs : fn_single(x,**kwargs)+self.base
        self.fname = fnname
        self.endfn = endfn
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
    
        # make list of initial paramters 
        self.p0 = [{k:float(p[k].get()) for k in p.keys() if 'base' not in k} for p in p0]
    
        # baseline 
        if self.fname in ('Lorentzian','Gaussian'):
            self.base = float(p0[0]['base'].get())
            y = np.ones(len(self.x))*self.base
            self.baseline = self.ax.plot(self.x,y,zorder=20,ls='--')[0]
        else:
            self.base = 0
            self.baseline = dummybaseline()
    
        # draw each line with initial parameters
        self.lines = [self.ax.plot(self.x,
                                   fn_single(self.x,**self.p0[i])+self.base,
                                   zorder=20,ls='--')[0] for i in range(ncomp)]
        
        # make and draw function for the sum 
        self.sumfn = lambda x: np.sum([fn_single(x,**p) for p in self.p0],axis=0)+self.base
        self.sumline = self.ax.plot(self.x,self.sumfn(self.x),zorder=21,ls='-')[0]
        
        # reset ylims
        self.ax.set_ylim(ylims)
        
        # make title 
        self.ax.set_title('Press enter to save parameters',fontsize='small')
        self.fig.tight_layout()
        
        # connect enter key
        self.fig.canvas.mpl_connect('key_release_event',self.do_end)
        
        # resonance measurements ----------------------------------------------
        if self.fname in ('Lorentzian','Gaussian'):
            
            # if points are not saved they are garbage collected
            self.list_points = {'peak':[],'width':[]}
            
            # make points
            for i,(p,line) in enumerate(zip(self.p0,self.lines)):
                peakpt,widthpt = self.run_1f_single(p,line,'C%d'%(i+1))
                self.list_points['peak'].append(peakpt)
                self.list_points['width'].append(widthpt)
        
            self.list_points['base'] = self.run_1f_base(self.list_points['width'],'C0')
        
        # SLR measurements ----------------------------------------------------
        elif self.fname in ('Exp','Str Exp'):
            
            # if points are not saved they are garbage collected
            self.list_points = {'amp':[],'lam':[]}
            
            if self.fname == 'Str Exp':
                self.list_points['beta'] = []
            
            # make points
            for i,(p,line) in enumerate(zip(self.p0,self.lines)):
                self.list_points['amp'].append(self.run_20_initial(p,line,'C%d'%i))
                self.list_points['lam'].append(self.run_20_lambda(p,line,'C%d'%i))
                
                if self.fname == 'Str Exp':
                    self.list_points['beta'].append(self.run_20_beta(p,line,'C%d'%i))
            
            # connect point shifter
            self.fig.canvas.mpl_connect('button_release_event',self.shift_20_pts_resize)
            
    # ======================================================================= #
    def run_1f_base(self,widths,color):
        """
            widths: list of points for widths, need to update y values
        """
        
        def update_base(x,y):
            
            # base point
            oldbase = self.base
            self.base = y
            for i in range(len(self.p0)):
                self.p0[i]['amp'] -= oldbase-y
            
            # update width points
            for p0,wpoint,line in zip(self.p0,widths,self.lines): 
                wpoint.point.set_ydata(self.fn(p0['peak']+p0['width'],**p0))
                
                # update other lines
                line.set_ydata(self.fn(self.x,**p0))
            
            # update sumline
            self.sumline.set_ydata(self.sumfn(self.x))
            
            # update baseline line
            self.baseline.set_ydata(np.ones(self.npts)*self.base)    
            self.fig.canvas.draw()    
             
        # return so matplotlib doesn't garbage collect
        xpt = self.ax.get_xticks()[-1]
        return DraggablePoint(self,update_base,xpt,
                                 self.base,
                                 color=color,setx=False)
    
    # ======================================================================= #
    def run_1f_single(self,p0,line,color):
        
        # make point for width
        def update_width(x,y):
            
            # width point
            p0['width'] = abs(p0['peak']-x)
            
            # update line
            line.set_ydata(self.fn(self.x,**p0))
            
            # update sum line
            self.sumline.set_ydata(self.sumfn(self.x))
            self.fig.canvas.draw()    
             
        x = p0['peak']+p0['width']
        widthpt = DraggablePoint(self,update_width,x,self.fn(x,**p0),
                                 color=color,sety=False)
        
        # make point for peak
        def update_peak(x,y):
        
            # peak point
            p0['amp'] = self.base-y
            p0['peak'] = x
        
            # width point
            x2 = x+p0['width']
            widthpt.point.set_xdata(x2)
            widthpt.point.set_ydata(self.fn(x2,**p0))
            
            # update line
            line.set_ydata(self.fn(self.x,**p0))
            
            # update sum line
            self.sumline.set_ydata(self.sumfn(self.x))
            self.fig.canvas.draw()    
        
        peakpt = DraggablePoint(self,update_peak,p0['peak'],
                                self.base-p0['amp'],color=color)
        
        return (peakpt,widthpt)
        
    # ======================================================================= #
    def run_20_initial(self,p0,line,color):
        def update(x,y):
            # initial asymmetry
            p0['amp'] = max(0,y)
            line.set_ydata(self.fn(self.x,**p0))
            
            # update sumline
            self.sumline.set_ydata(self.sumfn(self.x))
            self.fig.canvas.draw()    
             
        # return so matplotlib doesn't garbage collect
        return DraggablePoint(self,update,0,p0['amp'],
                              color=color,setx=False)
    
    # ======================================================================= #
    def run_20_lambda(self,p0,line,color):
        def update(x,y):
            # 1/T1
            p0['lam'] = max(0,1/x)
            line.set_ydata(self.fn(self.x,**p0))
            
            # update sumline
            self.sumline.set_ydata(self.sumfn(self.x))
            self.fig.canvas.draw()    
             
        # return so matplotlib doesn't garbage collect
        x = np.ones(1)/p0['lam']
        ylim = self.ax.get_ylim()[0]
        y = min([i for i in self.ax.get_yticks() if i>ylim])
        return DraggablePoint(self,update,x,y,
                              color=color,sety=False)
    
    # ======================================================================= #
    def run_20_beta(self,p0,line,color):
        def update(x,y):
    
            # beta - put y axis on a range of 0 to 1
            ylo,yhi = self.ax.get_ylim()
            y = (y-ylo)/(yhi-ylo)
            p0['beta'] = y
            line.set_ydata(self.fn(self.x,**p0))
            
            # update sumline
            self.sumline.set_ydata(self.sumfn(self.x))
            self.fig.canvas.draw()    
             
        # return so matplotlib doesn't garbage collect
        ylo,yhi = self.ax.get_ylim()
        xlo,xhi = self.ax.get_xlim()
        x = max([i for i in self.ax.get_xticks() if i < xhi])
        return DraggablePoint(self,update,x,p0['beta']*(yhi-ylo)+ylo,
                              color=color,setx=False)
    
    # ======================================================================= #
    def shift_20_pts_resize(self,event):
        """Move the points so they fit in the screen"""
        
        xlo,xhi = self.ax.get_xlim()
        ylo,yhi = self.ax.get_ylim()
        
        for lam in self.list_points['lam']:
            ypos = lam.point.get_ydata()
            lam.point.set_ydata(min([i for i in self.ax.get_yticks() if i>ylo]))
        
        if 'beta' in self.list_points.keys():
            for beta in self.list_points['beta']:
                xpos = beta.point.get_xdata()
                beta.point.set_xdata(max([i for i in self.ax.get_xticks() if i<xhi])) 
    
    # ======================================================================= #
    def do_end(self,event):
        if event.key == 'enter':
            plt.close(self.fig.number)
            self.endfn(self.p0,self.base)
        

class dummybaseline(object):
    def __init__(self):pass
    def set_ydata(self,y) : pass
                
class DraggablePoint:

    # http://stackoverflow.com/questions/21654008/matplotlib-drag-overlapping-points-interactively
    # https://stackoverflow.com/questions/28001655/draggable-line-with-draggable-points
    
    lock = None #  only one can be animated at a time
    size=0.01

    # ======================================================================= #
    def __init__(self,parent,updatefn,x,y,setx=True,sety=True,color=None):
        """
            parent: parent object
            updatefn: funtion which updates the line in the correct way
                updatefn(xdata,ydata)
            x,y: initial point position
            setx,sety: if true, allow setting this parameter
            color: point color
        """
        self.parent = parent
        self.point = parent.ax.plot(x,y,zorder=25,color=color,alpha=0.5,
                                 marker='s',markersize=8)[0]
        
        self.point.set_pickradius(8)
        self.updatefn = updatefn
        self.setx = setx
        self.sety = sety
        self.press = None
        self.background = None
        self.connect()
        
    # ======================================================================= #
    def connect(self):
        """connect to all the events we need"""
        self.cidpress = self.point.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.point.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.point.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)

    # ======================================================================= #
    def on_press(self, event):
        if event.inaxes != self.point.axes: return
        if DraggablePoint.lock is not None: return
        contains, attrd = self.point.contains(event)
        if not contains: return
        DraggablePoint.lock = self
        
    # ======================================================================= #
    def on_motion(self, event):

        if DraggablePoint.lock is not self: return
        if event.inaxes != self.point.axes: return
        
        # get data
        x = event.xdata
        y = event.ydata
        
        # move the point
        if self.setx:   self.point.set_xdata(x)
        if self.sety:   self.point.set_ydata(y)

        # update the line
        self.updatefn(x,y)        

    # ======================================================================= #
    def on_release(self, event):
        'on release we reset the press data'
        if DraggablePoint.lock is not self: return
        DraggablePoint.lock = None
        
    # ======================================================================= #
    def disconnect(self):

        'disconnect all the stored connection ids'

        self.point.figure.canvas.mpl_disconnect(self.cidpress)
        self.point.figure.canvas.mpl_disconnect(self.cidrelease)
        self.point.figure.canvas.mpl_disconnect(self.cidmotion)
