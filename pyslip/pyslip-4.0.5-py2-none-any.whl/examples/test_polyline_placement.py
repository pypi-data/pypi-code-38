"""
Program to test polyline map-relative and view-relative placement.
Select what to show and experiment with placement parameters.

Usage: test_polyline_placement.py [-h|--help] [-d] [(-t|--tiles) (GMT|OSM)]
"""


import os
import sys
import wx
import pyslip
from appstaticbox import AppStaticBox
from rotextctrl import ROTextCtrl
import pyslip.tkinter_error as tkinter_error


######
# Various demo constants
######

# demo name/version
DemoName = 'Test polyline placement, pySlip %s' % pyslip.__version__
DemoVersion = '1.1'

# initial values
InitialViewLevel = 4
InitialViewPosition = (145.0, -20.0)

# tiles info
MinTileLevel = 0

# the number of decimal places in a lon/lat display
LonLatPrecision = 3

# startup size of the application
DemoWidth = 1000
DemoHeight = 700
DefaultAppSize = (DemoWidth, DemoHeight)

# general defaults
DefaultWidth = 5
DefaultColour = 'red'

# initial values in map-relative LayerControl
DefaultPlacement = 'ne'
DefaultX = 145.0
DefaultY = -20.0
DefaultOffsetX = 0
DefaultOffsetY = 0

# initial values in view-relative LayerControl
DefaultViewPlacement = 'ne'
DefaultViewX = 0
DefaultViewY = 0
DefaultViewOffsetX = 0
DefaultViewOffsetY = 0

# polyline map- and view-relative data
PolyPoints = [(140.0,-17.5), (144.0,-19.0), (142.5,-15.0), (147.5,-15.0),
              (146.0,-19.0), (150.0,-17.5), (150.0,-22.5), (146.0,-21.0),
              (147.5,-25.0), (142.5,-25.0), (144.0,-21.0), (140.0,-22.5)]

PolyViewPoints = [(-100,-50), (-20,-20), (-50,-100), (50,-100),
                  (20,-20), (100,-50), (100,50), (20,20),
                  (50,100), (-50,100), (-20,20), (-100,50)]

######
# Various GUI layout constants
######

# sizes of various spacers
#HSpacerSize = (0,1)         # horizontal in application screen
#VSpacerSize = (1,1)         # vertical in control pane
HSpacerSize = 5         # horizontal in application screen
VSpacerSize = 5         # vertical in control pane

# border width when packing GUI elements
PackBorder = 0


###############################################################################
# Class for a LayerControl widget.
#
# This is used to control each type of layer, whether map- or view-relative.
###############################################################################

myEVT_DELETE = wx.NewEventType()
myEVT_UPDATE = wx.NewEventType()

EVT_DELETE = wx.PyEventBinder(myEVT_DELETE, 1)
EVT_UPDATE = wx.PyEventBinder(myEVT_UPDATE, 1)

class LayerControlEvent(wx.PyCommandEvent):
    """Event sent when a LayerControl is changed."""

    def __init__(self, eventType, id):
        wx.PyCommandEvent.__init__(self, eventType, id)

