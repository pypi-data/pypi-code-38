"""
Program to test image map-relative and view-relative placement.
Select which to show and experiment with placement parameters.

Usage: test_image_placement.py [-h|--help] [-d] [(-t|--tiles) (GMT|OSM)]
"""


import os
import sys
import wx
import pyslip
import pyslip.tkinter_error as tkinter_error
import pyslip.log as log
from appstaticbox import AppStaticBox
from rotextctrl import ROTextCtrl
try:
    log = log.Log('pyslip.log')
except AttributeError:
    # already set up, ignore exception
    pass


######
# Various demo constants
######

# demo name/version
DemoName = 'Test image placement, pySlip %s' % pyslip.__version__
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
DemoHeight = 800
DefaultAppSize = (DemoWidth, DemoHeight)

# initial values in map-relative LayerControl
DefaultFilename = 'graphics/shipwreck.png'
DefaultPlacement = 'ne'
DefaultPointColour = 'red'
DefaultPointRadius = 3
DefaultX = 145.0
DefaultY = -20.0
DefaultOffsetX = 0
DefaultOffsetY = 0

# initial values in view-relative LayerControl
DefaultViewFilename = 'graphics/compass_rose.png'
DefaultViewPlacement = 'ne'
PointRadiusChoices = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
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

    def __init__(self, parent, title, filename='', placement=DefaultPlacement,
                 pointradius=DefaultPointRadius, pointcolour=DefaultPointColour,
                 x=0, y=0, offset_x=0, offset_y=0, **kwargs):
        """Initialise a LayerControl instance.

        parent       reference to parent object
        title        text to show in static box outline
        filename     filename of image to show
        placement    placement string for image
        pointradius  radius of the image point
        pointcolour  colour of the image point
        x, y         X and Y coords
        offset_x     X offset of image
        offset_y     Y offset of image
        **kwargs     keyword args for Panel
        """

        # create and initialise the base panel
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY, **kwargs)
        self.SetBackgroundColour(wx.WHITE)

        self.v_filename = filename
        self.v_placement = placement
        self.v_pointradius = str(pointradius)
        self.v_pointcolour = pointcolour
        self.v_x = x
        self.v_y = y
        self.v_offset_x = offset_x
        self.v_offset_y = offset_y

        box = AppStaticBox(self, title)
        sbs = wx.StaticBoxSizer(box, orient=wx.VERTICAL)
        gbs = wx.GridBagSizer(vgap=10, hgap=10)

        # row 0
        row = 0
        gbs.Add(3, 1, (row,0))
        label = wx.StaticText(self, wx.ID_ANY, 'filename: ')
        gbs.Add(label, (row,1), border=0,
                flag=(wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT))
        self.filename = ROTextCtrl(self, self.v_filename)
        gbs.Add(self.filename, (row,2), span=(1,3), border=0, flag=wx.EXPAND)
        gbs.Add(3, 1, (row,5))

        # row 1
        row += 1
        label = wx.StaticText(self, wx.ID_ANY, 'placement: ')
        gbs.Add(label, (row,1), border=0,
                flag=(wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT))
        choices = ['nw', 'cn', 'ne', 'ce', 'se', 'cs', 'sw', 'cw', 'cc', 'none']
        style=wx.CB_DROPDOWN|wx.CB_READONLY
        self.placement = wx.ComboBox(self, value=self.v_placement,
                                     choices=choices, style=style)
        gbs.Add(self.placement, (row,2), border=0)

        # row 2
        row += 1
        label = wx.StaticText(self, wx.ID_ANY, 'point radius: ')
        gbs.Add(label, (row,1), border=0,
                flag=(wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT))
        style=wx.CB_DROPDOWN|wx.CB_READONLY
        self.pointradius = wx.ComboBox(self, value=self.v_pointradius,
                                       choices=PointRadiusChoices, style=style)
        gbs.Add(self.pointradius, (row,2),
                border=0, flag=(wx.ALIGN_CENTER_VERTICAL|wx.EXPAND))
        label = wx.StaticText(self, wx.ID_ANY, 'point colour: ')
        gbs.Add(label, (row,3), border=0,
        flag=(wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT))
        self.pointcolour = wx.Button(self, label='')
        self.pointcolour.SetBackgroundColour(self.v_pointcolour)
        gbs.Add(self.pointcolour, (row,4), border=0, flag=wx.EXPAND)

        # row 3
        row += 1
        label = wx.StaticText(self, wx.ID_ANY, 'x: ')
        gbs.Add(label, (row,1), border=0,
                flag=(wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT))
        self.x = wx.TextCtrl(self, value=str(self.v_x))
        gbs.Add(self.x, (row,2), border=0, flag=wx.EXPAND)

        label = wx.StaticText(self, wx.ID_ANY, 'y: ')
        gbs.Add(label, (row,3), border=0,
                flag=(wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT))
        self.y = wx.TextCtrl(self, value=str(self.v_y))
        gbs.Add(self.y, (row,4), border=0, flag=wx.EXPAND)

        # row 4
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

        # row 5
        row += 1
        delete_button = wx.Button(self, label='Remove')
        gbs.Add(delete_button, (row,2), border=10, flag=wx.EXPAND)
        update_button = wx.Button(self, label='Update')
        gbs.Add(update_button, (row,4), border=10, flag=wx.EXPAND)

        sbs.Add(gbs)
        self.SetSizer(sbs)
        sbs.Fit(self)

        # row 6 (just a spacer)
        row += 1
        gbs.Add(1, 3, (row,0))

        # bind events to handlers
        self.filename.Bind(wx.EVT_LEFT_UP, self.onFilename)
        self.pointcolour.Bind(wx.EVT_BUTTON, self.onPointColour)
        delete_button.Bind(wx.EVT_BUTTON, self.onDelete)
        update_button.Bind(wx.EVT_BUTTON, self.onUpdate)

    def onFilename(self, event):
        """Change image filename."""

        wildcard = ("PNG files (*.png)|*.png|"
                    "JPG files (*.jpg)|*.jpg|"
                    "All files (*.*)|*.*")

        filepath = None

        dialog = wx.FileDialog(None, "Choose an image file",
                               os.getcwd(), "", wildcard, wx.FD_OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            filepath = dialog.GetPath()
        dialog.Destroy()

        if filepath:
            self.filename.SetValue(filepath)

    def onPointColour(self, event):
        """Change text colour."""

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
        """Remove image from map."""

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
        """Update image on map."""

        # get x/y/offset_x/offset_y and check valid
        (orig_x, x) = self.get_numeric_value(self.x)
        (orig_y, y) = self.get_numeric_value(self.y)
        (orig_offset_x, offset_x) = self.get_numeric_value(self.offset_x)
        (orig_offset_y, offset_y) = self.get_numeric_value(self.offset_y)

        if (x is not None and y is not None
                and offset_x is not None and offset_y is not None):
            event = LayerControlEvent(myEVT_UPDATE, self.GetId())

            event.filename = self.filename.GetValue()
            event.placement = self.placement.GetValue()
            event.radius = int(self.pointradius.GetValue())
            event.colour = self.pointcolour.GetBackgroundColour()
            event.x = self.x.GetValue()
            event.y = self.y.GetValue()
            event.offset_x = self.offset_x.GetValue()
            event.offset_y = self.offset_y.GetValue()

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
    def __init__(self, tile_dir=TileDirectory, levels=None):
        wx.Frame.__init__(self, None, size=DefaultAppSize,
                          title='%s, test version %s' % (DemoName, DemoVersion))
        self.SetMinSize(DefaultAppSize)
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.panel.SetBackgroundColour(wx.WHITE)
        self.panel.ClearBackground()

        self.tile_directory = tile_dir
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
        self.image_layer = None
        self.image_view_layer = None

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

        # make the map widget, place it at left
        self.pyslip = pyslip.pySlip(parent, tile_src=self.tile_source,
                                    style=wx.SIMPLE_BORDER)
        all_display.Add(self.pyslip, proportion=2, border=0, flag=wx.EXPAND)

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

        # controls for map-relative image layer
        self.image = self.make_gui_image(parent)
        controls.Add(self.image, proportion=0, flag=wx.EXPAND|wx.ALL)
        self.image.Bind(EVT_DELETE, self.imageDelete)
        self.image.Bind(EVT_UPDATE, self.imageUpdate)

        # vertical spacer
        controls.AddSpacer(VSpacerSize)

        # controls for image-relative image layer
        self.image_view = self.make_gui_image_view(parent)
        controls.Add(self.image_view, proportion=0, flag=wx.EXPAND|wx.ALL)
        self.image_view.Bind(EVT_DELETE, self.imageViewDelete)
        self.image_view.Bind(EVT_UPDATE, self.imageViewUpdate)

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

    def make_gui_image(self, parent):
        """Build the image part of the controls part of GUI.

        parent  reference to parent

        Returns reference to containing sizer object.
        """

        # create widgets
        image_obj = LayerControl(parent, 'Image, map-relative',
                                 filename=DefaultFilename,
                                 placement=DefaultPlacement,
                                 x=DefaultX, y=DefaultY,
                                 offset_x=DefaultOffsetX,
                                 offset_y=DefaultOffsetY)

        return image_obj

    def make_gui_image_view(self, parent):
        """Build the view-relative image part of the controls part of GUI.

        parent  reference to parent

        Returns reference to containing sizer object.
        """

        # create widgets
        image_obj = LayerControl(parent, 'Image, view-relative',
                                 filename=DefaultViewFilename,
                                 placement=DefaultViewPlacement,
                                 x=DefaultViewX, y=DefaultViewY,
                                 offset_x=DefaultViewOffsetX,
                                 offset_y=DefaultViewOffsetY)

        return image_obj

    ######
    # event handlers
    ######

##### map-relative image layer

    def imageUpdate(self, event):
        """Display updated image."""

        # remove any previous layer
        if self.image_layer:
            self.pyslip.DeleteLayer(self.image_layer)

        # convert values to sanity for layer attributes
        image = event.filename

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

        radius = event.radius
        colour = event.colour

        image_data = [(x, y, image, {'placement': placement,
                                     'radius': radius,
                                     'colour': colour,
                                     'offset_x': off_x,
                                     'offset_y': off_y})]
        self.image_layer = self.pyslip.AddImageLayer(image_data, map_rel=True,
                                                     visible=True,
                                                     name='<image_layer>')

    def imageDelete(self, event):
        """Delete the image map-relative layer."""

        if self.image_layer:
            self.pyslip.DeleteLayer(self.image_layer)
        self.image_layer = None

##### view-relative image layer

    def imageViewUpdate(self, event):
        """Display updated image."""

        if self.image_view_layer:
            self.pyslip.DeleteLayer(self.image_view_layer)

        # convert values to sanity for layer attributes
        image = event.filename
        placement = event.placement
        if placement == 'none':
            placement= ''

        x = event.x
        if not x:
            x = 0
        x = int(x)

        y = event.y
        if not y:
            y = 0
        y = int(y)

        off_x = event.offset_x
        if not off_x:
            off_x = 0
        off_x = int(off_x)

        off_y = event.offset_y
        if not off_y:
            off_y = 0
        off_y = int(off_y)

        radius = event.radius
        colour = event.colour

        # create a new image layer
        image_data = [(x, y, image, {'placement': placement,
                                     'radius': radius,
                                     'colour': colour,
                                     'offset_x': off_x,
                                     'offset_y': off_y})]
        self.image_view_layer = self.pyslip.AddImageLayer(image_data,
                                                          map_rel=False,
                                                          visible=True,
                                                          name='<image_layer>')

    def imageViewDelete(self, event):
        """Delete the image view-relative layer."""

        if self.image_view_layer:
            self.pyslip.DeleteLayer(self.image_view_layer)
        self.image_view_layer = None

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
    app_frame = AppFrame()
    app_frame.Show()

    if debug:
        log('Showing wxpython inspector')
        import wx.lib.inspection
        wx.lib.inspection.InspectionTool().Show()

    app.MainLoop()

