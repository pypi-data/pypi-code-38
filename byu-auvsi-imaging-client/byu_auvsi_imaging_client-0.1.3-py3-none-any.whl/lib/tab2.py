import sys
sys.path.append('..')

if sys.version_info[0] < 3:
    import Tkinter as tk
    import ttk
else:
    import tkinter as tk
    from tkinter import ttk
from lib import tab_tools, client_rest
import time
import numpy as np
import imutils


"""
# TODO:
    disable moving to next/prev when in the alphanumeric entry
    show not only submission status, but what you submitted??
    Change disable color
    Verify rotating picture based on yaw angle
    Show past classifications on the left with autofill option
    Bug tabbing into emergent description and trying to leave w/o subbmitting
"""

class Tab2():
    """
    Pull cropped iamges and submit classification for images
    """
    def __init__(self,master,notebook,interface):
        self.master = master
        self.n = notebook
        self.interface = interface
        self.initialized = False
        self.resize_counter_tab2 = time.time()

        self.pingServer()
        self.cropped_im = tab_tools.np2im(self.cropped_np)
        self.cropped_width,self.cropped_height = self.cropped_im.size
        self.cropped_tk = tab_tools.im2tk(self.cropped_im)

        # Tab 2 variables
        self.t2_functional = False # prevent
        self.t2_entry_focus = False

        # TAB 2: CLASSIFICATION ------------------------------------------------
        self.tab2 = ttk.Frame(self.n)   # second page
        self.n.add(self.tab2, text='Classification')

        for x in range(16):
            tk.Grid.columnconfigure(self.tab2,x,weight=1)
        for y in range(50):
            tk.Grid.rowconfigure(self.tab2,y,weight=1)

        # Column One
        self.t2c1title = ttk.Label(self.tab2, anchor=tk.CENTER, text='                  ')
        self.t2c1title.grid(row=0,column=0,columnspan=4,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)

        # Column Two
        self.t2sep12 = ttk.Separator(self.tab2, orient=tk.VERTICAL)
        self.t2sep12.grid(row=0, column=4, rowspan=50,sticky=tk.N+tk.S+tk.E+tk.W, pady=5)
        self.t2c2title = ttk.Label(self.tab2, anchor=tk.CENTER, text='Classification')
        self.t2c2title.grid(row=0,column=4,columnspan=8,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t2c2i1 = ttk.Label(self.tab2, anchor=tk.CENTER,image=self.cropped_tk)
        self.t2c2i1.image = self.cropped_tk
        self.t2c2i1.grid(row=2,column=4,rowspan=38,columnspan=8,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t2c2l1 = ttk.Label(self.tab2, anchor=tk.CENTER, text='Shape')
        self.t2c2l1.grid(row=40,column=4,columnspan=2,rowspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        shape_options = ('circle','semicircle','quarter_circle','triangle','square','rectangle','trapezoid','pentagon','hexagon','heptagon','octagon','star','cross')
        self.t2c2l2_var = tk.StringVar(self.master)
        self.t2c2l2 = ttk.OptionMenu(self.tab2,self.t2c2l2_var,shape_options[0],*shape_options)
        self.t2c2l2.grid(row=42,column=4,columnspan=2,rowspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t2c2l3 = ttk.Label(self.tab2, anchor=tk.CENTER, text='Alphanumeric')
        self.t2c2l3.grid(row=40,column=6,columnspan=2,rowspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t2c2l4_var = tk.StringVar(self.master)
        alphanumericValidateCommand = self.master.register(self.alphanumericValidate)
        self.t2c2l4 = ttk.Entry(self.tab2,textvariable=self.t2c2l4_var,validate=tk.ALL,validatecommand=(alphanumericValidateCommand, '%d','%P'))
        self.t2c2l4.grid(row=42,column=6,columnspan=2,rowspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t2c2l5 = ttk.Label(self.tab2, anchor=tk.CENTER, text='Orientation')
        self.t2c2l5.grid(row=40,column=8,columnspan=4,rowspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        orientation_options = ('N','NE','E','SE','S','SW','W','NW')
        self.t2c2l6_var = tk.StringVar(self.master)
        self.t2c2l6 = ttk.OptionMenu(self.tab2,self.t2c2l6_var,orientation_options[0],*orientation_options)
        self.t2c2l6.grid(row=42,column=8,columnspan=4,rowspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t2c2l9 = ttk.Label(self.tab2, anchor=tk.CENTER, text='Background Color')
        self.t2c2l9.grid(row=44,column=4,columnspan=2,rowspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        color_options = ('white','black','gray','red','blue','green','yellow','purple','brown','orange')
        self.t2c2l10_var = tk.StringVar(self.master)
        self.t2c2l10 = ttk.OptionMenu(self.tab2,self.t2c2l10_var,color_options[0],*color_options)
        self.t2c2l10.grid(row=46,column=4,columnspan=2,rowspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t2c2l11 = ttk.Label(self.tab2, anchor=tk.CENTER, text='Alphanumeric Color')
        self.t2c2l11.grid(row=44,column=6,columnspan=2,rowspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t2c2l12_var = tk.StringVar(self.master)
        self.t2c2l12 = ttk.OptionMenu(self.tab2,self.t2c2l12_var,color_options[0],*color_options)
        self.t2c2l12.grid(row=46,column=6,columnspan=2,rowspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t2c2l13 = ttk.Label(self.tab2, anchor=tk.CENTER, text='Target Type')
        self.t2c2l13.grid(row=44,column=8,columnspan=2,rowspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t2c2l14_var = tk.StringVar(self.master)
        target_options = ('standard','emergent','off_axis')
        self.t2c2l14 = ttk.OptionMenu(self.tab2,self.t2c2l14_var,target_options[0],*target_options)
        self.t2c2l14.grid(row=46,column=8,columnspan=2,rowspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t2c2l14_var.trace("w",self.disableEmergentDescription)
        self.t2c2l15 = ttk.Label(self.tab2, anchor=tk.CENTER, text='Emergent Description')
        self.t2c2l15.grid(row=44,column=10,columnspan=2,rowspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t2c2l16_var = tk.StringVar()
        self.t2c2l16_var.set(None)
        self.t2c2l16 = ttk.Entry(self.tab2,textvariable=self.t2c2l16_var)
        self.t2c2l16.grid(row=46,column=10,columnspan=2,rowspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t2c2r48a = ttk.Label(self.tab2, anchor=tk.E, text='Submission Status: ')
        self.t2c2r48a.grid(row=48,column=4,columnspan=2,rowspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t2c2lr48b = ttk.Label(self.tab2, anchor=tk.W, text='N/A')
        self.t2c2lr48b.grid(row=48,column=6,columnspan=2,rowspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t2c2l17 = ttk.Button(self.tab2, text="Submit Classification",command=self.submitClassification)
        self.t2c2l17.grid(row=48,column=8,columnspan=4,rowspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.disableEmergentDescription()

        # Column Three
        self.t2sep23 = ttk.Separator(self.tab2, orient=tk.VERTICAL)
        self.t2sep23.grid(row=0, column=12, rowspan=50,sticky=tk.N+tk.S+tk.E+tk.W, pady=5)
        self.t2c3title = ttk.Label(self.tab2, anchor=tk.CENTER, text='                      ')
        self.t2c3title.grid(row=0,column=12,columnspan=4,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        t2c2i1_np = tab_tools.get_image('assets/compass.jpg')
        self.t2c3i1_im = tab_tools.np2im(t2c2i1_np)
        self.t2c3i1_default_width,self.t2c3i1_default_height = self.t2c3i1_im.size
        self.t2c3i1_tk = tab_tools.im2tk(self.t2c3i1_im)
        # place image
        self.t2c3i1 = ttk.Label(self.tab2, anchor=tk.CENTER,image=self.t2c3i1_tk)
        self.t2c3i1.image = self.t2c3i1_tk
        self.t2c3i1.grid(row=2,column=12,rowspan=38,columnspan=4,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)

        self.initialized = True

    def run(self,interface):
        self.interface = interface
        self.resizeEventTab2()
        # setup all keybindings
        self.master.bind("<Right>",self.nextCropped)
        self.master.bind("<Left>",self.previousCropped)
        self.master.unbind("<d>")
        self.master.unbind("<a>")
        self.master.bind("<Configure>",self.resizeEventTab2)
        self.master.unbind("<Control-z>")
        self.master.bind("<Return>",self.submitClassification)
        self.t2c2l16.bind("<FocusIn>",self.entry_focus_in)
        self.t2c2l16.bind("<FocusOut>",self.entry_focus_out)
        self.t2c2l16.bind("<Leave>",self.entry_focus_out)

    def stoprun(self):
        # unbind when switching to a new tab
        self.t2c2l16.unbind("<FocusIn>")
        self.t2c2l16.unbind("<FocusOut>")
        self.t2c2l16.unbind("<Leave>")

    def pingServer(self):
        """
        Checks if server is correctly connected

        @rtype:  None
        @return: None
        """
        self.serverConnected = self.interface.ping()
        if self.serverConnected:
            self.cropped_np = tab_tools.get_image('assets/classify_instructions.jpg')
        else:
            self.cropped_np = tab_tools.get_image('assets/server_error.jpg')

    def resizeEventTab2(self,event=None):
        """
        Resizes picture on Tab2
        @type  event: event
        @param event: resize window event

        @rtype:  None
        @return: None
        """
        if self.initialized and (time.time()-self.resize_counter_tab2) > 0.050:
            if self.t2c2i1.winfo_width() > 1:
                self.resize_counter_tab2 = time.time()
                self.master.update()
                self.t2c2i1_width = self.t2c2i1.winfo_width()
                self.t2c2i1_height = self.t2c2i1.winfo_height()
                self.cropped_resized_im = tab_tools.resizeIm(self.cropped_im,self.cropped_width,self.cropped_height,self.t2c2i1_width,self.t2c2i1_height)
                self.cropped_tk = tab_tools.im2tk(self.cropped_resized_im)
                self.t2c2i1.configure(image=self.cropped_tk)

    def nextCropped(self,event=None):
        """
        Requests and displays next cropped image

        @type  event: event
        @param event: Right arrow event

        @rtype:  None
        @return: None
        """
        if not(self.t2_entry_focus):
            self.serverConnected = self.interface.ping()
            if self.serverConnected:
                query = self.interface.getNextCroppedImage()
                if query == None:
                    self.t2_functional = False
                    self.noNextCropped()
                else:
                    self.t2_functional = True
                    self.imageID = query[1]
                    self.cropped_np = np.array(query[0])
                    yaw_angle = tab_tools.getYawAngle(self.interface,self.imageID)
                    self.cropped_np = imutils.rotate_bound(self.cropped_np,yaw_angle)
                    status = query[2]
                    if status:
                        self.t2c2lr48b.configure(text='submitted',foreground='green')
                    else:
                        self.t2c2lr48b.configure(text='unsubmitted',foreground='red')
                self.cropped_im = tab_tools.np2im(self.cropped_np)
                self.cropped_width,self.cropped_height = self.cropped_im.size
                self.cropped_resized_im = tab_tools.resizeIm(self.cropped_im,self.cropped_width,self.cropped_height,self.t2c2i1_width,self.t2c2i1_height)
                self.cropped_tk = tab_tools.im2tk(self.cropped_resized_im)
                self.t2c2i1.configure(image=self.cropped_tk)

    def previousCropped(self,event):
        """
        Requests and displays previous cropped image

        @type  event: event
        @param event: Left arrow event

        @rtype:  None
        @return: None
        """
        if not(self.t2_entry_focus):
            focus = self.tab2.focus_get()
            self.serverConnected = self.interface.ping()
            if self.serverConnected:
                query = self.interface.getPrevCroppedImage()
                if query == None:
                    self.t2_functional = False
                    self.noPreviousCropped()
                else:
                    self.t2_functional = True
                    self.imageID = query[1]
                    self.cropped_np = np.array(query[0])
                    yaw_angle = tab_tools.getYawAngle(self.interface,self.imageID)
                    self.cropped_np = imutils.rotate_bound(self.cropped_np,yaw_angle)
                    status = query[2]
                    if status:
                        self.t2c2lr48b.configure(text='submitted',foreground='green')
                    else:
                        self.t2c2lr48b.configure(text='unsubmitted',foreground='red')
                self.cropped_im = tab_tools.np2im(self.cropped_np)
                self.cropped_width,self.cropped_height = self.cropped_im.size
                self.cropped_resized_im = tab_tools.resizeIm(self.cropped_im,self.cropped_width,self.cropped_height,self.t2c2i1_width,self.t2c2i1_height)
                self.cropped_tk = tab_tools.im2tk(self.cropped_resized_im)
                self.t2c2i1.configure(image=self.cropped_tk)

    def noNextCropped(self):
        """
        Checks if server is correctly connected

        @rtype:  None
        @return: None
        """
        self.serverConnected = self.interface.ping()
        if self.serverConnected:
            self.cropped_np = tab_tools.get_image('assets/noNextCropped.jpg')
            self.t2c2lr48b.configure(text='N/A',foreground='#636363')
        else:
            self.cropped_np = tab_tools.get_image('assets/server_error.jpg')
            self.t2c2lr48b.configure(text='N/A',foreground='#636363')

    def noPreviousCropped(self):
        """
        Checks if server is correctly connected

        @rtype:  None
        @return: None
        """
        self.serverConnected = self.interface.ping()
        if self.serverConnected:
            self.cropped_np = tab_tools.get_image('assets/noPreviousCropped.jpg')
            self.t2c2lr48b.configure(text='N/A',foreground='#636363')
        else:
            self.cropped_np = tab_tools.get_image('assets/server_error.jpg')
            self.t2c2lr48b.configure(text='N/A',foreground='#636363')


    def disableEmergentDescription(self,*args):
        """
        Disables emergent discription unless emergent target selected

        @rtype:  None
        @return: None
        """
        if self.t2c2l14_var.get() == 'emergent':
            self.t2c2l16.configure(state=tk.NORMAL)
            self.t2c2l2.configure(state=tk.DISABLED)
            self.t2c2l4.configure(state=tk.DISABLED)
            self.t2c2l6.configure(state=tk.DISABLED)
            self.t2c2l10.configure(state=tk.DISABLED)
            self.t2c2l12.configure(state=tk.DISABLED)
        else:
            self.t2c2l16_var.set(None)
            self.t2c2l16.configure(state=tk.DISABLED)
            self.t2c2l2.configure(state=tk.NORMAL)
            self.t2c2l4.configure(state=tk.NORMAL)
            self.t2c2l6.configure(state=tk.NORMAL)
            self.t2c2l10.configure(state=tk.NORMAL)
            self.t2c2l12.configure(state=tk.NORMAL)


    def alphanumericChanged(self,*args):
        """
        Fixes if you entered something wrong

        @rtype:  None
        @return: None
        """
        input = self.t2c2l4.get()
        if len(input) != 1:
            print("INPUT ERROR!")

    def alphanumericValidate(self,type, entry):
        """
        Fixes alphanumeric to be uppercase letter or digit

        @rtype:  None
        @return: None
        """
        if type == '1':
        # runs if you try to insert something
            if len(entry) == 1 and (entry.isdigit() or entry.isalpha()):
                if entry.isupper():
                    return True
                else:
                    self.t2c2l4_var.set(entry.upper())
                    return True
            else:
                return False
        else:
            return True

    def submitClassification(self,event=None):
        """
        Submits classification of image to server

        @type  event: event
        @param event: Enter press event

        @rtype:  None
        @return: None
        """
        if self.t2_functional:
            type = self.t2c2l14_var.get()
            if type == 'emergent':
                description = self.t2c2l16_var.get()
                classification = client_rest.Classification(self.imageID,type,desc = description)
                self.interface.postClass(classification)
                self.entry_focus_out()
                self.nextCropped()
            else:
                alphanumeric = self.t2c2l4.get()
                if alphanumeric != "":
                    shape = self.t2c2l2_var.get()
                    orientation = self.t2c2l6_var.get()
                    background_color = self.t2c2l10_var.get()
                    alpha_color = self.t2c2l12_var.get()
                    classification = client_rest.Classification(self.imageID,type,orientation=orientation,shape=shape,bgColor=background_color,alpha=alphanumeric,alphaColor=alpha_color)
                    self.interface.postClass(classification)
                    self.entry_focus_out()
                    self.nextCropped()

    def entry_focus_in(self,event=None):
        self.t2_entry_focus = True

    def entry_focus_out(self,event=None):
        self.t2_entry_focus = False
        # set focus onto image (away from entry widget)
        self.t2c2i1.focus_set()
