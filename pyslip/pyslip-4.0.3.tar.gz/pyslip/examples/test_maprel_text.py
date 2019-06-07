"""Test PySlip map-relative text.

Usage: test_maprel_text.py [-h] [-t (OSM|GMT)]
"""


import os
import sys
import wx
import pyslip
from appstaticbox import AppStaticBox

######
# Various demo constants
######

DemoWidth = 1000
DemoHeight = 800
DefaultAppSize = (DemoWidth, DemoHeight)

MinTileLevel = 0
InitViewLevel = 3
InitViewPosition = (133.87, -23.7)      # Alice Springs

TextMapData = [(151.20, -33.85, 'Sydney cc', {'placement': 'cc'}),
               (144.95, -37.84, 'Melbourne ne', {'placement': 'ne'}),
               (153.08, -27.48, 'Brisbane ce', {'placement': 'ce'}),
               (115.86, -31.96, 'Perth se', {'placement': 'se'}),
               (138.30, -35.52, 'Adelaide cs', {'placement': 'cs'}),
               (130.98, -12.61, 'Darwin sw', {'placement': 'sw'}),
               (147.31, -42.96, 'Hobart cw', {'placement': 'cw'}),
               (149.20, -35.31, 'Canberra nw', {'placement': 'nw',
                                                'colour': 'red',
                                                'textcolour': 'blue',
                                                'fontsize': 10}),
               (133.90, -23.70, 'Alice Springs cn', {'placement': 'cn'})]


################################################################################
# The main application frame
################################################################################

class TestFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, size=DefaultAppSize,
                          title=('PySlip %s - map-relative text test'
                                 % pyslip.__version__))
        self.SetMinSize(DefaultAppSize)
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

        # add test test layer
        self.text_layer = self.pyslip.AddTextLayer(TextMapData,
                                                   map_rel=True,
                                                   name='<text_map_layer>',
                                                   offset_x=5, offset_y=1)

        # set initial view position
        wx.CallLater(25, self.final_setup, InitViewLevel, InitViewPosition)

    def final_setup(self, level, position):
        """Perform final setup.

        level     zoom level required
        position  position to be in centre of view

        We do this in a CallLater() function for those operations that
        must not be done while the GUI is "fluid".
        """

        self.pyslip.GotoLevelAndPosition(level, position)

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

    # plug our handler into the python system
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

