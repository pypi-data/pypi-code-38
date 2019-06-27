import time
start = time.time()
from time import strftime
import sys

from os.path import *
home = expanduser("~")
import os
path = os.path.join(home, '.texteditrc\edit_settings.cfg')
his = os.path.join(home, '.texteditrc\history-debug.cfg')
import os


if not os.path.isfile(his):
    open(his, 'w+')
try:
    os.mkdir(os.path.dirname(path))
except:
    pass
if os.path.isfile(path):
    try:
        settings = eval(open(path).read())
    except:
        print('error while reading settings reseting the settings...', flush=True,file=sys.stderr)
        with open(path, 'w+') as fh:
            fh.write("{'font': 'Arial', 'size': 12, 'color': 'black', 'bg': 'white'}, 'text': 'normal'")
            settings={'font': 'Arial', 'size': 12, 'color': 'black', 'bg': 'white', 'text': 'normal'}
        print('done!')
        
else:
    with open(path, 'w+') as fh:
        fh.write("{'font': 'Arial', 'size': 12, 'color': 'black', 'bg': 'white'}, 'text': 'normal'")
        settings={'font': 'Arial', 'size': 12, 'color': 'black', 'bg': 'white', 'text': 'normal'}
def update_settings(event=None):
    global settings, path, font, size
    settings['size'] = size
    settings['font'] = font
    with open(path, 'w+') as fh:
        fh.write(str(settings))
v=sys.version
if "2.7" in v:
    from Tkinter import * 
    import tkFileDialog
else:
    from tkinter import *
    from tkinter.constants import *
    from tkinter.scrolledtext import ScrolledText as Text
    from tkinter import Tk
    import tkinter.filedialog as tkFileDialog
    from tkinter import messagebox as tkMessageBox
    from idlelib.undo import *
class _Text(Text, UndoDelegator):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        UndoDelegator.__init__(self)
DEBUG=False
if 'debug_run' in globals():
    DEBUG=True
def print_debug(*msg):
    import sys
    global DEBUG
    new = ''
    for i in msg:
        new += str(i)
    msg = new
    if DEBUG == True:
        print('DEBUG:', flush=True)
        print(msg,file=sys.stderr,flush=True)
def print_startup(*msg):
    import sys
    global DEBUG
    new = ''
    for i in msg:
        new += str(i)
    msg = new
    stamp = strftime("%Y-%m-%d %H:%M:%S")
    if DEBUG == True:
        print('DEBUG:', flush=True)
        print(f'startup info(startup on python: {sys.version}, time: {stamp}), on operation system: {sys.platform}, starting in debug mode')
        print(msg,file=sys.stderr,flush=True)
    else:
        if __name__ == '__main__':
            print(f'startup info(python version: {sys.version}, time: {stamp})')
            print(msg,file=sys.stderr,flush=True)

STARTUP = Print = PRINT_STARTUP = print_startup
print_debug('mode: ' + str(__name__))
print_debug("STARTING:")
print_debug("making Tk window")
root=Tk("Text Editor", 'file: ', 'Text Editor')
f = Frame(root)
f.grid(column=3, row=0, rowspan=4)
PRINT = debug_print = print_debug
PRINT('making text widget')
text=_Text(root, wrap=NONE, width=100, height=35)


def crash(event=None, *args, **kwargs):
    global root, text
    with open('backup.text', 'w+') as file:
        try:
            file.write(text.get('1.0', END))
        except:
            pass
    if __name__ == '__main__':
        tkMessageBox.showerror('ERROR!', 'restarting in debug mode')
        globals().update({'debug_run': True})
        root.destroy()
        del root
        exec(open(__file__).read(), globals())
    else:
        tkMessageBox.showerror('ERROR!', 'restarting in debug mode')
        root.destroy()
        globals().update({'debug_run': True})
        from os_sys import text_editor as te
        exec(open(te.__file__).read(), globals())



text.place(x=0,y=30,width=880,height=630)

PRINT('making menu buttons')
font_=Menubutton(root, text="File") 
font_.grid(row=0, sticky=W) 
font_.menu=Menu(font_, tearoff=0) 
font_["menu"]=font_.menu
Helvetica=IntVar() 
arial=IntVar() 
times=IntVar() 
Courier=IntVar()
run=Menubutton(root, text="Run")
run.place(x=60)
run.menu = Menu(run, tearoff=0)
run["menu"] = run.menu
edit=Menubutton(root, text="Edit") 
edit.place(x=90) 
edit.menu=Menu(edit, tearoff=0) 
edit["menu"]=edit.menu
#xscrollbar.config(command=text.xview)
#
# An Introduction to Tkinter
#
# Copyright (c) 1997 by Fredrik Lundh
#
# This copyright applies to Dialog, askinteger, askfloat and asktring
#
# fredrik@pythonware.com
# http://www.pythonware.com
#
"""This modules handles dialog boxes.

It contains the following public symbols:

SimpleDialog -- A simple but flexible modal dialog box

Dialog -- a base class for dialogs

askinteger -- get an integer from the user

askfloat -- get a float from the user

askstring -- get a string from the user
"""

from tkinter import *
from tkinter import messagebox

import tkinter # used at _QueryDialog for tkinter._default_root
PRINT('making dialog classes')
class SimpleDialog:

    def __init__(self, master,
                 text='', buttons=[], default=None, cancel=None,
                 title=None, class_=None):
        if class_:
            self.root = Toplevel(master, class_=class_)
        else:
            self.root = Toplevel(master)
        if title:
            self.root.title(title)
            self.root.iconname(title)
        self.message = Message(self.root, text=text, aspect=400)
        self.message.pack(expand=1, fill=BOTH)
        self.frame = Frame(self.root)
        self.frame.pack()
        self.num = default
        self.cancel = cancel
        self.default = default
        self.root.bind('<Return>', self.return_event)
        for num in range(len(buttons)):
            s = buttons[num]
            b = Button(self.frame, text=s,
                       command=(lambda self=self, num=num: self.done(num)))
            if num == default:
                b.config(relief=RIDGE, borderwidth=8)
            b.pack(side=LEFT, fill=BOTH, expand=1)
        self.root.protocol('WM_DELETE_WINDOW', self.wm_delete_window)
        self._set_transient(master)

    def _set_transient(self, master, relx=0.5, rely=0.3):
        widget = self.root
        widget.withdraw() # Remain invisible while we figure out the geometry
        widget.transient(master)
        widget.update_idletasks() # Actualize geometry information
        if master.winfo_ismapped():
            m_width = master.winfo_width()
            m_height = master.winfo_height()
            m_x = master.winfo_rootx()
            m_y = master.winfo_rooty()
        else:
            m_width = master.winfo_screenwidth()
            m_height = master.winfo_screenheight()
            m_x = m_y = 0
        w_width = widget.winfo_reqwidth()
        w_height = widget.winfo_reqheight()
        x = m_x + (m_width - w_width) * relx
        y = m_y + (m_height - w_height) * rely
        if x+w_width > master.winfo_screenwidth():
            x = master.winfo_screenwidth() - w_width
        elif x < 0:
            x = 0
        if y+w_height > master.winfo_screenheight():
            y = master.winfo_screenheight() - w_height
        elif y < 0:
            y = 0
        widget.geometry("+%d+%d" % (x, y))
        widget.deiconify() # Become visible at the desired location

    def go(self):
        self.root.wait_visibility()
        self.root.grab_set()
        self.root.mainloop()
        self.root.destroy()
        return self.num

    def return_event(self, event):
        if self.default is None:
            self.root.bell()
        else:
            self.done(self.default)

    def wm_delete_window(self):
        if self.cancel is None:
            self.root.bell()
        else:
            self.done(self.cancel)

    def done(self, num):
        self.num = num
        self.root.quit()


