#!/usr/bin/env python3

from tkinter import *
import pyperclip
from ccfunctions import *

#### Main Window:
window = Tk()
window.title("CCypher")
window.geometry('750x350') #Width x Height
window.config(background="white")

v = IntVar()
v.set(2)  # Initialize on/off button selection to 'off' when window opens.
g = IntVar()

# Click to run function
def clickRun():
    enteredText = inBox.get(0.0, END)  #This collects text from text entry box
    outBox.delete(0.0, END)
    outputText = ''
    try:
        if g.get() == 1:
            outputText = superEncrypt(enteredText)
            outLabel.configure(text="Output:Encrypted")
        elif g.get() == 2:
            outputText = superEncrypt(enteredText, 'decrypt')
            outLabel.configure(text="Output:Decrypted")
    except:
        if enteredText == '':
            outputText = "No text entered. \nPlease enter some text and try again."
    outBox.insert(END, outputText)

# Configure enabled/disabled cypher widgets
def buttonConfig():
    if v.get() == 1:
        g.set(1)
        c.configure(state=NORMAL)
        c2.configure(state=NORMAL)
        cLabel.configure(state=NORMAL)
        inLabel.configure(state=NORMAL)
        inBox.configure(state=NORMAL)
        inBox.focus_set()
        outBox.configure(state=NORMAL)
        runButton.configure(state=NORMAL)
        outLabel.configure(state=NORMAL)
        clearInButton.configure(state=NORMAL)
        clearOutButton.configure(state=NORMAL)
        copyOutButton.configure(state=NORMAL)
    elif v.get() == 2:
        g.set(0)
        c.configure(state=DISABLED)
        c2.configure(state=DISABLED)
        cLabel.configure(state=DISABLED)
        inLabel.configure(state=DISABLED)
        inBox.configure(state=DISABLED)
        outLabel.configure(state=DISABLED)
        outBox.configure(state=DISABLED)
        runButton.configure(state=DISABLED)
        clearInButton.configure(state=DISABLED)
        clearOutButton.configure(state=DISABLED)
        copyOutButton.configure(state=DISABLED)

def copyOut():
    outText = outBox.get(0.0, END)
    try:
        pyperclip.copy(outText)
    except:
        pyperclip.copy(pyperclip.paste())

def clearInBox():
    inBox.delete(0.0, END)
    
def clearOutBox():
    outBox.delete(0.0, END)

def copySel(event):
    thisCopy = event.widget.get(SEL)
    pyperclip.copy(thisCopy)

def pasteSel(event):
    thisPaste = pyperclip.paste()
    event.widget.insert(INSERT, thisPaste)

# Blank Row
inLabel = Label(window, text="", bg="white", fg="white", font="none 12 bold")
inLabel.grid(row=5, column=0, sticky=W)
    
# Input text box label
inLabel = Label(window, text="Input: Origional Text", bg="white", fg="black", font="none 12 bold")
inLabel.grid(row=7, column=0, sticky=W)

# Input text box
inBox = Text(window, width=40, height=6, wrap=WORD, bg="white")
inBox.grid(row=8, column=0, columnspan=2, sticky=W)
inBox.configure(bd=3, relief=RIDGE)
inBox.bind("<Command-C>", copySel)
inBox.bind("<Command-P>", pasteSel)

# 'Clear Inbox Text' Button
clearInButton = Button(window, text="CLEAR", width=6, command=clearInBox)
clearInButton.grid(row=7, column=1, sticky=W)

# 'Clear Outbox Text' Button
clearOutButton = Button(window, text="CLEAR", width=6, command=clearOutBox)
clearOutButton.grid(row=7, column=4, sticky=E)

# 'Run' Button
runButton = Button(window, text="RUN", width=6, command=clickRun)
runButton.grid(row=8, column=2, sticky=W)

# Output text box label
outLabel = Label(window, text="Output:Encrypted", bg="white", fg="black", font="none 12 bold")
outLabel.grid(row=7, column=3, sticky=W)

# Output text box
outBox = Text(window, width=40, height=6, wrap=WORD, bg="white",)
outBox.grid(row=8, column=3, columnspan=2, sticky=W)
outBox.configure(bd=3, relief=RIDGE)
outBox.bind("<Key>", lambda e: "break")
outBox.bind("<Command-C>", copySel)

# 'Copy Output' Button
copyOutButton = Button(window, text="COPY", width=6, command=copyOut)
copyOutButton.grid(row=7, column=4, sticky=W)

# Cypher Encrypt/Decrypt Label
cLabel = Label(window, text="Encryption Type: ", bg="white", fg="black", font="none 12 bold")
cLabel.grid(row=2, column=1, sticky=W)

# Cypher Encrypt/Decrypt Buttons
c = Radiobutton(window, text="Encrypt Input Text", variable=g, value=1, bg="white", fg="black")
c2 = Radiobutton(window, text="Decrypt Input Text", variable=g, value=2, bg="white", fg="black")
c.grid(row=3, column=1, sticky=W)
c2.grid(row=4, column=1, sticky=W)

# Function is called to initialize configurations
buttonConfig()

# Title Label
Label(window, text="CCYPHER", bg="white", fg="red", font="none 20 bold") .grid(row=1, column=0, sticky=NS)

# Cypher On/Off Label
Label(window, text="Toggle Cypher: ", bg="white", fg="black", font="none 12 bold") .grid(row=2, column=0, sticky=W)

# On/Off Checkboxes
b = Radiobutton(window, text="Cypher On", variable=v, command=buttonConfig, value=1, bg="white", fg="black")
b2 = Radiobutton(window, text="Cypher Off", variable=v, command=buttonConfig, value=2, bg="white", fg="black")
b.grid(row=3, column=0, sticky=W)
b2.grid(row=4, column=0, sticky=W)

# Blank Row
inLabel = Label(window, text="", bg="white", fg="white", font="none 12 bold")
inLabel.grid(row=9, column=0, sticky=W)

# Exit label
Label(window, text="Click to exit", bg="white", fg="black", font="none 12 bold") .grid(row=10, column=0, sticky=NS)

# Exit function
def close_window():
    window.destroy()
    sys.exit()

# Add an exit button
Button(window, text="EXIT", width=10, command=close_window) .grid(row=11, column=0, sticky=NS)

# Weight added to widgets in widow


#### Run the main loop
window.mainloop()
