import os
import curses
from .menu import Tree, Text
from .menu import msgBox, Application, ColorConfig

class FileTree(Tree):

    def get_left_cursor(self):
        p = self.cursor if not self.cursor.endswith("/") else self.cursor[:-1]
        p = os.path.dirname(p)
        return p
    
    def get_right_cursor(self):
        item = self.m.datas[self.m.ix]
        d = os.path.join(self.cursor, item)
        if os.path.isdir(d):
            return d
        return  self.cursor
  
    def get_parent(self, cursor):
        p = self.get_left_cursor()
        return os.listdir(p)
    
    def get_sub(self, cursor, item=None):
        i = self.get_right_cursor()
        if os.path.isdir(i):
            d = os.listdir(i)
            if not d:
                d.append("")
            return  d
        return  ['']
    
    def get_current(self, cursor):
        return  os.listdir(cursor)

    def update_when_cursor_change(self, item, ch):
        s = self.get_sub(self.cursor, item)
        self.r.datas = s
        Application.instance.refresh(clear=True)

        msgBox(msg="%d/%d%% %s" % (self.m.ix, self.m.height, self.cursor))

if __name__ == "__main__":
    main = Application()
    
    e = Text(id='text')
    
    t = FileTree(os.path.expanduser("~/Documents"))
    main.focus("middle")
    main.add_widget(e)
    
    curses.wrapper(main.loop)
    curses.endwin()



