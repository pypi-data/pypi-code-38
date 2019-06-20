#! python3

# __main__.py - A GUI Calculator
# -*- coding: UTF-8 -*-

from tkinter import Tk, Button, Entry, StringVar
""" import all the necessary modules """

statement = ""
""" create the variable of the math statement """

def press(num):
    global statement
    statement += str(num)
    equation.set(statement)
""" Create the press function to take the pressed button and input it into the statement """

def equal():
    try:
        global statement
        total = str(eval(statement))
        equation.set(total)

        statement = ""

    except:
        equation.set(" error ")
        statement = ""
""" creating the equal function to represent what the statement should interpret when given an expression  """

def clear():
    global statement
    statement = ""
    equation.set("")
""" creating the clear function to interpret what to do when we press the clear button """

### MAIN CODE

calculator = Tk() # Creating the windows
calculator.configure(background="blue") # Color the background of the calculator
calculator.title("Calculator") # Title of the window
calculator.geometry("263x150") # Setting the width and height of the application
calculator.resizable(0, 0) # Stating that the application cannot be resized.
equation = StringVar() # creating a value holder for string variables
statement_field = Entry(calculator, textvariable=equation) # Entry widget which allows displaying simple text.
statement_field.grid(columnspan=4, ipadx=70) # tells where to place the entry field
equation.set("Enter your statement! Let us start!") # sets the starting message
# CREATING ALL THE BUTTONS
plus = Button(calculator, text= " + ", fg="black", bg="white", command=lambda: press("+"), height=1, width=7)
plus.grid(row=2, column=0)
buttonOne = Button(calculator, text=" 1 ", fg="black", bg="white", command=lambda: press(1), height=1, width=7)
buttonOne.grid(row=2, column=1)
buttonTwo = Button(calculator, text=" 2 ", fg="black", bg="white", command=lambda: press(2), height=1, width=7)
buttonTwo.grid(row=2, column=2)
buttonThree = Button(calculator, text=" 3 ", fg="black", bg="white", command=lambda: press(3), height=1, width=7)
buttonThree.grid(row=2, column=3)
minus = Button(calculator, text=" - ", fg="black", bg="white", command=lambda: press("-"), height=1, width=7)
minus.grid(row=3, column=0)
buttonFour = Button(calculator, text=" 4 ", fg="black", bg="white", command=lambda: press(4), height=1, width=7)
buttonFour.grid(row=3, column=1)
buttonFive = Button(calculator, text=" 5 ", fg="black", bg="white", command=lambda: press(5), height=1, width=7)
buttonFive.grid(row=3, column=2)
buttonSix = Button(calculator, text=" 6 ", fg="black", bg="white", command=lambda: press(6), height=1, width=7)
buttonSix.grid(row=3, column=3)
multiply = Button(calculator, text=" * ", fg="black", bg="white", command=lambda: press("*"), height=1, width=7)
multiply.grid(row=4, column=0)
buttonSeven = Button(calculator, text=" 7 ", fg="black", bg="white", command=lambda: press(7), height=1, width=7)
buttonSeven.grid(row=4, column=1)
buttonEight = Button(calculator, text=" 8 ", fg="black", bg="white", command=lambda: press(8), height=1, width=7)
buttonEight.grid(row=4, column=2)
buttonNine = Button(calculator, text=" 9 ", fg="black", bg="white", command=lambda: press(9), height=1, width=7)
buttonNine.grid(row=4, column=3)
divide = Button(calculator, text=" / ", fg="black", bg="white", command=lambda: press("/"), height=1, width=7)
divide.grid(row=5, column=0)
point = Button(calculator, text=" . ", fg="black", bg="white", command=lambda: press("."), height=1, width=7)
point.grid(row=5, column=1)
zero = Button(calculator, text=" 0 ", fg="black", bg="white", command=lambda: press(0), height=1, width=7)
zero.grid(row=5, column=2)
clearButton = Button(calculator, text=" C ", fg="black", bg="white", command=clear, height=1, width=7)
clearButton.grid(row=5, column=3)
equalButton = Button(calculator, text=" = ", fg="black", bg="white", command=equal, height=1, width=7)
equalButton.grid(row=6, columnspan=4)
calculator.mainloop() # Run the main application
