#!/usr/bin/env python3
from IPython.core.magic import register_line_cell_magic
import ipywidgets as ip
import subprocess as sub
import pty
import tty
from select import select
import os
import sys
import re
from IPython.core.display import HTML, display, Javascript
from threading import Thread
from time import sleep

class Stream:
    def __init__(self,out):
        self.out = out
        self.buf = b''
    def write(self,buf):
        self.buf += buf
    def flush(self):
        if len(self.buf) > 0:
            self.out.append_stdout(self.buf.decode())
            self.buf = b''

def bashin(cmd,tmp_file):
    textinput = ['']

    pid = [-1]
    killed = [False]
    sig = [2]

    def kill_proc(button):
        if pid[0] >= 0:
            try:
                ret = os.killpg(pid[0],sig[0])
            except ProcessLookupError as pe:
                # Process is already dead, stop
                # trying to kill it
                pid[0] = -1
                return
            killed[0] = True
            if sig[0] == 2:
                sig[0] = 9

    status = ip.Label(value="Status: Running, Input:")
    textw = ip.Text()
    readtext = [False]

    def settext(tf):
        textinput[0] = textw.value
        readtext[0] = True
        textw.value = ''

    textw.on_submit(settext)
    outw = ip.Output()
    strw = Stream(outw)
    killb = ip.Button(description="Kill")
    killb.on_click(kill_proc)
    hb = ip.HBox([status,textw,killb])
    display(ip.VBox([hb,outw]))

    killed[0] = False
    m, s = pty.openpty()
    # For some reason, os.kill does not work.
    # Therefore we use setsid to make a process
    # group and use os.killpg
    proc = sub.Popen(cmd,
                     preexec_fn=os.setsid,
                     stdout=s,
                     stderr=s,
                     stdin=s,
                     bufsize=1,
                     close_fds=True)
    os.close(s)
    pid[0] = proc.pid
    n = 0
    wait = .5
    sleep_time = 0
    while True:
         n += 1
         # Unless this sleep statement executes,
         # input text or buttons cannot be
         # processed.
         sleep(sleep_time)
         sleep_time = 0
         r, w, e = select([m],[],[],wait)
         if len(r) == 0 or n == 50:
             strw.flush()
             n = 0
             if tmp_file is not None:
                 os.remove(tmp_file)
                 tmp_file = None
         if killed[0]:
             strw.write(b" ** Killed **")
             break
         elif m in r:
             try:
                o = os.read(m,1)
                if o == b'\n':
                    sleep_time = 0.1
                strw.write(o) 
             except OSError as oe:
                break
         elif readtext[0]:
             n=os.write(m,textinput[0].encode()+b'\n')
             textinput[0] = ''
             readtext[0] = False
         elif proc.poll() is None:
             pass
         else:
             break
    strw.flush()
    textw.disabled = True
    killb.disabled = True
    status.value = "Status: Done, Input:"
    if tmp_file is not None:
         os.remove(tmp_file)

@register_line_cell_magic
def jbash(line,cell=None):
    thread = None
    tf = None
    if cell is None or cell.strip()=="":
        line = line.strip()
        if line == "bash":
            cmd = ["bash"]
        else:
            cmd = ["bash","-c",line]
    else:
        tf = os.environ["HOME"]+"/.temp_shell_%d.sh" % os.getpid()
        with open(tf,"w") as fd:
            print(cell,file=fd)
        cmd = ["bash",tf]
    thread = Thread(target=bashin,args=(cmd,tf))
    thread.start()

def load_ipython_extension(shell):
    shell.register_magic_function(jbash,'line_cell')
    #shell.register_magics(jbash)
