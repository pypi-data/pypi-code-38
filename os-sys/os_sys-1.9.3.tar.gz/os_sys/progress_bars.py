__all__ = ['bar', 'update_progress', 'show_progres', 'total_bar', 'tkinter_bars']
qSteps  = ['', u'\u258E',u'\u258C',u'\u258A']
import sys
import os

def total_bar(i):
    steps = i
    step = 'procent: ' + str(i)
    done    = u'\u2588'*i
    todo    = ' '*(25-len(done))
    barStr  = '[%s%s|]%s
'%(done, todo, step)
    sys.stderr.write(barStr + '
')

def bar(rn):
    



    loading = '\b' * rn  # for strings, * is the repeat operator


    # this loop replaces each dot with a hash!
    print('\r%s Loading at %3d percent!' % (loading, rn), end='
')
def update_progress(progress):
    barLength = 10 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r
"
    if progress < 0:
        progress = 0
        status = "Halt...\r
"
    if progress >= 1:
        progress = 1
        status = "Done...\r
"
    block = int(round(barLength*progress))
    text = "\rPercent: [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), progress*100, status)
    sys.stdout.write(text + '
')
    sys.stdout.flush()
p = 0
def show_progres(progres):
    global p
    import time, sys
    from tqdm import tqdm
    p += progres
    start = 0
    r = range(start, p)
    for i in tqdm(r):
        pass
    def reset():
        global p
        p = 0
from tkinter import *
import tkinter as Tkinter
import tkinter as tk
Tk().withdraw()
Tkinter.Tk().withdraw()
tk.Tk().withdraw()
import tkinter as tk

from tkinter import ttk            
class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.button = ttk.Button(text="start", command=self.start)
        self.button.pack()
        self.progress = ttk.Progressbar(self, orient="horizontal",
                                        length=200, mode="determinate")
        self.progress.pack()

        self.bytes = 0
        self.maxbytes = 0

    def start(self):
        self.progress["value"] = 0
        self.maxbytes = 50000
        self.progress["maximum"] = 200
        self.read_bytes()

    def read_bytes(self, progres):
        '''simulate reading 500 bytes; update progress bar'''
        
        self.progress["value"] = progres * 2
        



class tkinter_bars:
    def hide():
        try:
            Tk().withdraw()
        except:
            pass
        try:
            Tkinter.Tk().witdraw()
        except:
            pass
        try:
            tk.Tk().withdraw()
        except:
            pass
    class bar:
        def init(title):
            mGui = Tk()

            mGui.geometry('200x200')
            mGui.title(title)
            mpb = ttk.Progressbar(mGui,orient ="horizontal",length = 200, mode ="determinate")
            mpb.pack()
            mpb["maximum"] = 200
            mpb["value"] = 0
            mpb.update()
        def update_bar(progres):
            try:
                mpb['value'] = progres * 2
            except Exception:
                print('Warning!: you need to init bar first')
                return
            
        def kill():
            mGui.withdraw()
            del mpb
            del mGui
    class bar2:
        def init():
            app = SampleApp()
            u = app.read_bytes
            def update(i):
                u(i)
                app.update()
            update(0)
        def update_bar(progres):
            update(progres)
        def kill():
            del update, app, u
            