class LayerControl(wx.Panel):

    def __init__(self, parent, title,
                 placement=DefaultPlacement, width=DefaultWidth,
                 colour=DefaultColour, offset_x=0, offset_y=0, **kwargs):
        """Initialise a LayerControl instance.

        parent       reference to parent object
        title        text to show in static box outline around control
        placement    placement string for object
        width        width in pixels of the drawn polygon
        colour       sets the colour of the polygon outline
        offset_x     X offset of object
        offset_y     Y offset of object
        **kwargs     keyword args for Panel
        """

        # save parameters
        self.v_placement = placement
        self.v_width = width
        self.v_colour = colour
        self.v_offset_x = offset_x
        self.v_offset_y = offset_y

        # create and initialise the base panel
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY, **kwargs)
        self.SetBackgroundColour(wx.WHITE)

        # create the widget
        box = AppStaticBox(self, title)
        sbs = wx.StaticBoxSizer(box, orient=wx.VERTICAL)
        gbs = wx.GridBagSizer(vgap=2, hgap=2)

        # row 0
        row = 0
        gbs.Add(3, 1, (row,0))
        label = wx.StaticText(self, wx.ID_ANY, 'placement: ')
        gbs.Add(label, (row,1), border=0,
                flag=(wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT))
        choices = ['nw', 'cn', 'ne', 'ce', 'se', 'cs', 'sw', 'cw', 'cc', 'none']
        style=wx.CB_DROPDOWN|wx.CB_READONLY
        self.placement = wx.ComboBox(self, value=self.v_placement,
                                     choices=choices, style=style)
        gbs.Add(self.placement, (row,2), border=0,
                flag=(wx.ALIGN_CENTER_VERTICAL|wx.EXPAND))

        label = wx.StaticText(self, wx.ID_ANY, 'width: ')
        gbs.Add(label, (row,3), border=0,
                flag=(wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT))
        choices = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
        style=wx.CB_DROPDOWN|wx.CB_READONLY
        self.width = wx.ComboBox(self, value=self.v_width,
                                 choices=choices, style=style)
        gbs.Add(self.width, (row,4),
                border=0, flag=(wx.ALIGN_CENTER_VERTICAL|wx.EXPAND))
        gbs.Add(3, 1, (row,5))

        # row 1
        row += 1
        label = wx.StaticText(self, wx.ID_ANY, 'colour: ')
        gbs.Add(label, (row,1), border=0,
                flag=(wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT))
        self.polycolour = wx.Button(self, label='')
        self.polycolour.SetBackgroundColour(self.v_colour)
        gbs.Add(self.polycolour, (row,2), border=0, flag=wx.EXPAND)

        # row 2
        row += 1
        label = wx.StaticText(self, wx.ID_ANY, 'offset_x: ')
        gbs.Add(label, (row,1), border=0,
                flag=(wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT))
        self.offset_x = wx.TextCtrl(self, value=str(self.v_offset_x))
        gbs.Add(self.offset_x, (row,2), border=0, flag=wx.EXPAND)

        label = wx.StaticText(self, wx.ID_ANY, '  offset_y: ')
        gbs.Add(label, (row,3), border=0,
                flag=(wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT))
        self.offset_y = wx.TextCtrl(self, value=str(self.v_offset_y))
        gbs.Add(self.offset_y, (row,4), border=0, flag=wx.EXPAND)

        # row 3
        row += 1
        delete_button = wx.Button(self, label='Remove')
        gbs.Add(delete_button, (row,2), border=10, flag=wx.EXPAND)
        update_button = wx.Button(self, label='Update')
        gbs.Add(update_button, (row,4), border=10, flag=wx.EXPAND)

        sbs.Add(gbs)
        self.SetSizer(sbs)
        sbs.Fit(self)

        self.polycolour.Bind(wx.EVT_BUTTON, self.onPolyColour)
        delete_button.Bind(wx.EVT_BUTTON, self.onDelete)
        update_button.Bind(wx.EVT_BUTTON, self.onUpdate)

        # row 4 - spacer
        row += 1
        gbs.Add(1, 3, (row,0))

    def onPolyColour(self, event):
        """Change polyline colour."""

        colour = self.polycolour.GetBackgroundColour()
        wxcolour = wx.ColourData()
        wxcolour.SetColour(colour)

        dialog = wx.ColourDialog(self, data=wxcolour)
        dialog.GetColourData().SetChooseFull(True)
        new_colour = None
        if dialog.ShowModal() == wx.ID_OK:
            new_colour = dialog.GetColourData().Colour
        dialog.Destroy()

        if new_colour:
            self.polycolour.SetBackgroundColour(new_colour)

    def onDelete(self, event):
        """Remove object from map."""

        event = LayerControlEvent(myEVT_DELETE, self.GetId())
        self.GetEventHandler().ProcessEvent(event)

    def onUpdate(self, event):
        """Update object on map."""

        event = LayerControlEvent(myEVT_UPDATE, self.GetId())

        event.placement = self.placement.GetValue()
        event.width = int(self.width.GetValue())
        event.colour = self.polycolour.GetBackgroundColour()
        event.offset_x = self.offset_x.GetValue()
        event.offset_y = self.offset_y.GetValue()

        self.GetEventHandler().ProcessEvent(event)

################################################################################
# The main application frame
################################################################################

class AppFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, size=DefaultAppSize,
                          title='%s, test version %s' % (DemoName, DemoVersion))
        self.SetMinSize(DefaultAppSize)
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.panel.SetBackgroundColour(wx.WHITE)
        self.panel.ClearBackground()

        self.tile_source = Tiles.Tiles()

        # build the GUI
        self.make_gui(self.panel)

        # set initial view position
        self.map_level.SetLabel('%d' % InitialViewLevel)
        wx.CallAfter(self.final_setup, InitialViewLevel, InitialViewPosition)

        # force pyslip initialisation
        self.pyslip.OnSize()

        # finally, set up application window position
        self.Centre()

        # initialise state variables
        self.poly_layer = None
        self.poly_view_layer = None

        # finally, bind pySlip events to handlers
        self.pyslip.Bind(pyslip.EVT_PYSLIP_POSITION, self.handle_position_event)
        self.pyslip.Bind(pyslip.EVT_PYSLIP_LEVEL, self.handle_level_change)

