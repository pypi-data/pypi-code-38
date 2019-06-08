from graphics import *
import time
import keyboard

windowName = "PyMaker"
width = 500
height = 500
bgcolor = "white"
fps = 60

cpright = True
loadingtext = "Made with PyMaker"

win = GraphWin(windowName, width, height, autoflush=True)
if (cpright == True):
    win.setBackground("white")
    text1 = Text(Point(250, 250), loadingtext)
    ltext = Text(Point(250, 270), "Loading...")
    text1.draw(win)
    ltext.draw(win)
    time.sleep(1)
win.close()

objects = []

def init():

    global windowName
    global width
    global height
    global bgcolor
    global fps
    global win

    win = GraphWin(windowName, width, height, autoflush=False)

def frame():

    update(fps)

    for x in range(len(objects)):
        objects[x].undraw()

    del objects[0 : len(objects) - 1]

def drawpixel(x, y):
    r = Rectangle(Point(x, y), Point(x + 10, y + 10))
    r.setFill("black")

    try:
        r.draw(win)
    except:
        sys.exit()


    objects.append(r)

def drawrectangle(x, y, x2, y2):
    r = Rectangle(Point(x, y), Point(x2, y2))
    r.setFill("black")

    try:
        r.draw(win)
    except:
        sys.exit()

    objects.append(r)

def drawcircle(x, y, rad):
    c = Circle(Point(x, y), rad)
    c.setFill("black")

    try:
        c.draw(win)
    except:
        sys.exit()

    objects.append(c)

def drawtext(x, y, text):
    t = Text(Point(x, y), text)
    
    try:
        t.draw(win)
    except:
        sys.exit()

    objects.append(t)

def keypressed(key):
    if (keyboard.is_pressed(key)):
        return True
    else:
        return False

def getkey():
    keyString = win.checkKey()
    return keyString