class Dialog(Toplevel):

    '''Class to open dialogs.

    This class is intended as a base class for custom dialogs
    '''

    def __init__(self, parent, title = None):

        '''Initialize a dialog.

        Arguments:

            parent -- a parent window (the application window)

            title -- the dialog title
        '''
        Toplevel.__init__(self, parent)

        self.withdraw() # remain invisible for now
        # If the master is not viewable, don't
        # make the child transient, or else it
        # would be opened withdrawn
        if parent.winfo_viewable():
            self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent

        self.result = None

        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        if self.parent is not None:
            self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                      parent.winfo_rooty()+50))

        self.deiconify() # become visible now

        self.initial_focus.focus_set()

        # wait for window to appear on screen before calling grab_set
        self.wait_visibility()
        self.grab_set()
        self.wait_window(self)

    def destroy(self):
        '''Destroy the window'''
        self.initial_focus = None
        Toplevel.destroy(self)

    #
    # construction hooks

    def body(self, master):
        '''create dialog body.

        return widget that should have initial focus.
        This method should be overridden, and is called
        by the __init__ method.
        '''
        pass

    def buttonbox(self):
        '''add standard button box.

        override if you do not want the standard buttons
        '''

        box = Frame(self)

        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    #
    # standard button semantics

    def ok(self, event=None):

        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        try:
            self.apply()
        finally:
            self.cancel()

    def cancel(self, event=None):

        # put focus back to the parent window
        if self.parent is not None:
            self.parent.focus_set()
        self.destroy()

    #
    # command hooks

    def validate(self):
        '''validate the data

        This method is called automatically to validate the data before the
        dialog is destroyed. By default, it always validates OK.
        '''

        return 1 # override

    def apply(self):
        '''process the data

        This method is called automatically to process the data, *after*
        the dialog is destroyed. By default, it does nothing.
        '''

        pass # override


# --------------------------------------------------------------------
# convenience dialogues
PRINT('making query dialog class')
class _QueryDialog(Dialog):

    def __init__(self, title, prompt,
                 initialvalue=None,
                 minvalue = None, maxvalue = None,
                 parent = None):

        if not parent:
            parent = tkinter._default_root

        self.prompt   = prompt
        self.minvalue = minvalue
        self.maxvalue = maxvalue

        self.initialvalue = initialvalue

        Dialog.__init__(self, parent, title)

    def destroy(self):
        self.entry = None
        Dialog.destroy(self)

    def body(self, master):

        w = Label(master, text=self.prompt, justify=LEFT)
        w.grid(row=0, padx=5, sticky=W)

        self.entry = Entry(master, name="entry")
        self.entry.grid(row=1, padx=5, sticky=W+E)

        if self.initialvalue is not None:
            self.entry.insert(0, self.initialvalue)
            self.entry.select_range(0, END)

        return self.entry

    def validate(self):
        try:
            result = self.getresult()
        except ValueError:
            messagebox.showwarning(
                "Illegal value",
                self.errormessage + "\nPlease try again",
                parent = self
            )
            return 0

        if self.minvalue is not None and result < self.minvalue:
            messagebox.showwarning(
                "Too small",
                "The allowed minimum value is %s. "
                "Please try again." % self.minvalue,
                parent = self
            )
            return 0

        if self.maxvalue is not None and result > self.maxvalue:
            messagebox.showwarning(
                "Too large",
                "The allowed maximum value is %s. "
                "Please try again." % self.maxvalue,
                parent = self
            )
            return 0

        self.result = result

        return 1

PRINT('making ask functions:')
class _QueryInteger(_QueryDialog):
    errormessage = "Not an integer."
    def getresult(self):
        return self.getint(self.entry.get())
PRINT('int')
def askinteger(title, prompt, **kw):
    '''get an integer from the user

    Arguments:

        title -- the dialog title
        prompt -- the label text
        **kw -- see SimpleDialog class

    Return value is an integer
    '''
    d = _QueryInteger(title, prompt, **kw)
    return d.result

class _QueryFloat(_QueryDialog):
    errormessage = "Not a floating point value."
    def getresult(self):
        return self.getdouble(self.entry.get())
PRINT('float')
def askfloat(title, prompt, **kw):
    '''get a float from the user

    Arguments:

        title -- the dialog title
        prompt -- the label text
        **kw -- see SimpleDialog class

    Return value is a float
    '''
    d = _QueryFloat(title, prompt, **kw)
    return d.result

class _QueryString(_QueryDialog):
    def __init__(self, *args, **kw):
        if "show" in kw:
            self.__show = kw["show"]
            del kw["show"]
        else:
            self.__show = None
        _QueryDialog.__init__(self, *args, **kw)

    def body(self, master):
        entry = _QueryDialog.body(self, master)
        if self.__show is not None:
            entry.configure(show=self.__show)
        return entry

    def getresult(self):
        return self.entry.get()
PRINT('string')
def askstring(prompt='', file=None, **kw):
    '''get a string from the user

    Arguments:

        title -- the dialog title
        prompt -- the label text
        **kw -- see SimpleDialog class

    Return value is a string
    '''
    title='input'
    
    d = _QueryString(title, prompt, **kw)
    return d.result
PRINT('ADDING COMMANDS TO MENU\'S')
root.resizable(False, False)
from idlelib.search import find, find_again, find_selection
PRINT('making func: show_find')
def show_find(event=None):
    find(text)
PRINT('making func: show_find_again')
def show_find_again(event=None):
    find_again(text)
PRINT('making func: show_find_selection')
def show_find_selection(event=None):
    find_selection(text)
PRINT('adding search')
edit.menu.add_command(label='search (ctrl-f)', command=show_find)
PRINT('adding find again')
edit.menu.add_command(label='find_again (ctrl-g)', command=show_find_again)
PRINT('adding find selection')
edit.menu.add_command(label='find selection (ctrl-f3)', command=show_find_selection)
def replace(event=None):
    replace1 = askstring('what do you want to replace:')
    replace2 = askstring('with:')
    global text
    t = text.get("1.0", "end-1c")
    text.delete(1.0, END)
    text.insert(END, t.replace(replace1,replace2))
from idlelib.replace import replace as rplc
PRINT('making rp(replace) func')
def rp():
    rplc(text)