#####
# Build the GUI
#####

    def make_gui(self, parent):
        """Create application GUI."""

        # start application layout
        all_display = wx.BoxSizer(wx.HORIZONTAL)
        parent.SetSizer(all_display)

        # put map view in left of horizontal box
        self.pyslip = pyslip.pySlip(parent, tile_src=self.tile_source,
                                    style=wx.SIMPLE_BORDER)
        all_display.Add(self.pyslip, proportion=1, border=0, flag=wx.EXPAND)

        # small spacer here - separate view and controls
        all_display.AddSpacer(HSpacerSize)

        # add controls to right of spacer
        controls = self.make_gui_controls(parent)
        all_display.Add(controls, proportion=0, border=0)

        parent.SetSizerAndFit(all_display)

    def make_gui_controls(self, parent):
        """Build the 'controls' part of the GUI

        parent  reference to parent

        Returns reference to containing sizer object.
        """

        # all controls in vertical box sizer
        controls = wx.BoxSizer(wx.VERTICAL)

        # add the map level in use widget
        level = self.make_gui_level(parent)
        controls.Add(level, proportion=0, flag=wx.EXPAND|wx.ALL)

        # vertical spacer
        controls.AddSpacer(VSpacerSize)

        # add the mouse position feedback stuff
        mouse = self.make_gui_mouse(parent)
        controls.Add(mouse, proportion=0, flag=wx.EXPAND|wx.ALL)

        # vertical spacer
        controls.AddSpacer(VSpacerSize)

        # controls for map-relative object layer
        self.poly = self.make_gui_poly(parent)
        controls.Add(self.poly, proportion=0, flag=wx.EXPAND|wx.ALL)
        self.poly.Bind(EVT_DELETE, self.polyDelete)
        self.poly.Bind(EVT_UPDATE, self.polyUpdate)

        # vertical spacer
        controls.AddSpacer(VSpacerSize)

        # controls for view-relative text layer
        self.poly_view = self.make_gui_poly_view(parent)
        controls.Add(self.poly_view, proportion=0, flag=wx.EXPAND|wx.ALL)
        self.poly_view.Bind(EVT_DELETE, self.polyViewDelete)
        self.poly_view.Bind(EVT_UPDATE, self.polyViewUpdate)

        # vertical spacer
        controls.AddSpacer(VSpacerSize)

        return controls

    def make_gui_level(self, parent):
        """Build the control that shows the level.

        parent  reference to parent

        Returns reference to containing sizer object.
        """

        # create objects
        txt = wx.StaticText(parent, wx.ID_ANY, 'Level: ')
        self.map_level = wx.StaticText(parent, wx.ID_ANY, ' ')

        # lay out the controls
        sb = AppStaticBox(parent, 'Map level')
        box = wx.StaticBoxSizer(sb, orient=wx.HORIZONTAL)
        box.Add(txt, border=PackBorder, flag=(wx.ALIGN_CENTER_VERTICAL
                                     |wx.ALIGN_RIGHT|wx.LEFT))
        box.Add(self.map_level, proportion=0, border=PackBorder,
                flag=wx.RIGHT|wx.TOP)

        return box

    def make_gui_mouse(self, parent):
        """Build the mouse part of the controls part of GUI.

        parent  reference to parent

        Returns reference to containing sizer object.
        """

        # create objects
        txt = wx.StaticText(parent, wx.ID_ANY, 'Lon/Lat: ')
        self.mouse_position = ROTextCtrl(parent, '', size=(150,-1),
                                         tooltip=('Shows the mouse '
                                                  'longitude and latitude '
                                                  'on the map'))

        # lay out the controls
        sb = AppStaticBox(parent, 'Mouse position')
        box = wx.StaticBoxSizer(sb, orient=wx.HORIZONTAL)
        box.Add(txt, border=PackBorder, flag=(wx.ALIGN_CENTER_VERTICAL
                                     |wx.ALIGN_RIGHT|wx.LEFT))
        box.Add(self.mouse_position, proportion=1, border=PackBorder,
                flag=wx.RIGHT|wx.TOP|wx.BOTTOM)

        return box

    def make_gui_poly(self, parent):
        """Build the polygon map-relative part of the controls part of GUI.

        parent  reference to parent

        Returns reference to containing sizer object.
        """

        # create widgets
        poly_obj = LayerControl(parent, 'Polygon, map-relative',
                                placement=DefaultPlacement,
                                width=str(DefaultWidth),
                                colour=DefaultColour,
                                offset_x=DefaultOffsetX,
                                offset_y=DefaultOffsetY)

        return poly_obj

    def make_gui_poly_view(self, parent):
        """Build the view-relative polygon part of the controls part of GUI.

        parent  reference to parent

        Returns reference to containing sizer object.
        """

        # create widgets
        poly_obj = LayerControl(parent, 'Polygon, view-relative',
                                 placement=DefaultPlacement,
                                 width=str(DefaultWidth),
                                 colour=DefaultColour,
                                 offset_x=DefaultViewOffsetX,
                                 offset_y=DefaultViewOffsetY)

        return poly_obj

    ######
    # event handlers
    ######

