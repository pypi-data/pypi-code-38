import re
import curses
from termcolor import COLORS, RESET, ATTRIBUTES, HIGHLIGHTS
from .log import log

C_R = {'\x1b[%dm'%v: 'COLOR_%s' % k.upper() for k,v in COLORS.items()}
A_R = {'\x1b[%dm'%v: 'A_%s' % k.upper() for k,v in ATTRIBUTES.items()}
H_R = {'\x1b[%dm'%v: 'COLOR_%s' % k[3:].upper() for k,v in HIGHLIGHTS.items()}
COLORS_R = {'\x1b[%dm'%v:k for k,v in COLORS.items()} 
COLOR_SCAN = re.compile(r'(\x1b\[\d+m)')

def ascii2filter(words):
    if isinstance(words, list):
        strings = COLOR_SCAN.sub('',' '.join(words)).split()
    else:
        strings = COLOR_SCAN.sub('',words)
    return strings


def ascii2curses(context,row,col,string, colors=None):
    attr = None 
    color = None
    strings = COLOR_SCAN.split(string)

    first = strings.pop(0)
    
    attr = 0
    color = 0
    if first:
        if colors.last_use_color:
            color = colors.last_use_color 
        if colors.last_use_attr:
            a = colors.last_use_attr
            if a in A_R:
                attr = A_R[a]
            context.addstr(row, col,first, attr | colors.get(color))
        else:
            context.addstr(row, col,first)
        col += len(first)
    for i in range(len(strings)//2):
        a,msg = strings[i*2:(i+1)*2]

        if a in A_R and hasattr(curses, A_R[a]):
            attr = getattr(curses, A_R[a])
            #log(attr)
        elif a in COLORS_R:
            color = COLORS_R[a]
        elif a == RESET:
            attr = 0
            color = 0

        if msg:
            #log(msg,row,col, COLORS_R[a],first)
            context.addstr(row,col,msg, attr |  colors.get(color))
            col += len(msg)

    colors.last_use_color = color
    colors.last_use_attr = attr


