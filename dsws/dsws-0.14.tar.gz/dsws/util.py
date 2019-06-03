"""
Data Science Workspace Utility

Collection of utility functions used throughout the workspace
connection types:
 - pretty: formatted table output for jupyter sessions
 - sp: subprocess call wrapper for OS operations
 - which_ui: centralize method to determine environment
 from only environment variables and sys.platform
 - launch_term: launches a cli tool in a terminal, determines
 environment within the method
 - launch_url: launches a webpage, works only within jupyter
 and CDSW
 - standard_conn_qry: returns the standard qry form for dsws type conn
 - standard_sess_qry: returns the standard qry form for dsws type sess
 - no_return: helper function for when no return data expected
"""

import subprocess
import os
import sys
import os
from IPython.core.display import display
from IPython.core.display import HTML
import numpy as np
import re
import shlex
import time 


def pretty(df, max_lines=50, col="lightgray"):
    df = df[:max_lines].to_html(index=False)
    df = df.replace('<th>','<th style="text-align:center;background-color:%s">' % col)
    display(HTML("<div align=center>" + df + "</div>"))


def sp(cmd_lst,shell=False):
    alt_env = os.environ.copy()
    #REF: Haven't neded yet, can use alt_env
    #alt_env["PATH"] = "/usr/bin:" + alt_env["PATH"]
    sp = subprocess.Popen(cmd_lst, env=alt_env, 
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          shell=shell)
    return(sp.communicate())

def which_ui():
    if 'CDSW_ENGINE_ID'   in os.environ:
        return 'cdsw'
    elif 'JPY_PARENT_PID' in os.environ:
        return 'jupyter'
    elif 'PYCHARM_HOSTED' in os.environ:
        return 'pycharm'
    elif 'RSTUDIO' in os.environ:
        return 'rstudio'
    elif sys.platform == 'linux':
        return 'edgenode'
    elif sys.platform == 'darwin':
        return 'local_mac'
    elif sys.platform in ["win32","msys"]:
        return 'local_win'
    else:
        return 'unknown'
  
def launch_term(cli=''):
    ui = which_ui() 
    if ui in ['cdsw','jupyter']:
        if ui == 'cdsw':
            id=os.environ["CDSW_ENGINE_ID"]
            cd=os.environ["CDSW_DOMAIN"]
            tp = [p for p in sp(["ps","aux"])[0].split() \
                  if b'--path' in p][0][8:]
            url="http://tty-%s.%s/%s/"%(id,cd,tp.decode('utf8'))
            picker=['.','.picker']
        elif ui == 'jupyter':
            # by convention, we want jupyter to run from our project root which has an nb folder:
            url = ['..',]
            picker = []
            path = os.getcwd().split('/')
            while 'nb' not in os.listdir('/'.join(path)):
                url.append('..')
                picker.append('..')
                path = path[:-1]
            url.append('terminals')
            url.append(cli.split(' ')[0].split('-')[0])
            url = '/'.join(url)
            picker.append('.picker')
        else:
            url = 'about:blank'
        with open("/".join(picker),"wb") as f:
            f.write(cli.encode('utf8'))
        script='<script type="text/Javascript">window.open("%s");</script>'%url
        display(HTML(script))
        time.sleep(6) 
        with open("/".join(picker),"wb") as f:
            f.write(''.encode('utf-8'))
    else:
        print('TODO: Write unsupported environment')

def launch_url(url=None):
    """
    Launches url, intended for cdsw and jupyter environments
    """
    script='<script type="text/Javascript">window.open("%s");</script>'%url
    display(HTML(script))
    time.sleep(4)
    
def standard_conn_qry(qry):
    """
    Standard form for connection queries
    
    Allows grouping of commands using ";" seperator
    Each command can have the following form:
       Standard executable statement
       single file, read as sql
    """
    if qry.__class__ == str:
        qry=[q for q in qry.split(";") if q!='']
    rslt=[]
    for q in qry:
        if q[0]=="-":
            q=" ".join(q.split()[1:]).strip('"').strip("'")
        if "." in q.split()[0]:
            f==q.split()[0]
            if "/" not in f:
                os.environ['PROJECT_HOME']="/home/cdsw"
                f=os.environ['PROJECT_HOME']+"/sql/"+f
            f=open(f,'r')
            l=[x for x in f.read().split('\n') if x[:2]!='--']
            q=[re.sub('\\s+',' ',x) for x in " ".join(l).split(";") if x!='']
        rslt+=[q,]
    return(rslt)


def standard_sess_qry(qry):
    """
    Standard form for session queries
    
    Does not allow grouping of commands using ";" seperator
    only first query selected if found.
    Each command can have the following form:
       Standard executable statement
       single file, read as sql
    """
    if qry.__class__ == str:
        qry=qry.split(";")[0]
    q=qry
    if "." in q.split()[0]:
        f==q.split()
        if "/" not in f:
            os.environ['PROJECT_HOME']="/home/cdsw"
            f=os.environ['PROJECT_HOME']+"/sql/"+f
        f=open(f,'r')
        l=[x for x in f.read().split('\n') if x[:2]!='--']
        q=[re.sub('\\s+',' ',x) for x in " ".join(l).split(";") if x!='']
    return(q)

def no_return(qry):
    """
    Query logic to capture queries that have no return
    other than successfull or not"""
    return(("CREATE TABLE" in qry.upper()) |
           (("SELECT" not in qry.upper()) & ("SHOW" not in qry.upper())) )