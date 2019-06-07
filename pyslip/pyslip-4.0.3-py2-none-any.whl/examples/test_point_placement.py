"""
Program to test point map-relative and view-relative placement.
Select what to show and experiment with placement parameters.

Usage: test_point_placement.py [-h|--help] [-d] [(-t|--tiles) (GMT|OSM)]
"""


import os
import sys
import wx
import pyslip
from appstaticbox import AppStaticBox
from rotextctrl import ROTextCtrl
import pyslip.tkinter_error as tkinter_error
import pyslip.log
log = pyslip.log('pyslip.log')


######
# Various demo constants
######

# demo name/version
DemoName = 'Test point placement, pySlip %s' % pyslip.__version__
DemoVersion = '1.1'

# initial values
InitialViewLevel = 4
InitialViewPosition = (145.0, -20.0)

# tiles info
TileDirectory = 'tiles'
MinTileLevel = 0

# the number of decimal places in a lon/lat display
LonLatPrecision = 3

# startup size of the application
DemoWidth = 1000
DemoHeight = 700
DefaultAppSize = (DemoWidth, DemoHeight)

# general defaults
DefaultPointRadius = 5
DefaultPointColour = 'red'

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

# various GUI element sizes
TextBoxSize = (160, 25)
PlacementBoxSize = (60, 25)
OffsetBoxSize = (60, 25)
FontBoxSize = (160, 25)
FontsizeBoxSize = (60, 25)
PointRadiusBoxSize = (60, 25)
FontChoices = None
FontsizeChoices = ['8', '10', '12', '14', '16', '18', '20']
PointRadiusChoices = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']


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

    OKColour = '#ffffff40'
    ErrorColour = '#ff000020'

    def __init__(self, parent, title,
                 pointradius=DefaultPointRadius, pointcolour=DefaultPointColour,
                 placement=DefaultPlacement,
                 x=0, y=0, offset_x=0, offset_y=0, **kwargs):
        """Initialise a LayerControl instance.

        parent       reference to parent object
        title        text to show in static box outline around control
        pointradius  radius of point (not drawn if 0)
        pointcolour  colour of point
        placement    placement string for object
        x, y         X and Y coords
        offset_x     X offset of object
        offset_y     Y offset of object
        **kwargs     keyword args for Panel
        """

        # save parameters
        self.v_pointradius = str(pointradius)
        self.v_pointcolour = pointcolour
        self.v_placement = placement
        self.v_x = x
        self.v_y = y
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
        label = wx.StaticText(self, wx.ID_ANY, 'point radius: ')
        gbs.Add(label, (row,1), border=0,
                flag=(wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT))
        style=wx.CB_DROPDOWN|wx.CB_READONLY
        self.pointradius = wx.ComboBox(self, value=self.v_pointradius,
                                       #size=PointRadiusBoxSize,
                                       choices=PointRadiusChoices, style=style)
        gbs.Add(self.pointradius, (row,2),
                border=0, flag=(wx.ALIGN_CENTER_VERTICAL|wx.EXPAND))
        label = wx.StaticText(self, wx.ID_ANY, 'point colour: ')
        gbs.Add(label, (row,3), border=0,
                flag=(wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT))
        self.pointcolour = wx.Button(self, label='')
        self.pointcolour.SetBackgroundColour(self.v_pointcolour)
        gbs.Add(self.pointcolour, (row,4), border=0, flag=wx.EXPAND)
        gbs.Add(3, 1, (row,5))

        # row 1
        row += 1
        label = wx.StaticText(self, wx.ID_ANY, 'placement: ')
        gbs.Add(label, (row,1), border=0,
                flag=(wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT))
        choices = ['nw', 'cn', 'ne', 'ce', 'se', 'cs', 'sw', 'cw', 'cc', 'none']
        style=wx.CB_DROPDOWN|wx.CB_READONLY
        self.placement = wx.ComboBox(self, value=self.v_placement,
                                     #size=PlacementBoxSize,
                                     choices=choices, style=style)
        gbs.Add(self.placement, (row,2), border=0,
                flag=(wx.ALIGN_CENTER_VERTICAL|wx.EXPAND))

        # row 2
        row += 1
        label = wx.StaticText(self, wx.ID_ANY, 'x: ')
        gbs.Add(label, (row,1), border=0,
                flag=(wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT))
        self.x = wx.TextCtrl(self, value=str(self.v_x))#, size=OffsetBoxSize)
        gbs.Add(self.x, (row,2), border=0, flag=wx.EXPAND)

        label = wx.StaticText(self, wx.ID_ANY, 'y: ')
        gbs.Add(label, (row,3), border=0,
                flag=(wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT))
        self.y = wx.TextCtrl(self, value=str(self.v_y))#, size=OffsetBoxSize)
        gbs.Add(self.y, (row,4), border=0, flag=wx.EXPAND)

        # row 3
        row += 1
        label = wx.StaticText(self, wx.ID_ANY, 'offset_x: ')
        gbs.Add(label, (row,1), border=0,
                flag=(wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT))
        self.offset_x = wx.TextCtrl(self, value=str(self.v_offset_x))
                                    #size=OffsetBoxSize)
        gbs.Add(self.offset_x, (row,2), border=0, flag=wx.EXPAND)

        label = wx.StaticText(self, wx.ID_ANY, '  offset_y: ')
        gbs.Add(label, (row,3), border=0,
                flag=(wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT))
        self.offset_y = wx.TextCtrl(self, value=str(self.v_offset_y))
                                    #size=OffsetBoxSize)
        gbs.Add(self.offset_y, (row,4), border=0, flag=wx.EXPAND)

        # row 4
        row += 1
        delete_button = wx.Button(self, label='Remove')
        gbs.Add(delete_button, (row,2), border=10, flag=wx.EXPAND)
        btn_update = wx.Button(self, label='Update')
        gbs.Add(btn_update, (row,4), border=10, flag=wx.EXPAND)

        sbs.Add(gbs)
        self.SetSizer(sbs)
        sbs.Fit(self)

        self.pointcolour.Bind(wx.EVT_BUTTON, self.onPointColour)
        delete_button.Bind(wx.EVT_BUTTON, self.onDelete)
        btn_update.Bind(wx.EVT_BUTTON, self.onUpdate)

        # row 5 - just a spacer
        row += 1
        gbs.Add(1, 3, (row,0))

    def onPointColour(self, event):
        """Change point colour."""

        colour = self.pointcolour.GetBackgroundColour()
        wxcolour = wx.ColourData()
        wxcolour.SetColour(colour)

        dialog = wx.ColourDialog(self, data=wxcolour)
        dialog.GetColourData().SetChooseFull(True)
        new_colour = None
        if dialog.ShowModal() == wx.ID_OK:
            new_colour = dialog.GetColourData().Colour
        dialog.Destroy()

        if new_colour:
            self.pointcolour.SetBackgroundColour(new_colour)

    def onDelete(self, event):
        """Remove object from map."""

        event = LayerControlEvent(myEVT_DELETE, self.GetId())
        self.GetEventHandler().ProcessEvent(event)

    def get_numeric_value(self, control):
        """Get numeric value of a textbox.

        control  the textbox to query

        Return numeric value as a float.
        """

        orig_value = control.GetValue()
        if not orig_value:
            value = '0'
            control.SetValue('0')
        else:
            value = orig_value

        try:
            value = float(value)
        except ValueError:
            return (orig_value, None)
        return (orig_value, value)

    def onUpdate(self, event):
        """Update object on map."""

        # get x/y/offset_x/offset_y and check valid
        (orig_x, x) = self.get_numeric_value(self.x)
        (orig_y, y) = self.get_numeric_value(self.y)
        (orig_offset_x, offset_x) = self.get_numeric_value(self.offset_x)
        (orig_offset_y, offset_y) = self.get_numeric_value(self.offset_y)

        if (x is not None and y is not None
                and offset_x is not None and offset_y is not None):
            event = LayerControlEvent(myEVT_UPDATE, self.GetId())

            event.pointradius = int(self.pointradius.GetValue())
            event.pointcolour = self.pointcolour.GetBackgroundColour()
            event.placement = self.placement.GetValue()
            event.x = x
            event.y = y
            event.offset_x = int(offset_x)
            event.offset_y = int(offset_y)

            self.GetEventHandler().ProcessEvent(event)
        else:
            msg = 'These controls have bad values:\n'
            if x is None:
                name = ('x:' + ' '*20)[:12]
                msg += "\t%s\t%s\n" % (name, str(orig_x))
            if y is None:
                name = ('y:' + ' '*20)[:12]
                msg += "\t%s\t%s\n" % (name, str(orig_y))
            if offset_x is None:
                name = ('offset_x:' + ' '*20)[:12]
                msg += "\t%s\t%s\n" % (name, str(orig_offset_x))
            if offset_y is None:
                name = ('offset_y:' + ' '*20)[:12]
                msg += "\t%s\t%s\n" % (name, str(orig_offset_y))
            wx.MessageBox(msg, 'Warning', wx.OK | wx.ICON_ERROR)

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
        self.point_layer = None
        self.point_view_layer = None

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
        self.pyslip = pyslip.pySlip(parent,
                                    tile_src=self.tile_source,
                                    style=wx.SIMPLE_BORDER)
        all_display.Add(self.pyslip, proportion=1, border=0, flag=wx.EXPAND)

        # small spacer here - separate view and controls
        all_display.AddSpacer(HSpacerSize)

        # add controls to right of spacer
        controls = self.make_gui_controls(parent)
        all_display.Add(controls, proportion=0, border=0)

        parent.SetSizerAndFit(all_display)

    def make_gui_view(self, parent):
        """Build the map view widget

        parent  reference to the widget parent

        Returns the static box sizer.
        """

        # create gui objects
        sb = AppStaticBox(parent, '')
        self.pyslip = pyslip.pySlip(parent, tile_src=self.tile_source)

        # lay out objects
        box = wx.StaticBoxSizer(sb, orient=wx.HORIZONTAL)
        box.Add(self.pyslip, proportion=1, border=0, flag=wx.EXPAND)

        return box

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
        self.point = self.make_gui_point(parent)
        controls.Add(self.point, proportion=0, flag=wx.EXPAND|wx.ALL)
        self.point.Bind(EVT_DELETE, self.pointDelete)
        self.point.Bind(EVT_UPDATE, self.pointUpdate)

        # vertical spacer
        controls.AddSpacer(VSpacerSize)

        # controls for view-relative text layer
        self.point_view = self.make_gui_point_view(parent)
        controls.Add(self.point_view, proportion=0, flag=wx.EXPAND|wx.ALL)
        self.point_view.Bind(EVT_DELETE, self.pointViewDelete)
        self.point_view.Bind(EVT_UPDATE, self.pointViewUpdate)

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

    def make_gui_point(self, parent):
        """Build the point map-relative part of the controls part of GUI.

        parent  reference to parent

        Returns reference to containing sizer object.
        """

        # create widgets
        point_obj = LayerControl(parent, 'Point, map-relative',
                                 pointradius=DefaultPointRadius,
                                 pointcolour=DefaultPointColour,
                                 placement=DefaultPlacement,
                                 x=DefaultX, y=DefaultY,
                                 offset_x=DefaultOffsetX,
                                 offset_y=DefaultOffsetY)

        return point_obj

    def make_gui_point_view(self, parent):
        """Build the view-relative point part of the controls part of GUI.

        parent  reference to parent

        Returns reference to containing sizer object.
        """

        # create widgets
        point_obj = LayerControl(parent, 'Point, view-relative',
                                 pointradius=DefaultPointRadius,
                                 pointcolour=DefaultPointColour,
                                 placement=DefaultViewPlacement,
                                 x=DefaultViewX, y=DefaultViewY,
                                 offset_x=DefaultViewOffsetX,
                                 offset_y=DefaultViewOffsetY)

        return point_obj

    ######
    # event handlers
    ######

