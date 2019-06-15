import sys
sys.path.append('..')

if sys.version_info[0] < 3:
	import Tkinter as tk
	import ttk
else:
	import tkinter as tk
	from tkinter import ttk
from lib import client_rest, tab_tools
import time


"""
# TODO:
	add error handling if entries aren't in the right format
	add error handling if not connected to correct wifi
"""

class Tab0():
	"""
	Setting up the server settings
	"""
	def __init__(self,master,notebook):
		# itialize variables
		self.version_num = "Version 0.1.5"
		self.master = master
		self.n = notebook
		self.initialized = False
		#self.default_host = '127.0.0.1' # host if running on own machine
		self.default_host = '192.168.1.10'
		self.default_port = '5000'
		self.default_idnum = 9999
		self.default_debug = False
		self.interface = client_rest.ImagingInterface(host=self.default_host,port=self.default_port,numIdsStored=self.default_idnum,isDebug=self.default_debug)
		self.resize_counter_tab0 = time.time()


		# Tab 0: SETTINGS ------------------------------------------------------
		self.tab0 = ttk.Frame(self.n)
		self.n.add(self.tab0, text='Settings')
		# makes resizing possible
		for x in range(6):
			tk.Grid.columnconfigure(self.tab0,x,weight=1)
		for y in range(10):
			tk.Grid.rowconfigure(self.tab0,y,weight=1)
		# Left Column
		self.t0c0r0 = ttk.Label(self.tab0, anchor=tk.CENTER, text='                               ')
		self.t0c0r0.grid(row=0,column=0,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
		self.t0c1r0 = ttk.Label(self.tab0, anchor=tk.CENTER, text='                               ')
		self.t0c1r0.grid(row=0,column=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)

		# Middle Column
		self.logo_np = tab_tools.get_image('assets/logo.png')
		self.logo_im = tab_tools.np2im(self.logo_np)
		self.logo_width,self.logo_height = self.logo_im.size
		self.logo_tk = tab_tools.im2tk(self.logo_im)

		self.t0c2r0 = ttk.Label(self.tab0, anchor=tk.CENTER,image=self.logo_tk)
		self.t0c2r0.image = self.logo_tk
		self.t0c2r0.grid(row=0,column=2,rowspan=5,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
		self.t0c2r5 = ttk.Label(self.tab0, anchor=tk.E, text='Host:')
		self.t0c2r5.grid(row=5,column=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
		self.t0c3host = tk.StringVar()
		self.t0c3host.set(self.default_host)
		self.t0c3r5 = ttk.Entry(self.tab0,textvariable=self.t0c3host)
		self.t0c3r5.grid(row=5,column=3,sticky=tk.N+tk.S+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
		self.t0c2r6 = ttk.Label(self.tab0, anchor=tk.E, text='Port:')
		self.t0c2r6.grid(row=6,column=2,sticky=tk.N+tk.E+tk.S+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
		self.t0c3port = tk.StringVar()
		self.t0c3port.set(self.default_port)
		self.t0c3r6 = ttk.Entry(self.tab0,textvariable=self.t0c3port)
		self.t0c3r6.grid(row=6,column=3,sticky=tk.N+tk.S+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
		self.t0c2r7 = ttk.Label(self.tab0, anchor=tk.E, text='Number of IDs Stored:')
		self.t0c2r7.grid(row=7,column=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
		self.t0c3ids = tk.StringVar()
		self.t0c3ids.set(self.default_idnum)
		self.t0c3r7 = ttk.Entry(self.tab0,textvariable=self.t0c3ids)
		self.t0c3r7.grid(row=7,column=3,sticky=tk.N+tk.S+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
		self.t0c2r8 = ttk.Label(self.tab0, anchor=tk.E, text='Debug Mode:')
		self.t0c2r8.grid(row=8,column=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
		self.t0c3debug = tk.IntVar()
		self.t0c3r8 = ttk.Radiobutton(self.tab0,text='True',value=0,variable=self.t0c3debug)
		self.t0c3r8.grid(row=8,column=3,sticky=tk.N+tk.S+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
		self.t0c3r8b = ttk.Radiobutton(self.tab0,text='False',value=1,variable=self.t0c3debug)
		self.t0c3r8b.grid(row=8,column=3,sticky=tk.N+tk.S,padx=5,pady=5,ipadx=5,ipady=5)
		if not self.default_debug:
			self.t0c3debug.set(1)
		self.t0c2r9 = ttk.Button(self.tab0, text="Apply Settings",command=self.updateSettings)
		self.t0c2r9.grid(row=9,column=2,columnspan=2,sticky=tk.N+tk.S,padx=5,pady=5,ipadx=5,ipady=5)
		# Right Column
		self.t0c4r0 = ttk.Label(self.tab0, anchor=tk.CENTER, text='                                   ')
		self.t0c4r0.grid(row=0,column=4,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
		self.t0c5r0 = ttk.Label(self.tab0, anchor=tk.CENTER, text='                                   ')
		self.t0c5r0.grid(row=0,column=5,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
		self.t0c4r6 = ttk.Label(self.tab0, anchor=tk.S, text=self.version_num)
		self.t0c4r6.grid(row=6,column=4,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
		self.t0c4r7 = ttk.Button(self.tab0, text="  Save Database  ",command=self.saveDatabase)
		self.t0c4r7.grid(row=7,column=4,columnspan=2,sticky=tk.N+tk.S,padx=5,pady=5,ipadx=5,ipady=5)
		self.t0c4r8 = ttk.Button(self.tab0, text="  Load Database  ",command=self.loadDatabase)
		self.t0c4r8.grid(row=8,column=4,columnspan=2,sticky=tk.N+tk.S,padx=5,pady=5,ipadx=5,ipady=5)
		if not self.default_debug:
			self.t0c4r8.configure(state=tk.DISABLED)
		self.t0c4r9 = tk.Button(self.tab0, text="Delete Database",command=self.deleteDatabase, \
								bg='red',fg='white',bd=2)
		self.t0c4r9.grid(row=9,column=4,columnspan=2,sticky=tk.N+tk.S,padx=5,pady=5,ipadx=5,ipady=5)
		if not self.default_debug:
			self.t0c4r9.configure(state=tk.DISABLED)

		# Done with initialization
		self.initialized = True

	def updateSettings(self,event=None):
		"""
		Attempts to connect to server when settings are changed

		@type  event: event
		@param event: Enter press or button press event

		@rtype:  None
		@return: None
		"""
		host_new = self.t0c3host.get()
		port_new = self.t0c3port.get()
		ids_new = int(self.t0c3ids.get())
		debug_new = not(self.t0c3debug.get())
		self.interface = client_rest.ImagingInterface(host=host_new,port=port_new,numIdsStored=ids_new,isDebug=debug_new)
		if debug_new:
			self.t0c4r8.configure(state=tk.NORMAL)
			self.t0c4r9.configure(state=tk.NORMAL)
		else:
			self.t0c4r8.configure(state=tk.DISABLED)
			self.t0c4r9.configure(state=tk.DISABLED)

	def run(self):
		self.resizeEventTab0()
		# setup all keybindings
		self.master.unbind("<Right>")
		self.master.unbind("<Left>")
		self.master.unbind("<d>")
		self.master.unbind("<a>")
		self.master.bind("<Configure>",self.resizeEventTab0)
		self.master.unbind("<Control-z>")
		self.master.bind("<Return>",self.updateSettings)

	def resizeEventTab0(self,event=None):
		"""
		Resizes picture on Tab0
		@type  event: event
		@param event: resize window event

		@rtype:  None
		@return: None
		"""
		if self.initialized and (time.time()-self.resize_counter_tab0) > 0.050:
			if self.t0c2r0.winfo_width() > 1:
				self.resize_counter_tab0 = time.time()
				self.master.update()
				# get container label height and width
				t0c2i1_width = self.t0c2r0.winfo_width()
				t0c2i1_height = self.t0c2r0.winfo_height()
				logoW, logoH = self.logo_im.size
				self.logo_resized_im = tab_tools.resizeIm(self.logo_im, logoW, logoH, t0c2i1_width, t0c2i1_height)
				self.logo_tk = tab_tools.im2tk(self.logo_resized_im)
				self.t0c2r0.configure(image=self.logo_tk)

	def interfaceCall(self):
		# return interface according to current settings
		return self.interface

	def saveDatabase(self):
		result = self.interface.postSaveDatabase()
		if result:
			print("successfully saved database")

	def loadDatabase(self):
		print("load database (currently un-implemented server side)")

	def deleteDatabase(self):
		result = self.interface.postDeleteDatabase()
		if result:
			print("successfully deleted database")
