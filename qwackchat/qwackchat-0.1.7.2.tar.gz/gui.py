import tkinter as t
from tkinter.scrolledtext import ScrolledText
from PIL import Image
class Qui:

    msgs = ['a','b','c','d','e']
    conns = ['10.1.1.5','10.1.1.6','10.1.1.102','10.1.1.35','10.1.1.78','10.1.1.11','10.1.1.19','10.1.1.220','10.1.1.74','10.1.1.13']
    
    
    def _exit(self):
        print('shutting_down')
        try:
            self.window.destroy()
            print('shutdown success')
        except:
            print('failed to destroy')
    
    def __init__(self,messages=msgs,connections=conns):
        self.exit = False
        self.bg = 'black'
        self.fg = 'white'
        self.message = None
        
        #self.msg = messages
        self.conns =connections
    
        self.window = t.Tk()
        self.window.title("QwackChatRoom")
        self.window.minsize(width=600,height=560)
        self.window.geometry('500x500')

        self.window.protocol('WM_DELETE_WINDOW',self._exit)

        self.conns_frame = t.Frame(bg='blue',width=3)
        self.conns_frame.pack(side=t.RIGHT)

        self.menu_frame = t.Frame(bg=self.bg)
        self.menu_frame.pack(side=t.RIGHT,fill=t.BOTH)

        self.conns_header = t.Label(self.menu_frame,text="Connections",bg=self.bg,fg=self.fg, font=("",15))
        self.conns_header.pack(fill=t.X,side=t.TOP,ipadx = 10,ipady=28)

        self.conns_text = ScrolledText(self.menu_frame,width=10,height=15)
        self.conns_text.pack(fill=t.X,padx=10,pady=10)

        for conn in self.conns:
            self.conns_text.insert(t.END,conn+'\n')

        self.chat_frame = t.Frame(bg=self.bg)
        self.chat_frame.pack(fill=t.BOTH)

        self.header = t.Label(self.chat_frame,text="Welcome to QwackChat",bg=self.bg,fg=self.fg, font=("",25))
        self.header.pack(fill=t.X,expand=1,side=t.TOP,ipadx = 10,ipady=20)


        '''
        CHAT_DISPALY_TEXT
        '''
        self.chat_window = ScrolledText(self.chat_frame)
        self.chat_window.pack(fill=t.X,padx=10,pady=10)
        self.chat_window.configure(state='disabled')


        '''
        SEND_BUTTON
        '''
        self.send_btn = t.Button(self.chat_frame,text="send",bg=self.bg,fg=self.fg,command=self.send,height=4)
        self.send_btn.pack(side =t.LEFT,padx=10,pady=10)


        '''
        CHAT INPUT TEXT
        '''
        self.chat_input = ScrolledText(self.chat_frame)#,height=5)
        self.chat_input.pack(side =t.BOTTOM,fill=t.BOTH,padx=10,pady=10)
        
        
        
        
    def send(self,msg=None):
        print('###############################################################')
        if not msg: 
            print('no message')
            msg = self.chat_input.get("1.0",t.END)
        if len(msg) > 1:
            self.chat_window.configure(state='normal')
            self.chat_window.insert(t.END,'You_said>'+msg)
            self.chat_window.configure(state='disabled')
            self.chat_input.delete('1.0',t.END)
            self.message = msg
            return msg
        return None



    def close(self):
        self.window.destroy()

    def launch(self):
        while True:
            self.window.update_idletasks()
            self.window.update()