##### map-relative polygon layer

    def polyUpdate(self, event):
        """Display updated polygon."""

        if self.poly_layer:
            self.pyslip.DeleteLayer(self.poly_layer)

        # convert values to sanity for layer attributes
        placement = event.placement
        if placement == 'none':
            placement= ''

        width = event.width
        colour = event.colour

        off_x = event.offset_x
        if not off_x:
            off_x = 0
        try:
            off_x = int(off_x)
        except ValueError:
            off_x = 0

        off_y = event.offset_y
        if not off_y:
            off_y = 0
        try:
            off_y = int(off_y)
        except ValueError:
            off_y = 0

        poly_data = [(PolyPoints, {'placement': placement,
                                   'width': width,
                                   'colour': colour,
                                   'offset_x': off_x,
                                   'offset_y': off_y})]
        self.poly_layer = self.pyslip.AddPolygonLayer(poly_data, map_rel=True,
                                                      visible=True,
                                                      name='<poly_layer>')

    def polyDelete(self, event):
        """Delete the polygon map-relative layer."""

        if self.poly_layer:
            self.pyslip.DeleteLayer(self.poly_layer)
        self.poly_layer = None

##### view-relative polygon layer

    def polyViewUpdate(self, event):
        """Display updated polygon layer."""

        if self.poly_view_layer:
            self.pyslip.DeleteLayer(self.poly_view_layer)

        # convert values to sanity for layer attributes
        placement = event.placement
        if placement == 'none':
            placement= ''

        width = event.width
        colour = event.colour

        off_x = event.offset_x
        if not off_x:
            off_x = 0
        off_x = int(off_x)

        off_y = event.offset_y
        if not off_y:
            off_y = 0
        off_y = int(off_y)

        # create a new polygon layer
        poly_data = [(PolyViewPoints, {'placement': placement,
                                       'width': width,
                                       'colour': colour,
                                       'offset_x': off_x,
                                       'offset_y': off_y})]
        self.poly_view_layer = self.pyslip.AddPolygonLayer(poly_data,
                                                           map_rel=False,
                                                           visible=True,
                                                           name='<poly_layer>')

    def polyViewDelete(self, event):
        """Delete the polygon view-relative layer."""

        if self.poly_view_layer:
            self.pyslip.DeleteLayer(self.poly_view_layer)
        self.poly_view_layer = None

    def final_setup(self, level, position):
        """Perform final setup.

        level     zoom level required
        position  position to be in centre of view
        """

        self.pyslip.GotoLevelAndPosition(level, position)

    ######
    # Exception handlers
    ######

    def handle_position_event(self, event):
        """Handle a pySlip POSITION event."""

        posn_str = ''
        if event.mposn:
            (lon, lat) = event.mposn
            posn_str = ('%.*f / %.*f' % (LonLatPrecision, lon,
                                         LonLatPrecision, lat))

        self.mouse_position.SetValue(posn_str)

    def handle_level_change(self, event):
        """Handle a pySlip LEVEL event."""

        self.map_level.SetLabel('%d' % event.level)

###############################################################################

if __name__ == '__main__':
    import sys
    import getopt
    import traceback

    # our own handler for uncaught exceptions
    def excepthook(type, value, tb):
        msg = '\n' + '=' * 80
        msg += '\nUncaught exception:\n'
        msg += ''.join(traceback.format_exception(type, value, tb))
        msg += '=' * 80 + '\n'
        print(msg)
        tkinter_error.tkinter_error(msg)
        sys.exit(1)

    def usage(msg=None):
        if msg:
            print(('*'*80 + '\n%s\n' + '*'*80) % msg)
        print(__doc__)


    # plug our handler into the python system
    sys.excepthook = excepthook

    # decide which tiles to use, default is GMT
    argv = sys.argv[1:]

    try:
        (opts, args) = getopt.getopt(argv, 'dht:', ['debug', 'help', 'tiles='])
    except getopt.error:
        usage()
        sys.exit(1)

    tile_source = 'GMT'
    debug = False
    for (opt, param) in opts:
        if opt in ['-h', '--help']:
            usage()
            sys.exit(0)
        elif opt in ['-d', '--debug']:
            debug = True
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

    app_frame = AppFrame()
    app_frame.Show()

    if debug:
        import wx.lib.inspection
        wx.lib.inspection.InspectionTool().Show()

    app.MainLoop()

