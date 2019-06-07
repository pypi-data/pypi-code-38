"""Test PySlip view-relative polygons.

Usage: test_maprel_image.py [-h] [-t (OSM|GMT)]
"""

import os
import sys
import wx
import pyslip


######
# Various demo constants
######

DemoWidth = 1000
DemoHeight = 800
DefaultAppSize = (DemoWidth, DemoHeight)

MinTileLevel = 0
InitViewLevel = 2
InitViewPosition = (130.841111, -12.438056)      # Darwin

arrow_cn = ((0,0),(10,10),(5,10),(5,20),(-5,20),(-5,10),(-10,10))
arrow_ne = ((-1,0),(-1,10),(-4,8),(-9,13),(-14,8),(-9,3),(-11,0))
arrow_ce = ((-1,0),(-11,10),(-11,5),(-21,5),(-21,-5),(-11,-5),(-11,-10))
arrow_se = ((-1,-1),(-1,-10),(-4,-8),(-9,-13),(-14,-8),(-9,-3),(-11,-1))
arrow_cs = ((0,-1),(-10,-11),(-5,-11),(-5,-21),(5,-21),(5,-11),(10,-11))
arrow_sw = ((0,-1),(0,-10),(3,-8),(8,-13),(13,-8),(8,-3),(10,-1))
arrow_cw = ((0,0),(10,10),(10,5),(20,5),(20,-5),(10,-5),(10,-10))
arrow_nw = ((0,0),(0,10),(3,8),(8,13),(13,8),(8,3),(10,0))
filled_poly = ((-100,100),(-100,-100),(0,150),(100,-100),(100,100))

PolyViewData = [(arrow_cn, {'placement': 'cn'}),
                (arrow_ne, {'placement': 'ne'}),
                (arrow_ce, {'placement': 'ce'}),
                (arrow_se, {'placement': 'se'}),
                (arrow_cs, {'placement': 'cs'}),
                (arrow_sw, {'placement': 'sw'}),
                (arrow_cw, {'placement': 'cw'}),
                (arrow_nw, {'placement': 'nw'}),
                (filled_poly, {'placement': 'cc', 'width': 8,
                               'fillcolour': '#ff000020',
                               'colour': '#00ff0040',
                               'filled': True}),
               ]

################################################################################
# The main application frame
################################################################################

class TestFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, size=DefaultAppSize,
                          title=('PySlip %s - view-relative polygon test'
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
        self.panel.SetSizer(box)
        self.panel.Layout()
        self.Centre()
        self.Show(True)

        # set initial view position
        wx.CallLater(25, self.final_setup, InitViewLevel, InitViewPosition)

        # add test test layer
        self.text_layer = self.pyslip.AddPolygonLayer(PolyViewData,
                                                      map_rel=False,
                                                      name='<poly_map_layer>',
                                                      offset_x=0, offset_y=0,
                                                      closed=True)

    def final_setup(self, level, position):
        """Perform final setup.

        level     zoom level required
        position  position to be in centre of view

        We do this in a CallAfter() function for those operations that
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