PRINT('adding replace')
edit.menu.add_command(label='replace (ctrl-h)', command=rp)
PRINT(DEBUG)
debugger_on_now = DEBUG
from idlelib.colorizer import *
from idlelib.percolator import Percolator
DEBUG = debugger_on_now
PRINT('adding precolator')
p = Percolator(text)
PRINT(DEBUG)
if DEBUG:
    
    PRINT(p)
    PRINT(Percolator)
from idlelib.undo import *
from idlelib.delegator import Delegator
class Tracer(Delegator):
        def __init__(self, name):
            self.name = name
            self.delgate=text
            self.file=his

        def insert(self, *args):
            PRINT(self.name, ": insert", args)
            with open(self.file,'a') as fh:
                try:
                    fh.write(' '.join(args))
                except:
                    fh.write(str(args))
                fh.write('<<<,>>>')
            self.delegate.insert(*args)

        def delete(self, *args):
            PRINT(self.name, ": delete", args)
            with open(self.file,'a') as fh:
                try:
                    fh.write(' '.join(args))
                except:
                    fh.write(str(args))
                fh.write('<<<,>>>')
            self.delegate.delete(*args)
d = UndoDelegator()
PRINT('adding trace filter')
#_filter = Tracer('tracer')
#p.insertfilter(_filter)
import re
import string
text.insert('1.0', ' ')
text.edit_modified(False)
PRINT('making func: update_text_color')
def update_text_color(color):
    begin = time.time()
    color = color
    settings['color'] = color
    text.tag_add("here", "1.0", END)
    text.tag_config("here", foreground=color)
    if time.time() - begin > 0.2:
        crash()
try:
    update_text_color(settings['color'])
except:
    settings['color'] = 'black'
def command_root():
    try:
        text.tag_add("NONEANYTTESUGEUHFEUIHDSIHDUIDGSUYjhghgfgvbfdfvdfvvgfgfg", "1.0", END)
    except:
        pass
    try:
        pok
        text.tag_config("NONEANYTTESUGEUHFEUIHDSIHDUIDGSUYjhghgfgvbfdfvdfvvgfgfg", foreground=color)
    except:
        pass
    root.after(100, command_root)
root.after(10, command_root)
class Monkey(object):
    def __init__(self, filename):
        if filename == '':
            self.init = False
            return
        self._cached_stamp = os.stat(filename).st_mtime
        self.filename = filename
        self.init = True
        self.started = False
    def start(self):
        self.started = True
    def ook(self):
        if self.init == False:
            return
        if self.started == False:
            return
        stamp = os.stat(self.filename).st_mtime
        if stamp != self._cached_stamp:
            self._cached_stamp = stamp
            if tkMessageBox.askquestion('file edited', 'the file you have opened now is edited by someone or something else.\ndo you want to reload the file?'):
                open_(True)
            else:
                self._cached_stamp = stamp
    def off(self):
        self.started = False
    def on(self):
        self.started = True
    def reload(self):
        self.self._cached_stamp = os.stat(self.filename).st_mtime
    def update_filename(self,filename):
        self._cached_stamp = os.stat(filename).st_mtime
        self.filename = filename
        self.started = False
        self.init = True
monkey = Monkey('')
def update_bg(color):
    text['bg'] = color
    settings['bg'] = color
try:
    update_bg(settings['bg'])
except:
    settings['bg'] = 'white' 
p.insertfilter(d)
from threading import Thread
class thread(Thread):
    def __init__(self, start, handler, wait=5):
        super().__init__()
        self._start=start
        self.handler=handler
        self.wait_time=wait
    def run(self):
        import time
        self.done=False
        while time.time() - self._start <= self.wait_time:
            time.sleep(0.01)
        if self.done != False:
            return
        else:
            self.handler()
handler = thread
p.filter = True
def exec_return(code, re=globals(), debug=False, window=True):
    import sys
    from io import StringIO
    import contextlib
    class Proxy(object):
        def __init__(self,stdout,stringio):
            self._stdout = stdout
            self._stringio = stringio
        def __getattr__(self,name):
            if name in ('_stdout','_stringio','write'):
                object.__getattribute__(self,name)
            else:
                return getattr(self._stringio,name)
        def write(self,data):
             self._stdout.write(data)
             self._stringio.write(data)

    @contextlib.contextmanager
    def stdoutIO(stdout=None):
        old = sys.stdout
        if stdout is None:
            stdout = StringIO()
        sys.stdout = Proxy(sys.stdout,stdout)
        yield sys.stdout
        sys.stdout = old


    with stdoutIO() as s:
        request = re
        input = askstring
        re.update({'input': askstring})
        if not debug:
            exec(code, re)
        elif debug:
            count = 0
            line = 0
            errors = []
            l = code.split('\n')
            PRINT(len(l))
            for i in l:
                if i.startswith('    '):
                    continue
                try:
                    exec(i.replace('    ', ''), re)
                    PRINT(line+1)
                except Exception as ex:
                    PRINT(ex)
                    count += 1
                    errors.append({'count': count, 'line': line, 'traceback': str(ex), 'type': type(ex).__name__})
                line += 1
    if window:
        def thread():
            from tkinter import Tk as tk
            window = tk('text editor pyshell','text editor pyshell','text editor pyshell')
            from idlelib.percolator import Percolator
            txt = Text(window)
            pk = Percolator(txt)
            dp1 = ColorDelegator()
            from idlelib.undo import UndoDelegator
            dl = UndoDelegator()
            import re
            import string


            pk.insertfilter(dl)
            pk.insertfilter(dp1)
            txt.grid()
            txt.insert(END, s.getvalue())
            txt.insert(END, '\n>>> ')
            def exec_enter(event=None):
                al = txt.get('1.0', END)
                command=al.split('>>>')[-1]
                command=command.rstrip('\n')
                try:
                    out = exec_return(command, window=False)
                except Exception as ex:
                    out = str(ex.__class__).replace("<class '", '', 1).replace("'>", ' ', 1) + str(ex)
                txt.insert(END, '\n')
                txt.insert(END, out)
                txt.insert(END, '\n>>>')
            txt.bind('<Return>', exec_enter)
            window.mainloop()
        from threading import Thread
        thread_class = Thread(target=thread)
        thread_class.start()
        
            
        
        
    if not debug:
        return s.getvalue()
    elif debug:
        return [s.getvalue(), {'counts': count, 'errors': errors}]
def new_file(event=None):
    save()
    global text,file_name,root,file_open
    text.delete('1.0', END)
    file_name=''
    file_open=False
    root.title('Text Editor')
def execute(event=None):
    global text
    
    t = text.get("1.0", "end-1c")
    if text.edit_modified():
        tkMessageBox.showerror('ERROR!', 'you need to save an py file before execute')
        return
    try:
        out = exec_return(t)
    except Exception as ex:
        tkMessageBox.showerror('Error', ex.with_traceback(ex.__traceback__))
    except Warning as warn:
        tkMessageBox.showwarning('Warning!', warn)
    else:
        tkMessageBox.showinfo('succes! output:', out)
