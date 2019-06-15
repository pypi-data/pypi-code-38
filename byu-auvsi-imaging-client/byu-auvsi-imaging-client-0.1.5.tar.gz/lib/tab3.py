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

"""
# TODO:
    Show in blue which target it's pulling the "to submit" classificaiton from
    Change radiobuttons to match ttktheme
    Fix resizing issues
    Possibly auto updating? (if other people are pushing classifications)
"""

class Tab3():
    """
    Display results for manual classification
    """
    def __init__(self,master,notebook,interface):
        self.master = master
        self.n = notebook
        self.interface = interface
        self.initialized = False

        # Tab 3 variables
        self.resize_counter_tab3 = time.time()
        self.t3_total_targets  = 0
        self.t3_current_target = 1
        self.submit_crop_id = None
        self.submit_orientation = None
        self.submit_bg_color = None
        self.submit_alpha_color = None
        self.submit_desc = None

        '''
        # new radiobutton Style
        s = ttk.Style()
        s.configure('Centered.TRadiobutton',width=30,justify=tk.CENTER)
        s.configure('Centered.TRadiobutton',justify=tk.CENTER)
        '''

        # TAB 3: MANUAL TARGET SUBMISSION ------------------------------------------------
        self.tab3 = ttk.Frame(self.n)
        self.n.add(self.tab3, text='Manual Target Submission')

        for x in range(12):
            tk.Grid.columnconfigure(self.tab3,x,weight=1)
        for y in range(21):
            tk.Grid.rowconfigure(self.tab3,y,weight=1)

        self.t3_default_np = tab_tools.get_image('assets/noClassifiedTargets.jpg')
        self.t3_default_im = tab_tools.np2im(self.t3_default_np)
        self.t3_default_width,self.t3_default_height = self.t3_default_im.size
        self.t3_default_tk = tab_tools.im2tk(self.t3_default_im)

        # Title
        self.t3titleA = ttk.Label(self.tab3, anchor=tk.CENTER, text='Target # %i out of %i'%(self.t3_current_target,self.t3_total_targets))
        self.t3titleA.grid(row=0,column=2,columnspan=3,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)

        self.t3titleB = ttk.Label(self.tab3, anchor=tk.CENTER, text='Showing %i images out of %i that exsist'%(0,0))
        self.t3titleB.grid(row=0,column=5,columnspan=3,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)

        # Column One
        self.t3c1title = ttk.Label(self.tab3, anchor=tk.CENTER, text='Pic 1')
        self.t3c1title.grid(row=1,column=0,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c1i1_im = self.t3_default_im.copy()
        self.t3c1i1_tk = tab_tools.im2tk(self.t3c1i1_im)
        self.t3c1i1_org_width,self.t3c1i1_org_height = self.t3c1i1_im.size
        self.t3c1i1 = ttk.Label(self.tab3, anchor=tk.CENTER,image=self.t3c1i1_tk)
        self.t3c1i1.image = self.t3c1i1_tk
        self.t3c1i1.grid(row=3,column=0,rowspan=1,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        # Characteristics
        self.submissionImage = tk.IntVar()
        self.t3c1r4 = tk.Radiobutton(self.tab3,value=1,variable=self.submissionImage,command=self.selectImage)
        self.t3c1r4.configure(foreground="#5c616c",background="#f5f6f7",highlightthickness=0,anchor=tk.N)
        self.t3c1r4.grid(row=4,column=0,columnspan=2,sticky=tk.N+tk.E+tk.W+tk.S,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c1ar5 = ttk.Label(self.tab3, anchor=tk.CENTER, text="Shape:")
        self.t3c1ar5.grid(row=5,column=0,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c1br5 = ttk.Label(self.tab3, anchor=tk.CENTER, text="N/A")
        self.t3c1br5.grid(row=5,column=1,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c1ar7 = ttk.Label(self.tab3, anchor=tk.S, text="Background Color:")
        self.t3c1ar7.grid(row=7,column=0,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c1br7 = ttk.Label(self.tab3, anchor=tk.S, text="N/A")
        self.t3c1br7.grid(row=7,column=1,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.submissionBackgroundColor = tk.IntVar()
        self.t3c1r8 = tk.Radiobutton(self.tab3,value=1,variable=self.submissionBackgroundColor,command=self.selectBackgroundColor)
        self.t3c1r8.configure(foreground="#5c616c",background="#f5f6f7",highlightthickness=0,anchor=tk.N)
        self.t3c1r8.grid(row=8,column=0,columnspan=2,sticky=tk.N+tk.E+tk.W+tk.S,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c1ar9 = ttk.Label(self.tab3, anchor=tk.CENTER, text="Alphanumeric:")
        self.t3c1ar9.grid(row=9,column=0,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c1br9 = ttk.Label(self.tab3, anchor=tk.CENTER, text="N/A")
        self.t3c1br9.grid(row=9,column=1,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c1ar11 = ttk.Label(self.tab3, anchor=tk.S, text="Alphanumeric Color:")
        self.t3c1ar11.grid(row=11,column=0,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c1br11 = ttk.Label(self.tab3, anchor=tk.S, text="N/A")
        self.t3c1br11.grid(row=11,column=1,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.submissionAlphanumericColor = tk.IntVar()
        self.t3c1r12 = tk.Radiobutton(self.tab3,value=1,variable=self.submissionAlphanumericColor,command=self.selectAlphanumericColor)
        self.t3c1r12.configure(foreground="#5c616c",background="#f5f6f7",highlightthickness=0,anchor=tk.N)
        self.t3c1r12.grid(row=12,column=0,columnspan=2,sticky=tk.N+tk.E+tk.W+tk.S,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c1ar13 = ttk.Label(self.tab3, anchor=tk.S, text="Orientation:")
        self.t3c1ar13.grid(row=13,column=0,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c1br13 = ttk.Label(self.tab3, anchor=tk.S, text="N/A")
        self.t3c1br13.grid(row=13,column=1,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.submissionOrientation = tk.IntVar()
        self.t3c1r14 = tk.Radiobutton(self.tab3,value=1,variable=self.submissionOrientation,command=self.selectOrientation)
        self.t3c1r14.configure(foreground="#5c616c",background="#f5f6f7",highlightthickness=0,anchor=tk.N)
        self.t3c1r14.grid(row=14,column=0,columnspan=2,sticky=tk.N+tk.E+tk.W+tk.S,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c1ar15 = ttk.Label(self.tab3, anchor=tk.CENTER, text="Target Type:")
        self.t3c1ar15.grid(row=15,column=0,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c1br15 = ttk.Label(self.tab3, anchor=tk.CENTER, text="N/A")
        self.t3c1br15.grid(row=15,column=1,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c1r17 = ttk.Label(self.tab3, anchor=tk.CENTER, text="Description:")
        self.t3c1r17.grid(row=17,column=0,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c1r18 = ttk.Label(self.tab3, anchor=tk.CENTER, text="N/A")
        self.t3c1r18.grid(row=18,column=0,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.submissionDescription = tk.IntVar()
        self.t3c1r19 = tk.Radiobutton(self.tab3,value=1,variable=self.submissionDescription,command=self.selectDescription)
        self.t3c1r19.configure(foreground="#5c616c",background="#f5f6f7",highlightthickness=0,anchor=tk.N)
        self.t3c1r19.grid(row=19,column=0,columnspan=2,sticky=tk.N+tk.E+tk.W+tk.S,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c1b1 = ttk.Button(self.tab3, text="Delete Classification",command=self.deleteClassification1)
        self.t3c1b1.grid(row=20,column=0,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)



        # Column Two
        self.t3c2title = ttk.Label(self.tab3, anchor=tk.CENTER, text='Pic 2')
        self.t3c2title.grid(row=1,column=2,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c2i1_im = self.t3_default_im.copy()
        self.t3c2i1_tk = tab_tools.im2tk(self.t3c2i1_im)
        self.t3c2i1_org_width,self.t3c2i1_org_height = self.t3c2i1_im.size
        self.t3c2i1 = ttk.Label(self.tab3, anchor=tk.CENTER,image=self.t3c2i1_tk)
        self.t3c2i1.image = self.t3c2i1_tk
        self.t3c2i1.grid(row=3,column=2,rowspan=1,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        # Characteristics
        self.t3c2r4 = tk.Radiobutton(self.tab3,value=2,variable=self.submissionImage,command=self.selectImage)
        self.t3c2r4.configure(foreground="#5c616c",background="#f5f6f7",highlightthickness=0,anchor=tk.N)
        self.t3c2r4.grid(row=4,column=2,columnspan=2,sticky=tk.N+tk.E+tk.W+tk.S,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c2ar5 = ttk.Label(self.tab3, anchor=tk.CENTER, text="Shape:")
        self.t3c2ar5.grid(row=5,column=2,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c2br5 = ttk.Label(self.tab3, anchor=tk.CENTER, text="N/A")
        self.t3c2br5.grid(row=5,column=3,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c2ar7 = ttk.Label(self.tab3, anchor=tk.S, text="Background Color:")
        self.t3c2ar7.grid(row=7,column=2,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c2br7 = ttk.Label(self.tab3, anchor=tk.S, text="N/A")
        self.t3c2br7.grid(row=7,column=3,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c2r8 = tk.Radiobutton(self.tab3,value=2,variable=self.submissionBackgroundColor,command=self.selectBackgroundColor)
        self.t3c2r8.configure(foreground="#5c616c",background="#f5f6f7",highlightthickness=0,anchor=tk.N)
        self.t3c2r8.grid(row=8,column=2,columnspan=2,sticky=tk.N+tk.E+tk.W+tk.S,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c2ar9 = ttk.Label(self.tab3, anchor=tk.CENTER, text="Alphanumeric:")
        self.t3c2ar9.grid(row=9,column=2,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c2br9 = ttk.Label(self.tab3, anchor=tk.CENTER, text="N/A")
        self.t3c2br9.grid(row=9,column=3,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c2ar11 = ttk.Label(self.tab3, anchor=tk.S, text="Alphanumeric Color:")
        self.t3c2ar11.grid(row=11,column=2,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c2br11 = ttk.Label(self.tab3, anchor=tk.S, text="N/A")
        self.t3c2br11.grid(row=11,column=3,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c2r12 = tk.Radiobutton(self.tab3,value=2,variable=self.submissionAlphanumericColor,command=self.selectAlphanumericColor)
        self.t3c2r12.configure(foreground="#5c616c",background="#f5f6f7",highlightthickness=0,anchor=tk.N)
        self.t3c2r12.grid(row=12,column=2,columnspan=2,sticky=tk.N+tk.E+tk.W+tk.S,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c2ar13 = ttk.Label(self.tab3, anchor=tk.S, text="Orientation:")
        self.t3c2ar13.grid(row=13,column=2,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c2br13 = ttk.Label(self.tab3, anchor=tk.S, text="N/A")
        self.t3c2br13.grid(row=13,column=3,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c2r14 = tk.Radiobutton(self.tab3,value=2,variable=self.submissionOrientation,command=self.selectOrientation)
        self.t3c2r14.configure(foreground="#5c616c",background="#f5f6f7",highlightthickness=0,anchor=tk.N)
        self.t3c2r14.grid(row=14,column=2,columnspan=2,sticky=tk.N+tk.E+tk.W+tk.S,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c2ar15 = ttk.Label(self.tab3, anchor=tk.CENTER, text="Target Type:")
        self.t3c2ar15.grid(row=15,column=2,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c2br15 = ttk.Label(self.tab3, anchor=tk.CENTER, text="N/A")
        self.t3c2br15.grid(row=15,column=3,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c2r17 = ttk.Label(self.tab3, anchor=tk.CENTER, text="Description:")
        self.t3c2r17.grid(row=17,column=2,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c2r18 = ttk.Label(self.tab3, anchor=tk.CENTER, text="N/A")
        self.t3c2r18.grid(row=18,column=2,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c2r19 = tk.Radiobutton(self.tab3,value=2,variable=self.submissionDescription,command=self.selectDescription)
        self.t3c2r19.configure(foreground="#5c616c",background="#f5f6f7",highlightthickness=0,anchor=tk.N)
        self.t3c2r19.grid(row=19,column=2,columnspan=2,sticky=tk.N+tk.E+tk.W+tk.S,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c2b1 = ttk.Button(self.tab3, text="Delete Classification",command=self.deleteClassification2)
        self.t3c2b1.grid(row=20,column=2,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)


        # Column Three
        self.t3c3title = ttk.Label(self.tab3, anchor=tk.CENTER, text='Pic 3')
        self.t3c3title.grid(row=1,column=4,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c3i1_im = self.t3_default_im.copy()
        self.t3c3i1_tk = tab_tools.im2tk(self.t3c3i1_im)
        self.t3c3i1_org_width,self.t3c3i1_org_height = self.t3c3i1_im.size
        self.t3c3i1 = ttk.Label(self.tab3, anchor=tk.CENTER,image=self.t3c3i1_tk)
        self.t3c3i1.image = self.t3c3i1_tk
        self.t3c3i1.grid(row=3,column=4,rowspan=1,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        # Characteristics
        self.t3c3r4 = tk.Radiobutton(self.tab3,value=3,variable=self.submissionImage,command=self.selectImage)
        self.t3c3r4.configure(foreground="#5c616c",background="#f5f6f7",highlightthickness=0,anchor=tk.N)
        self.t3c3r4.grid(row=4,column=4,columnspan=2,sticky=tk.N+tk.E+tk.W+tk.S,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c3ar5 = ttk.Label(self.tab3, anchor=tk.CENTER, text="Shape:")
        self.t3c3ar5.grid(row=5,column=4,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c3br5 = ttk.Label(self.tab3, anchor=tk.CENTER, text="N/A")
        self.t3c3br5.grid(row=5,column=5,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c3ar7 = ttk.Label(self.tab3, anchor=tk.S, text="Background Color:")
        self.t3c3ar7.grid(row=7,column=4,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c3br7 = ttk.Label(self.tab3, anchor=tk.S, text="N/A")
        self.t3c3br7.grid(row=7,column=5,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c3r8 = tk.Radiobutton(self.tab3,value=3,variable=self.submissionBackgroundColor,command=self.selectBackgroundColor)
        self.t3c3r8.configure(foreground="#5c616c",background="#f5f6f7",highlightthickness=0,anchor=tk.N)
        self.t3c3r8.grid(row=8,column=4,columnspan=2,sticky=tk.N+tk.E+tk.W+tk.S,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c3ar9 = ttk.Label(self.tab3, anchor=tk.CENTER, text="Alphanumeric:")
        self.t3c3ar9.grid(row=9,column=4,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c3br9 = ttk.Label(self.tab3, anchor=tk.CENTER, text="N/A")
        self.t3c3br9.grid(row=9,column=5,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c3ar11 = ttk.Label(self.tab3, anchor=tk.S, text="Alphanumeric Color:")
        self.t3c3ar11.grid(row=11,column=4,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c3br11 = ttk.Label(self.tab3, anchor=tk.S, text="N/A")
        self.t3c3br11.grid(row=11,column=5,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c3r12 = tk.Radiobutton(self.tab3,value=3,variable=self.submissionAlphanumericColor,command=self.selectAlphanumericColor)
        self.t3c3r12.configure(foreground="#5c616c",background="#f5f6f7",highlightthickness=0,anchor=tk.N)
        self.t3c3r12.grid(row=12,column=4,columnspan=2,sticky=tk.N+tk.E+tk.W+tk.S,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c3ar13 = ttk.Label(self.tab3, anchor=tk.S, text="Orientation:")
        self.t3c3ar13.grid(row=13,column=4,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c3br13 = ttk.Label(self.tab3, anchor=tk.S, text="N/A")
        self.t3c3br13.grid(row=13,column=5,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c3r14 = tk.Radiobutton(self.tab3,value=3,variable=self.submissionOrientation,command=self.selectOrientation)
        self.t3c3r14.configure(foreground="#5c616c",background="#f5f6f7",highlightthickness=0,anchor=tk.N)
        self.t3c3r14.grid(row=14,column=4,columnspan=2,sticky=tk.N+tk.E+tk.W+tk.S,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c3ar15 = ttk.Label(self.tab3, anchor=tk.CENTER, text="Target Type:")
        self.t3c3ar15.grid(row=15,column=4,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c3br15 = ttk.Label(self.tab3, anchor=tk.CENTER, text="N/A")
        self.t3c3br15.grid(row=15,column=5,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c3r17 = ttk.Label(self.tab3, anchor=tk.CENTER, text="Description:")
        self.t3c3r17.grid(row=17,column=4,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c3r18 = ttk.Label(self.tab3, anchor=tk.CENTER, text="N/A")
        self.t3c3r18.grid(row=18,column=4,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c3r19 = tk.Radiobutton(self.tab3,value=3,variable=self.submissionDescription,command=self.selectDescription)
        self.t3c3r19.configure(foreground="#5c616c",background="#f5f6f7",highlightthickness=0,anchor=tk.N)
        self.t3c3r19.grid(row=19,column=4,columnspan=2,sticky=tk.N+tk.E+tk.W+tk.S,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c3b1 = ttk.Button(self.tab3, text="Delete Classification",command=self.deleteClassification3)
        self.t3c3b1.grid(row=20,column=4,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)


        # Column Four
        self.t3c4title = ttk.Label(self.tab3, anchor=tk.CENTER, text='Pic 4')
        self.t3c4title.grid(row=1,column=6,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c4i1_im = self.t3_default_im.copy()
        self.t3c4i1_tk = tab_tools.im2tk(self.t3c4i1_im)
        self.t3c4i1_org_width,self.t3c4i1_org_height = self.t3c4i1_im.size
        self.t3c4i1 = ttk.Label(self.tab3, anchor=tk.CENTER,image=self.t3c4i1_tk)
        self.t3c4i1.image = self.t3c4i1_tk
        self.t3c4i1.grid(row=3,column=6,rowspan=1,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        # Characteristics
        self.t3c4r4 = tk.Radiobutton(self.tab3,value=4,variable=self.submissionImage,command=self.selectImage)
        self.t3c4r4.configure(foreground="#5c616c",background="#f5f6f7",highlightthickness=0,anchor=tk.N)
        self.t3c4r4.grid(row=4,column=6,columnspan=2,sticky=tk.N+tk.E+tk.W+tk.S,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c4ar5 = ttk.Label(self.tab3, anchor=tk.CENTER, text="Shape:")
        self.t3c4ar5.grid(row=5,column=6,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c4br5 = ttk.Label(self.tab3, anchor=tk.CENTER, text="N/A")
        self.t3c4br5.grid(row=5,column=7,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c4ar7 = ttk.Label(self.tab3, anchor=tk.S, text="Background Color:")
        self.t3c4ar7.grid(row=7,column=6,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c4br7 = ttk.Label(self.tab3, anchor=tk.S, text="N/A")
        self.t3c4br7.grid(row=7,column=7,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c4r8 = tk.Radiobutton(self.tab3,value=4,variable=self.submissionBackgroundColor,command=self.selectBackgroundColor)
        self.t3c4r8.configure(foreground="#5c616c",background="#f5f6f7",highlightthickness=0,anchor=tk.N)
        self.t3c4r8.grid(row=8,column=6,columnspan=2,sticky=tk.N+tk.E+tk.W+tk.S,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c4ar9 = ttk.Label(self.tab3, anchor=tk.CENTER, text="Alphanumeric:")
        self.t3c4ar9.grid(row=9,column=6,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c4br9 = ttk.Label(self.tab3, anchor=tk.CENTER, text="N/A")
        self.t3c4br9.grid(row=9,column=7,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c4ar11 = ttk.Label(self.tab3, anchor=tk.S, text="Alphanumeric Color:")
        self.t3c4ar11.grid(row=11,column=6,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c4br11 = ttk.Label(self.tab3, anchor=tk.S, text="N/A")
        self.t3c4br11.grid(row=11,column=7,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c4r12 = tk.Radiobutton(self.tab3,value=4,variable=self.submissionAlphanumericColor,command=self.selectAlphanumericColor)
        self.t3c4r12.configure(foreground="#5c616c",background="#f5f6f7",highlightthickness=0,anchor=tk.N)
        self.t3c4r12.grid(row=12,column=6,columnspan=2,sticky=tk.N+tk.E+tk.W+tk.S,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c4ar13 = ttk.Label(self.tab3, anchor=tk.S, text="Orientation:")
        self.t3c4ar13.grid(row=13,column=6,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c4br13 = ttk.Label(self.tab3, anchor=tk.S, text="N/A")
        self.t3c4br13.grid(row=13,column=7,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c4r14 = tk.Radiobutton(self.tab3,value=4,variable=self.submissionOrientation,command=self.selectOrientation)
        self.t3c4r14.configure(foreground="#5c616c",background="#f5f6f7",highlightthickness=0,anchor=tk.N)
        self.t3c4r14.grid(row=14,column=6,columnspan=2,sticky=tk.N+tk.E+tk.W+tk.S,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c4ar15 = ttk.Label(self.tab3, anchor=tk.CENTER, text="Target Type:")
        self.t3c4ar15.grid(row=15,column=6,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c4br15 = ttk.Label(self.tab3, anchor=tk.CENTER, text="N/A")
        self.t3c4br15.grid(row=15,column=7,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c4r17 = ttk.Label(self.tab3, anchor=tk.CENTER, text="Description:")
        self.t3c4r17.grid(row=17,column=6,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c4r18 = ttk.Label(self.tab3, anchor=tk.CENTER, text="N/A")
        self.t3c4r18.grid(row=18,column=6,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c4r19 = tk.Radiobutton(self.tab3,value=4,variable=self.submissionDescription,command=self.selectDescription)
        self.t3c4r19.configure(foreground="#5c616c",background="#f5f6f7",highlightthickness=0,anchor=tk.N)
        self.t3c4r19.grid(row=19,column=6,columnspan=2,sticky=tk.N+tk.E+tk.W+tk.S,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c4b1 = ttk.Button(self.tab3, text="Delete Classification",command=self.deleteClassification4)
        self.t3c4b1.grid(row=20,column=6,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)



        # Column Five
        self.t3c5title = ttk.Label(self.tab3, anchor=tk.CENTER, text='Pic 5')
        self.t3c5title.grid(row=1,column=8,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c5i1_im = self.t3_default_im.copy()
        self.t3c5i1_tk = tab_tools.im2tk(self.t3c5i1_im)
        self.t3c5i1_org_width,self.t3c5i1_org_height = self.t3c5i1_im.size
        self.t3c5i1 = ttk.Label(self.tab3, anchor=tk.CENTER,image=self.t3c5i1_tk)
        self.t3c5i1.image = self.t3c5i1_tk
        self.t3c5i1.grid(row=3,column=8,rowspan=1,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        # Characteristics
        self.t3c5r4 = tk.Radiobutton(self.tab3,value=5,variable=self.submissionImage,command=self.selectImage)
        self.t3c5r4.configure(foreground="#5c616c",background="#f5f6f7",highlightthickness=0,anchor=tk.N)
        self.t3c5r4.grid(row=4,column=8,columnspan=2,sticky=tk.N+tk.E+tk.W+tk.S,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c5ar5 = ttk.Label(self.tab3, anchor=tk.CENTER, text="Shape:")
        self.t3c5ar5.grid(row=5,column=8,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c5br5 = ttk.Label(self.tab3, anchor=tk.CENTER, text="N/A")
        self.t3c5br5.grid(row=5,column=9,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c5ar7 = ttk.Label(self.tab3, anchor=tk.S, text="Background Color:")
        self.t3c5ar7.grid(row=7,column=8,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c5br7 = ttk.Label(self.tab3, anchor=tk.S, text="N/A")
        self.t3c5br7.grid(row=7,column=9,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c5r8 = tk.Radiobutton(self.tab3,value=5,variable=self.submissionBackgroundColor,command=self.selectBackgroundColor)
        self.t3c5r8.configure(foreground="#5c616c",background="#f5f6f7",highlightthickness=0,anchor=tk.N)
        self.t3c5r8.grid(row=8,column=8,columnspan=2,sticky=tk.N+tk.E+tk.W+tk.S,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c5ar9 = ttk.Label(self.tab3, anchor=tk.CENTER, text="Alphanumeric:")
        self.t3c5ar9.grid(row=9,column=8,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c5br9 = ttk.Label(self.tab3, anchor=tk.CENTER, text="N/A")
        self.t3c5br9.grid(row=9,column=9,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c5ar11 = ttk.Label(self.tab3, anchor=tk.S, text="Alphanumeric Color:")
        self.t3c5ar11.grid(row=11,column=8,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c5br11 = ttk.Label(self.tab3, anchor=tk.S, text="N/A")
        self.t3c5br11.grid(row=11,column=9,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c5r12 = tk.Radiobutton(self.tab3,value=5,variable=self.submissionAlphanumericColor,command=self.selectAlphanumericColor)
        self.t3c5r12.configure(foreground="#5c616c",background="#f5f6f7",highlightthickness=0,anchor=tk.N)
        self.t3c5r12.grid(row=12,column=8,columnspan=2,sticky=tk.N+tk.E+tk.W+tk.S,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c5ar13 = ttk.Label(self.tab3, anchor=tk.S, text="Orientation:")
        self.t3c5ar13.grid(row=13,column=8,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c5br13 = ttk.Label(self.tab3, anchor=tk.S, text="N/A")
        self.t3c5br13.grid(row=13,column=9,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c5r14 = tk.Radiobutton(self.tab3,value=5,variable=self.submissionOrientation,command=self.selectOrientation)
        self.t3c5r14.configure(foreground="#5c616c",background="#f5f6f7",highlightthickness=0,anchor=tk.N)
        self.t3c5r14.grid(row=14,column=8,columnspan=2,sticky=tk.N+tk.E+tk.W+tk.S,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c5ar15 = ttk.Label(self.tab3, anchor=tk.CENTER, text="Target Type:")
        self.t3c5ar15.grid(row=15,column=8,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c5br15 = ttk.Label(self.tab3, anchor=tk.CENTER, text="N/A")
        self.t3c5br15.grid(row=15,column=9,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c5r17 = ttk.Label(self.tab3, anchor=tk.CENTER, text="Description:")
        self.t3c5r17.grid(row=17,column=8,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c5r18 = ttk.Label(self.tab3, anchor=tk.CENTER, text="N/A")
        self.t3c5r18.grid(row=18,column=8,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c5r19 = tk.Radiobutton(self.tab3,value=5,variable=self.submissionDescription,command=self.selectDescription)
        self.t3c5r19.configure(foreground="#5c616c",background="#f5f6f7",highlightthickness=0,anchor=tk.N)
        self.t3c5r19.grid(row=19,column=8,columnspan=2,sticky=tk.N+tk.E+tk.W+tk.S,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c5b1 = ttk.Button(self.tab3, text="Delete Classification",command=self.deleteClassification5)
        self.t3c5b1.grid(row=20,column=8,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)


        # Column Six
        self.t3sep56 = ttk.Separator(self.tab3, orient=tk.VERTICAL)
        self.t3sep56.grid(row=1, column=10, rowspan=20,sticky=tk.N+tk.S+tk.E+tk.W, pady=5)
        self.t3c6title = ttk.Label(self.tab3, anchor=tk.CENTER, text='To Submit')
        self.t3c6title.grid(row=1,column=10,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c6i1_im = self.t3_default_im.copy()
        self.t3c6i1_tk = tab_tools.im2tk(self.t3c6i1_im)
        self.t3c6i1_org_width,self.t3c6i1_org_height = self.t3c6i1_im.size
        self.t3c6i1 = ttk.Label(self.tab3, anchor=tk.CENTER,image=self.t3c6i1_tk)
        self.t3c6i1.image = self.t3c6i1_tk
        self.t3c6i1.grid(row=3,column=10,rowspan=1,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        # Characteristics
        self.t3c6ar5 = ttk.Label(self.tab3, anchor=tk.CENTER, text="Shape:")
        self.t3c6ar5.grid(row=5,column=10,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c6br5 = ttk.Label(self.tab3, anchor=tk.CENTER, text="N/A")
        self.t3c6br5.grid(row=5,column=11,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c6ar7 = ttk.Label(self.tab3, anchor=tk.CENTER, text="Background Color:")
        self.t3c6ar7.grid(row=7,column=10,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c6br7 = ttk.Label(self.tab3, anchor=tk.CENTER, text="N/A")
        self.t3c6br7.grid(row=7,column=11,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c6ar9 = ttk.Label(self.tab3, anchor=tk.CENTER, text="Alphanumeric:")
        self.t3c6ar9.grid(row=9,column=10,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c6br9 = ttk.Label(self.tab3, anchor=tk.CENTER, text="N/A")
        self.t3c6br9.grid(row=9,column=11,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c6ar11 = ttk.Label(self.tab3, anchor=tk.CENTER, text="Alphanumeric Color:")
        self.t3c6ar11.grid(row=11,column=10,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c6br11 = ttk.Label(self.tab3, anchor=tk.CENTER, text="N/A")
        self.t3c6br11.grid(row=11,column=11,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c6ar13 = ttk.Label(self.tab3, anchor=tk.CENTER, text="Orientation:")
        self.t3c6ar13.grid(row=13,column=10,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c6br13 = ttk.Label(self.tab3, anchor=tk.CENTER, text="N/A")
        self.t3c6br13.grid(row=13,column=11,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c6ar15 = ttk.Label(self.tab3, anchor=tk.CENTER, text="Target Type:")
        self.t3c6ar15.grid(row=15,column=10,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c6br15 = ttk.Label(self.tab3, anchor=tk.CENTER, text="N/A")
        self.t3c6br15.grid(row=15,column=11,columnspan=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c6r17 = ttk.Label(self.tab3, anchor=tk.CENTER, text="Description:")
        self.t3c6r17.grid(row=17,column=10,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.t3c6r18 = ttk.Label(self.tab3, anchor=tk.CENTER, text="N/A")
        self.t3c6r18.grid(row=18,column=10,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        # Submit button
        self.t3c6b1 = ttk.Button(self.tab3, text="Submit Target",command=self.submitTarget)
        self.t3c6b1.grid(row=20,column=10,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)

        self.initialized = True

    def run(self,interface):
        self.interface = interface
        self.resizeEventTab3()
        # setup all keybindings
        self.master.bind("<Right>",self.nextClassified)
        self.master.bind("<Left>",self.previousClassified)
        self.master.unbind("<d>")
        self.master.unbind("<a>")
        self.master.bind("<Configure>",self.resizeEventTab3)
        self.master.unbind("<Control-z>")
        self.master.bind("<Return>",self.submitTarget)
        # bind images to radiobuttons
        self.t3c1i1.bind("<Button-1>",self.click_image1)
        self.t3c2i1.bind("<Button-1>",self.click_image2)
        self.t3c3i1.bind("<Button-1>",self.click_image3)
        self.t3c4i1.bind("<Button-1>",self.click_image4)
        self.t3c5i1.bind("<Button-1>",self.click_image5)


        self.updateManualSubmissionTab()

    def stoprun(self):
        self.t3c1i1.unbind("<Button-1>")
        self.t3c2i1.unbind("<Button-1>")
        self.t3c3i1.unbind("<Button-1>")
        self.t3c4i1.unbind("<Button-1>")
        self.t3c5i1.unbind("<Button-1>")


    def resizeEventTab3(self,event=None):
        """
        Resizes picture on Tab3
        @type  event: event
        @param event: resize window event

        @rtype:  None
        @return: None
        """
        if self.initialized and (time.time()-self.resize_counter_tab3) > 0.050:
            if self.t3c1i1.winfo_width() > 1:
                self.resize_counter_tab3 = time.time()
                self.master.update()
                # Col 1 Image
                self.t3c1i1_width = self.t3c1i1.winfo_width()
                self.t3c1i1_height = self.t3c1i1.winfo_height()
                resized_im = tab_tools.resizeIm(self.t3c1i1_im,self.t3c1i1_org_width,self.t3c1i1_org_height,self.t3c1i1_width,self.t3c1i1_height)
                self.t3c1i1_tk = tab_tools.im2tk(resized_im)
                self.t3c1i1.configure(image=self.t3c1i1_tk)
                # Col 2 Image
                self.t3c2i1_width = self.t3c2i1.winfo_width()
                self.t3c2i1_height = self.t3c2i1.winfo_height()
                resized_im = tab_tools.resizeIm(self.t3c2i1_im,self.t3c2i1_org_width,self.t3c2i1_org_height,self.t3c2i1_width,self.t3c2i1_height)
                self.t3c2i1_tk = tab_tools.im2tk(resized_im)
                self.t3c2i1.configure(image=self.t3c2i1_tk)
                # Col 3 Image
                self.t3c3i1_width = self.t3c3i1.winfo_width()
                self.t3c3i1_height = self.t3c3i1.winfo_height()
                resized_im = tab_tools.resizeIm(self.t3c3i1_im,self.t3c3i1_org_width,self.t3c3i1_org_height,self.t3c3i1_width,self.t3c3i1_height)
                self.t3c3i1_tk = tab_tools.im2tk(resized_im)
                self.t3c3i1.configure(image=self.t3c3i1_tk)
                # Col 4 Image
                self.t3c4i1_width = self.t3c4i1.winfo_width()
                self.t3c4i1_height = self.t3c4i1.winfo_height()
                resized_im = tab_tools.resizeIm(self.t3c4i1_im,self.t3c4i1_org_width,self.t3c4i1_org_height,self.t3c4i1_width,self.t3c4i1_height)
                self.t3c4i1_tk = tab_tools.im2tk(resized_im)
                self.t3c4i1.configure(image=self.t3c4i1_tk)
                # Col 5 Image
                self.t3c5i1_width = self.t3c5i1.winfo_width()
                self.t3c5i1_height = self.t3c5i1.winfo_height()
                resized_im = tab_tools.resizeIm(self.t3c5i1_im,self.t3c5i1_org_width,self.t3c5i1_org_height,self.t3c5i1_width,self.t3c5i1_height)
                self.t3c5i1_tk = tab_tools.im2tk(resized_im)
                self.t3c5i1.configure(image=self.t3c5i1_tk)
                # Col 6 Image
                self.t3c6i1_width = self.t3c6i1.winfo_width()
                self.t3c6i1_height = self.t3c6i1.winfo_height()
                resized_im = tab_tools.resizeIm(self.t3c6i1_im,self.t3c6i1_org_width,self.t3c6i1_org_height,self.t3c6i1_width,self.t3c6i1_height)
                self.t3c6i1_tk = tab_tools.im2tk(resized_im)
                self.t3c6i1.configure(image=self.t3c6i1_tk)

    def updateManualSubmissionTab(self):
        """
        This function populates the images and characteristics when
        you move between targets
        """
        self.serverConnected = self.interface.ping()
        if self.serverConnected:
            self.pendingList = self.interface.getPendingSubmissions()

            if self.pendingList == None:
                pics = 0
                self.t3titleA.configure(text='Target # %i out of %i'%(0,0))
                self.t3titleB.configure(text='Showing %i images out of %i that exsist'%(0,0))
                self.t3c1i1_im = self.t3_default_im.copy()
                self.t3c1i1_tk = tab_tools.im2tk(self.t3c1i1_im)
                self.t3c1i1_org_width,self.t3c1i1_org_height = self.t3c1i1_im.size
                self.t3c1i1.configure(image=self.t3c1i1_tk)
                self.t3c2i1_im = self.t3_default_im.copy()
                self.t3c2i1_tk = tab_tools.im2tk(self.t3c2i1_im)
                self.t3c2i1_org_width,self.t3c2i1_org_height = self.t3c2i1_im.size
                self.t3c2i1.configure(image=self.t3c2i1_tk)
                self.t3c3i1_im = self.t3_default_im.copy()
                self.t3c3i1_tk = tab_tools.im2tk(self.t3c3i1_im)
                self.t3c3i1_org_width,self.t3c3i1_org_height = self.t3c3i1_im.size
                self.t3c3i1.configure(image=self.t3c3i1_tk)
                self.t3c4i1_im = self.t3_default_im.copy()
                self.t3c4i1_tk = tab_tools.im2tk(self.t3c4i1_im)
                self.t3c4i1_org_width,self.t3c4i1_org_height = self.t3c4i1_im.size
                self.t3c4i1.configure(image=self.t3c4i1_tk)
                self.t3c5i1_im = self.t3_default_im.copy()
                self.t3c5i1_tk = tab_tools.im2tk(self.t3c5i1_im)
                self.t3c5i1_org_width,self.t3c5i1_org_height = self.t3c5i1_im.size
                self.t3c5i1.configure(image=self.t3c5i1_tk)
                self.t3c6i1_im = self.t3_default_im.copy()
                self.t3c6i1_tk = tab_tools.im2tk(self.t3c6i1_im)
                self.t3c6i1_org_width,self.t3c6i1_org_height = self.t3c6i1_im.size
                self.t3c6i1.configure(image=self.t3c6i1_tk)
                self.t3c1br5.configure(text="N/A")
                self.t3c1br7.configure(text="N/A")
                self.t3c1br9.configure(text="N/A")
                self.t3c1br11.configure(text="N/A")
                self.t3c1br13.configure(text="N/A")
                self.t3c1br15.configure(text="N/A")
                self.t3c1r18.configure(text="N/A")
                self.t3c1r4.configure(state=tk.DISABLED)
                self.t3c1r8.configure(state=tk.DISABLED)
                self.t3c1r12.configure(state=tk.DISABLED)
                self.t3c1r14.configure(state=tk.DISABLED)
                self.t3c1r19.configure(state=tk.DISABLED)
                self.t3c1b1.configure(state=tk.DISABLED)
                self.t3c6br5.configure(text="N/A")
                self.t3c6br7.configure(text="N/A")
                self.t3c6br9.configure(text="N/A")
                self.t3c6br11.configure(text="N/A")
                self.t3c6br13.configure(text="N/A")
                self.t3c6br15.configure(text="N/A")
                self.t3c6r18.configure(text="N/A")
                self.resizeEventTab3()
            else:
                self.t3_total_targets = len(self.pendingList)
                if self.t3_current_target == 0:
                    self.t3_current_target = 1
                elif self.t3_current_target > self.t3_total_targets:
                    self.t3_current_target = self.t3_total_targets
                self.t3titleA.configure(text='Target # %i out of %i'%(self.t3_current_target,self.t3_total_targets))
                pics = len(self.pendingList[self.t3_current_target-1])
                self.target_id = self.pendingList[self.t3_current_target-1][0].target
                pics_total = pics
                if pics > 5:
                    pics = 5
                pics_shown = pics
                self.t3titleB.configure(text='Showing %i images out of %i that exsist'%(pics_shown,pics_total))
                # Because of the preceeding if/else statement there will always be at least 1 pic
                query = self.interface.getCroppedImage(self.pendingList[self.t3_current_target-1][0].crop_id)
                self.t3c1i1_im = query[0]
                yaw_angle = tab_tools.getYawAngle(self.interface,query[1])
                self.t3c1i1_im = self.t3c1i1_im.rotate(-yaw_angle,expand=1)
                self.t3c1i1_org_width,self.t3c1i1_org_height = self.t3c1i1_im.size
                self.t3c1i1_tk = tab_tools.im2tk(self.t3c1i1_im)
                self.t3c1i1.configure(image=self.t3c1i1_tk)
                display_shape = self.pendingList[self.t3_current_target-1][0].shape
                if display_shape != None:
                    self.t3c1br5.configure(text=display_shape)
                else:
                    self.t3c1br5.configure(text="N/A")
                display_bg_color = self.pendingList[self.t3_current_target-1][0].background_color
                if display_bg_color != None:
                    self.t3c1br7.configure(text=display_bg_color)
                else:
                    self.t3c1br7.configure(text="N/A")
                display_alphanumeric = self.pendingList[self.t3_current_target-1][0].alphanumeric
                if display_alphanumeric != None:
                    self.t3c1br9.configure(text=display_alphanumeric)
                else:
                    self.t3c1br9.configure(text="N/A")
                display_alpha_color = self.pendingList[self.t3_current_target-1][0].alphanumeric_color
                if display_alpha_color != None:
                    self.t3c1br11.configure(text=display_alpha_color)
                else:
                    self.t3c1br11.configure(text="N/A")
                display_orientation = self.pendingList[self.t3_current_target-1][0].orientation
                if display_orientation != None:
                    self.t3c1br13.configure(text=display_orientation)
                else:
                    self.t3c1br13.configure(text="N/A")
                display_decription = self.pendingList[self.t3_current_target-1][0].description
                if display_decription != "":
                    self.t3c1r18.configure(text=display_decription)
                else:
                    self.t3c1r18.configure(text="N/A")
                self.t3c1br15.configure(text=self.pendingList[self.t3_current_target-1][0].type)
                if self.pendingList[self.t3_current_target-1][0].type == "emergent":
                    self.t3c1r4.configure(state=tk.NORMAL)
                    self.t3c1r8.configure(state=tk.DISABLED)
                    self.t3c1r12.configure(state=tk.DISABLED)
                    self.t3c1r14.configure(state=tk.DISABLED)
                    self.t3c1r19.configure(state=tk.NORMAL)
                    self.t3c1b1.configure(state=tk.NORMAL)
                else:
                    self.t3c1r4.configure(state=tk.NORMAL)
                    self.t3c1r8.configure(state=tk.NORMAL)
                    self.t3c1r12.configure(state=tk.NORMAL)
                    self.t3c1r14.configure(state=tk.NORMAL)
                    self.t3c1r19.configure(state=tk.DISABLED)
                    self.t3c1b1.configure(state=tk.NORMAL)
                self.pending_bg_color = [self.pendingList[self.t3_current_target-1][0].background_color]
                self.pending_alpha_color = [self.pendingList[self.t3_current_target-1][0].alphanumeric_color]
                self.pending_orientation = [self.pendingList[self.t3_current_target-1][0].orientation]
                self.pending_description = [self.pendingList[self.t3_current_target-1][0].description]

            if pics > 1:
                query = self.interface.getCroppedImage(self.pendingList[self.t3_current_target-1][1].crop_id)
                self.t3c2i1_im = query[0]
                yaw_angle = tab_tools.getYawAngle(self.interface,query[1])
                self.t3c2i1_im = self.t3c2i1_im.rotate(-yaw_angle,expand=1)
                self.t3c2i1_org_width,self.t3c2i1_org_height = self.t3c2i1_im.size
                self.t3c2i1_tk = tab_tools.im2tk(self.t3c2i1_im)
                self.t3c2i1.configure(image=self.t3c2i1_tk)
                display_shape = self.pendingList[self.t3_current_target-1][1].shape
                if display_shape != None:
                    self.t3c2br5.configure(text=display_shape)
                else:
                    self.t3c2br5.configure(text="N/A")
                display_bg_color = self.pendingList[self.t3_current_target-1][1].background_color
                if display_bg_color != None:
                    self.t3c2br7.configure(text=display_bg_color)
                else:
                    self.t3c2br7.configure(text="N/A")
                display_alphanumeric = self.pendingList[self.t3_current_target-1][1].alphanumeric
                if display_alphanumeric != None:
                    self.t3c2br9.configure(text=display_alphanumeric)
                else:
                    self.t3c2br9.configure(text="N/A")
                display_alpha_color = self.pendingList[self.t3_current_target-1][1].alphanumeric_color
                if display_alpha_color != None:
                    self.t3c2br11.configure(text=display_alpha_color)
                else:
                    self.t3c2br11.configure(text="N/A")
                display_orientation = self.pendingList[self.t3_current_target-1][1].orientation
                if display_orientation != None:
                    self.t3c2br13.configure(text=display_orientation)
                else:
                    self.t3c2br13.configure(text="N/A")
                display_decription = self.pendingList[self.t3_current_target-1][1].description
                if display_decription != "":
                    self.t3c2r18.configure(text=display_decription)
                else:
                    self.t3c2r18.configure(text="N/A")
                self.t3c2br15.configure(text=self.pendingList[self.t3_current_target-1][1].type)
                if self.pendingList[self.t3_current_target-1][1].type == "emergent":
                    self.t3c2r4.configure(state=tk.NORMAL)
                    self.t3c2r8.configure(state=tk.DISABLED)
                    self.t3c2r12.configure(state=tk.DISABLED)
                    self.t3c2r14.configure(state=tk.DISABLED)
                    self.t3c2r19.configure(state=tk.NORMAL)
                    self.t3c2b1.configure(state=tk.NORMAL)
                else:
                    self.t3c2r4.configure(state=tk.NORMAL)
                    self.t3c2r8.configure(state=tk.NORMAL)
                    self.t3c2r12.configure(state=tk.NORMAL)
                    self.t3c2r14.configure(state=tk.NORMAL)
                    self.t3c2r19.configure(state=tk.DISABLED)
                    self.t3c2b1.configure(state=tk.NORMAL)
                self.pending_bg_color.append(self.pendingList[self.t3_current_target-1][1].background_color)
                self.pending_alpha_color.append(self.pendingList[self.t3_current_target-1][1].alphanumeric_color)
                self.pending_orientation.append(self.pendingList[self.t3_current_target-1][1].orientation)
                self.pending_description.append(self.pendingList[self.t3_current_target-1][1].description)

            else:
                self.t3c2i1_im = self.t3_default_im.copy()
                self.t3c2i1_org_width,self.t3c2i1_org_height = self.t3c2i1_im.size
                self.t3c2i1_tk = tab_tools.im2tk(self.t3c2i1_im)
                self.t3c2i1.configure(image=self.t3c2i1_tk)
                self.t3c2br5.configure(text="N/A")
                self.t3c2br7.configure(text="N/A")
                self.t3c2br9.configure(text="N/A")
                self.t3c2br11.configure(text="N/A")
                self.t3c2br13.configure(text="N/A")
                self.t3c2br15.configure(text="N/A")
                self.t3c2r18.configure(text="N/A")
                self.t3c2r4.configure(state=tk.DISABLED)
                self.t3c2r8.configure(state=tk.DISABLED)
                self.t3c2r12.configure(state=tk.DISABLED)
                self.t3c2r14.configure(state=tk.DISABLED)
                self.t3c2r19.configure(state=tk.DISABLED)
                self.t3c2b1.configure(state=tk.DISABLED)

            if pics > 2:
                query = self.interface.getCroppedImage(self.pendingList[self.t3_current_target-1][2].crop_id)
                self.t3c3i1_im = query[0]
                yaw_angle = tab_tools.getYawAngle(self.interface,query[1])
                self.t3c3i1_im = self.t3c3i1_im.rotate(-yaw_angle,expand=1)
                self.t3c3i1_org_width,self.t3c3i1_org_height = self.t3c3i1_im.size
                self.t3c3i1_tk = tab_tools.im2tk(self.t3c3i1_im)
                self.t3c3i1.configure(image=self.t3c3i1_tk)
                display_shape = self.pendingList[self.t3_current_target-1][2].shape
                if display_shape != None:
                    self.t3c3br5.configure(text=display_shape)
                else:
                    self.t3c3br5.configure(text="N/A")
                display_bg_color = self.pendingList[self.t3_current_target-1][2].background_color
                if display_bg_color != None:
                    self.t3c3br7.configure(text=display_bg_color)
                else:
                    self.t3c3br7.configure(text="N/A")
                display_alphanumeric = self.pendingList[self.t3_current_target-1][2].alphanumeric
                if display_alphanumeric != None:
                    self.t3c3br9.configure(text=display_alphanumeric)
                else:
                    self.t3c3br9.configure(text="N/A")
                display_alpha_color = self.pendingList[self.t3_current_target-1][2].alphanumeric_color
                if display_alpha_color != None:
                    self.t3c3br11.configure(text=display_alpha_color)
                else:
                    self.t3c3br11.configure(text="N/A")
                display_orientation = self.pendingList[self.t3_current_target-1][2].orientation
                if display_orientation != None:
                    self.t3c3br13.configure(text=display_orientation)
                else:
                    self.t3c3br13.configure(text="N/A")
                display_decription = self.pendingList[self.t3_current_target-1][2].description
                if display_decription != "":
                    self.t3c3r18.configure(text=display_decription)
                else:
                    self.t3c3r18.configure(text="N/A")
                self.t3c3br15.configure(text=self.pendingList[self.t3_current_target-1][2].type)
                if self.pendingList[self.t3_current_target-1][2].type == "emergent":
                    self.t3c3r4.configure(state=tk.NORMAL)
                    self.t3c3r8.configure(state=tk.DISABLED)
                    self.t3c3r12.configure(state=tk.DISABLED)
                    self.t3c3r14.configure(state=tk.DISABLED)
                    self.t3c3r19.configure(state=tk.NORMAL)
                    self.t3c3b1.configure(state=tk.NORMAL)
                else:
                    self.t3c3r4.configure(state=tk.NORMAL)
                    self.t3c3r8.configure(state=tk.NORMAL)
                    self.t3c3r12.configure(state=tk.NORMAL)
                    self.t3c3r14.configure(state=tk.NORMAL)
                    self.t3c3r19.configure(state=tk.DISABLED)
                    self.t3c3b1.configure(state=tk.NORMAL)
                self.pending_bg_color.append(self.pendingList[self.t3_current_target-1][2].background_color)
                self.pending_alpha_color.append(self.pendingList[self.t3_current_target-1][2].alphanumeric_color)
                self.pending_orientation.append(self.pendingList[self.t3_current_target-1][2].orientation)
                self.pending_description.append(self.pendingList[self.t3_current_target-1][2].description)

            else:
                self.t3c3i1_im = self.t3_default_im.copy()
                self.t3c3i1_org_width,self.t3c3i1_org_height = self.t3c3i1_im.size
                self.t3c3i1_tk = tab_tools.im2tk(self.t3c3i1_im)
                self.t3c3i1.configure(image=self.t3c3i1_tk)
                self.t3c3br5.configure(text="N/A")
                self.t3c3br7.configure(text="N/A")
                self.t3c3br9.configure(text="N/A")
                self.t3c3br11.configure(text="N/A")
                self.t3c3br13.configure(text="N/A")
                self.t3c3br15.configure(text="N/A")
                self.t3c3r18.configure(text="N/A")
                self.t3c3r4.configure(state=tk.DISABLED)
                self.t3c3r8.configure(state=tk.DISABLED)
                self.t3c3r12.configure(state=tk.DISABLED)
                self.t3c3r14.configure(state=tk.DISABLED)
                self.t3c3r19.configure(state=tk.DISABLED)
                self.t3c3b1.configure(state=tk.DISABLED)

            if pics > 3:
                query = self.interface.getCroppedImage(self.pendingList[self.t3_current_target-1][3].crop_id)
                self.t3c4i1_im = query[0]
                yaw_angle = tab_tools.getYawAngle(self.interface,query[1])
                self.t3c4i1_im = self.t3c4i1_im.rotate(-yaw_angle,expand=1)
                self.t3c4i1_org_width,self.t3c4i1_org_height = self.t3c4i1_im.size
                self.t3c4i1_tk = tab_tools.im2tk(self.t3c4i1_im)
                self.t3c4i1.configure(image=self.t3c4i1_tk)
                display_shape = self.pendingList[self.t3_current_target-1][3].shape
                if display_shape != None:
                    self.t3c4br5.configure(text=display_shape)
                else:
                    self.t3c4br5.configure(text="N/A")
                display_bg_color = self.pendingList[self.t3_current_target-1][3].background_color
                if display_bg_color != None:
                    self.t3c4br7.configure(text=display_bg_color)
                else:
                    self.t3c4br7.configure(text="N/A")
                display_alphanumeric = self.pendingList[self.t3_current_target-1][3].alphanumeric
                if display_alphanumeric != None:
                    self.t3c4br9.configure(text=display_alphanumeric)
                else:
                    self.t3c4br9.configure(text="N/A")
                display_alpha_color = self.pendingList[self.t3_current_target-1][3].alphanumeric_color
                if display_alpha_color != None:
                    self.t3c4br11.configure(text=display_alpha_color)
                else:
                    self.t3c4br11.configure(text="N/A")
                display_orientation = self.pendingList[self.t3_current_target-1][3].orientation
                if display_orientation != None:
                    self.t3c4br13.configure(text=display_orientation)
                else:
                    self.t3c4br13.configure(text="N/A")
                display_decription = self.pendingList[self.t3_current_target-1][3].description
                if display_decription != "":
                    self.t3c4r18.configure(text=display_decription)
                else:
                    self.t3c4r18.configure(text="N/A")
                self.t3c4br15.configure(text=self.pendingList[self.t3_current_target-1][3].type)
                if self.pendingList[self.t3_current_target-1][3].type == "emergent":
                    self.t3c4r4.configure(state=tk.NORMAL)
                    self.t3c4r8.configure(state=tk.DISABLED)
                    self.t3c4r12.configure(state=tk.DISABLED)
                    self.t3c4r14.configure(state=tk.DISABLED)
                    self.t3c4r19.configure(state=tk.NORMAL)
                    self.t3c4b1.configure(state=tk.NORMAL)
                else:
                    self.t3c4r4.configure(state=tk.NORMAL)
                    self.t3c4r8.configure(state=tk.NORMAL)
                    self.t3c4r12.configure(state=tk.NORMAL)
                    self.t3c4r14.configure(state=tk.NORMAL)
                    self.t3c4r19.configure(state=tk.DISABLED)
                    self.t3c4b1.configure(state=tk.NORMAL)
                self.pending_bg_color.append(self.pendingList[self.t3_current_target-1][3].background_color)
                self.pending_alpha_color.append(self.pendingList[self.t3_current_target-1][3].alphanumeric_color)
                self.pending_orientation.append(self.pendingList[self.t3_current_target-1][3].orientation)
                self.pending_description.append(self.pendingList[self.t3_current_target-1][3].description)

            else:
                self.t3c4i1_im = self.t3_default_im.copy()
                self.t3c4i1_org_width,self.t3c4i1_org_height = self.t3c4i1_im.size
                self.t3c4i1_tk = tab_tools.im2tk(self.t3c4i1_im)
                self.t3c4i1.configure(image=self.t3c4i1_tk)
                self.t3c4br5.configure(text="N/A")
                self.t3c4br7.configure(text="N/A")
                self.t3c4br9.configure(text="N/A")
                self.t3c4br11.configure(text="N/A")
                self.t3c4br13.configure(text="N/A")
                self.t3c4br15.configure(text="N/A")
                self.t3c4r18.configure(text="N/A")
                self.t3c4r4.configure(state=tk.DISABLED)
                self.t3c4r8.configure(state=tk.DISABLED)
                self.t3c4r12.configure(state=tk.DISABLED)
                self.t3c4r14.configure(state=tk.DISABLED)
                self.t3c4r19.configure(state=tk.DISABLED)
                self.t3c4b1.configure(state=tk.DISABLED)

            if pics > 4:
                query = self.interface.getCroppedImage(self.pendingList[self.t3_current_target-1][4].crop_id)
                self.t3c5i1_im = query[0]
                yaw_angle = tab_tools.getYawAngle(self.interface,query[1])
                self.t3c5i1_im = self.t3c5i1_im.rotate(-yaw_angle,expand=1)
                self.t3c5i1_org_width,self.t3c5i1_org_height = self.t3c5i1_im.size
                self.t3c5i1_tk = tab_tools.im2tk(self.t3c5i1_im)
                self.t3c5i1.configure(image=self.t3c5i1_tk)
                display_shape = self.pendingList[self.t3_current_target-1][4].shape
                if display_shape != None:
                    self.t3c5br5.configure(text=display_shape)
                else:
                    self.t3c5br5.configure(text="N/A")
                display_bg_color = self.pendingList[self.t3_current_target-1][4].background_color
                if display_bg_color != None:
                    self.t3c5br7.configure(text=display_bg_color)
                else:
                    self.t3c5br7.configure(text="N/A")
                display_alphanumeric = self.pendingList[self.t3_current_target-1][4].alphanumeric
                if display_alphanumeric != None:
                    self.t3c5br9.configure(text=display_alphanumeric)
                else:
                    self.t3c5br9.configure(text="N/A")
                display_alpha_color = self.pendingList[self.t3_current_target-1][4].alphanumeric_color
                if display_alpha_color != None:
                    self.t3c5br11.configure(text=display_alpha_color)
                else:
                    self.t3c5br11.configure(text="N/A")
                display_orientation = self.pendingList[self.t3_current_target-1][4].orientation
                if display_orientation != None:
                    self.t3c5br13.configure(text=display_orientation)
                else:
                    self.t3c5br13.configure(text="N/A")
                display_decription = self.pendingList[self.t3_current_target-1][4].description
                if display_decription != "":
                    self.t3c5r18.configure(text=display_decription)
                else:
                    self.t3c5r18.configure(text="N/A")
                self.t3c5br15.configure(text=self.pendingList[self.t3_current_target-1][4].type)
                if self.pendingList[self.t3_current_target-1][4].type == "emergent":
                    self.t3c5r4.configure(state=tk.NORMAL)
                    self.t3c5r8.configure(state=tk.DISABLED)
                    self.t3c5r12.configure(state=tk.DISABLED)
                    self.t3c5r14.configure(state=tk.DISABLED)
                    self.t3c5r19.configure(state=tk.NORMAL)
                    self.t3c5b1.configure(state=tk.NORMAL)
                else:
                    self.t3c5r4.configure(state=tk.NORMAL)
                    self.t3c5r8.configure(state=tk.NORMAL)
                    self.t3c5r12.configure(state=tk.NORMAL)
                    self.t3c5r14.configure(state=tk.NORMAL)
                    self.t3c5r19.configure(state=tk.DISABLED)
                    self.t3c5b1.configure(state=tk.NORMAL)
                self.pending_bg_color.append(self.pendingList[self.t3_current_target-1][4].background_color)
                self.pending_alpha_color.append(self.pendingList[self.t3_current_target-1][4].alphanumeric_color)
                self.pending_orientation.append(self.pendingList[self.t3_current_target-1][4].orientation)
                self.pending_description.append(self.pendingList[self.t3_current_target-1][4].description)

            else:
                self.t3c5i1_im = self.t3_default_im.copy()
                self.t3c5i1_org_width,self.t3c5i1_org_height = self.t3c5i1_im.size
                self.t3c5i1_tk = tab_tools.im2tk(self.t3c5i1_im)
                self.t3c5i1.configure(image=self.t3c5i1_tk)
                self.t3c5br5.configure(text="N/A")
                self.t3c5br7.configure(text="N/A")
                self.t3c5br9.configure(text="N/A")
                self.t3c5br11.configure(text="N/A")
                self.t3c5br13.configure(text="N/A")
                self.t3c5br15.configure(text="N/A")
                self.t3c5r18.configure(text="N/A")
                self.t3c5r4.configure(state=tk.DISABLED)
                self.t3c5r8.configure(state=tk.DISABLED)
                self.t3c5r12.configure(state=tk.DISABLED)
                self.t3c5r14.configure(state=tk.DISABLED)
                self.t3c5r19.configure(state=tk.DISABLED)
                self.t3c5b1.configure(state=tk.DISABLED)

            if self.pendingList != None:
                # Possible Submission
                self.t3c6i1_im = self.t3c1i1_im.copy()
                self.t3c6i1_org_width,self.t3c6i1_org_height = self.t3c6i1_im.size
                self.t3c6i1_tk = tab_tools.im2tk(self.t3c6i1_im)
                self.t3c6i1.configure(image=self.t3c6i1_tk)
                display_shape = self.pendingList[self.t3_current_target-1][0].shape
                if display_shape != None:
                    self.t3c6br5.configure(text=display_shape)
                else:
                    self.t3c6br5.configure(text="N/A")
                display_alphanumeric = self.pendingList[self.t3_current_target-1][0].alphanumeric
                if display_alphanumeric != None:
                    self.t3c6br9.configure(text=display_alphanumeric)
                else:
                    self.t3c6br9.configure(text="N/A")
                self.t3c6br15.configure(text=self.pendingList[self.t3_current_target-1][0].type)
                display_bg_color = self.findMostCommonValue(self.pending_bg_color)
                if display_bg_color != None:
                    self.t3c6br7.configure(text=display_bg_color)
                else:
                    self.t3c6br7.configure(text="N/A")
                display_alpha_color = self.findMostCommonValue(self.pending_alpha_color)
                if display_alpha_color != None:
                    self.t3c6br11.configure(text=display_alpha_color)
                else:
                    self.t3c6br11.configure(text="N/A")
                display_orientation = self.findMostCommonValue(self.pending_orientation)
                if display_orientation != None:
                    self.t3c6br13.configure(text=display_orientation)
                else:
                    self.t3c6br13.configure(text="N/A")
                display_description = self.findMostCommonValue(self.pending_description)
                if display_description != "":
                    self.t3c6r18.configure(text=display_description)
                else:
                    self.t3c6r18.configure(text="N/A")
                for ii in range(5):
                    self.resizeEventTab3()

        else:
            error_np = tab_tools.get_image('assets/server_error.jpg')
            error_im = tab_tools.np2im(error_np)
            self.t3c1i1_im = error_im.copy()
            self.t3c1i1_tk = tab_tools.im2tk(self.t3c1i1_im)
            self.t3c1i1_org_width,self.t3c1i1_org_height = self.t3c1i1_im.size
            self.t3c1i1.configure(image=self.t3c1i1_tk)
            self.t3c2i1_im = error_im.copy()
            self.t3c2i1_tk = tab_tools.im2tk(self.t3c2i1_im)
            self.t3c2i1_org_width,self.t3c2i1_org_height = self.t3c2i1_im.size
            self.t3c2i1.configure(image=self.t3c2i1_tk)
            self.t3c3i1_im = error_im.copy()
            self.t3c3i1_tk = tab_tools.im2tk(self.t3c3i1_im)
            self.t3c3i1_org_width,self.t3c3i1_org_height = self.t3c3i1_im.size
            self.t3c3i1.configure(image=self.t3c3i1_tk)
            self.t3c4i1_im = error_im.copy()
            self.t3c4i1_tk = tab_tools.im2tk(self.t3c4i1_im)
            self.t3c4i1_org_width,self.t3c4i1_org_height = self.t3c4i1_im.size
            self.t3c4i1.configure(image=self.t3c4i1_tk)
            self.t3c5i1_im = error_im.copy()
            self.t3c5i1_tk = tab_tools.im2tk(self.t3c5i1_im)
            self.t3c5i1_org_width,self.t3c5i1_org_height = self.t3c5i1_im.size
            self.t3c5i1.configure(image=self.t3c5i1_tk)
            self.t3c6i1_im = error_im.copy()
            self.t3c6i1_tk = tab_tools.im2tk(self.t3c6i1_im)
            self.t3c6i1_org_width,self.t3c6i1_org_height = self.t3c6i1_im.size
            self.t3c6i1.configure(image=self.t3c6i1_tk)
            self.resizeEventTab3()

    def nextClassified(self,event):
        """
        Goes to next classified target group

        @type  event: event
        @param event: Right arrow event

        @rtype:  None
        @return: None
        """
        #self.updateManualSubmissionTab()
        self.serverConnected = self.interface.ping()
        if self.serverConnected:
            if self.pendingList == None:
                self.t3_current_target = 0
            elif self.t3_current_target < len(self.pendingList):
                self.t3_current_target += 1
            else:
                pass

        #reset submission variables
        self.submit_crop_id = None
        self.submit_orientation = None
        self.submit_bg_color = None
        self.submit_alpha_color = None
        self.submit_desc = None

        self.submissionBackgroundColor.set(None)
        self.selectBackgroundColor()
        self.submissionAlphanumericColor.set(None)
        self.selectAlphanumericColor()
        self.submissionOrientation.set(None)
        self.selectOrientation()
        self.submissionDescription.set(None)
        self.selectDescription()
        self.submissionImage.set(None)
        self.selectImage()
        self.updateManualSubmissionTab()


    def previousClassified(self,event):
        """
        Goes to previous classified target group

        @type  event: event
        @param event: Right arrow event

        @rtype:  None
        @return: None
        """
        #self.updateManualSubmissionTab()
        self.serverConnected = self.interface.ping()
        if self.serverConnected:
            if self.t3_current_target > 1:
                self.t3_current_target -= 1
            elif self.pendingList == None:
                self.t3_current_target = 0
            else:
                pass

        #reset submission variables
        self.submit_crop_id = None
        self.submit_orientation = None
        self.submit_bg_color = None
        self.submit_alpha_color = None
        self.submit_desc = None

        self.submissionBackgroundColor.set(None)
        self.selectBackgroundColor()
        self.submissionAlphanumericColor.set(None)
        self.selectAlphanumericColor()
        self.submissionOrientation.set(None)
        self.selectOrientation()
        self.submissionDescription.set(None)
        self.selectDescription()
        self.submissionImage.set(None)
        self.selectImage()
        self.updateManualSubmissionTab()


    def submitTarget(self,event=None):
        """
        Submits Target to server

        @type  event: event
        @param event: Enter press or button press event

        @rtype:  None
        @return: None
        """
        submission = client_rest.TargetSubmission(self.submit_crop_id,self.submit_orientation,self.submit_bg_color,self.submit_alpha_color,self.submit_desc)
        self.interface.postSubmitTargetById(self.target_id,submission)
        if self.t3_current_target == self.t3_total_targets:
            self.t3_current_target -= 1
        self.submissionBackgroundColor.set(None)
        self.selectBackgroundColor()
        self.submissionAlphanumericColor.set(None)
        self.selectAlphanumericColor()
        self.submissionOrientation.set(None)
        self.selectOrientation()
        self.submissionDescription.set(None)
        self.selectDescription()
        self.submissionImage.set(None)
        self.selectImage()
        self.updateManualSubmissionTab()

    def findMostCommonValue(self, classifications):
        """
        Calculate the most common value in a specified column (useful for all the enum columns)

        @type classifications: list of value lists (ie: from a cursor.fetchall())
        @param classifications: database rows to use to calculate the average
        @type clmnNun: int
        @param clmnNum: Integer of the column to access in each row to get values for avg calculation
        """

        # dictionary keeps track of how many times we've seen a particular column value
        # EX: {
        #       "red": 2,
        #        "white": 1}
        valueCounts = {}
        # for each classification in our list of classifications
        # a classification here is a list
        for classification in classifications:
            if classification is not None:
                # if the value at the classification has not been added to our dictionary yet
                if classification not in valueCounts:
                    valueCounts[classification] = 0
                valueCounts[classification] += 1 # increment the particular value in the dict

        if valueCounts: # if the dictionary isnt empty
            mostCommon = max(valueCounts, key=valueCounts.get)
            return mostCommon
        return None # if there are no values for this particular field, return None



    def selectBackgroundColor(self):
        try:
            value = self.submissionBackgroundColor.get()
        except Exception:
            value = None
        self.t3c1ar7.configure(foreground='#636363')#,font=('normal','11'))
        self.t3c1br7.configure(foreground='#636363')
        self.t3c2ar7.configure(foreground='#636363')
        self.t3c2br7.configure(foreground='#636363')
        self.t3c3ar7.configure(foreground='#636363')
        self.t3c3br7.configure(foreground='#636363')
        self.t3c4ar7.configure(foreground='#636363')
        self.t3c4br7.configure(foreground='#636363')
        self.t3c5ar7.configure(foreground='#636363')
        self.t3c5br7.configure(foreground='#636363')
        self.t3c6ar7.configure(foreground='#636363')
        self.t3c6br7.configure(foreground='#636363')

        if value == None:
            pass
        else:
            self.t3c6ar7.configure(foreground='blue')
            self.t3c6br7.configure(foreground='blue')
            if value == 1:
                self.t3c1br7.configure(foreground='blue')
                self.t3c1ar7.configure(foreground='blue')
            elif value == 2:
                self.t3c2ar7.configure(foreground='blue')
                self.t3c2br7.configure(foreground='blue')
            elif value == 3:
                self.t3c3ar7.configure(foreground='blue')
                self.t3c3br7.configure(foreground='blue')
            elif value == 4:
                self.t3c4ar7.configure(foreground='blue')
                self.t3c4br7.configure(foreground='blue')
            else:
                self.t3c5ar7.configure(foreground='blue')
                self.t3c5br7.configure(foreground='blue')
            self.t3c6br7.configure(text=self.pendingList[self.t3_current_target-1][value-1].background_color)
            self.submit_bg_color = self.pendingList[self.t3_current_target-1][value-1].class_id

    def selectAlphanumericColor(self):
        try:
            value = self.submissionAlphanumericColor.get()
        except Exception:
            value = None
        self.t3c1ar11.configure(foreground='#636363')#,font=('normal','11'))
        self.t3c1br11.configure(foreground='#636363')
        self.t3c2ar11.configure(foreground='#636363')
        self.t3c2br11.configure(foreground='#636363')
        self.t3c3ar11.configure(foreground='#636363')
        self.t3c3br11.configure(foreground='#636363')
        self.t3c4ar11.configure(foreground='#636363')
        self.t3c4br11.configure(foreground='#636363')
        self.t3c5ar11.configure(foreground='#636363')
        self.t3c5br11.configure(foreground='#636363')
        self.t3c6ar11.configure(foreground='#636363')
        self.t3c6br11.configure(foreground='#636363')

        if value == None:
            pass
        else:
            self.t3c6ar11.configure(foreground='blue')
            self.t3c6br11.configure(foreground='blue')
            if value == 1:
                self.t3c1br11.configure(foreground='blue')
                self.t3c1ar11.configure(foreground='blue')
            elif value == 2:
                self.t3c2ar11.configure(foreground='blue')
                self.t3c2br11.configure(foreground='blue')
            elif value == 3:
                self.t3c3ar11.configure(foreground='blue')
                self.t3c3br11.configure(foreground='blue')
            elif value == 4:
                self.t3c4ar11.configure(foreground='blue')
                self.t3c4br11.configure(foreground='blue')
            else:
                self.t3c5ar11.configure(foreground='blue')
                self.t3c5br11.configure(foreground='blue')
            self.t3c6br11.configure(text=self.pendingList[self.t3_current_target-1][value-1].alphanumeric_color)
            self.submit_alpha_color = self.pendingList[self.t3_current_target-1][value-1].class_id

    def selectOrientation(self):
        try:
            value = self.submissionOrientation.get()
        except Exception:
            value = None

        self.t3c1ar13.configure(foreground='#636363')#,font=('normal','11'))
        self.t3c1br13.configure(foreground='#636363')
        self.t3c2ar13.configure(foreground='#636363')
        self.t3c2br13.configure(foreground='#636363')
        self.t3c3ar13.configure(foreground='#636363')
        self.t3c3br13.configure(foreground='#636363')
        self.t3c4ar13.configure(foreground='#636363')
        self.t3c4br13.configure(foreground='#636363')
        self.t3c5ar13.configure(foreground='#636363')
        self.t3c5br13.configure(foreground='#636363')
        self.t3c6ar13.configure(foreground='#636363')
        self.t3c6br13.configure(foreground='#636363')

        if value == None:
            pass
        else:
            self.t3c6ar13.configure(foreground='blue')
            self.t3c6br13.configure(foreground='blue')
            if value == 1:
                self.t3c1br13.configure(foreground='blue')
                self.t3c1ar13.configure(foreground='blue')
            elif value == 2:
                self.t3c2ar13.configure(foreground='blue')
                self.t3c2br13.configure(foreground='blue')
            elif value == 3:
                self.t3c3ar13.configure(foreground='blue')
                self.t3c3br13.configure(foreground='blue')
            elif value == 4:
                self.t3c4ar13.configure(foreground='blue')
                self.t3c4br13.configure(foreground='blue')
            else:
                self.t3c5ar13.configure(foreground='blue')
                self.t3c5br13.configure(foreground='blue')
            self.t3c6br13.configure(text=self.pendingList[self.t3_current_target-1][value-1].orientation)
            self.submit_orientation = self.pendingList[self.t3_current_target-1][value-1].class_id

    def selectDescription(self):
        try:
            value = self.submissionDescription.get()
        except Exception:
            value = None
        self.t3c1r17.configure(foreground='#636363')#,font=('normal','11'))
        self.t3c1r18.configure(foreground='#636363')
        self.t3c2r17.configure(foreground='#636363')
        self.t3c2r18.configure(foreground='#636363')
        self.t3c3r17.configure(foreground='#636363')
        self.t3c3r18.configure(foreground='#636363')
        self.t3c4r17.configure(foreground='#636363')
        self.t3c4r18.configure(foreground='#636363')
        self.t3c5r17.configure(foreground='#636363')
        self.t3c5r18.configure(foreground='#636363')
        self.t3c6r17.configure(foreground='#636363')
        self.t3c6r18.configure(foreground='#636363')

        if value == None:
            pass
        else:
            self.t3c6r17.configure(foreground='blue')
            self.t3c6r18.configure(foreground='blue')
            if value == 1:
                self.t3c1r18.configure(foreground='blue')
                self.t3c1r17.configure(foreground='blue')
            elif value == 2:
                self.t3c2r17.configure(foreground='blue')
                self.t3c2r18.configure(foreground='blue')
            elif value == 3:
                self.t3c3r17.configure(foreground='blue')
                self.t3c3r18.configure(foreground='blue')
            elif value == 4:
                self.t3c4r17.configure(foreground='blue')
                self.t3c4r18.configure(foreground='blue')
            else:
                self.t3c5r17.configure(foreground='blue')
                self.t3c5r18.configure(foreground='blue')
            self.t3c6r18.configure(text=self.pendingList[self.t3_current_target-1][value-1].description)
            self.submit_desc = self.pendingList[self.t3_current_target-1][value-1].class_id

    def selectImage(self):
        try:
            value = self.submissionImage.get()
        except Exception:
            value = None

        if value == None:
            pass
        else:
            if value == 1:
                self.t3c6i1_im = self.t3c1i1_im.copy()
            elif value == 2:
                self.t3c6i1_im = self.t3c2i1_im.copy()
            elif value == 3:
                self.t3c6i1_im = self.t3c3i1_im.copy()
            elif value == 4:
                self.t3c6i1_im = self.t3c4i1_im.copy()
            else:
                self.t3c6i1_im = self.t3c5i1_im.copy()
            self.t3c6i1_org_width,self.t3c6i1_org_height = self.t3c6i1_im.size
            self.t3c6i1_tk = tab_tools.im2tk(self.t3c6i1_im)
            self.t3c6i1.configure(image=self.t3c6i1_tk)
            self.submit_crop_id = self.pendingList[self.t3_current_target-1][value-1].class_id

    def deleteClassification1(self):
        classification_id = self.pendingList[self.t3_current_target-1][0].class_id
        self.interface.deleteClass(classification_id)

        #reset submission variables if they were the deleted classification
        class_id = self.pendingList[self.t3_current_target-1][0].class_id
        if self.submit_crop_id == class_id:
            self.submissionImage.set(None)
            self.selectImage()
        if self.submit_orientation == class_id:
            self.submissionOrientation.set(None)
            self.selectOrientation()
        if self.submit_bg_color == class_id:
            self.submissionBackgroundColor.set(None)
            self.selectBackgroundColor()
        if self.submit_alpha_color == class_id:
            self.submissionAlphanumericColor.set(None)
            self.selectAlphanumericColor()
        if self.submit_desc == class_id:
            self.submissionDescription.set(None)
            self.selectDescription()

        self.updateManualSubmissionTab()

    def deleteClassification2(self):
        classification_id = self.pendingList[self.t3_current_target-1][1].class_id
        self.interface.deleteClass(classification_id)

        #reset submission variables if they were the deleted classification
        class_id = self.pendingList[self.t3_current_target-1][1].class_id
        if self.submit_crop_id == class_id:
            self.submissionImage.set(None)
            self.selectImage()
        if self.submit_orientation == class_id:
            self.submissionOrientation.set(None)
            self.selectOrientation()
        if self.submit_bg_color == class_id:
            self.submissionBackgroundColor.set(None)
            self.selectBackgroundColor()
        if self.submit_alpha_color == class_id:
            self.submissionAlphanumericColor.set(None)
            self.selectAlphanumericColor()
        if self.submit_desc == class_id:
            self.submissionDescription.set(None)
            self.selectDescription()

        self.updateManualSubmissionTab()

    def deleteClassification3(self):
        classification_id = self.pendingList[self.t3_current_target-1][2].class_id
        self.interface.deleteClass(classification_id)

        #reset submission variables if they were the deleted classification
        class_id = self.pendingList[self.t3_current_target-1][2].class_id
        if self.submit_crop_id == class_id:
            self.submissionImage.set(None)
            self.selectImage()
        if self.submit_orientation == class_id:
            self.submissionOrientation.set(None)
            self.selectOrientation()
        if self.submit_bg_color == class_id:
            self.submissionBackgroundColor.set(None)
            self.selectBackgroundColor()
        if self.submit_alpha_color == class_id:
            self.submissionAlphanumericColor.set(None)
            self.selectAlphanumericColor()
        if self.submit_desc == class_id:
            self.submissionDescription.set(None)
            self.selectDescription()

        self.updateManualSubmissionTab()

    def deleteClassification4(self):
        classification_id = self.pendingList[self.t3_current_target-1][3].class_id
        self.interface.deleteClass(classification_id)

        #reset submission variables if they were the deleted classification
        class_id = self.pendingList[self.t3_current_target-1][3].class_id
        if self.submit_crop_id == class_id:
            self.submissionImage.set(None)
            self.selectImage()
        if self.submit_orientation == class_id:
            self.submissionOrientation.set(None)
            self.selectOrientation()
        if self.submit_bg_color == class_id:
            self.submissionBackgroundColor.set(None)
            self.selectBackgroundColor()
        if self.submit_alpha_color == class_id:
            self.submissionAlphanumericColor.set(None)
            self.selectAlphanumericColor()
        if self.submit_desc == class_id:
            self.submissionDescription.set(None)
            self.selectDescription()

        self.updateManualSubmissionTab()

    def deleteClassification5(self):
        classification_id = self.pendingList[self.t3_current_target-1][4].class_id
        self.interface.deleteClass(classification_id)

        #reset submission variables if they were the deleted classification
        class_id = self.pendingList[self.t3_current_target-1][4].class_id
        if self.submit_crop_id == class_id:
            self.submissionImage.set(None)
            self.selectImage()
        if self.submit_orientation == class_id:
            self.submissionOrientation.set(None)
            self.selectOrientation()
        if self.submit_bg_color == class_id:
            self.submissionBackgroundColor.set(None)
            self.selectBackgroundColor()
        if self.submit_alpha_color == class_id:
            self.submissionAlphanumericColor.set(None)
            self.selectAlphanumericColor()
        if self.submit_desc == class_id:
            self.submissionDescription.set(None)
            self.selectDescription()
        self.updateManualSubmissionTab()

    def click_image1(self,event=None):
        self.submissionImage.set(1)
        self.selectImage()

    def click_image2(self,event=None):
        self.submissionImage.set(2)
        self.selectImage()

    def click_image3(self,event=None):
        self.submissionImage.set(3)
        self.selectImage()

    def click_image4(self,event=None):
        self.submissionImage.set(4)
        self.selectImage()

    def click_image5(self,event=None):
        self.submissionImage.set(5)
        self.selectImage()
