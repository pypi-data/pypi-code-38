import sys

v=sys.version
if "2.7" in v:
    from Tkinter import * 
    import tkFileDialog
else:
    from tkinter import *
    from tkinter import Tk
    import tkinter.filedialog as tkFileDialog
root=Tk("Text Editor", 'file: ', 'Text Editor')
text=Text(root) 
text.grid()
file_name=''
file_open = False
from tkinter import messagebox as tkMessageBox
warner = tkMessageBox.askokcancel
def protocolhandler():
    if tkMessageBox.askokcancel("Exit", "Wanna leave?"):
        if tkMessageBox.askokcancel("Exit", "Are you sure?"):
            if text.edit_modified():
                if tkMessageBox.askokcancel("Exit", "Really? becuse there are un saved changes"):
                    pass
                else:
                    return
            root.destroy()
root.protocol("WM_DELETE_WINDOW", protocolhandler)
def check():
    global text
    if file_open:
        if text.edit_modified():
            return True
    return False
def open_():
    global text
    global file_open
    if file_open and text.edit_modified():
        if warner('Warning!', 'you are going to close this file\n but you have un saved changes\n are you shure you want to lose the changes?'):
            pass
        else:
            return
    text.delete(1.0, END)
    global file_name
    file_name = tkFileDialog.askopenfilename()
    text.insert(END, open(file_name, 'rb').read())
    root.title(f'Text Editor    {file_name}')
    file_open = True
button=Button(root, text="Open", command=open_) 
button.grid()
def saveas():

    global text
    global file_name
    t = text.get("1.0", "end-1c")

    savelocation=tkFileDialog.asksaveasfilename()
    if type(t) == type(bytes()):
        file1=open(savelocation, "wb")
    else:
        file1=open(savelocation, "w+")

    file1.write(t)

    file1.close()
    text.edit_modified(False)
    file_name = savelocation
button=Button(root, text="Save as", command=saveas) 
button.grid()

def save():

    global text

    t = text.get("1.0", "end-1c")
    global file_name
    if file_name == '':
        tkMessageBox.showerror('error', 'no file open\nchoise an file to open or:\nmake an new file with save as')
        return
    savelocation=file_name

    if type(t) == type(bytes()):
        file1=open(savelocation, "wb")
    else:
        file1=open(savelocation, "w+")

    file1.write(t)

    file1.close()
    text.edit_modified(False)
button=Button(root, text="Save", command=save) 
button.grid()
def FontHelvetica():

    global text

    text.config(font="Helvetica")
def FontCourier():

    global text

    text.config(font="Courier")
font=Menubutton(root, text="Font") 
font.grid() 
font.menu=Menu(font, tearoff=0) 
font["menu"]=font.menu
Helvetica=IntVar() 
arial=IntVar() 
times=IntVar() 
Courier=IntVar()

font.menu.add_command(label="Courier",
command=FontCourier)
font.menu.add_command(label="Helvetica",
command=FontHelvetica) 
root.mainloop()