def debug(event=None):
    global text
    t = text.get("1.0", "end-1c")
    if text.edit_modified():
        tkMessageBox.showerror('ERROR!', 'you need to save an py file before execute')
        return
    try:
        out = exec_return(t, debug=True)
    except:
        pass
    error_data = out[1]
    if error_data['counts'] == 0:
        tkMessageBox.showinfo('error count:', 'errors counted:\n' + str(error_data['counts']))
        pass
    else:
        tkMessageBox.showinfo('error count:', 'errors counted:\n' + str(error_data['counts']))
        for i in error_data['errors']:
            tkMessageBox.showwarning(f'error {i["count"]}', f"""error in line {i['line']}:
    type: {i['type']}:
        in line {i['traceback']}
            traceback:{i[traceback]}""")
            
    tkMessageBox.showinfo('succes! output:', out[0])
run.menu.add_command(label="execute (F5)",
command=execute)
run.menu.add_command(label="debug (F6)", command=debug)
file_name=''
file_open = False
from tkinter import messagebox as tkMessageBox
warner = tkMessageBox.askokcancel
try:
    import docx
except:
    import os_sys.docx as docx

def getText(filename):
    doc = docx.getdocumenttext(docx.opendocx(filename))
    docs = []
    for i in doc:
        try:
            docs.append(''.join(i).replace('\n', '\n\n').replace('.', '.\n'))
        except:
            docs.append('error with processing this part of the file')
    return docs
def protocolhandler():
    now = time.time()
    global settings, size, font, root
    settings['size'] = size
    settings['font'] = font
    for i in range(0,3):
        update_settings()
    if file_name != '':
        save()
    PRINT('test')
    global DEBUG
    later = time.time()
    time_used = time.time() - now
    if time_used > 0.5:
        with open('backup.text', 'w+') as file:
            file.write(text.get('1.0', END))
        if __name__ == '__main__':
            tkMessageBox.showerror('ERROR!', 'restarting in debug mode')
            globals().update({'debug_run': True})
            root.destroy()
            del root
            exec(open(__file__).read(), globals())
        else:
            tkMessageBox.showerror('ERROR!', 'restarting in debug mode')
            root.destroy()
            globals().update({'debug_run': True})
            from os_sys import text_editor as te
            exec(open(te.__file__).read(), globals())
    if tkMessageBox.askokcancel("Exit", "Wanna leave?"):
        if DEBUG:
            PRINT('DEBUG:\nfirst')
        if tkMessageBox.askokcancel("Exit", "Are you sure?"):
            if DEBUG:
                PRINT('DEBUG:\nsecond')
            if text.edit_modified():
                if tkMessageBox.askokcancel("Exit", "Really? becuse there are un saved changes"):
                    pass
                else:
                    return
            if DEBUG:
                
                PRINT('destroy')
            root.destroy()
            if len(open(his).read()) >1000000000000000000000000:
                data = open(his).read()
                data = ''.join(data.split('<<<,>>>')[:100])
                with open(his, 'w+') as fh:
                    fh.write(data)
            
            for i in range(1001):
                try:
                    root.destroy()
                except:
                    pass
        else:
            PRINT('no')
            if DEBUG:
                PRINT('DEBUG:\nseccond say no')
root.protocol("WM_DELETE_WINDOW", protocolhandler)

class MultiStatusBar(Frame):

    def __init__(self, master, **kw):
        Frame.__init__(self, master, **kw)
        self.labels = {}

    def set_label(self, name, text='', side='left', width=0):
        if name not in self.labels:
            label = Label(self, borderwidth=0, anchor='w')
            label.pack(side=side, pady=0, padx=4)
            self.labels[name] = label
        else:
            label = self.labels[name]
        if width != 0:
            label.config(width=width)
        label.config(text=text)
n = Label(root)
n.place(y=659,x=0)
kk = Label(root)
kk.grid(row=3, column=0)
kk.place(y=659, x=50)
def update(event=None):
    global bar
    line, column = text.index(INSERT).split('.')
    n.config(text=f'line: {line}')
    kk.config(text=f'column: {column}')
    root.after(100, update)
root.after(100, update)
def check():
    global text
    if file_open:
        if text.edit_modified():
            return True
    return False
dp = ColorDelegator()

def open_(event=None):
    monkey.off()
    global text, dp, p
    global file_open
    if text.edit_modified():
        if warner('Warning!', 'you are going to close this file\n but you have un saved changes\n are you shure you want to lose the changes?'):
            pass
        else:
            return
    text.delete(1.0, END)
    global file_name
    if event != 'RESTART' and event != True:
        file_name = tkFileDialog.askopenfilename()
        
        monkey.update_filename(file_name)
    elif event == True:
         pass
    else:
        file_name = 'backup.text'
    if file_name.endswith('.py'):
        try:
            color_config(text)
            p.insertfilter(dp)
        except:
            pass
    else:
        try:
            p.removefilter(dp)
        except:
            pass
    if file_name.endswith('gjguix'):
        with open(file_name.replace('.docx', '.txt'), 'w+') as txt:
            txt.write('\n'.join(getText(file_name)))
        file_name=file_name.replace('.docx', '.txt')
    start = time.time()
    open_handler = handler(start,crash)
    open_handler.start()
    text.insert(END, open(file_name, 'rb').read())
    open_handler.done=True
    if time.time() - start > 5:
        crash()
    if event != 'RESTART':
        root.title(f'Text Editor    {file_name}')
    if event == 'RESTART':
        root.title('* Text Editor')
    file_open = True
    text.edit_modified(False)

    if '.py' in file_name:
        try:
            color_config(text)
            p.insertfilter(dp)
        except:
            pass
    else:
        try:
            p.removefilter(dp)
        except:
            pass
    global prev
    prev = text.get('1.0', END)
    monkey.start()
font_.menu.add_command(label="Open (ctrl-o)", command=open_) 

def saveas(event=None):
    monkey.off()
    global text
    global file_name
    t = text.get("1.0", "end-1c")
    if type(t) == type(''):
        t = t.encode()
    savelocation=tkFileDialog.asksaveasfilename()
    file1=open(savelocation, "wb")

    file1.write(t)

    file1.close()
    text.edit_modified(False)
    file_name = savelocation
    root.title(f'Text Editor    {file_name}')
    global prev
    prev = text.get('1.0', END)
    monkey.update_filename(file_name)
    global dp, p
    if '.py' in file_name:
        color_config(text)
        p.insertfilter(dp)
    else:
        try:
            p.removefilter(dp)
        except:
            pass
    monkey.reload()
    monkey.on()
font_.menu.add_command(label="Save as (ctrl-shift-s)", command=saveas) 
def monk():
    monkey.ook()
    root.after(100, monk)
root.after(100, monk)
if os.path.isfile('backup.text'):
    open_('RESTART')
    os.remove('backup.text')
