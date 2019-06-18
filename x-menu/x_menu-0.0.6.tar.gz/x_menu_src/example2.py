import curses
from .menu import Application, Stack, CheckBox, msgBox, Text, Menu, TextPanel
from .event import listener
import termcolor
from termcolor import COLORS, ATTRIBUTES
T = """
1. The Zen of Python, by Tim Peters
2. Beautiful is better than ugly.eautiful is better thaeautiful is better tha
3.Explicit is better than impliciplicit is better than plicit is better than t.
Simple is better than complex.   le is one two three four five six seven eight night ten
Complex is better than complicatelex is better than comlex is better than comd.
Flat is better than nested.       is better than nested is better than nested
Sparse is better than dense.     se is better than densse is better than dens
Readability counts.              ability counts.       ability counts.
Now is better than never.        is better than never. is better than never.
Although never is often better though never is often beough never is often bean *right* now.
If the implementation is hard to he implementation is hhe implementation is hexplain, it's a bad idea.
If the implementation is easy to he implementation is ehe implementation is eexplain, it may be a good idea.
Namespaces are one honking great spaces are one honkingspaces are one honkingidea -- let's do more of those!""".split('\n')
T = [str(i) + termcolor.colored(v, list(COLORS.keys())[i % len(COLORS)],attrs=[list(ATTRIBUTES.keys())[i % len(ATTRIBUTES)]] ) for i,v in enumerate(T)]
T = '\n'.join(T)

class Test(Stack):

    @listener(10)
    def enter(self):
        # res = Test.Popup(["hello", "world","more power","awsl", "这个是什么时代的啊啊啊啊","exit"], context=self, exit_key=147)

        res = TextPanel.Popup(T, context=self)
        msgBox(msg=res)

    @listener('i')
    def info_item(self):
        Text.Popup(content="this is a test !!!",context=self, width=40)

if __name__ =="__main__":
    main = Application()
    import random
    
    r1 = CheckBox({"hello for no: "+str(i):random.randint(0,1) for i in range(138)}, id='check')
    r2 = Test(["random test ... s2"+str(i) for i in range(50)], id='2')
    r3 = Test(["you can ? to see"+str(i) for i in range(160)], id='3')
    r4 = Test(["vim keymap to move "+str(i) for i in range(270)], id='4')
    r5 = Test(["s3"+str(i) for i in range(270)], id='5')
    # e = Menu(["a", "b", "c", "exit"], id='s', x=30, y =30)
    main.add_widget(r1)
    main.add_widget(r2)
    main.add_widget(r3)
    main.add_widget(r4)
    main.add_widget(r5, weight=0.5)
    # main.add_widget(t)
    
    # tl = FileTree(os.listdir(os.path.expanduser("~/")), root_path=os.path.expanduser("~/"), id='left')
    # tm = FileTree(os.listdir(os.path.expanduser("~/Documents")), path_root=os.path.expanduser("~/Documents"), id='middle')
    # tr = FileTree([''], id='right')

    # main.add_widget(tl,weight=1)
    # main.add_widget(tm,weight=2)
    # main.add_widget(tr,weight=3)
    
    
    # main.add_widget(e)
    main.focus("2")
    curses.wrapper(main.loop)
    print(T)

