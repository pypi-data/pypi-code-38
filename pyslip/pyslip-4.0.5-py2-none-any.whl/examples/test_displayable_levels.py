"""
Test if we can have a list of "allowable levels" and if a user requests
the display of a level not in that list we CANCEL the zoom operation.

Usage: test_displayable_levels.py [-d] [-h] [-t (OSM|GMT)]
"""


import sys
import wx
import pyslip

# initialize the logging system
import pyslip.log as log
try:
    log = log.Log("pyslip.log")
except AttributeError:
    # already set up, ignore exception
    pass


######
# Various constants
######

DemoName = 'pySlip %s - Zoom undo test' % pyslip.__version__
DemoWidth = 1000
DemoHeight = 800
DemoAppSize = (DemoWidth, DemoHeight)

InitViewLevel = 2
InitViewPosition = (100.494167, 13.7525)    # Bangkok


################################################################################
# The main application frame
################################################################################

class TestFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, size=DemoAppSize,
                          title=('PySlip %s - zoom undo test'
                                 % pyslip.__version__))
        self.SetMinSize(DemoAppSize)
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.panel.SetBackgroundColour(wx.WHITE)
        self.panel.ClearBackground()

        # create the tile source object
        self.tile_src = Tiles.Tiles()

        # build the GUI
        box = wx.BoxSizer(wx.HORIZONTAL)
        self.panel.SetSizer(box)
        self.pyslip = pyslip.pySlip(self.panel, tile_src=self.tile_src,
                                    style=wx.SIMPLE_BORDER)
        box.Add(self.pyslip, proportion=1, border=1, flag=wx.EXPAND)
        self.panel.SetSizerAndFit(box)
        self.panel.Layout()
        self.Centre()
        self.Show(True)

        # set initial view position
        wx.CallLater(25, self.final_setup, InitViewLevel, InitViewPosition)


        # bind the pySlip widget to the "zoom undo" method
        self.pyslip.Bind(pyslip.EVT_PYSLIP_LEVEL, self.onZoom)

    def final_setup(self, level, position):
        """Perform final setup.

        level     zoom level required
        position  position to be in centre of view

        We do this in a CallAfter() function for those operations that
        must not be done while the GUI is "fluid".
        """

        self.pyslip.GotoLevelAndPosition(level, position)

    def onZoom(self, event):
        """Catch and undo a zoom.

        The pySlip widget automatically zooms if there are tiles available.
        Simulate the amount of work a user handler might do before deciding to
        undo a zoom.

        We must check the level we are zooming to.  If we don't, the GotoLevel()
        method below will trigger another exception, which we catch, etc, etc.
        """

        print('Trying to zoom to level %d' % event.level)

        # do some busy waiting - simulates user code
        for _ in range(1000000):
            pass

        l = [InitViewLevel, InitViewLevel, InitViewLevel, InitViewLevel,
             InitViewLevel, InitViewLevel, InitViewLevel, InitViewLevel,
             InitViewLevel, InitViewLevel, InitViewLevel, InitViewLevel,
             InitViewLevel, InitViewLevel, InitViewLevel, InitViewLevel,
             InitViewLevel, InitViewLevel, InitViewLevel, InitViewLevel,
            ]

        if event.level not in l:
            # zoomed level isn't aallowed, go back to the original level
            print('Undoing zoom to %d' % event.level)
            self.pyslip.GotoLevel(InitViewLevel)

################################################################################

if __name__ == '__main__':
    import sys
    import getopt
    import traceback

    # print some usage information
    def usage(msg=None):
        if msg:
            print(msg+'\n')
        print(__doc__)        # module docstring used

    # our own handler for uncaught exceptions
    def excepthook(type, value, tb):
        msg = '\n' + '=' * 80
        msg += '\nUncaught exception:\n'
        msg += ''.join(traceback.format_exception(type, value, tb))
        msg += '=' * 80 + '\n'
        print(msg)
        sys.exit(1)
    sys.excepthook = excepthook

    # decide which tiles to use, default is GMT
    argv = sys.argv[1:]

    try:
        (opts, args) = getopt.getopt(argv, 'ht:', ['help', 'tiles='])
    except getopt.error:
        usage()
        sys.exit(1)

    tile_source = 'GMT'
    for (opt, param) in opts:
        if opt in ['-h', '--help']:
            usage()
            sys.exit(0)
        elif opt in ('-t', '--tiles'):
            tile_source = param
    tile_source = tile_source.lower()

    # set up the appropriate tile source
    if tile_source == 'gmt':
        import pyslip.gmt_local as Tiles
    elif tile_source == 'osm':
        import pyslip.open_street_map as Tiles
    else:
        usage('Bad tile source: %s' % tile_source)
        sys.exit(3)

    # start wxPython app
    app = wx.App()
    TestFrame().Show()
    app.MainLoop()

