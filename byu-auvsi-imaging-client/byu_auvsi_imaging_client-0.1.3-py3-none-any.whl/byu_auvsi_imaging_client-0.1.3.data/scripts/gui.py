'''
Authors: D. Knowles, B. McBride, T. Miller
'''

'''
TODO:
    possible threading behind the scene to autosize other tabs
    use consistent naming patterns (camel case, snake case)
    change text font, size, color, etc.
    organize functions into a logical order

Tab4:
    create everything

KNOWN BUGS:
    When you click on the 2nd tab right at the beginning, and then use the left/right
        buttons, it moves one tab, then unbinds like it's supposed to.

SERVER SETUP NOTES
sudo su postgres
cd auvsi/src/imaging/server/setup/internal
psql -f setup_database.sql

roscore
cd auvsi
source devel/setup.bash
cd ausvsi/src/imaging/server/src

ros_ingester.py

'''

import sys
if sys.version_info[0] < 3:
    import Tkinter as tk
    import ttk
else:
    import tkinter as tk
    from tkinter import ttk
from ttkthemes import ThemedStyle
from lib import tab0, tab1, tab2, tab3, tab4


class GuiClass(tk.Frame):
    """
    Graphical User Interface for 2019 AUVSI competition

    @type  tk.Frame: nothing
    @param tk.Frame: nothing
    """
    def __init__(self,master=None):
        """
        initialization for Gui Class

        @rtype:  None
        @return: None
        """
        tk.Frame.__init__(self,master=None)
        self.master = master # gui master handle
        try:
            self.master.attributes('-zoomed', True) # maximizes screen for linux
        except (Exception) as e:
            w, h = master.winfo_screenwidth(), master.winfo_screenheight()
            master.geometry("%dx%d+0+0" % (w, h)) # maximizes screen for mac
        self.master.title("BYU AUVSI COMPETITION 2019")

        self.n = ttk.Notebook(self.master) # create tabs
        self.n.pack(fill=tk.BOTH, expand=1) # expand across space
        tk.Grid.rowconfigure(self.master,0,weight=1) # allow for resizing
        tk.Grid.columnconfigure(self.master,0,weight=1) # allow for resizing
        self.active_tab_prev = 0


        # -----------------------  Tab 0: SETTINGS  ----------------------------
        self.tab0 = tab0.Tab0(self.master,self.n)
        self.interface = self.tab0.interfaceCall()

        # -----------------------  Tab 1: CROPPPING  ---------------------------
        self.tab1 = tab1.Tab1(self.master,self.n,self.interface)

        # ---------------------  Tab 2: CLASSIFICATION  ------------------------
        self.tab2 = tab2.Tab2(self.master,self.n,self.interface)

        # -------------------  Tab 3: TARGET SUBMISSION  -----------------------
        self.tab3 = tab3.Tab3(self.master,self.n,self.interface)

        # --------------  Tab 4: AUTONOMOUS TARGET SUBMISSION  -----------------
        self.tab4 = tab4.Tab4(self.master,self.n,self.interface)


        # ----------------------------KEY BINDINGS -----------------------------
        self.master.bind("<<NotebookTabChanged>>",self.tabChanged)
        self.master.bind("<Escape>",self.close_window)

    def tabChanged(self,event):
        """
        Performs the correct keybindings when you move to a new tab of the gui

        @type  event: event
        @param event: Tab changed event

        @rtype:  None
        @return: None
        """
        active_tab = self.n.index(self.n.select())

        # get interface call if changed away from tab 0
        if active_tab != 0 and self.active_tab_prev == 0:
            self.interface = self.tab0.interfaceCall()
        # stop tab2 widget bindings if changed away from tab 2
        if active_tab != 2 and self.active_tab_prev == 2:
            self.tab2.stoprun()
        # stop tab1 wiget bindings if changed away from tab 3
        if active_tab != 3 and self.active_tab_prev == 3:
            self.tab3.stoprun()

        if active_tab == 0:
            self.tab0.run()
        elif active_tab == 1:
            self.tab1.run(self.interface)
        elif active_tab == 2:
            self.tab2.run(self.interface)
        elif active_tab == 3:
            self.tab3.run(self.interface)
        elif active_tab == 4:
            self.tab4.run(self.interface)
        self.master.focus_set()
        self.active_tab_prev = active_tab # store previous tab

    def close_window(self,event):
        """
        Closes gui safely
        @type  event: event
        @param event: ESC event

        @rtype:  None
        @return: None
        """
        self.master.destroy()
        sys.exit()

def main():
    root = tk.Tk()
    # change ttk style to something that looks decent
    style = ThemedStyle(root)
    style.set_theme("arc")
    gui = GuiClass(root)
    try:
        gui.mainloop()
    except KeyboardInterrupt:
        root.destroy()
        sys.exit()

if __name__ == "__main__":
    main()