def save(event=None):
    global dp, p
    global text
    global prev
    monkey.off()
    t = text.get("1.0", "end-1c")
    if type(t) == type(''):
        t = t.encode()
    global file_name
    if file_name == '':
        

        savelocation=tkFileDialog.asksaveasfilename()
        file1=open(savelocation, "wb")

        file1.write(t)

        file1.close()
        text.edit_modified(False)
        file_name = savelocation
        root.title(f'Text Editor    {file_name}')
        monkey.update_filename(file_name)
        prev = text.get('1.0', END)
        if '.py' in file_name:
            color_config(text)
            p.insertfilter(dp)
        else:
            try:
                p.removefilter(dp)
            except:
                pass
        monkey.reload()
        monkey.on()
        return
    savelocation=file_name

    file1=open(savelocation, "wb")

    file1.write(t)

    file1.close()
    text.edit_modified(False)
    prev = text.get('1.0', END)
    
    if '.py' in file_name:
        color_config(text)
        p.insertfilter(dp)
    else:
        try:
            p.removefilter(dp)
        except:
            pass
    monkey.reload()
    monkey.on()
font_.menu.add_command(label="Save (ctrl-s)", command=save)

size = settings['size']
font = settings['font']
fonts = ['System', 'Terminal', 'Fixedsys', 'Modern', 'Roman', 'Script', 'Courier', 'MS Serif', 'MS Sans Serif', 'Small Fonts', 'Marlett', 'Arial', 'Arabic Transparent', 'Arial Baltic', 'Arial CE', 'Arial CYR', 'Arial Greek', 'Arial TUR', 'Arial Black', 'Bahnschrift Light', 'Bahnschrift SemiLight', 'Bahnschrift', 'Bahnschrift SemiBold', 'Bahnschrift Light SemiCondensed', 'Bahnschrift SemiLight SemiConde', 'Bahnschrift SemiCondensed', 'Bahnschrift SemiBold SemiConden', 'Bahnschrift Light Condensed', 'Bahnschrift SemiLight Condensed', 'Bahnschrift Condensed', 'Bahnschrift SemiBold Condensed', 'Calibri', 'Calibri Light', 'Cambria', 'Cambria Math', 'Candara', 'Comic Sans MS', 'Consolas', 'Constantia', 'Corbel', 'Courier New', 'Courier New Baltic', 'Courier New CE', 'Courier New CYR', 'Courier New Greek', 'Courier New TUR', 'Ebrima', 'Franklin Gothic Medium', 'Gabriola', 'Gadugi', 'Georgia', 'Impact', 'Ink Free', 'Javanese Text', 'Leelawadee UI', 'Leelawadee UI Semilight', 'Lucida Console', 'Lucida Sans Unicode', 'Malgun Gothic', '@Malgun Gothic', 'Malgun Gothic Semilight', '@Malgun Gothic Semilight', 'Microsoft Himalaya', 'Microsoft JhengHei', '@Microsoft JhengHei', 'Microsoft JhengHei UI', '@Microsoft JhengHei UI', 'Microsoft JhengHei Light', '@Microsoft JhengHei Light', 'Microsoft JhengHei UI Light', '@Microsoft JhengHei UI Light', 'Microsoft New Tai Lue', 'Microsoft PhagsPa', 'Microsoft Sans Serif', 'Microsoft Tai Le', 'Microsoft YaHei', '@Microsoft YaHei', 'Microsoft YaHei UI', '@Microsoft YaHei UI', 'Microsoft YaHei Light', '@Microsoft YaHei Light', 'Microsoft YaHei UI Light', '@Microsoft YaHei UI Light', 'Microsoft Yi Baiti', 'MingLiU-ExtB', '@MingLiU-ExtB', 'PMingLiU-ExtB', '@PMingLiU-ExtB', 'MingLiU_HKSCS-ExtB', '@MingLiU_HKSCS-ExtB', 'Mongolian Baiti', 'MS Gothic', '@MS Gothic', 'MS UI Gothic', '@MS UI Gothic', 'MS PGothic', '@MS PGothic', 'MV Boli', 'Myanmar Text', 'Nirmala UI', 'Nirmala UI Semilight', 'Palatino Linotype', 'Segoe MDL2 Assets', 'Segoe Print', 'Segoe Script', 'Segoe UI', 'Segoe UI Black', 'Segoe UI Emoji', 'Segoe UI Historic', 'Segoe UI Light', 'Segoe UI Semibold', 'Segoe UI Semilight', 'Segoe UI Symbol', 'SimSun', '@SimSun', 'NSimSun', '@NSimSun', 'SimSun-ExtB', '@SimSun-ExtB', 'Sitka Small', 'Sitka Text', 'Sitka Subheading', 'Sitka Heading', 'Sitka Display', 'Sitka Banner', 'Sylfaen', 'Symbol', 'Tahoma', 'Times New Roman', 'Times New Roman Baltic', 'Times New Roman CE', 'Times New Roman CYR', 'Times New Roman Greek', 'Times New Roman TUR', 'Trebuchet MS', 'Verdana', 'Webdings', 'Wingdings', 'Yu Gothic', '@Yu Gothic', 'Yu Gothic UI', '@Yu Gothic UI', 'Yu Gothic UI Semibold', '@Yu Gothic UI Semibold', 'Yu Gothic Light', '@Yu Gothic Light', 'Yu Gothic UI Light', '@Yu Gothic UI Light', 'Yu Gothic Medium', '@Yu Gothic Medium', 'Yu Gothic UI Semilight', '@Yu Gothic UI Semilight', 'HoloLens MDL2 Assets', 'Agency FB', 'Algerian', 'Book Antiqua', 'Arial Narrow', 'Arial Rounded MT Bold', 'Baskerville Old Face', 'Bauhaus 93', 'Bell MT', 'Bernard MT Condensed', 'Bodoni MT', 'Bodoni MT Black', 'Bodoni MT Condensed', 'Bodoni MT Poster Compressed', 'Bookman Old Style', 'Bradley Hand ITC', 'Britannic Bold', 'Berlin Sans FB', 'Berlin Sans FB Demi', 'Broadway', 'Brush Script MT', 'Bookshelf Symbol 7', 'Californian FB', 'Calisto MT', 'Castellar', 'Century Schoolbook', 'Centaur', 'Century', 'Chiller', 'Colonna MT', 'Cooper Black', 'Copperplate Gothic Bold', 'Copperplate Gothic Light', 'Curlz MT', 'Dubai', 'Dubai Light', 'Dubai Medium', 'Elephant', 'Engravers MT', 'Eras Bold ITC', 'Eras Demi ITC', 'Eras Light ITC', 'Eras Medium ITC', 'Felix Titling', 'Forte', 'Franklin Gothic Book', 'Franklin Gothic Demi', 'Franklin Gothic Demi Cond', 'Franklin Gothic Heavy', 'Franklin Gothic Medium Cond', 'Freestyle Script', 'French Script MT', 'Footlight MT Light', 'Garamond', 'Gigi', 'Gill Sans MT', 'Gill Sans MT Condensed', 'Gill Sans Ultra Bold Condensed', 'Gill Sans Ultra Bold', 'Gloucester MT Extra Condensed', 'Gill Sans MT Ext Condensed Bold', 'Century Gothic', 'Goudy Old Style', 'Goudy Stout', 'Harlow Solid Italic', 'Harrington', 'Haettenschweiler', 'High Tower Text', 'Imprint MT Shadow', 'Informal Roman', 'Blackadder ITC', 'Edwardian Script ITC', 'Kristen ITC', 'Jokerman', 'Juice ITC', 'Kunstler Script', 'Wide Latin', 'Lucida Bright', 'Lucida Calligraphy', 'Leelawadee', 'Lucida Fax', 'Lucida Handwriting', 'Lucida Sans', 'Lucida Sans Typewriter', 'Magneto', 'Maiandra GD', 'Matura MT Script Capitals', 'Mistral', 'Modern No. 20', 'Microsoft Uighur', 'Monotype Corsiva', 'Niagara Engraved', 'Niagara Solid', 'OCR A Extended', 'Old English Text MT', 'Onyx', 'MS Outlook', 'Palace Script MT', 'Papyrus', 'Parchment', 'Perpetua', 'Perpetua Titling MT', 'Playbill', 'Poor Richard', 'Pristina', 'Rage Italic', 'Ravie', 'MS Reference Sans Serif', 'MS Reference Specialty', 'Rockwell Condensed', 'Rockwell', 'Rockwell Extra Bold', 'Script MT Bold', 'Showcard Gothic', 'Snap ITC', 'Stencil', 'Tw Cen MT', 'Tw Cen MT Condensed', 'Tw Cen MT Condensed Extra Bold', 'Tempus Sans ITC', 'Viner Hand ITC', 'Vivaldi', 'Vladimir Script', 'Wingdings 2', 'Wingdings 3', 'MT Extra']

