"""Test PySlip view-relative points.

Usage: test_viewrel_point.py [-h] [-t (OSM|GMT)]
"""

import os
import sys
import wx
import pyslip


######
# Various demo constants
######

DefaultAppSize = (1000, 600)

MinTileLevel = 0
InitViewLevel = 2
InitViewPosition = (133.87, -23.7)      # Alice Springs

PointViewDataNW = [( 0, 0), ( 2, 0), ( 4, 0), ( 6, 0), ( 8, 0),
                   (10, 0), ( 0, 2), ( 0, 4), ( 0, 6), ( 0, 8),
                   ( 0,10), ( 2, 2), ( 4, 4), ( 6, 6), ( 8, 8),
                   (10,10), (12,12), (14,14), (16,16), (18,18),
                   (20,20)
                  ]

PointViewDataCN = [(  0,  0), ( -2,  2), ( -4,  4), ( -6,  6),
                   ( -8,  8), (-10, 10), (  2,  2), (  4,  4),
                   (  6,  6), (  8,  8), ( 10, 10), (  0,  2),
                   (  0,  4), (  0,  6), (  0,  8), (  0, 10),
                   (  0, 12), (  0, 14), (  0, 16), (  0, 18),
                   (  0, 20)
                  ]

PointViewDataNE = [(  0,  0), ( -2,  0), ( -4,  0), ( -6,  0),
                   ( -8,  0), (-10,  0), (  0,  2), (  0,  4),
                   (  0,  6), (  0,  8), (  0, 10), ( -2,  2),
                   ( -4,  4), ( -6,  6), ( -8,  8), (-10, 10),
                   (-12, 12), (-14, 14), (-16, 16), (-18, 18),
                   (-20, 20)
                  ]

PointViewDataCE = [(  0,  0), ( -2, -2), ( -4, -4), ( -6, -6),
                   ( -8, -8), (-10,-10), ( -2,  2), ( -4,  4),
                   ( -6,  6), ( -8,  8), (-10, 10), ( -2,  0),
                   ( -4,  0), ( -6,  0), ( -8,  0), (-10,  0),
                   (-12,  0), (-14,  0), (-16,  0), (-18,  0),
                   (-20,  0)
                  ]

PointViewDataSE = [(  0,  0), (  0, -2), (  0, -4), (  0, -6),
                   (  0, -8), (  0,-10), ( -2,  0), ( -4,  0),
                   ( -6,  0), ( -8,  0), (-10,  0), ( -2, -2),
                   ( -4, -4), ( -6, -6), ( -8, -8), (-10,-10),
                   (-12,-12), (-14,-14), (-16,-16), (-18,-18),
                   (-20,-20)
                  ]

PointViewDataCS = [(  0,  0), ( -2, -2), ( -4, -4), ( -6, -6),
                   ( -8, -8), (-10,-10), (  2, -2), (  4, -4),
                   (  6, -6), (  8, -8), ( 10,-10), (  0, -2),
                   (  0, -4), (  0, -6), (  0, -8), (  0,-10),
                   (  0,-12), (  0,-14), (  0,-16), (  0,-18),
                   (  0,-20)
                  ]

PointViewDataSW = [(  0,  0), (  0, -2), (  0, -4), (  0, -6),
                   (  0, -8), (  0,-10), (  2,  0), (  4,  0),
                   (  6,  0), (  8,  0), ( 10,  0), (  2, -2),
                   (  4, -4), (  6, -6), (  8, -8), ( 10,-10),
                   ( 12,-12), ( 14,-14), ( 16,-16), ( 18,-18),
                   ( 20,-20)
                  ]

PointViewDataCW = [(  0,  0), (  2, -2), (  4, -4), (  6, -6),
                   (  8, -8), ( 10,-10), (  2,  2), (  4,  4),
                   (  6,  6), (  8,  8), ( 10, 10), (  2,  0),
                   (  4,  0), (  6,  0), (  8,  0), ( 10,  0),
                   ( 12,  0), ( 14,  0), ( 16,  0), ( 18,  0),
                   ( 20,  0)
                  ]

PointViewDataCC = [(  0,  0), (  2, -2), (  4, -4), (  6, -6),
                   (  8, -8), ( 10,-10),
                   (  0,  0), (  2,  2), (  4,  4), (  6,  6),
                   (  8,  8), ( 10, 10),
                   (  0,  0), ( -2, -2), ( -4, -4), ( -6, -6),
                   ( -8, -8), (-10,-10),
                   (  0,  0), ( -2,  2), ( -4,  4), ( -6,  6),
                   ( -8,  8), (-10, 10),
                  ]

################################################################################
# The main application frame
################################################################################

class TestFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, size=DefaultAppSize,
                          title=('PySlip %s - view-relative point test'
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

        # add test point layers
        self.pyslip.AddPointLayer(PointViewDataNW, placement='nw',
                                  map_rel=False, colour='blue', radius=2,
                                  offset_x=0, offset_y=0,
                                  name='<point_map_layer>')

        self.pyslip.AddPointLayer(PointViewDataCN, placement='cn',
                                  map_rel=False, colour='red', radius=2,
                                  offset_x=0, offset_y=0,
                                  name='<point_map_layer>')

        self.pyslip.AddPointLayer(PointViewDataNE, placement='ne',
                                  map_rel=False, colour='green', radius=2,
                                  offset_x=0, offset_y=0,
                                  name='<point_map_layer>')

        self.pyslip.AddPointLayer(PointViewDataCE, placement='ce',
                                  map_rel=False, colour='black', radius=2,
                                  offset_x=0, offset_y=0,
                                  name='<point_map_layer>')

        self.pyslip.AddPointLayer(PointViewDataSE, placement='se',
                                  map_rel=False, colour='yellow', radius=2,
                                  offset_x=0, offset_y=0,
                                  name='<point_map_layer>')

        self.pyslip.AddPointLayer(PointViewDataCS, placement='cs',
                                  map_rel=False, colour='gray', radius=2,
                                  offset_x=0, offset_y=0,
                                  name='<point_map_layer>')

        self.pyslip.AddPointLayer(PointViewDataSW, placement='sw',
                                  map_rel=False, colour='#7f7fff', radius=2,
                                  offset_x=0, offset_y=0,
                                  name='<point_map_layer>')

        self.pyslip.AddPointLayer(PointViewDataCW, placement='cw',
                                  map_rel=False, colour='#ff7f7f', radius=2,
                                  offset_x=0, offset_y=0,
                                  name='<point_map_layer>')

        self.pyslip.AddPointLayer(PointViewDataCC, placement='cc',
                                  map_rel=False, colour='#7fff7f', radius=2,
                                  offset_x=0, offset_y=0,
                                  name='<point_map_layer>')

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

