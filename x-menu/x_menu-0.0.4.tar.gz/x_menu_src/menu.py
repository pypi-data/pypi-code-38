import curses
import os, sys
import re
from .event import EventMix, listener
from .log import log
from .charactors import SYMBOL
from curses.textpad import Textbox, rectangle
import time


def msgBox(screen=None, msg='None'):
    if not screen:
        screen = curses.initscr()
    _,w = screen.getmaxyx()
    msg = msg + ' ' * (w-len(msg) -1 )
    screen.addstr(0, 0, msg, curses.A_REVERSE)
    screen.refresh()

def infoShow(screen, win):
    cy,cx = screen.getyx()
    h,w = screen.getmaxyx()
    wh = win.height
    ww = win.width
    msgBox(screen, "id:%s yx:%d,%d ix:%d  py:%d, height:%d, screen_h:%d screen_w:%d cur:%d" % (win.id, cy,cx, win.ix, win.py, wh, h,ww, win.cursor))

class ColorConfig:
    config = {
        'label':11,
        'normal':2,
        'spicial':3,
        'link':4,
        'finish':9,
        'attrs':5,
        'map':6,
        'green':7,
    }
    @classmethod
    def default(cls):
        curses.init_pair(cls.config['finish'],curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(cls.config['attrs'],curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(cls.config['label'], curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(cls.config['normal'],curses.COLOR_RED , curses.COLOR_BLACK)
        curses.init_pair(cls.config['link'],curses.COLOR_BLUE , curses.COLOR_BLACK)
        curses.init_pair(cls.config['map'],curses.COLOR_WHITE , curses.COLOR_BLACK)
        curses.init_pair(cls.config['green'],curses.COLOR_GREEN , curses.COLOR_WHITE)

    @classmethod
    def get(cls, label):
        return curses.color_pair(cls.config.get(label, 'normal'))


class Application(EventMix):
    height,width = 0,0
    widgets = {}
    extra_widgets = []
    instance = None
    editor = None
    last_focus = None
    init_screen = None
    top = 1
    def __init__(self, top_margin=1):
        self.border = 1
        self.borders = []
        self.screen = None#curses.initscr()
        # self.widgets = {}
        self.widgets_opts = {}
        self.top = top_margin
        self.ids = []
        Application.top = self.top
        if Application.instance is None:
            Application.instance = self

    def __setitem__(self, id, widget, **kargs):
        self.widgets_opts[id].update(kargs)
        self.__class__.widgets[id] = widget

    def __getitem__(self, id):
        return  self.__class__.widgets[id]

    @property
    def weight(self):
        return float(self.size[1]) / sum([self.widgets_opts[i]['weight'] for i in self.widgets_opts])

    @classmethod
    def Size(cls):
        if cls.init_screen is None:
            cls.init_screen = curses.initscr()
            curses.start_color()
            ColorConfig.default()
        Application.height, Application.width = cls.init_screen.getmaxyx()
        return Application.height, Application.width


    @property
    def size(self):
        Application.height, Application.width = self.screen.getmaxyx()
        return Application.height, Application.width

    def add_widget(self, widget,id=None, weight=1, direct='r', **kargs):
        kargs.update({
            'weight':weight,
        })

        if not id:
            if widget.id:
                id = widget.id
        if not id:
            id = os.urandom(8).hex()
        widget.top = self.top

        #import pdb;pdb.set_trace();

        if direct == 'r':
            if len(self.ids) > 0:
                widget.left_widget = self.__class__.widgets[self.ids[-1]]
                self.__class__.widgets[self.ids[-1]].right_widget = widget
            self.ids.append(id)
        else:
            if len(self.ids) > 0:
                widget.right_widget = self.__class__.widgets[self.ids[0]]
                self.__class__.widgets[self.ids[0]].left_widget = widget
            self.ids.insert(0, id)

        self.__class__.widgets[id] = widget
        self.widgets_opts[id] = kargs

    def clear_widget(self):
        self.widgets_opts = {}
        self.ids = []
        self.__class__.widgets = {}

    def del_widget(self, id):
        del self.widgets_opts[id]
        self.ids.remove(id)
        del self.__class__.widgets[id]


    def update_all(self, top=1,ch=None):
        width_weight = self.weight
        now_x = 0
        is_not_first = False
        for widget in self.widgets.values():
            if widget.focus:
                widget.action_listener(ch)

        for widget in self.__class__.extra_widgets:
            if widget.focus:
                widget.action_listener(ch)

        for id, widget in self.widgets.items():
            if isinstance(widget, Text):continue
            if hasattr(widget, 'update_widgets'):
                widget.update_widgets()
            ops = self.widgets_opts[id]
            y = top
            pad_width = int(ops['weight'] * width_weight)
            widget.update(self.screen,y,now_x, pad_width,ch=ch)
            if is_not_first:
                self.draw_extra(y, now_x)

            now_x += pad_width
            if not is_not_first:
                is_not_first = True

        for widget in self.__class__.extra_widgets:
            widget.update(self.screen, ch=ch)

        if ch:
            self.ready_key(ch)

    def focus(self, idx):
        for v in self.widgets.values():
            v.focus = False
        self.widgets[idx].focus = True

    @classmethod
    def LossFocus(cls):
        for i,v in cls.widgets.items():
            if v.focus:
                v.focus = False
                cls.last_focus = i
    @classmethod
    def ResumeFocus(cls):
        cls.Focus(cls.last_focus)

    @classmethod
    def Focus(cls, idx):
        cls.widgets[idx].focus = True

    def draw_extra(self, y ,x):
        if self.border:
            # self.draw_border(y, x)
            pass

    def draw_border(self, y ,x):
        h,_ = self.size
        for r in range(self.top,h):
            self.screen.addch(r,x-1, ord('|'))

    def refresh(self,focus=None, k=0, clear=False):
        if self.screen == None:
            return
        if clear:
            self.screen.clear()

        if focus:
            self.focus(focus)
        # import pdb;pdb.set_trace()
        self.update_all(self.top, ch=k)
        curses.doupdate()
        self.screen.refresh()
        # self.screen.refresh()


    def loop(self, stdscr):
        k = 0
        if not self.screen:
            self.screen = stdscr
        curses.curs_set(0)
        # curses.keypad(1)
        self.refresh(clear=True)

        ColorConfig.default()
        c = -1
        while k != ord('q'):
            if c == -1:
                self.refresh(k=k)
                c  = 1
            # else:
                # self.refresh(k=k, clear=True)
            self.refresh(k=k)
            # msgBox(stdscr, "type: %d " % k)

            k = self.screen.getch()
            #self.screen.clear()
            #self.screen.refresh()



    @classmethod
    def get_widget_by_id(cls, id):
        return cls.widgets.get(id)

class _Textbox(Textbox):

    def __init__(self, win, insert_mode=True):
        super(_Textbox, self).__init__(win, insert_mode)


    def do_command(self, ch):
        if ch == 127:  # BackSpace
            Textbox.do_command(self, 8)

        return Textbox.do_command(self, ch)

class Text(EventMix):

    def __init__(self,content=None,title=None, id=None,y=None,x=None,width=80, height=30, **ops):
        self.screen = None
        self.cursor = 0
        self.border = 1
        self.focus = False
        self.left_widget = None
        self.right_widget = None
        self.id = id
        self.pad = None
        self.top = 0

        self.px = None
        self.py = None
        self.Spy, self.Spx = None, None
        self.text = ''

        Height, Width  =  Application.Size()
        #Height = min([Height, height])
        #Width = min([Width, width])
        if not y or not x:

            self.height = Height // 3
            self.width = Width -3
            self.rect = [self.height * 2 , 0, Height-2, Width -3]
            self.loc = [self.height - 3 , self.width -1 , self.height * 2 + 1, 1]
            self.msg = None
            self.title = "Ctrl-G to exit "
        else:
            if x + width > Width:
                x = Width - width -3
            if y + 4 > Height:
                y = Height - 8

            if width + x >= Width -3:
                self.width = Width -3 - x
            else:
                self.width = width

            if y + height  > Height - 3:
                self.height = Height -3 - y
            else:
                self.height = height


            if content:
                self.text = content
                # height = len(content) // self.width
                height = content.count('\n')
                log('hh', height)
                if height < 2:
                    height =2
            else:
                height = 2

            if height + y >= Height -3 :
                # self.height = Height - 2 - y
                y = Height -3 - height
                self.height = height
            else:
                self.height = height
            log('x',x,'heigt:', height, 'self.height', self.height)
            log('App:', Height, Width)


            self.rect = [y , x, y + self.height , x + self.width]
            self.loc = [self.height - 1, self.width -1 , y+1, x +1]
            self.msg = None
            self.title = "Ctrl-G to exit " if not title else title

            log('rect:', self.rect)


        if not Application.editor:
            Application.editor = self

    def update(self, screen, pad_width=30,pad_height=30,ch=None, draw=True, style='label',title=None):
        if not self.screen:
            self.screen = screen
        if title:
            self.title = title
        stdscr = self.screen

        log('self.loc', self.loc)
        lines = self.text.split("\n")
        if len(lines) > self.loc[0]:
            self.rect[2] += len(lines) - self.loc[0]
            self.loc[0] = len(lines)
        editwin = curses.newwin(*self.loc)
        curses.curs_set(1)
        if self.text:
            for row, l in enumerate(lines):
                log('row', row, len(l))
                editwin.addstr(row,0, l.strip()[:self.width])

        rectangle(stdscr, *self.rect)
        log('self.loc', self.loc, 'self.rect', self.rect)
        if style == 'label':
            msg = ' '+ self.title + (self.width - len(self.title) - 2) * ' ' if self.width - len(self.title) > 2 else self.title
            stdscr.addstr(self.rect[0]-1, self.rect[1]+1, msg, curses.A_BOLD | curses.A_REVERSE | ColorConfig.get('label') )
        else:
            msg = 'ctrl + G exit: ' + str(title)
            stdscr.addstr(self.rect[0], self.rect[1]+4, msg, curses.A_BOLD |  ColorConfig.get('map') )
        stdscr.refresh()

        box = _Textbox(editwin)

        # Let the user edit until Ctrl-G is struck.
        box.edit()

        # Get resulting contents
        message = box.gather()
        curses.curs_set(0)
        self.msg = message
        Application.instance.refresh(clear=True)

    @classmethod
    def Popup(cls,content=None,context=None, screen=None,title=None, y=None,x=None,height=20, width=80, **opts ):
        if context:
            y,x = context.cursor_yx
            y+=2
            x+=3
            screen = context.screen
        editor = cls(title=title,content=content, id='text', y=y, x=x, width=width, height=height, **opts)
        #if height:
        #    editor.height = height
        editor.update(screen, pad_height=height,title=title, style=opts.get('style'))
        return editor.msg


class Stack(EventMix):
    last_popup = None

    def __init__(self, datas,id=None,mode='chains',border_len=1, **opts):
        self.screen = None
        self.datas = datas
        self.cursor = 0

        self.focus = False
        self.left_widget = None
        self.right_widget = None
        self.id = id
        self.pad = None
        self.top = 0
        self.ix = 0
        self.px = None
        self.py = None
        self.Spy, self.Spx = None, None
        self.c_y,self.c_x = 0,0
        self.mode = mode
        self.border_len = border_len
        self.start_y,self.start_x = 0,0
        self.end_y = 0

    @property
    def cursor_yx(self):
        return self.c_y + self.py, self.c_x + self.px

    @property
    def width(self):
        return max([len(i.encode()) for i in self.datas])
    @property
    def height(self):
        return len(self.datas)

    def update_when_cursor_change(self, item, ch=None):
        infoShow(self.screen, self)

    @listener("k")
    def up(self):
        if self.cursor > 0 and self.py == self.Spy:
            self.cursor -= 1
        elif self.cursor == 0 and self.py == self.Spy:
            self.py = self.end_y - self.border_len * 2 - self.start_y - 1
            if self.height > Application.height:
                self.cursor = self.height -  self.end_y + self.start_y + self.border_len * 2
                # self.py += self.border_len * 2 -1
            # infoShow(self.screen, self)
        else:
            if self.py > 0:
               self.py -= 1
               self.screen.move(self.py ,self.px)
            #    infoShow(self.screen, self)

            #self.py -= 1
        self.ix -= 1
        if self.ix < 0:
            self.ix = self.height - 1
        log("ix:",self.ix)
        self.update_when_cursor_change(self.get_text(self.ix), ch="k")

    @listener('?')
    def show_help(self):
        msg = '\n'.join([ str(chr(k).encode()) + ":" + str(k)+":  "+v for k,v in self.instances.items() if hasattr(self, v) ])
        Text.Popup(context=self,title='show key to handle, Ctrl+G exit and change keymap',content=msg)


    @listener('h')
    def left(self):
        if self.left_widget and self.mode == 'chains':
            self.focus = False
            self.left_widget.focus = True
            # infoShow(self.screen,self.left_widget)
        self.update_when_cursor_change(self.get_text(self.ix), ch="h")

    @listener('l')
    def right(self):
        # invoid right and right and right,
        # only right -> id's window
        if self.right_widget and self.mode == 'chains':
            self.focus = False
            self.right_widget.focus = True
            # infoShow(self.screen,self.right_widget)
        self.update_when_cursor_change(self.get_text(self.ix), ch="l")

    @listener("j")
    def down(self):

        sm = self.end_y
        if self.py >= self.end_y - self.start_y  - self.border_len*2 - 1:
            if self.py + self.cursor >= self.height -1 :
                self.cursor = 0
                self.py = self.Spy
                self.ix = 0
            else:
                # msgBox(msg="if")
                self.cursor += 1
                self.ix += 1
            # infoShow(self.screen, self)
        elif self.py > sm -1 - self.start_y and self.cursor < sm:
            # msgBox(msg='elif')
            if self.height > self.end_y:
                self.cursor += 1
                self.ix += 1
            else:
                self.cursor = 0
                self.py = self.Spy
                self.ix = 0
            # infoShow(self.screen, self)
        else:
            # msgBox(msg='else')
            # infoShow(self.screen, self)
            self.py += 1
            self.screen.move(self.py ,self.px)
            self.ix += 1
            # infoShow(self.screen, self)
        # self.ix += 1
        if self.ix >= self.height - 1:
            self.ix = 0
        self.ix = self.py + self.cursor    


        self.update_when_cursor_change(self.get_text(self.ix), ch="j")

    @listener(10)
    def enter(self):
        msgBox(self.screen," hello world")
        # r_x = self.width
        # r_y = self.py
        text = Application.get_widget_by_id("text")
        if text:
            text.update(self.screen)



    def _show(self,text):
        time.sleep(0.03)
        TextPanel.Cl()
        self.Redraw()
        TextPanel.Popup(text, screen=self.screen,x=self.width//2, y=self.ix + 10, focus=False, width=len(text)+3)
    def show(self, text):
        Stack.run_background(self._show, text)

    def get_input(self, title):
        res = Text.Popup(content='', height=0,screen=self.screen, x=self.width // 4,y = self.ix+5, max_height=1, exit_key=10, style='norm', title=title)
        return res

    def update(self, screen, y=None, x=None, pad_width=None,pad_height=None,ch=None, draw=True,refresh=False):
        if not self.screen:
            self.screen = screen
        self.start_y,self.start_x = y,x
        max_heigh,_ = Application.Size()
        if pad_height:
            max_heigh = min([max_heigh, y + pad_height])
        max_heigh = min([max_heigh, y + self.height + self.border_len * 2])
        self.end_y = max_heigh
        if self.py is None:
            # self.py,self.px = screen.getyx()
            # self.Spy, self.Spx = screen.getyx()
            self.py,self.px = 0,0
            # log(self.id,max_heigh, self.py, self.px)
            self.Spy, self.Spx = 0,0
        datas = self.datas
        # log('y',y)
        cursor = self.cursor
        if isinstance(datas, list):

            datas = datas[cursor:cursor+ max_heigh - y - self.border_len]
        else:
            datas = dict(list(datas.items())[cursor:cursor+ max_heigh - y - self.border_len ])


        if draw:
            self.draw(datas, screen, y,x , pad_width, refresh=refresh)

    def on_text(self,msg ,ix):
        return msg

    def get_text(self, ix, datas=None):
        if not datas:
            datas = self.datas
        if isinstance(datas, dict):
            return self.on_text(list(datas.keys())[ix], ix)
        else:
            try:
                return self.on_text(str(datas[ix]), ix)
            except IndexError:
                return self.on_text('',ix)

    def get_now_text(self):
        if isinstance(self.datas, list):
            return self.on_text(self.datas[self.ix], self.ix)
        else:
            return self.on_text(list(self.datas.keys())[self.ix], self.ix)

    def draw_text(self,row, col, text,max_width=None, attrs=1,prefix='',prefix_attrs=None, mark=False):
        if mark:
            attrs |= curses.A_REVERSE
            # self.pad.addstr(row, col, text,curses.A_REVERSE | attrs )
        if prefix:
            if prefix_attrs:
                self.pad.addstr(row, col, prefix, prefix_attrs)
            else:
                self.pad.addstr(row, col, prefix)
            text = self.padding_space(text, max_width, mark=mark)
            self.pad.addstr(text, attrs)
        else:
            text = self.padding_space(text, max_width, mark=mark)
            self.pad.addstr(row, col, text, attrs)

    def padding_space(self, content, max_width, mark=False, direct='r'):
        content = content.replace("\n","")
        content = content[:max_width-2] if len(content.encode()) >= max_width -2 else content
        if mark:
            if direct == 'r':
                msg = content + ' '*  (max_width - len(content.encode()) -3)
            else:
                msg =  ' '*  (max_width - len(content.encode()) -3) + content
        else:
            if direct != 'r':
                msg =  ' '*  (max_width - len(content.encode()) -3) + content
            else:
                msg = content
        return msg

    def draw(self,datas,screen,y,x, max_width,refresh=False):
        border_len = self.border_len
        max_h = self.end_y - y
        self.pad = curses.newpad(max_h, max_width)
        self.end_x = self.start_x + max_width
        self.c_y, self.c_x = y, x

        # if self.py == 0:
        #     self.py += border_len
        for row in range(len(datas)):
            content = self.get_text(row, datas=datas)
            if row == self.py and self.focus:
                self.draw_text(row + border_len ,1, content,max_width=max_width,  mark=True)
                self.c_x += 1
            else:

                self.draw_text(row + border_len,1, content, max_width=max_width, attrs=ColorConfig.get('normal'))

        # rectangle(screen, y,x, y + len(datas) -1 , x+ max_width -1)
        if self.border_len > 0:
            self.pad.border(0)
        # self.pad.refresh(0,0,y,x, y+len(datas) - 1,x+ max_width -1)
        self.last_refresh = [0,0,y,x, y +max_h - 1, x + max_width -1 ]
        log('save refresh:',self.last_refresh)

        if refresh:
            self.pad.refresh(0,0,y,x, y+max_h -1,x+ max_width -1)
        else:
            self.pad.noutrefresh(0,0,y,x, y+ max_h -1,x+ max_width -1)

    def Redraw(self):
        if hasattr(self, 'last_refresh'):
            self.pad.refresh(*self.last_refresh)

    @classmethod
    def Cl(cls):
        if cls.last_popup and hasattr(cls.last_popup, 'last_refresh'):
            cls.last_popup.pad.clear()
            cls.last_popup.pad.refresh(*cls.last_popup.last_refresh)
            

    @classmethod
    def Popup(cls,datas=None,context=None, screen=None, y=None ,x=None,focus=True,title='Select', max_height=10, exit_key=147, width=30):
        if context:
            y,x = context.cursor_yx
            y+=1
            x+=1
            screen = context.screen
        select = cls(datas, id='unknow')
        cls.last_popup = select
        H,W = Application.Size()
        if y + len(datas) -1 >=  H:
            y = H - len(datas) if H - len(datas) > 0 else y
        if x + 2 + width - 1 >= W:
            log("over width !!! ", x, width)
            x = W - width - 2
        k = -1
        select.focus = True
        msgBox(msg=title)
        if not  hasattr(screen, 'refresh'):
            screen = Application.init_screen
        if focus:
            while k != exit_key:
                select.action_listener(k)
                select.update(screen, ch=k, y=y, x=x+2, pad_width=width,pad_height=max_height, refresh=True)
                select.ready_key(k)

                # screen.refresh()
                # select.pad.refresh()
                k = screen.getch()
                log(k)

            # Application.instance.refresh(clear=True)
            screen.refresh()
            return select.get_now_text()
        else:
            select.update(screen, ch=k, y=y, x=x+2, pad_width=width,pad_height=max_height, refresh=True)
            # screen.refresh()



class TextPanel(Stack):
    def __init__(self, text, id=None,max_width=None,*args, **opts):
        datas = text.split('\n')
        lines = []
        if not max_width:
            H,W = Application.Size()
            max_width = W
        for l in datas:
            if len(l) >= max_width - 1:
                now = ''
                for w in l.split():
                    if len(now) + len(w) >= max_width -2:
                        lines.append(now[1:])
                        now = ''
                    else:
                        now += ' ' + w
                if len(now) > 0:
                    lines.append(now)

            else:
                lines.append(l)


        super().__init__(lines, id=id, *args, **opts)
        self.pro = 0
    def reload_text(self, text, max_width=None):
        datas = text.split('\n')
        lines = []
        if not max_width:
            H,W = Application.Size()
            max_width = W
        for l in datas:
            if len(l) >= max_width - 1:
                now = ''
                for w in l.split():
                    if len(now) + len(w) >= max_width -2:
                        lines.append(now[1:])
                        now = ''
                    else:
                        now += ' ' + w
                if len(now) > 0:
                    lines.append(now)

            else:
                lines.append(l)
        self.datas = lines        

    @listener('h')
    def left(self):
        if self.ix > 0:
            line_words_num = len(self.datas[self.ix - 1].split())
        else:
            return
        if self.px > 0:
            self.px -= 1
        else:
            self.px = line_words_num - 1
            if self.py ==0:
                if self.cursor > 0:
                    self.cursor -= 1
            else:
                self.py -= 1

            self.ix -= 1


    @listener('l')
    def right(self):
        line_words_num = len(self.datas[self.ix].split()) - 1
        log('line ',line_words_num)
        if self.px  < line_words_num:
            self.px += 1
        else:
            self.px = 0

            if self.ix < self.height - 1:
                self.ix += 1

                if self.py > self.end_y - self.start_y - self.border_len * 2 - 3:
                    self.cursor += 1
                else:
                    self.py += 1


    def update_when_cursor_change(self, item, ch=None):
        word = item.split()
        if word:
            px = self.px
            if self.px >= len(word):
                px = len(word) - 1
            if px >= 0:
                self.px = px
                word = word[px]
            else:
                return
        else:
            return
        if len(word) > 0:
            # Application.init_screen.refresh()
            #self.__class__.RunShell("date; echo %s " % word, self, w_pad=self.width)
            pass
    # @listener('t')
    # def trans(self):
        # word = self.datas[self.ix].split()[self.px]
        # self.__class__.RunShell(" trans -x 'localhost:8123' :zh '%s' " % word, self, w_pad=self.width)

    def draw_text(self,row, col, text,max_width=None, attrs=1,prefix='',prefix_attrs=None, mark=False):
        words = text.split()

            # self.pad.addstr(row, col, text,curses.A_REVERSE | attrs )
        self.draw_words(row, words, max_width, attrs=attrs, mark=mark)
        # self.pad.addstr(row, col, text, attrs)


    def draw_words(self,row,  words, max_width,attrs=None, mark=False):
        if mark:
            m = attrs
            mark_m = m | curses.A_REVERSE

        else:
            m = attrs
            mark_m = m
        w_now = 1
        no = 0
        for word in words:
            if self.px == no:
                self.pad.addstr(row, w_now, word, mark_m)
            else:
                self.pad.addstr(row, w_now, word, m)
            w_now += (len(word) + 1)
            no += 1

    @classmethod
    def RunShell(cls, cmd, context, w_pad=20, max_h=15):
        def cmder(cmd, y,x,screen):
            return os.popen(cmd).read(),None,screen ,y,x, False,max_h
        y,x = context.start_y, context.start_x
        y += 1
        x += w_pad
        cls.run_background(cmder, cmd,y, x, context.screen, callback=cls.Popup)

    @classmethod
    def Popup(cls,text,context=None, screen=None, y=None ,x=None,focus=True,  max_height=30,exit_keys=[147],width=50):
        if context:
            y,x = context.cursor_yx
            y+=1
            x+=1
            screen = context.screen
        select = cls(text, id='unknow', max_width=width)
        cls.last_popup = select
        H,W = Application.Size()
        #H = min([H, max_height])
        if y + select.height -1 >=  H:
            y = H - select.height if H - select.height > 0 else y
        if x + width - 1 >= W:
            x = W - width
        k = -1
        select.focus = True
        msgBox(msg='alt+q to exit')
        if not  hasattr(screen, 'refresh'):
            screen = Application.init_screen
        log('y/x',y,x)
        if focus:
            while k not in exit_keys:
                select.action_listener(k)
                select.update(screen, ch=k, y=y, x=x+2, pad_width=width, pad_height=max_height,refresh=True)
                screen.addstr(select.start_y,x+4, '%.1f%% ' % (select.ix / select.height * 100 ))
                select.ready_key(k)

                # screen.refresh()
                # select.pad.refresh()
                k = screen.getch()
                log(k)

            # Application.instance.refresh(clear=True)
            screen.refresh()
            return select.get_now_text()
        else:
            select.update(screen, ch=k, y=y, x=x+2, pad_width=width, pad_height=max_height,refresh=True)
            screen.refresh()


class Menu(Stack):

    def __init__(self,  datas, id='select', x=None,y=None,mode='chains', max_width=30, **opts):
        super().__init__(datas, id=id, mode=mode, *opts)
        if not x:
            self.x = Application.width // 2
        else:
            self.x = x + 1

        if not y:
            self.y = Application.height // 2 - self.height // 2
            if self.y < 0:
                self.y = 1
        else:
            self.y = y
        if self.y + self.height +3 > Application.height:
            self.y = Application.height - self.height - 3
        self.return_item = None
        self.max_width = max_width
        # self.py = 0
        self.target_widget = None

    def update(self, screen, ch):
        # log(self.pad)
        if not self.screen:
            self.screen = screen
        max_heigh,_ = screen.getmaxyx()
        if self.py is None:
            # self.py,self.px = screen.getyx()
            self.py,self.px = 0,0
            # log(self.id,max_heigh, self.py, self.px)
            self.Spy, self.Spx = 0,0
        datas = self.datas

        cursor = self.cursor
        datas = datas[cursor:cursor+ max_heigh - self.y]

        self.draw(datas, screen,ch)

    @listener(10)
    def enter(self):
        self.return_item = self.get_text(self.ix)
        if self.target_widget:
            self.target_widget.callback_value = self.return_item
        Application.extra_widgets.remove(self)
        # msgBox(msg=self.return_item)
        Application.instance.refresh(clear=True)
        Application.ResumeFocus()

        # Application.instance.refresh()

    def draw(self, datas, screen, ch):
        max_h = len(datas) + 2
        max_width = min([max(self.width,self.max_width) + 3, Application.width])

        self.pad = curses.newpad(max_h, max_width)
        self.pad.border(0)
        self.pad.keypad(1)
        for row in range(len(datas)):
            content = self.get_text(row, datas=datas)
            if row == self.py and self.focus:
                content = content.replace("\n","")
                msg = content + ' '*  (max_width - len(content.encode()) -3)
                self.draw_text(row+1,1, msg[:-1], max_width=max_width, mark=True)
            else:
                content = content.replace("\n","")
                M = content[:max_width-2] if len(content.encode()) >= max_width -2 else content
                self.draw_text(row+1,1, M.strip()[:max_width-2], max_width=max_width, attrs=ColorConfig.get('normal'))
        log('%d %d ' %(self.y, self.x))
        right_width = min([self.x+ max_width +1,Application.width -1])
        self.pad.noutrefresh(0,0,self.y,self.x+1, self.y+len(datas) + 1,right_width)

    @classmethod
    def which_one(cls, datas, y=3 ,x=1 , max_width=30, max_height=10):
        select = cls(datas, id='select', y=y, x=x, max_width=max_width)
        Application.LossFocus()
        select.focus = True
        Application.extra_widgets.append(select)

    @classmethod
    def Popup(cls, datas=None, context=None, screen=None, y=None ,x=None ,exit_key=10, width=30, max_height=10):
        if context:
            y,x = context.cursor_yx
            y+=1
            x+=1
            screen = context.screen

        select = cls(datas, id='select',  y=y, x=x, max_width=width)
        k = 0
        # Application.F
        select.focus = True
        while k != exit_key:
            select.action_listener(k)
            select.update(screen, k)
            select.ready_key(k)
            screen.refresh()
            k = screen.getch()
        Application.instance.refresh(clear=True)
        return select.get_now_text()

class Map(Stack):

    def __init__(self, map_res, id=None, max_width=None, *args, **opts):
        self.place_dict = self.get_map_dict(map_res)
        if isinstance(map_res, str):
            map_res = map_res.split("\n")

        self.border_len = 0
        super().__init__(map_res, id=id, *args, **opts)
        self.cursor_x = 0


    def update(self, screen, y=None, x=None, pad_width=None,pad_height=None,ch=None, draw=True,refresh=False):
        if not self.screen:
            self.screen = screen
        self.start_y,self.start_x = y,x
        max_heigh,max_width = Application.Size()
        if pad_height:
            max_heigh = min([max_heigh, y + pad_height])
        max_heigh = min([max_heigh, y + self.height + self.border_len * 2])
        self.end_y = max_heigh
        self.end_x = pad_width
        if self.py is None:
            # self.py,self.px = screen.getyx()
            # self.Spy, self.Spx = screen.getyx()
            self.py,self.px = 0,0
            # log(self.id,max_heigh, self.py, self.px)
            self.Spy, self.Spx = 0,0
        datas = self.datas
        # log('y',y)
        cursor = self.cursor
        if isinstance(datas, list):

            datas = datas[cursor:cursor+ max_heigh - y - self.border_len]
        else:
            datas = dict(list(datas.items())[cursor:cursor+ max_heigh - y - self.border_len ])
        if draw:
            self.draw(datas, screen, y,x , pad_width, refresh=refresh)

    def padding_space(self, content, max_width, mark=False, direct='r'):
        content = content.replace("\n","")
        content = content[self.cursor_x: self.cursor_x + max_width-2] if len(content.encode()) >= max_width -2 else content
        if mark:
            if direct == 'r':
                msg = content + ' '*  (max_width - len(content.encode()) -3)
            else:
                msg =  ' '*  (max_width - len(content.encode()) -3) + content
        else:
            if direct != 'r':
                msg =  ' '*  (max_width - len(content.encode()) -3) + content
            else:
                msg = content
        return msg

    def get_map_dict(self,map_res):
        w = re.compile(r'([\w\'\s]+)')
        places = [i.strip() for i in w.findall(map_res) if i.strip()]
        lines = map_res.split("\n")
        map_dict = {}
        for r,l in enumerate(lines):
            for p in places:
                if p in l:
                    col = l.index(p) + len(p)//2
                    map_dict[p] = (r, col)
        return map_dict

    def draw(self,datas,screen,y,x, max_width,refresh=False):
        border_len = self.border_len
        max_h = self.end_y - y
        self.pad = curses.newpad(max_h, max_width)
        self.c_y, self.c_x = y, x

        # if self.py == 0:
        #     self.py += border_len
        for row in range(len(datas)):
            content = self.get_text(row, datas=datas)
            if row == self.py and self.focus:
                self.draw_text(row + border_len ,1, content,max_width=max_width,  mark=True, attrs=ColorConfig.get('map'))
                self.c_x += 1
            else:
                self.draw_text(row + border_len,1, content, max_width=max_width, attrs=ColorConfig.get('map'))

        # rectangle(screen, y,x, y + len(datas) -1 , x+ max_width -1)
        if self.border_len > 0:
            self.pad.border(0)
        # self.pad.refresh(0,0,y,x, y+len(datas) - 1,x+ max_width -1)
        if refresh:
            self.pad.refresh(0,0,y,x, y+max_h -1,x+ max_width -1)
        else:
            self.pad.noutrefresh(0,0,y,x, y+ max_h -1,x+ max_width -1)

    def draw_text(self,row, col, text,max_width=None, attrs=1,prefix='',prefix_attrs=None, mark=False):
        # if mark:
        #     attrs |= curses.A_REVERSE
            # self.pad.addstr(row, col, text,curses.A_REVERSE | attrs )

        if prefix:
            if prefix_attrs:
                self.pad.addstr(row, col, prefix, prefix_attrs)
            else:
                self.pad.addstr(row, col, prefix)
            text = self.padding_space(text, max_width, mark=mark)
            self.pad.addstr(text, attrs)
        else:
            # log("col:", col, "px", self.px)
            if mark:
                pxs = []
                citis = re.findall(r'([\w\s\']+)',text)
                for c in citis:
                    s = text.index(c)
                    log("test eq:",s + len(c) // 2 - self.cursor_x , self.px, 'row', row, "cursor:",self.cursor_x)
                    if s + len(c) //2 - self.cursor_x == self.px:

                        for i in range(s, s+len(c)):
                            pxs.append(i)
            text = self.padding_space(text, max_width, mark=mark)
            for cx,ch in enumerate(text):
                if mark and cx + self.cursor_x in pxs:
                    attrs2 = ColorConfig.get('green') | curses.A_REVERSE
                    self.pad.addstr(row, cx+1, ch, attrs2)
                else:
                    self.pad.addstr(row, cx+1, ch, attrs)

    @listener('h')
    def left(self):
        if self.ix > 0:
            line_words_num = len(self.datas[self.ix - 1])
        else:
            return
        if self.px > 0:
            self.px -= 1
        else:
            self.px = line_words_num - 1
            if self.py ==0:
                if self.cursor > 0:
                    self.cursor -= 1
            else:
                self.py -= 1

            self.ix -= 1

    @listener('l')
    def right(self):
        line_words_num = len(self.datas[self.ix]) - 1
        log('line ',line_words_num)
        if self.px  < line_words_num:
            self.px += 1
        else:
            self.px = 0

    @listener("g")
    def choose_map_place(self):
        log(self.place_dict)
        place = Stack.Popup(list(self.place_dict.keys()), context=self, exit_key=10)
        log(place)
        city_y, city_x = self.place_dict[place]
        if city_x-self.cursor_x >  self.end_x:
            self.cursor_x = city_x - (self.end_x + self.start_x) // 2
            log("move R over")
            self.px = city_x - self.cursor_x
        elif city_x -self.cursor_x <  self.start_x:
            self.cursor_x = city_x - (self.end_x + self.start_x) // 2 
            self.px = (self.end_x + self.start_x) // 2
            log("move L over")
        else:
            self.px = city_x - self.cursor_x

        if city_y - self.cursor < self.start_y:
            self.cursor = (city_y - self.cursor) // 2

        if self.cursor_x < 0:
            self.cursor_x = 0
            self.px = city_x
        if self.cursor < 0:
            self.cursor = 0
            self.py = city_y
        self.py = city_y  - self.cursor
        log('city: row:%d , col:%d' % (city_y,city_x ),"py:",self.py, "px:", self.px)



class TreeStack(Stack):

    l_stack = None
    r_stack = None
    m_stack = None

    def __init__(self, datas, id='middle',controller=None, **kargs):
        super().__init__(datas, id=id, **kargs)
        self.controller = controller


    @listener('h')
    def left(self):
        self.controller.move_left()

    def update_when_cursor_change(self, item, ch):
        self.controller.update_when_cursor_change(item, ch)

    @listener('l')
    def right(self):
        self.controller.move_right()

class Tree:

    def __init__(self, cursor):
        self.cursor = cursor
        self.now = None
        self.get_tribble()

    def get_parent(self, cursor):
        raise NotImplementedError("")
    def get_sub(self, cursor):
        raise NotImplementedError("must implement")

    def get_current(self, cursor):
        raise NotImplementedError("must implement")

    def update_when_cursor_change(self, item, ch):
        raise NotImplementedError("must implemnt")

    def get_right_cursor(self):
        raise NotImplementedError()

    def get_left_cursor(self):
        raise NotImplementedError()

    def get_tribble(self):
        self.l = TreeStack(self.get_parent(self.cursor),controller=self, id='left')
        self.m = TreeStack(self.get_current(self.cursor), controller=self,id='middle')
        self.r = TreeStack(self.get_sub(self.cursor), controller=self,id='right')
        if 'left' not in Application.widgets:
            Application.instance.add_widget(self.l, id='left', weight=1)
        else:
            Application.instance['left'] = self.l

        if 'middle' not in Application.widgets:
            Application.instance.add_widget(self.m, id='middle', weight=2)
        else:
            Application.instance['middle'] = self.m

        if 'right' not in Application.widgets:
            Application.instance.add_widget(self.r, id='right', weight=3)
        else:
            Application.instance['right'] = self.r

        Application.instance.refresh(clear=True)
        Application.Focus("middle")
        self.now = self.m.datas[self.m.ix]



    def move_right(self):
        self.cursor = self.get_right_cursor()
        self.get_tribble()

    def move_left(self):
        self.cursor = self.get_left_cursor()
        self.get_tribble()


class CheckBox(Stack):

    comments = {}

    @property
    def width(self):
        return super().width + 3

    @listener(32)
    def space_to_change_staus(self):
        if isinstance(self.datas,dict):
            msg = self.get_now_text()[4:]
            log(msg)
            if self.datas.get(msg):
                self.datas[msg] = False
            else:
                self.datas[msg] = True

    @listener('c')
    def rw_comment(self):
        txt = self.get_now_text()[4:]
        if txt not in self.comments:
            self.comments[txt] = ''
        new_comment = Text.Popup(context=self, title='comment ctrl+g exit', content=self.comments[txt])
        self.comments[txt] = new_comment

    def on_text(self, msg, ix):
        if isinstance(self.datas,dict):
            if self.datas.get(msg):
                return '[%s] '% SYMBOL['bear'] + msg
            else:
                return '[%s] ' % SYMBOL['wait'] + msg
        return msg

    def draw_text(self,row, col, text, attrs=1,max_width=None, mark=False):

        if self.datas.get(text[4:].strip()):
            self.pad.addstr(row, col, text[:4], ColorConfig.get('finish') | curses.A_BOLD)
            attrs =  ColorConfig.get('finish') #| curses.A_UNDERLINE
        else:
            self.pad.addstr(row, col, text[:4],  curses.A_BOLD)

        if self.comments.get(text[4:].strip()):
            attrs = ColorConfig.get('attrs')
        if mark:
            attrs |= curses.A_REVERSE
        msg = self.padding_space(text[4:], max_width-3, mark=mark, direct='l')
        self.pad.addstr(msg, attrs )
    def get_options(self):
        res = []
        for k in self.datas:
            if self.datas[k]:
                res.append(k)
        return res
