import curses
from .menu import Application, Stack, CheckBox, msgBox, Text, Menu, TextPanel, Map
from .event import listener
from .map import map_res

if __name__ =="__main__":
    main = Application()
    import random
    r2 = Map(map_res)
    # r2 = Map2(map_res)
    main.add_widget(r2, id='map')
    main.focus("map")
    curses.wrapper(main.loop)
    