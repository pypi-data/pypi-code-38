from tkinter import *
import tkinter as Tk
import tkinter.ttk as ttk
import serial.tools.list_ports
from tkinter import messagebox
import os
from amarettopy.gui.util  import *
from amarettopy import *
import logging

logger = logging.getLogger("amarettopy")
NO_PORT = "-------------------------------"

class TopPanel(Tk.Frame):
     
    def __init__(self, amaretto, master):
        Tk.Frame.__init__(self, master)

        self.amaretto = amaretto
        self.port = None
        self.baud = 115200

        port_label = Label(self, text="PORT", anchor=W, font=("Arial", 8) )
        port_label.pack(padx=10, side="left")
        self.port0()

        baud_label = Label(self, text="BAUD RATE", anchor=W, font=("Arial", 8) )
        baud_label.pack(padx=10, side="left")
        self.baudrate() 

        devid_label = Label(self, text="DEVICE ID", anchor=W, font=("Arial", 8) )
        devid_label.pack(padx=10, side="left")
        self.device_id_list()

        self.button= Tk.Button(self, text='Connect', command=self.open)
        self.button.pack(padx=10, side="left")

        self.logo_O = PhotoImage(file=os.path.join(os.path.dirname(__file__), 'imgs', "LED-OFF.gif"))
        self.logo_G = PhotoImage(file=os.path.join(os.path.dirname(__file__), 'imgs', "LED-GREEN.gif"))

        self.isConnected = False

        self.connection_label = None
        self.led = None

        self.onDisconnected()

        self.onTick();

    def onConnected(self):

        #logger = logging.getLogger("AmarettoApp.amaretto_top.onConnected")
        logger.info("Connected ")

        if self.connection_label is not None : self.connection_label.forget()
        if self.led is not None : self.led.forget()

        self.connection_label = Label(self, text="CONNECTED({})".format(amarettoGuiInfo.targetDevId), anchor=W, font=("Arial", 8) )
        self.connection_label.pack(padx=10, side="left")

        self.led = Label(self, image=self.logo_G)
        self.led.pack(padx=10, side="left")

        self.button.configure(text='Disconnect', command=self.close)

    def onDisconnected(self):

        logger.info("Disconnected ")    

        if self.connection_label is not None : self.connection_label.forget()
        if self.led is not None : self.led.forget()

        self.connection_label = Label(self, text="DISCONNECTED", anchor=W, font=("Arial", 8) )
        self.connection_label.pack(padx=10, side="left")

        self.led = Label(self, image=self.logo_O)
        self.led.pack(padx=10, side="left")

        self.button.configure(text='Connect', command=self.open)
          
    def updateboxlist(self):
        list= serial.tools.list_ports.comports()
        self.box['values'] = ([NO_PORT] + list)

    def port0(self):
        
        self.box_value = StringVar()
        self.box = ttk.Combobox(self, textvariable=self.box_value, postcommand =self.updateboxlist)
        self.box.bind("<<ComboboxSelected>>",self.on_select) #assign function to combobox
        print(serial.tools.list_ports.comports())
        ports = serial.tools.list_ports.comports()
        self.box['values'] = ([NO_PORT] + ports)
        self.box.current(1 if len(ports) > 0 else 0)
        self.on_select(None)
        self.box.pack(padx=10, side="left")

    def on_select (self, event):
        
        logger.info("Current Port: %s" %self.port)
        
        print("port is called")
        self.port = self.box.get().split(' ')[0]
        print(self.port)

        logger.info("Port is selected")
        logger.info("Port: %s" %self.port)
         

    def open(self):
        

        if (self.port != NO_PORT):

            global amarettoGuiInfo
            amarettoGuiInfo.targetDevId = int(self.devidbox.get())
            tryAmaretto(lambda: self.amaretto.open(self.port, self.baud))
            self.isConnected = self.query() is not None

            if self.isConnected :
                self.onConnected()
                logger.info("onConnected")
            else:
                self.close()
                logger.info("close")
                

    def close(self):
        self.amaretto.close()
        self.onDisconnected()

        logger.info("Close")
        logger.info("------------------------------------------") 

    def baudrate(self):
        self.box1_value = StringVar()
        self.box1 = ttk.Combobox(self, textvariable=self.box1_value, state='readonly')
        self.box1.bind("<<ComboboxSelected>>", self.baud_select)
        self.box1['values'] =("115200", "57600", "38400", "28800", "19200",
                  "14400", "9600", "4800", "2400","1200","600","300")
        self.box1.current(0)  ##Set default baud rate value
        self.box1.pack(padx=10, side="left")

    def baud_select (self, event):
        print("baud_select is called")
        print(self.box1.get())
        
        #logger = logging.getLogger("AmarettoApp.amaretto_top.baud_select")
        logger.info("Baudrate is selected") 
        logger.info("baudrate: %s" %self.box1.get())        

    def device_id_list(self):
        self.devid_value = StringVar()
        self.devidbox = ttk.Combobox(self, textvariable=self.devid_value, state='readonly', width=5)
        self.devidbox.bind("<<ComboboxSelected>>", self.devid_select)
        self.devidbox['values'] =[str(x) for x in range(128)]
        self.devidbox.current(1)  ##Set default baud rate value
        self.devidbox.pack(padx=10, side="left")

    def devid_select (self, event):
        print("devid_select is called")
        print(self.devidbox.get())
        
        #logger = logging.getLogger("AmarettoApp.amaretto_top.baud_select")
        logger.info("devid is selected") 
        logger.info("devid: %s" %self.devidbox.get())        

    def query(self):

        #logger.info("query")
        if (self.amaretto.is_open()):
            return tryAmaretto(lambda: self.amaretto.query_servo_status(amarettoGuiInfo.targetDevId))
            logger.info(amaretto.query_servo_status)
        else:
            return None

    def onTick(self):
           
        if self.isConnected:
            servoStatus = self.query()
            self.isConnected = servoStatus is not None

            if (not self.isConnected) :
                self.close()

            global tickListener
            for l in tickListener:
                l.onTick(servoStatus)

        self.after(1, self.onTick)