##### map-relative point layer

    def pointUpdate(self, event):
        """Display updated point."""

        # remove existing point map-rel layer, if any
        if self.point_layer:
            self.pyslip.DeleteLayer(self.point_layer)

        # convert values to sanity for layer attributes
        pointradius = event.pointradius
        pointcolour = event.pointcolour

        placement = event.placement
        if placement == 'none':
            placement= ''

        x = event.x
        if not x:
            x = 0
        try:
            x = float(x)
        except ValueError:
            x = 0.0

        y = event.y
        if not y:
            y = 0
        try:
            y = float(y)
        except ValueError:
            y = 0.0

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

        point_data = [(x, y, {'placement': placement,
                              'radius': pointradius,
                              'colour': pointcolour,
                              'offset_x': off_x,
                              'offset_y': off_y})]
        self.point_layer = self.pyslip.AddPointLayer(point_data, map_rel=True,
                                                     visible=True,
                                                     name='<point_layer>')

    def pointDelete(self, event):
        """Delete the point map-relative layer."""

        if self.point_layer:
            self.pyslip.DeleteLayer(self.point_layer)
        self.point_layer = None

##### view-relative point layer

    def pointViewUpdate(self, event):
        """Display updated point."""

        if self.point_view_layer:
            self.pyslip.DeleteLayer(self.point_view_layer)

        # convert values to sanity for layer attributes
        pointradius = event.pointradius
        pointcolour = event.pointcolour

        placement = event.placement
        if placement == 'none':
            placement= ''

        x = event.x
        if not x:
            x = 0

        y = event.y
        if not y:
            y = 0

        off_x = event.offset_x
        if not off_x:
            off_x = 0

        off_y = event.offset_y
        if not off_y:
            off_y = 0

        # create a new point layer
        point_data = [(x, y, {'placement': placement,
                              'radius': pointradius,
                              'colour': pointcolour,
                              'offset_x': off_x,
                              'offset_y': off_y})]
        self.point_view_layer = self.pyslip.AddPointLayer(point_data,
                                                          map_rel=False,
                                                          visible=True,
                                                          name='<point_layer>')

    def pointViewDelete(self, event):
        """Delete the point view-relative layer."""

        if self.point_view_layer:
            self.pyslip.DeleteLayer(self.point_view_layer)
        self.point_view_layer = None

    def final_setup(self, level, position):
        """Perform final setup.

        level     zoom level required
        position  position to be in centre of view

        We do this in a CallAfter() function for those operations that
        must not be done while the GUI is "fluid".
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

    def prepare_font_choices():
        """Get list of all font faces available."""

        global FontChoices

        e = wx.FontEnumerator()
        e.EnumerateFacenames()
        elist= e.GetFacenames()
        elist.sort()

        FontChoices = [x for x in elist if x[0] != '.']

    # our own handler for uncaught exceptions
    def excepthook(type, value, tb):
        msg = '\n' + '=' * 80
        msg += '\nUncaught exception:\n'
        msg += ''.join(traceback.format_exception(type, value, tb))
        msg += '=' * 80 + '\n'
        log(msg)
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

    prepare_font_choices()    # fills global 'FontChoices'

    app_frame = AppFrame()
    app_frame.Show()

    if debug:
        import wx.lib.inspection
        wx.lib.inspection.InspectionTool().Show()

    app.MainLoop()