def FontHelvetica():

    global text, font

    text.config(font="Helvetica")
    font="Helvetica"
def FontCourier():

    global text, font

    text.config(font="Courier")
    font="Courier"
def arial():
    global text,font
    text.config(font="Arial")
    font="Arial"
def down():
    global size,font
    size = size - 1
    settings['size'] = size
    if size < 1:
        size = 1
    text.config(font=(font, size, settings['text']))
def up():
    global size,font
    if size == 150:
        return
    size += 1
    settings['size'] = size
    text.config(font=(font, size, settings['text']))
def str_len(string):
    assert isinstance(string, str), 'needs to be an string'
    return len(string.encode("utf8"))
size_label = Label(root, text=f'file size {str_len(text.get("1.0", END))}')
size_label.place(x=220,y=659)
def update_size_label():
    size_label.config(text=f'file size {str_len(text.get("1.0", END))}')
    root.after(50, update_size_label)
root.after(100, update_size_label)
text.config(font=(font, size, settings['text']))
size_btn = Label(root, text=f'letter size: {size}')
size_btn.place(x=125,y=659)
def update_size_btn():
    global size_btn, size
    size_btn.config(text=f'letter size: {size}')
    root.after(50, update_size_btn)
root.after(100, update_size_btn)
f_ont=Menubutton(root, text="Font") 
f_ont.place(x=30) 
f_ont.menu=Menu(f_ont, tearoff=0) 
f_ont["menu"]=f_ont.menu
Helvetica=IntVar() 
arial=IntVar() 
times=IntVar() 
Courier=IntVar()
COLORS = ['snow', 'ghost white', 'white smoke', 'gainsboro', 'floral white', 'old lace',
    'linen', 'antique white', 'papaya whip', 'blanched almond', 'bisque', 'peach puff',
    'navajo white', 'lemon chiffon', 'mint cream', 'azure', 'alice blue', 'lavender',
    'lavender blush', 'misty rose', 'dark slate gray', 'dim gray', 'slate gray',
    'light slate gray', 'gray', 'light grey', 'midnight blue', 'navy', 'cornflower blue', 'dark slate blue',
    'slate blue', 'medium slate blue', 'light slate blue', 'medium blue', 'royal blue',  'blue',
    'dodger blue', 'deep sky blue', 'sky blue', 'light sky blue', 'steel blue', 'light steel blue',
    'light blue', 'powder blue', 'pale turquoise', 'dark turquoise', 'medium turquoise', 'turquoise',
    'cyan', 'light cyan', 'cadet blue', 'medium aquamarine', 'aquamarine', 'dark green', 'dark olive green',
    'dark sea green', 'sea green', 'medium sea green', 'light sea green', 'pale green', 'spring green',
    'lawn green', 'medium spring green', 'green yellow', 'lime green', 'yellow green',
    'forest green', 'olive drab', 'dark khaki', 'khaki', 'pale goldenrod', 'light goldenrod yellow',
    'light yellow', 'yellow', 'gold', 'light goldenrod', 'goldenrod', 'dark goldenrod', 'rosy brown',
    'indian red', 'saddle brown', 'sandy brown',
    'dark salmon', 'salmon', 'light salmon', 'orange', 'dark orange',
    'coral', 'light coral', 'tomato', 'orange red', 'red', 'hot pink', 'deep pink', 'pink', 'light pink',
    'pale violet red', 'maroon', 'medium violet red', 'violet red',
    'medium orchid', 'dark orchid', 'dark violet', 'blue violet', 'purple', 'medium purple',
    'thistle', 'snow2', 'snow3',
    'snow4', 'seashell2', 'seashell3', 'seashell4', 'AntiqueWhite1', 'AntiqueWhite2',
    'AntiqueWhite3', 'AntiqueWhite4', 'bisque2', 'bisque3', 'bisque4', 'PeachPuff2',
    'PeachPuff3', 'PeachPuff4', 'NavajoWhite2', 'NavajoWhite3', 'NavajoWhite4',
    'LemonChiffon2', 'LemonChiffon3', 'LemonChiffon4', 'cornsilk2', 'cornsilk3',
    'cornsilk4', 'ivory2', 'ivory3', 'ivory4', 'honeydew2', 'honeydew3', 'honeydew4',
    'LavenderBlush2', 'LavenderBlush3', 'LavenderBlush4', 'MistyRose2', 'MistyRose3',
    'MistyRose4', 'azure2', 'azure3', 'azure4', 'SlateBlue1', 'SlateBlue2', 'SlateBlue3',
    'SlateBlue4', 'RoyalBlue1', 'RoyalBlue2', 'RoyalBlue3', 'RoyalBlue4', 'blue2', 'blue4',
    'DodgerBlue2', 'DodgerBlue3', 'DodgerBlue4', 'SteelBlue1', 'SteelBlue2',
    'SteelBlue3', 'SteelBlue4', 'DeepSkyBlue2', 'DeepSkyBlue3', 'DeepSkyBlue4',
    'SkyBlue1', 'SkyBlue2', 'SkyBlue3', 'SkyBlue4', 'LightSkyBlue1', 'LightSkyBlue2',
    'LightSkyBlue3', 'LightSkyBlue4', 'SlateGray1', 'SlateGray2', 'SlateGray3',
    'SlateGray4', 'LightSteelBlue1', 'LightSteelBlue2', 'LightSteelBlue3',
    'LightSteelBlue4', 'LightBlue1', 'LightBlue2', 'LightBlue3', 'LightBlue4',
    'LightCyan2', 'LightCyan3', 'LightCyan4', 'PaleTurquoise1', 'PaleTurquoise2',
    'PaleTurquoise3', 'PaleTurquoise4', 'CadetBlue1', 'CadetBlue2', 'CadetBlue3',
    'CadetBlue4', 'turquoise1', 'turquoise2', 'turquoise3', 'turquoise4', 'cyan2', 'cyan3',
    'cyan4', 'DarkSlateGray1', 'DarkSlateGray2', 'DarkSlateGray3', 'DarkSlateGray4',
    'aquamarine2', 'aquamarine4', 'DarkSeaGreen1', 'DarkSeaGreen2', 'DarkSeaGreen3',
    'DarkSeaGreen4', 'SeaGreen1', 'SeaGreen2', 'SeaGreen3', 'PaleGreen1', 'PaleGreen2',
    'PaleGreen3', 'PaleGreen4', 'SpringGreen2', 'SpringGreen3', 'SpringGreen4',
    'green2', 'green3', 'green4', 'chartreuse2', 'chartreuse3', 'chartreuse4',
    'OliveDrab1', 'OliveDrab2', 'OliveDrab4', 'DarkOliveGreen1', 'DarkOliveGreen2',
    'DarkOliveGreen3', 'DarkOliveGreen4', 'khaki1', 'khaki2', 'khaki3', 'khaki4',
    'LightGoldenrod1', 'LightGoldenrod2', 'LightGoldenrod3', 'LightGoldenrod4',
    'LightYellow2', 'LightYellow3', 'LightYellow4', 'yellow2', 'yellow3', 'yellow4',
    'gold2', 'gold3', 'gold4', 'goldenrod1', 'goldenrod2', 'goldenrod3', 'goldenrod4',
    'DarkGoldenrod1', 'DarkGoldenrod2', 'DarkGoldenrod3', 'DarkGoldenrod4',
    'RosyBrown1', 'RosyBrown2', 'RosyBrown3', 'RosyBrown4', 'IndianRed1', 'IndianRed2',
    'IndianRed3', 'IndianRed4', 'sienna1', 'sienna2', 'sienna3', 'sienna4', 'burlywood1',
    'burlywood2', 'burlywood3', 'burlywood4', 'wheat1', 'wheat2', 'wheat3', 'wheat4', 'tan1',
    'tan2', 'tan4', 'chocolate1', 'chocolate2', 'chocolate3', 'firebrick1', 'firebrick2',
    'firebrick3', 'firebrick4', 'brown1', 'brown2', 'brown3', 'brown4', 'salmon1', 'salmon2',
    'salmon3', 'salmon4', 'LightSalmon2', 'LightSalmon3', 'LightSalmon4', 'orange2',
    'orange3', 'orange4', 'DarkOrange1', 'DarkOrange2', 'DarkOrange3', 'DarkOrange4',
    'coral1', 'coral2', 'coral3', 'coral4', 'tomato2', 'tomato3', 'tomato4', 'OrangeRed2',
    'OrangeRed3', 'OrangeRed4', 'red2', 'red3', 'red4', 'DeepPink2', 'DeepPink3', 'DeepPink4',
    'HotPink1', 'HotPink2', 'HotPink3', 'HotPink4', 'pink1', 'pink2', 'pink3', 'pink4',
    'LightPink1', 'LightPink2', 'LightPink3', 'LightPink4', 'PaleVioletRed1',
    'PaleVioletRed2', 'PaleVioletRed3', 'PaleVioletRed4', 'maroon1', 'maroon2',
    'maroon3', 'maroon4', 'VioletRed1', 'VioletRed2', 'VioletRed3', 'VioletRed4',
    'magenta2', 'magenta3', 'magenta4', 'orchid1', 'orchid2', 'orchid3', 'orchid4', 'plum1',
    'plum2', 'plum3', 'plum4', 'MediumOrchid1', 'MediumOrchid2', 'MediumOrchid3',
    'MediumOrchid4', 'DarkOrchid1', 'DarkOrchid2', 'DarkOrchid3', 'DarkOrchid4',
    'purple1', 'purple2', 'purple3', 'purple4', 'MediumPurple1', 'MediumPurple2',
    'MediumPurple3', 'MediumPurple4', 'thistle1', 'thistle2', 'thistle3', 'thistle4',
    'gray1', 'gray2', 'gray3', 'gray4', 'gray5', 'gray6', 'gray7', 'gray8', 'gray9', 'gray10',
    'gray11', 'gray12', 'gray13', 'gray14', 'gray15', 'gray16', 'gray17', 'gray18', 'gray19',
    'gray20', 'gray21', 'gray22', 'gray23', 'gray24', 'gray25', 'gray26', 'gray27', 'gray28',
    'gray29', 'gray30', 'gray31', 'gray32', 'gray33', 'gray34', 'gray35', 'gray36', 'gray37',
    'gray38', 'gray39', 'gray40', 'gray42', 'gray43', 'gray44', 'gray45', 'gray46', 'gray47',
    'gray48', 'gray49', 'gray50', 'gray51', 'gray52', 'gray53', 'gray54', 'gray55', 'gray56',
    'gray57', 'gray58', 'gray59', 'gray60', 'gray61', 'gray62', 'gray63', 'gray64', 'gray65',
    'gray66', 'gray67', 'gray68', 'gray69', 'gray70', 'gray71', 'gray72', 'gray73', 'gray74',
    'gray75', 'gray76', 'gray77', 'gray78', 'gray79', 'gray80', 'gray81', 'gray82', 'gray83',
    'gray84', 'gray85', 'gray86', 'gray87', 'gray88', 'gray89', 'gray90', 'gray91', 'gray92',
    'gray93', 'gray94', 'gray95', 'gray97', 'gray98', 'gray99', 'Black', 'Blue','Green','White']
def update_font(_font):
    global font
    font = _font
    settings['font'] = font
    bold = settings['text']
    text.config(font=(font, size, bold))
try:
    update_font(settings['font'])
except:
    update_font('Arial')
PRINT('sorting colors')
COLORS.sort(key=lambda s: s.casefold())
PRINT('sorting fonts')
fonts.sort(key=lambda s: s.casefold())
sizes=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150]
_bolds=['roman', 'italic', 'bold', 'normal']
def update_type(_font):
    settings['text'] = _font
    text.config(font=(settings['font'], settings['size'], settings['text']))
bolds = Menu(root)
f_ont.menu.add_cascade(label='letter styles', menu=bolds)
PRINT('adding letter styles')
for i in _bolds:
    PRINT('adding: ' + i)
    exec(f'''def {str(i.replace(' ', '_'))}():
    update_type('{i}')''', globals())
    bolds.add_command(label=i.capitalize(), command=eval(i.replace(' ', '_')))
fonts_menu = Menu(root)
f_ont.menu.add_cascade(label='fonts', menu=fonts_menu)
PRINT('adding fonts')
for i in fonts:
    PRINT('adding: '+i)
    exec(f'''def {str(i.replace(' ', '_')).replace('@', '_').replace('-', '_').replace('.', '_')}():
    update_font('{i}')''', globals())
    fonts_menu.add_command(label=i.capitalize(), command=eval(i.replace(' ', '_').replace('@', '_').replace('-', '_').replace('.', '_')))
f_ont.menu.add_command(label="smaller letters (ctrl-minus)", command=down)
f_ont.menu.add_command(label="bigger letters (ctrl-+)", command=up)
new = Menu(root)
f_ont.menu.add_cascade(label="colors", menu=new)
PRINT('adding colors')
for i in COLORS:
    PRINT('adding: '+i)
    exec(f'''def {str(i.replace(' ', '_'))}():
    update_text_color('{i}')''', globals())
    new.add_command(label=i, command=eval(i.replace(' ', '_')))
_NEW = Menu(root)
f_ont.menu.add_cascade(label="size", menu=_NEW)
PRINT('adding sizes')
for i in sizes:
    PRINT('adding: '+str(i))
    exec(f'''def _{i}():
    global text,font,size
    size = {i}
    text.config(font=(font, size, ''))''', globals())
    _NEW.add_command(label=i, command=eval('_' + str(i)))
NEW = Menu(root)
f_ont.menu.add_cascade(label="bg colors", menu=NEW)
PRINT('adding bg colors')
for i in COLORS:
    PRINT('adding: '+i)
    exec(f'''def _{str(i.replace(' ', '_'))}():
    update_bg('{i}')''', globals())
    NEW.add_command(label=i, command=eval('_' + i.replace(' ', '_')))
#outputwindow.insert('end',Details1)
def tab(event):
    begin = time.time()
    seltext = None
    try:
       seltext = text.get(SEL_FIRST, SEL_LAST)
    except TclError:
       pass

    if seltext != '' and seltext != None:
       text.delete(SEL_FIRST, SEL_LAST)
    info = text.winfo_pointerxy()
    text.insert(INSERT, ' ' * 4)
    if time.time() - start > 0.2:
        crash()
    return 'break'
def undo_event(event=None):
    d.undo_event(event)
    global added
    if added  <= 0:
        return
    added = added - 1
    from time import sleep
    sleep(0.05)
def redo_event(event=None):
    d.redo_event(event)
    global added
    added += 1
    from time import sleep
    sleep(0.05)
added = 0
prev = text.get('1.0', END)
def checker():
    begin = time.time()
    global text, prev
    if prev == text.get('1.0', END):
        root.title(f'Text Editor    {file_name}')
        prev = text.get('1.0', END)
        text.edit_modified(False)
    else:
        root.title(f'* Text Editor    {file_name}')
    if time.time() - begin > 0.15:
        crash()
    root.after(100, checker)
root.after(100, checker)
def add(event=None):
    global added
    added += 1
def rrkk():
    update_settings()
    root.after(200, rrkk)
root.after(100, rrkk)
def main():
    PRINT('MAIN:')
    global DEBUG, root
    if 'debug_run' in globals():
        DEBUG=True
    PRINT('binding key combinations')
    text.bind('<space>', add)
    text.bind('<a>', add)
    text.bind('<b>', add)
    text.bind('<c>', add)
    text.bind('<d>', add)
    text.bind('<e>', add)
    text.bind('<f>', add)
    text.bind('<g>', add)
    text.bind('<h>', add)
    text.bind('<i>', add)
    text.bind('<j>', add)
    text.bind('<k>', add)
    text.bind('<l>', add)
    text.bind('<m>', add)
    text.bind('<n>', add)
    text.bind('<o>', add)
    text.bind('<p>', add)
    text.bind('<q>', add)
    text.bind('<r>', add)
    text.bind('<s>', add)
    text.bind('<t>', add)
    text.bind('<u>', add)
    text.bind('<v>', add)
    text.bind('<w>', add)
    text.bind('<x>', add)
    text.bind('<y>', add)
    text.bind('<z>', add)
    text.bind('<A>', add)
    text.bind('<B>', add)
    text.bind('<C>', add)
    text.bind('<D>', add)
    text.bind('<E>', add)
    text.bind('<F>', add)
    text.bind('<G>', add)
    text.bind('<H>', add)
    text.bind('<I>', add)
    text.bind('<J>', add)
    text.bind('<K>', add)
    text.bind('<L>', add)
    text.bind('<M>', add)
    text.bind('<N>', add)
    text.bind('<O>', add)
    text.bind('<P>', add)
    text.bind('<Q>', add)
    text.bind('<R>', add)
    text.bind('<S>', add)
    text.bind('<T>', add)
    text.bind('<U>', add)
    text.bind('<V>', add)
    text.bind('<W>', add)
    text.bind('<X>', add)
    text.bind('<Y>', add)
    text.bind('<Z>', add)
    text.bind('<Tab>', tab)
    text.bind('<F5>', execute)
    text.bind('<F6>', debug)
    search=show_find
    text.bind('<Control-Shift-S>', saveas)
    text.bind('<Control-s>', save)
    text.bind('<Control-o>', open_)
    text.bind('<Control-Shift-s>', saveas)
    text.bind('<Control-S>', save)
    text.bind('<Control-O>', open_)
    text.bind('<Control-z>', undo_event)
    text.bind('<Control-Z>', undo_event)
    text.bind('<Control-Shift-z>', redo_event)
    text.bind('<Control-Shift-Z>', redo_event)
    text.bind('<Control-f>', search)
    text.bind('<Control-F>', search)
    text.bind('<Control-G>', show_find_again)
    text.bind('<Control-g>', show_find_again)
    text.bind('<F3>', show_find_again)
    text.bind('<Control-F3>', show_find_selection)
    text.bind('<Control-H>', rp)
    text.bind('<Control-h>', rp)
    def event_down(event=None):
        down()
    text.bind('<Control-_>', event_down)
    text.bind('<Control-minus>', event_down)
    def event_up(event=None):
        up()
    text.bind('<Control-+>', event_up)
    text.bind('<Control-=>', event_up)
    tracer =Tracer('tr')
    def do(event=None):
        tracer.insert((repr(event.char), event.char, event))
    
    PRINT('lift the root window')
    root.lift()
    PRINT('resizeing root window')
    root.geometry("950x700")
    PRINT('started main loop')
    end = time.time()
    end_time = end-start
    if DEBUG != True:
        if end_time > 3:
            crash()
    STARTUP(f'text editor startup completed in {end_time} sec')
    while True:
        try:
            root.mainloop()
            break
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception:
            PRINT('restarting mainloop after error')
            STARTUP(f'text editor restart')
if __name__ == '__main__':
    main()
