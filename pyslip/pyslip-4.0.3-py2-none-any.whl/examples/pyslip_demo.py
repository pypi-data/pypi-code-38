"""
pySlip demonstration program with user-selectable tiles.

Usage: pyslip_demo.py <options>

where <options> is zero or more of:
    -d|--debug <level>
        where <level> is either a numeric debug level in the range [0, 50] or
        one of the symbolic debug level names:
            NOTSET    0     nothing is logged (default)
            DEBUG    10     everything is logged
            INFO     20     less than DEBUG, informational debugging
            WARNING  30     less than INFO, only non-fatal warnings
            ERROR    40     less than WARNING
            CRITICAL 50     less than ERROR
    -h|--help
        prints this help and stops
    -x
        turns on the wxPython InspectionTool
"""


import os
import sys
import copy
import getopt
import traceback
from functools import partial

try:
    import wx
except ImportError:
    msg = '*'*60 + '\nSorry, you must install wxPython\n' + '*'*60
    print(msg)
    sys.exit(1)

try:
    import pyslip
    import pyslip.gmt_local as tiles
    import pyslip.log as log
except ImportError:
    msg = '*'*60 + '\nSorry, you must install pySlip\n' + '*'*60
    print(msg)
    sys.exit(1)

# initialize the logging system
try:
    log = log.Log('pyslip.log')
except AttributeError:
    # already have a log file, ignore
    pass

# get the bits of the demo program we need
from layer_control import LayerControl, EVT_ONOFF, EVT_SHOWONOFF, EVT_SELECTONOFF
from appstaticbox import AppStaticBox
from rotextctrl import ROTextCtrl


######
# Various demo constants
######

# demo name/version
DemoName = 'pySlip %s - Demonstration' % pyslip.__version__
DemoVersion = '4.0'

DemoWidth = 1000
DemoHeight = 800

# initial view level and position
InitViewLevel = 4

# this will eventually be selectable within the app
# a selection of cities, position from WikiPedia, etc
InitViewPosition = (0.0, 0.0)                # "Null" Island
#InitViewPosition = (0.0, 51.48)             # Greenwich, England
#InitViewPosition = (5.33, 60.389444)        # Bergen, Norway
#InitViewPosition = (153.033333, -27.466667) # Brisbane, Australia
#InitViewPosition = (98.3786761, 7.8627326)  # Phuket (ภูเก็ต), Thailand
#InitViewPosition = (151.209444, -33.859972) # Sydney, Australia
#InitViewPosition = (-77.036667, 38.895111)  # Washington, DC, USA
#InitViewPosition = (132.455278, 34.385278)  # Hiroshima, Japan
#InitViewPosition = (-8.008889, 31.63)       # Marrakech (مراكش), Morocco
#InitViewPosition = (18.95, 69.65)           # Tromsø, Norway
#InitViewPosition = (-70.933333, -53.166667) # Punta Arenas, Chile
#InitViewPosition = (168.3475, -46.413056)   # Invercargill, New Zealand
#InitViewPosition = (-147.723056, 64.843611) # Fairbanks, AK, USA
#InitViewPosition = (103.851959, 1.290270)   # Singapore

# levels on which various layers show
MRPointShowLevels = [3, 4]
MRImageShowLevels = [3, 4]
MRTextShowLevels = [3, 4]
MRPolyShowLevels = [3, 4]
MRPolylineShowLevels = [3, 4]

# the number of decimal places in a lon/lat display
LonLatPrecision = 3

# default deltas for various layer types
DefaultPointMapDelta = 40
DefaultPointViewDelta = 40
DefaultImageMapDelta = 40
DefaultImageViewDelta = 40
DefaultTextMapDelta = 40
DefaultTextViewDelta = 40
DefaultPolygonMapDelta = 40
DefaultPolygonViewDelta = 40
DefaultPolylineMapDelta = 40
DefaultPolylineViewDelta = 40

# image used for shipwrecks, glassy buttons, etc
ShipImg = 'graphics/shipwreck.png'

GlassyImg2 = 'graphics/glassy_button_2.png'
SelGlassyImg2 = 'graphics/selected_glassy_button_2.png'
GlassyImg3 = 'graphics/glassy_button_3.png'
SelGlassyImg3 = 'graphics/selected_glassy_button_3.png'
GlassyImg4 = 'graphics/glassy_button_4.png'
SelGlassyImg4 = 'graphics/selected_glassy_button_4.png'
GlassyImg5 = 'graphics/glassy_button_5.png'
SelGlassyImg5 = 'graphics/selected_glassy_button_5.png'
GlassyImg6 = 'graphics/glassy_button_6.png'
SelGlassyImg6 = 'graphics/selected_glassy_button_6.png'

# image used for shipwrecks
CompassRoseGraphic = 'graphics/compass_rose.png'

# logging levels, symbolic to numeric mapping
LogSym2Num = {'CRITICAL': 50,
              'ERROR': 40,
              'WARNING': 30,
              'INFO': 20,
              'DEBUG': 10,
              'NOTSET': 0}

# list of modules containing tile sources
# list of (<long_name>, <module_name>)
# the <long_name>s go into the Tileselect menu
Tilesets = [
            ('BlueMarble tiles', 'blue_marble'),
            ('GMT tiles', 'gmt_local'),
#            ('ModestMaps tiles', 'modest_maps'),  # can't access?
#            ('MapQuest tiles', 'mapquest'),    # can't access?
            ('OpenStreetMap tiles', 'open_street_map'),
            ('Stamen Toner tiles', 'stamen_toner'),
            ('Stamen Transport tiles', 'stamen_transport'),
            ('Stamen Watercolor tiles', 'stamen_watercolor'),
           ]

# index into Tilesets above to set default tileset: GMT tiles
DefaultTilesetIndex = 1

# some layout constants
HorizSpacer = 5
VertSpacer = 5


###############################################################################
# A small class to popup a moveable window.
###############################################################################

class DemoPopup(wx.PopupWindow):
    """A class for a simple popup window.
   
    The popup window can be dragged with the left mouse button.
    It is dismissed with a right mouse button click.

    The basic idea comes from:
    https://stackoverflow.com/questions/23415125/wxpython-popup-window-bound-to-a-wxbutton
    """

    # padding size top/bottom/left/right
    Padding = 20

    def __init__(self, parent, style, text):
        """Constructor"""
        super().__init__(parent, style)

        panel = wx.Panel(self)
        self.panel = panel
        panel.SetBackgroundColour("LIGHT YELLOW")

        st = wx.StaticText(panel, -1, text,
                           pos=(DemoPopup.Padding//2,DemoPopup.Padding//2))
        sz = st.GetBestSize()
        self.SetSize( (sz.width+DemoPopup.Padding, sz.height+DemoPopup.Padding) )
        panel.SetSize( (sz.width+DemoPopup.Padding, sz.height+DemoPopup.Padding) )

        panel.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        panel.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        panel.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        panel.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)

        st.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        st.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        st.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        st.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)

        wx.CallAfter(self.Refresh)    

    def OnMouseLeftDown(self, evt):
        self.Refresh()
        self.ldPos = evt.GetEventObject().ClientToScreen(evt.GetPosition())
        self.wPos = self.ClientToScreen((0,0))
        self.panel.CaptureMouse()

    def OnMouseMotion(self, evt):
        if evt.Dragging() and evt.LeftIsDown():
            dPos = evt.GetEventObject().ClientToScreen(evt.GetPosition())
            nPos = (self.wPos.x + (dPos.x - self.ldPos.x),
                    self.wPos.y + (dPos.y - self.ldPos.y))
            self.Move(nPos)

    def OnMouseLeftUp(self, evt):
        if self.panel.HasCapture():
            self.panel.ReleaseMouse()

    def OnRightUp(self, evt):
        self.Show(False)
        self.Destroy()

###############################################################################
# A small class to manage tileset sources.
###############################################################################

class TilesetManager:
    """A class to manage multiple tileset objects.
  
        ts = TilesetManager(source_list)  # 'source_list' is list of tileset source modules
        ts.get_tile_source(index)         # 'index' into 'source_list' of source to use

    Features 'lazy' importing, only imports when the tileset is used
    the first time.
    """

    def __init__(self, mod_list):
        """Create a set of tile sources.
        
        mod_list  list of module filenames to manage

        The list is something like: ['open_street_map.py', 'gmt_local.py']

        We can access tilesets using the index of the module in the 'mod_list'.
        """

        self.modules = []
        for fname in mod_list:
            self.modules.append([fname, os.path.splitext(fname)[0], None])

    def get_tile_source(self, mod_index):
        """Get an open tileset source for given name.

        mod_index  index into self.modules of tileset to use
        """

        tileset_data = self.modules[mod_index]
        (filename, modulename, tile_obj) = tileset_data
        if not tile_obj:
            # have never used this tileset, import and instantiate
            obj = __import__('pyslip', globals(), locals(), [modulename])
            tileset = getattr(obj, modulename)
            tile_obj = tileset.Tiles()
            tileset_data[2] = tile_obj
        return tile_obj

###############################################################################
# The main application frame
###############################################################################

class AppFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, size=(DemoWidth, DemoHeight),
                               title='%s %s' % (DemoName, DemoVersion))

        # initialize the tileset handler
        self.tileset_manager = self.init_tiles()
        self.tile_source = self.tileset_manager.get_tile_source(DefaultTilesetIndex)

        # start the GUI
        self.SetMinSize((DemoWidth, DemoHeight))
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.panel.SetBackgroundColour(wx.WHITE)
        self.panel.ClearBackground()

        # build the GUI
        self.make_gui(self.panel)

        # do initialisation stuff - all the application stuff
        self.initData()

        # create tileset menuitems
        self.initMenu()

        # create select event dispatch directory
        self.demo_select_dispatch = {}

        # selected point, if not None
        self.point_layer = None

        # variables referencing various layers
        self.sel_text_highlight = None

        # finally, bind events to handlers
        self.pyslip.Bind(pyslip.EVT_PYSLIP_LEVEL, self.level_change_event)
        self.pyslip.Bind(pyslip.EVT_PYSLIP_POSITION, self.mouse_posn_event)
        self.pyslip.Bind(pyslip.EVT_PYSLIP_SELECT, self.select_event)
        self.pyslip.Bind(pyslip.EVT_PYSLIP_BOXSELECT, self.select_event)

        # set the size of the demo window, etc
        self.Centre()
        self.Show()

        # set initial view position
        wx.CallLater(25, self.final_setup, InitViewLevel, InitViewPosition)

    def onTilesetSelect(self, event):
        """User selected a tileset from the menu.

        event  the menu select event
        """

        self.change_tileset(event.GetId())

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
        all_display.Add(self.pyslip, proportion=1, flag=wx.EXPAND)

        # add controls at right
        controls = self.make_gui_controls(parent)
        all_display.Add(controls, proportion=0)

        parent.SetSizerAndFit(all_display)

    def make_gui_controls(self, parent):
        """Build the 'controls' part of the GUI

        parent  reference to parent

        Returns reference to containing sizer object.

        Should really use GridBagSizer layout.
        """

        # all controls in vertical box sizer
        controls = wx.BoxSizer(wx.VERTICAL)

        # put level and position into one 'controls' position
        tmp = wx.BoxSizer(wx.HORIZONTAL)
        tmp.AddSpacer(HorizSpacer)
        level = self.make_gui_level(parent)
        tmp.Add(level, proportion=0, flag=wx.EXPAND|wx.ALL)
        tmp.AddSpacer(HorizSpacer)
        mouse = self.make_gui_mouse(parent)
        tmp.Add(mouse, proportion=0, flag=wx.EXPAND|wx.ALL)
        tmp.AddSpacer(HorizSpacer)
        controls.Add(tmp, proportion=0, flag=wx.EXPAND|wx.ALL)
        controls.AddSpacer(VertSpacer)

        # controls for map-relative points layer
        tmp = wx.BoxSizer(wx.HORIZONTAL)
        tmp.AddSpacer(HorizSpacer)
        lc_point = self.make_gui_point(parent)
        tmp.Add(lc_point, proportion=1, flag=wx.EXPAND|wx.ALL)
        tmp.AddSpacer(HorizSpacer)
        controls.Add(tmp, proportion=0, flag=wx.EXPAND|wx.ALL)
        controls.AddSpacer(VertSpacer)

        # controls for view-relative points layer
        tmp = wx.BoxSizer(wx.HORIZONTAL)
        tmp.AddSpacer(HorizSpacer)
        lc_point_v = self.make_gui_point_view(parent)
        tmp.Add(lc_point_v, proportion=1, flag=wx.EXPAND|wx.ALL)
        tmp.AddSpacer(HorizSpacer)
        controls.Add(tmp, proportion=0, flag=wx.EXPAND|wx.ALL)
        controls.AddSpacer(VertSpacer)

        # controls for map-relative image layer
        tmp = wx.BoxSizer(wx.HORIZONTAL)
        tmp.AddSpacer(HorizSpacer)
        image = self.make_gui_image(parent)
        tmp.Add(image, proportion=1, flag=wx.EXPAND|wx.ALL)
        tmp.AddSpacer(HorizSpacer)
        controls.Add(tmp, proportion=0, flag=wx.EXPAND|wx.ALL)
        controls.AddSpacer(VertSpacer)

        # controls for view-relative image layer
        tmp = wx.BoxSizer(wx.HORIZONTAL)
        tmp.AddSpacer(HorizSpacer)
        image_view = self.make_gui_image_view(parent)
        tmp.Add(image_view, proportion=1, flag=wx.EXPAND|wx.ALL)
        tmp.AddSpacer(HorizSpacer)
        controls.Add(tmp, proportion=0, flag=wx.EXPAND|wx.ALL)
        controls.AddSpacer(VertSpacer)

        # controls for map-relative text layer
        tmp = wx.BoxSizer(wx.HORIZONTAL)
        tmp.AddSpacer(HorizSpacer)
        lc_text = self.make_gui_text(parent)
        tmp.Add(lc_text, proportion=1, flag=wx.EXPAND|wx.ALL)
        tmp.AddSpacer(HorizSpacer)
        controls.Add(tmp, proportion=0, flag=wx.EXPAND|wx.ALL)
        controls.AddSpacer(VertSpacer)

        # controls for view-relative text layer
        tmp = wx.BoxSizer(wx.HORIZONTAL)
        tmp.AddSpacer(HorizSpacer)
        lc_text_v = self.make_gui_text_view(parent)
        tmp.Add(lc_text_v, proportion=1, flag=wx.EXPAND|wx.ALL)
        tmp.AddSpacer(HorizSpacer)
        controls.Add(tmp, proportion=0, flag=wx.EXPAND|wx.ALL)
        controls.AddSpacer(VertSpacer)

        # controls for map-relative polygon layer
        tmp = wx.BoxSizer(wx.HORIZONTAL)
        tmp.AddSpacer(HorizSpacer)
        lc_poly = self.make_gui_poly(parent)
        tmp.Add(lc_poly, proportion=1, flag=wx.EXPAND|wx.ALL)
        tmp.AddSpacer(HorizSpacer)
        controls.Add(tmp, proportion=0, flag=wx.EXPAND|wx.ALL)
        controls.AddSpacer(VertSpacer)

        # controls for view-relative polygon layer
        tmp = wx.BoxSizer(wx.HORIZONTAL)
        tmp.AddSpacer(HorizSpacer)
        lc_poly_v = self.make_gui_poly_view(parent)
        tmp.Add(lc_poly_v, proportion=1, flag=wx.EXPAND|wx.ALL)
        tmp.AddSpacer(HorizSpacer)
        controls.Add(tmp, proportion=0, flag=wx.EXPAND|wx.ALL)
        controls.AddSpacer(VertSpacer)

        # controls for map-relative polyline layer
        tmp = wx.BoxSizer(wx.HORIZONTAL)
        tmp.AddSpacer(HorizSpacer)
        lc_poll = self.make_gui_polyline(parent)
        tmp.Add(lc_poll, proportion=1, flag=wx.EXPAND|wx.ALL)
        tmp.AddSpacer(HorizSpacer)
        controls.Add(tmp, proportion=0, flag=wx.EXPAND|wx.ALL)
        controls.AddSpacer(VertSpacer)

        # controls for view-relative polyline layer
        tmp = wx.BoxSizer(wx.HORIZONTAL)
        tmp.AddSpacer(HorizSpacer)
        lc_poll_v = self.make_gui_polyline_view(parent)
        tmp.Add(lc_poll_v, proportion=1, flag=wx.EXPAND|wx.ALL)
        tmp.AddSpacer(HorizSpacer)
        controls.Add(tmp, proportion=0, flag=wx.EXPAND|wx.ALL)

        return controls

    def initMenu(self):
        """Add the 'Tilesets' menu to the app."""

        # create tileset menuitems
        menuBar = wx.MenuBar()
        tile_menu = wx.Menu()

        # this dict: id -> (display_name, module_name, tileset_obj)
        self.id2tiledata = {}

        # create the tileset menuitems, add to menu and connect to handler
        for (tile_index, (name, module_name)) in enumerate(Tilesets):
            new_id = wx.NewId()
            tile_menu.Append(new_id, name, name, wx.ITEM_RADIO)
            self.Bind(wx.EVT_MENU, self.onTilesetSelect)
            self.id2tiledata[new_id] = (name, module_name, None)
#            self.name2guiid[name] = new_id
            if tile_index == DefaultTilesetIndex:
                self.default_tileset_name = name
                tile_menu.Check(new_id, True)

        if self.default_tileset_name is None:
            raise Exception('Bad DefaultTileset (%s) or Tilesets (%s)'
                            % (DefaultTileset, str(Tilesets)))

        menuBar.Append(tile_menu, "&Tileset")
        self.SetMenuBar(menuBar)

    def init_tiles(self):
        """Initialize the tileset manager.

        Return a reference to the manager object.
        """

        modules = []
        for (action_id, (name, module_name)) in enumerate(Tilesets):
            modules.append(module_name)

        return TilesetManager(modules)

    def change_tileset(self, menu_id):
        """Handle a tileset selection.

        menu_id  the index in self.id2tiledata of the required tileset
        """

        # get information for the required tileset
        try:
            (name, module_name, new_tile_obj) = self.id2tiledata[menu_id]
        except KeyError:
            # badly formed self.id2tiledata element
            raise RuntimeError('self.id2tiledata is badly formed:\n%s'
                               % str(self.id2tiledata))

        if new_tile_obj is None:
            # haven't seen this tileset before, import and instantiate
            obj = __import__('pyslip', globals(), locals(), [module_name])
            tileset = getattr(obj, module_name)
            tile_name = tileset.TilesetName
            new_tile_obj = tileset.Tiles()

            # update the self.id2tiledata element
            self.id2tiledata[menu_id] = (name, module_name, new_tile_obj)

        self.pyslip.ChangeTileset(new_tile_obj)

    def onClose(self):
        """Application is closing."""

        pass

        #self.Close(True)

    def make_gui_level(self, parent):
        """Build the control that shows the level.

        parent  reference to parent

        Returns reference to containing sizer object.
        """

        # create objects
        txt = wx.StaticText(parent, wx.ID_ANY, 'Level: ')
        self.map_level = ROTextCtrl(parent, '', size=(30,-1),
                                    tooltip='Shows map zoom level')

        # lay out the controls
        sb = AppStaticBox(parent, 'Map level')
        box = wx.StaticBoxSizer(sb, orient=wx.HORIZONTAL)
        box.Add(txt, flag=(wx.ALIGN_CENTER_VERTICAL
                           |wx.ALIGN_RIGHT|wx.LEFT))
        box.Add(self.map_level, proportion=0,
                flag=wx.LEFT|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)

        return box

    def make_gui_mouse(self, parent):
        """Build the mouse part of the controls part of GUI.

        parent  reference to parent

        Returns reference to containing sizer object.
        """

        # create objects
        txt = wx.StaticText(parent, wx.ID_ANY, 'Lon/Lat: ')
        self.mouse_position = ROTextCtrl(parent, '', size=(120,-1),
                                         tooltip=('Shows the mouse '
                                                  'longitude and latitude '
                                                  'on the map'))

        # lay out the controls
        sb = AppStaticBox(parent, 'Mouse position')
        box = wx.StaticBoxSizer(sb, orient=wx.HORIZONTAL)
        box.Add(txt, flag=(wx.ALIGN_CENTER_VERTICAL
                           |wx.ALIGN_RIGHT|wx.LEFT))
        box.Add(self.mouse_position, proportion=0,
                flag=wx.RIGHT|wx.TOP|wx.BOTTOM)

        return box

    def make_gui_point(self, parent):
        """Build the points part of the controls part of GUI.

        parent  reference to parent

        Returns reference to containing sizer object.
        """

        # create widgets
        point_obj = LayerControl(parent, 'Points, map relative %s'
                                         % str(MRPointShowLevels),
                                 selectable=True)

        # tie to event handler(s)
        point_obj.Bind(EVT_ONOFF, self.pointOnOff)
        point_obj.Bind(EVT_SHOWONOFF, self.pointShowOnOff)
        point_obj.Bind(EVT_SELECTONOFF, self.pointSelectOnOff)

        return point_obj

    def make_gui_point_view(self, parent):
        """Build the view-relative points part of the GUI.

        parent  reference to parent

        Returns reference to containing sizer object.
        """

        # create widgets
        point_obj = LayerControl(parent, 'Points, view relative',
                                 selectable=True)

        # tie to event handler(s)
        point_obj.Bind(EVT_ONOFF, self.pointViewOnOff)
        point_obj.Bind(EVT_SHOWONOFF, self.pointViewShowOnOff)
        point_obj.Bind(EVT_SELECTONOFF, self.pointViewSelectOnOff)

        return point_obj

    def make_gui_image(self, parent):
        """Build the image part of the controls part of GUI.

        parent  reference to parent

        Returns reference to containing sizer object.
        """

        # create widgets
        image_obj = LayerControl(parent, 'Images, map relative %s'
                                         % str(MRImageShowLevels),
                                 selectable=True)

        # tie to event handler(s)
        image_obj.Bind(EVT_ONOFF, self.imageOnOff)
        image_obj.Bind(EVT_SHOWONOFF, self.imageShowOnOff)
        image_obj.Bind(EVT_SELECTONOFF, self.imageSelectOnOff)

        return image_obj

    def make_gui_image_view(self, parent):
        """Build the view-relative image part of the controls part of GUI.

        parent  reference to parent

        Returns reference to containing sizer object.
        """

        # create widgets
        image_obj = LayerControl(parent, 'Images, view relative',
                                 selectable=True)

        # tie to event handler(s)
        image_obj.Bind(EVT_ONOFF, self.imageViewOnOff)
        image_obj.Bind(EVT_SHOWONOFF, self.imageViewShowOnOff)
        image_obj.Bind(EVT_SELECTONOFF, self.imageViewSelectOnOff)

        return image_obj

    def make_gui_text(self, parent):
        """Build the map-relative text part of the controls part of GUI.

        parent  reference to parent

        Returns reference to containing sizer object.
        """

        # create widgets
        text_obj = LayerControl(parent,
                                'Text, map relative %s' % str(MRTextShowLevels),
                                selectable=True, editable=False)

        # tie to event handler(s)
        text_obj.Bind(EVT_ONOFF, self.textOnOff)
        text_obj.Bind(EVT_SHOWONOFF, self.textShowOnOff)
        text_obj.Bind(EVT_SELECTONOFF, self.textSelectOnOff)

        return text_obj

    def make_gui_text_view(self, parent):
        """Build the view-relative text part of the controls part of GUI.

        parent  reference to parent

        Returns reference to containing sizer object.
        """

        # create widgets
        text_view_obj = LayerControl(parent, 'Text, view relative',
                                     selectable=True)

        # tie to event handler(s)
        text_view_obj.Bind(EVT_ONOFF, self.textViewOnOff)
        text_view_obj.Bind(EVT_SHOWONOFF, self.textViewShowOnOff)
        text_view_obj.Bind(EVT_SELECTONOFF, self.textViewSelectOnOff)

        return text_view_obj

    def make_gui_poly(self, parent):
        """Build the map-relative polygon part of the controls part of GUI.

        parent  reference to parent

        Returns reference to containing sizer object.
        """

        # create widgets
        poly_obj = LayerControl(parent,
                                'Polygon, map relative %s'
                                     % str(MRPolyShowLevels),
                                selectable=True)

        # tie to event handler(s)
        poly_obj.Bind(EVT_ONOFF, self.polyOnOff)
        poly_obj.Bind(EVT_SHOWONOFF, self.polyShowOnOff)
        poly_obj.Bind(EVT_SELECTONOFF, self.polySelectOnOff)

        return poly_obj

    def make_gui_poly_view(self, parent):
        """Build the view-relative polygon part of the controls part of GUI.

        parent  reference to parent

        Returns reference to containing sizer object.
        """

        # create widgets
        poly_view_obj = LayerControl(parent, 'Polygon, view relative',
                                     selectable=True)

        # tie to event handler(s)
        poly_view_obj.Bind(EVT_ONOFF, self.polyViewOnOff)
        poly_view_obj.Bind(EVT_SHOWONOFF, self.polyViewShowOnOff)
        poly_view_obj.Bind(EVT_SELECTONOFF, self.polyViewSelectOnOff)

        return poly_view_obj

    def make_gui_polyline(self, parent):
        """Build the map-relative polyline part of the controls part of GUI.

        parent  reference to parent

        Returns reference to containing sizer object.
        """

        # create widgets
        poly_obj = LayerControl(parent,
                                'Polyline, map relative %s'
                                     % str(MRPolyShowLevels),
                                selectable=True)

        # tie to event handler(s)
        poly_obj.Bind(EVT_ONOFF, self.polylineOnOff)
        poly_obj.Bind(EVT_SHOWONOFF, self.polylineShowOnOff)
        poly_obj.Bind(EVT_SELECTONOFF, self.polylineSelectOnOff)

        return poly_obj

    def make_gui_polyline_view(self, parent):
        """Build the view-relative polyline part of the controls part of GUI.

        parent  reference to parent

        Returns reference to containing sizer object.
        """

        # create widgets
        poly_view_obj = LayerControl(parent, 'Polyline, view relative',
                                     selectable=True)

        # tie to event handler(s)
        poly_view_obj.Bind(EVT_ONOFF, self.polylineViewOnOff)
        poly_view_obj.Bind(EVT_SHOWONOFF, self.polylineViewShowOnOff)
        poly_view_obj.Bind(EVT_SELECTONOFF, self.polylineViewSelectOnOff)

        return poly_view_obj

    ######
    # demo control event handlers
    ######

##### map-relative point layer

    def pointOnOff(self, event):
        """Handle OnOff event for point layer control."""

        if event.state:
            self.point_layer = \
                self.pyslip.AddPointLayer(PointData, map_rel=True,
                                          colour=PointDataColour, radius=3,
                                          # offset points to exercise placement
                                          offset_x=0, offset_y=0, visible=True,
                                          show_levels=MRPointShowLevels,
                                          delta=DefaultPointMapDelta,
                                          placement='nw',   # check placement
                                          name='<pt_layer>')
        else:
            self.pyslip.DeleteLayer(self.point_layer)
            self.point_layer = None

            if self.sel_point_layer:
                self.pyslip.DeleteLayer(self.sel_point_layer)
                self.sel_point_layer = None
                self.sel_point = None

    def pointShowOnOff(self, event):
        """Handle ShowOnOff event for point layer control."""

        if event.state:
            self.pyslip.ShowLayer(self.point_layer)
            if self.sel_point_layer:
                self.pyslip.ShowLayer(self.sel_point_layer)
        else:
            self.pyslip.HideLayer(self.point_layer)
            if self.sel_point_layer:
                self.pyslip.HideLayer(self.sel_point_layer)

    def pointSelectOnOff(self, event):
        """Handle SelectOnOff event for point layer control."""

        layer = self.point_layer
        if event.state:
            self.add_select_handler(layer, self.pointSelect)
            self.pyslip.SetLayerSelectable(layer, True)
        else:
            self.del_select_handler(layer)
            self.pyslip.SetLayerSelectable(layer, False)

    def pointSelect(self, event):
        """Handle map-relative point select exception from the widget.

        event  the event that contains these attributes:
                   type       the type of point selection: single or box
                   layer_id   ID of the layer the select occurred on
                   selection  [list of] tuple (xgeo,ygeo) of selected point
                              (if None then no point(s) selected)
                   data       userdata object of the selected point
                   button     indicates the mouse button used

        The selection could be a single or box select.

        The point select is designed to be select point(s) for on, then select
        point(s) again for off.  Clicking away from the already selected point
        doesn't remove previously selected point(s) if nothing is selected.  We
        do this to show the selection/deselection of point(s) is up to the user,
        not the widget.

        This code also shows how to combine handling of EventSelect and
        EventBoxSelect events.
        """

        if event.selection == self.sel_point:
            # already have point selected, just deselect it
            self.pyslip.DeleteLayer(self.sel_point_layer)
            self.sel_point_layer = None
            self.sel_point = None
        elif event.selection:
            if event.button == pyslip.MouseLeft:
                # some other point(s) selected, delete previous selection, if any
                if self.sel_point_layer:
                    self.pyslip.DeleteLayer(self.sel_point_layer)
    
                # remember selection (need copy as highlight modifies attributes)
                self.sel_point = copy.deepcopy(event.selection)
    
                # choose different highlight colour for different type of selection
                selcolour = '#00ffff'
                if event.type == pyslip.EventSelect:
                    selcolour = '#0000ff'
    
                # get selected points into form for display layer
                # delete 'colour' and 'radius' attributes as we want different values
                highlight = []
                for (x, y, d) in event.selection:
                    del d['colour']     # AddLayer...() ensures keys exist
                    del d['radius']
                    highlight.append((x, y, d))
    
                # layer with highlight of selected poijnts
                self.sel_point_layer = \
                    self.pyslip.AddPointLayer(highlight, map_rel=True,
                                              colour=selcolour,
                                              radius=5, visible=True,
                                              show_levels=MRPointShowLevels,
                                              name='<sel_pt_layer>')
    
                # make sure highlight layer is BELOW selected layer
                self.pyslip.PlaceLayerBelowLayer(self.sel_point_layer,
                                                 self.point_layer)
            elif event.button == pyslip.MouseMiddle:
                log('SELECT event using middle mouse button at GEO coords (%.2f, %.2f)'
                        % (event.selection[0][0], event.selection[0][1]))
            elif event.button == pyslip.MouseRight:
                # RIGHT button, do a context popup, only a single point selected
                msg = ('Point at GEO coords (%.2f, %.2f)'
                        % (event.selection[0][0], event.selection[0][1]))
                self.show_popup(msg, event.vposn)
        # else: we ignore an empty selection

        return True

##### view-relative point layer

    def pointViewOnOff(self, event):
        """Handle OnOff event for point view layer control."""

        if event.state:
            self.point_view_layer = \
                self.pyslip.AddPointLayer(PointViewData, map_rel=False,
                                          placement=PointViewDataPlacement,
                                          colour=PointViewDataColour, radius=1,
                                          delta=DefaultPointViewDelta,
                                          visible=True,
                                          name='<point_view_layer>')
        else:
            self.pyslip.DeleteLayer(self.point_view_layer)
            self.point_view_layer = None
            if self.sel_point_view_layer:
                self.pyslip.DeleteLayer(self.sel_point_view_layer)
                self.sel_point_view_layer = None
                self.sel_point_view = None

    def pointViewShowOnOff(self, event):
        """Handle ShowOnOff event for point view layer control."""

        if event.state:
            self.pyslip.ShowLayer(self.point_view_layer)
            if self.sel_point_view_layer:
                self.pyslip.ShowLayer(self.sel_point_view_layer)
        else:
            self.pyslip.HideLayer(self.point_view_layer)
            if self.sel_point_view_layer:
                self.pyslip.HideLayer(self.sel_point_view_layer)

    def pointViewSelectOnOff(self, event):
        """Handle SelectOnOff event for point view layer control."""

        layer = self.point_view_layer
        if event.state:
            self.add_select_handler(layer, self.pointViewSelect)
            self.pyslip.SetLayerSelectable(layer, True)
        else:
            self.del_select_handler(layer)
            self.pyslip.SetLayerSelectable(layer, False)

    def pointViewSelect(self, event):
        """Handle view-relative point select exception from the widget.

        event  the event that contains these attributes:
                   type       the type of point selection: single or box
                   selection  [list of] tuple (xgeo,ygeo) of selected point
                              (if None then no point(s) selected)
                   data       userdata object of the selected point

        The selection could be a single or box select.

        The point select is designed to be click point for on, then any other
        select event turns that point off, whether there is a selection or not
        and whether the same point is selected or not.
        """

        # if there is a previous selection, remove it
        if self.sel_point_view_layer:
            self.pyslip.DeleteLayer(self.sel_point_view_layer)
            self.sel_point_view_layer = None

        if event.selection and event.selection != self.sel_point_view:
            # it's a box selection
            self.sel_point_view = event.selection

            # get selected points into form for display layer
            highlight = []
            for (x, y, d) in event.selection:
                del d['colour']
                del d['radius']
                highlight.append((x, y, d))

            # assume a box selection
            self.sel_point_view_layer = \
                self.pyslip.AddPointLayer(highlight, map_rel=False,
                                          placement='se',
                                          colour='#0000ff',
                                          radius=3, visible=True,
                                          name='<sel_pt_view_layer>')
        else:
            self.sel_point_view = None

        return True

##### map-relative image layer

    def imageOnOff(self, event):
        """Handle OnOff event for map-relative image layer control."""

        if event.state:
            self.image_layer = \
                self.pyslip.AddImageLayer(ImageData, map_rel=True,
                                          visible=True,
                                          delta=DefaultImageMapDelta,
                                          show_levels=MRImageShowLevels,
                                          name='<image_layer>')
        else:
            self.pyslip.DeleteLayer(self.image_layer)
            self.image_layer = None
            if self.sel_image_layer:
                self.pyslip.DeleteLayer(self.sel_image_layer)
                self.sel_image_layer = None
                self.sel_image = None

    def imageShowOnOff(self, event):
        """Handle ShowOnOff event for image layer control."""

        if event.state:
            self.pyslip.ShowLayer(self.image_layer)
            if self.sel_image_layer:
                self.pyslip.ShowLayer(self.sel_image_layer)
        else:
            self.pyslip.HideLayer(self.image_layer)
            if self.sel_image_layer:
                self.pyslip.HideLayer(self.sel_image_layer)

    def imageSelectOnOff(self, event):
        """Handle SelectOnOff event for image layer control."""

        layer = self.image_layer
        if event.state:
            self.add_select_handler(layer, self.imageSelect)
            self.pyslip.SetLayerSelectable(layer, True)
        else:
            self.del_select_handler(layer)
            self.pyslip.SetLayerSelectable(layer, False)

    def imageSelect(self, event):
        """Select event from the widget.

        event  the event that contains these attributes:
                   type       the type of point selection: single or box
                   selection  [list of] tuple (xgeo,ygeo) of selected point
                              (if None then no point(s) selected)
                   data       userdata object of the selected point

        The selection could be a single or box select.
        """

        #relsel = event.relsel
        selection = event.selection

        # select again, turn selection off
        if selection == self.sel_image:
            self.pyslip.DeleteLayer(self.sel_image_layer)
            self.sel_image_layer = self.sel_image = None
        elif selection:
            # new image selected, show highlight
            if self.sel_image_layer:
                self.pyslip.DeleteLayer(self.sel_image_layer)
            self.sel_image = selection

            # get selected points into form for display layer
            new_points = []
            for (x, y, f, d) in selection:
                del d['colour']
                del d['radius']
                new_points.append((x, y, d))

            self.sel_image_layer = \
                self.pyslip.AddPointLayer(new_points, map_rel=True,
                                          colour='#0000ff',
                                          radius=5, visible=True,
                                          show_levels=[3,4],
                                          name='<sel_pt_layer>')
            self.pyslip.PlaceLayerBelowLayer(self.sel_image_layer,
                                             self.image_layer)

        return True

    def imageBSelect(self, id, selection=None):
        """Select event from the widget."""

        # remove any previous selection
        if self.sel_image_layer:
            self.pyslip.DeleteLayer(self.sel_image_layer)
            self.sel_image_layer = None

        if selection:
            # get selected points into form for display layer
            points = []
            for (x, y, f, d) in selection:
                del d['colour']
                del d['radius']
                points.append((x, y, d))

            self.sel_image_layer = \
                self.pyslip.AddPointLayer(points, map_rel=True,
                                          colour='#e0e0e0',
                                          radius=13, visible=True,
                                          show_levels=[3,4],
                                          name='<boxsel_img_layer>')
            self.pyslip.PlaceLayerBelowLayer(self.sel_image_layer,
                                             self.image_layer)

        return True

##### view-relative image layer

    def imageViewOnOff(self, event):
        """Handle OnOff event for view-relative image layer control.
        
        event  the state of the leyer control master checkbox
        """

        if event.state:
            self.image_view_layer = \
                self.pyslip.AddImageLayer(ImageViewData, map_rel=False,
                                          delta=DefaultImageViewDelta,
                                          visible=True,
                                          name='<image_view_layer>')
        else:
            self.pyslip.DeleteLayer(self.image_view_layer)
            self.image_view_layer = None
            if self.sel_image_view_layer:
                self.pyslip.DeleteLayer(self.sel_image_view_layer)
                self.sel_image_view_layer = None
            if self.sel_imagepoint_view_layer:
                self.pyslip.DeleteLayer(self.sel_imagepoint_view_layer)
                self.sel_imagepoint_view_layer = None

    def imageViewShowOnOff(self, event):
        """Handle ShowOnOff event for image layer control."""

        if event.state:
            self.pyslip.ShowLayer(self.image_view_layer)
            if self.sel_image_view_layer:
                self.pyslip.ShowLayer(self.sel_image_view_layer)
            if self.sel_imagepoint_view_layer:
                self.pyslip.ShowLayer(self.sel_imagepoint_view_layer)
        else:
            self.pyslip.HideLayer(self.image_view_layer)
            if self.sel_image_view_layer:
                self.pyslip.HideLayer(self.sel_image_view_layer)
            if self.sel_imagepoint_view_layer:
                self.pyslip.HideLayer(self.sel_imagepoint_view_layer)

    def imageViewSelectOnOff(self, event):
        """Handle SelectOnOff event for image layer control."""

        layer = self.image_view_layer
        if event.state:
            self.add_select_handler(layer, self.imageViewSelect)
            self.pyslip.SetLayerSelectable(layer, True)
        else:
            self.del_select_handler(layer)
            self.pyslip.SetLayerSelectable(layer, False)

    def imageViewSelect(self, event):
        """View-relative image select event from the widget.

        event  the event that contains these attributes:
                   selection  [list of] tuple (xgeo,ygeo) of selected point
                              (if None then no point(s) selected)
                   relsel     relative position of single point select,
                              None if box select

        The selection could be a single or box select.

        The selection mode is different here.  An empty selection will remove
        any current selection.  This shows the flexibility that user code
        can implement.

        The code below doesn't assume a placement of the selected image, it
        figures out the correct position of the 'highlight' layers.  This helps
        with debugging, as we can move the compass rose anywhere we like.
        """

        selection = event.selection
        relsel = event.relsel       # None if box select

        # only one image selectable, remove old selections (if any)
        if self.sel_image_view_layer:
            self.pyslip.DeleteLayer(self.sel_image_view_layer)
            self.sel_image_view_layer = None
        if self.sel_imagepoint_view_layer:
            self.pyslip.DeleteLayer(self.sel_imagepoint_view_layer)
            self.sel_imagepoint_view_layer = None

        if selection:
            # figure out compass rose attributes
            attr_dict = ImageViewData[0][3]
            img_placement = attr_dict['placement']

            self.sel_imagepoint_view_layer = None
            if relsel:
                # unpack event relative selection point
                (sel_x, sel_y) = relsel     # select relative point in image

# FIXME  This should be cleaner, user shouldn't have to know internal structure
# FIXME  or fiddle with placement perturbations

                # add selection point
                CR_Height2 = CR_Height//2
                CR_Width2 = CR_Width//2
                point_place_coords = {'ne': '(sel_x - CR_Width, sel_y)',
                                      'ce': '(sel_x - CR_Width, sel_y - CR_Height2)',
                                      'se': '(sel_x - CR_Width, sel_y - CR_Height)',
                                      'cs': '(sel_x - CR_Width2, sel_y - CR_Height)',
                                      'sw': '(sel_x, sel_y - CR_Height)',
                                      'cw': '(sel_x, sel_y - CR_Height/2.0)',
                                      'nw': '(sel_x, sel_y)',
                                      'cn': '(sel_x - CR_Width2, sel_y)',
                                      'cc': '(sel_x - CR_Width2, sel_y - CR_Height2)',
                                      '':   '(sel_x, sel_y)',
                                      None: '(sel_x, sel_y)',
                                     }
                for (key, code) in point_place_coords.items():
                    point_place_coords[key] = compile(code, '<string>', mode='eval')

                point = eval(point_place_coords[img_placement])
                self.sel_imagepoint_view_layer = \
                    self.pyslip.AddPointLayer((point,), map_rel=False,
                                              colour='green',
                                              radius=5, visible=True,
                                              placement=img_placement,
                                              name='<sel_image_view_point>')

            # add polygon outline around image
            p_dict = {'placement': img_placement, 'width': 3, 'colour': 'green', 'closed': True}
            poly_place_coords = {'ne': '(((-CR_Width,0),(0,0),(0,CR_Height),(-CR_Width,CR_Height)),p_dict)',
                                 'ce': '(((-CR_Width,-CR_Height2),(0,-CR_Height2),(0,CR_Height2),(-CR_Width,CR_Height2)),p_dict)',
                                 'se': '(((-CR_Width,-CR_Height),(0,-CR_Height),(0,0),(-CR_Width,0)),p_dict)',
                                 'cs': '(((-CR_Width2,-CR_Height),(CR_Width2,-CR_Height),(CR_Width2,0),(-CR_Width2,0)),p_dict)',
                                 'sw': '(((0,-CR_Height),(CR_Width,-CR_Height),(CR_Width,0),(0,0)),p_dict)',
                                 'cw': '(((0,-CR_Height2),(CR_Width,-CR_Height2),(CR_Width,CR_Height2),(0,CR_Height2)),p_dict)',
                                 'nw': '(((0,0),(CR_Width,0),(CR_Width,CR_Height),(0,CR_Height)),p_dict)',
                                 'cn': '(((-CR_Width2,0),(CR_Width2,0),(CR_Width2,CR_Height),(-CR_Width2,CR_Height)),p_dict)',
                                 'cc': '(((-CR_Width2,-CR_Height2),(CR_Width2,-CR_Height2),(CR_Width2,CR_Heigh/2),(-CR_Width2,CR_Height2)),p_dict)',
                                 '':   '(((x, y),(x+CR_Width,y),(x+CR_Width,y+CR_Height),(x,y+CR_Height)),p_dict)',
                                 None: '(((x, y),(x+CR_Width,y),(x+CR_Width,y+CR_Height),(x,y+CR_Height)),p_dict)',
                                }
            for (key, code) in poly_place_coords.items():
                poly_place_coords[key] = compile(code, '<string>', mode='eval')

            pdata = eval(poly_place_coords[img_placement])
            self.sel_image_view_layer = \
                self.pyslip.AddPolygonLayer((pdata,), map_rel=False,
                                            name='<sel_image_view_outline>',
                                           )

        return True

##### map-relative text layer

    def textOnOff(self, event):
        """Handle OnOff event for map-relative text layer control."""

        if event.state:
            self.text_layer = \
                self.pyslip.AddTextLayer(TextData, map_rel=True,
                                         name='<text_layer>', visible=True,
                                         delta=DefaultTextMapDelta,
                                         show_levels=MRTextShowLevels,
                                         placement='ne')
        else:
            self.pyslip.DeleteLayer(self.text_layer)
            if self.sel_text_layer:
                self.pyslip.DeleteLayer(self.sel_text_layer)
                self.sel_text_layer = None
                self.sel_text_highlight = None

    def textShowOnOff(self, event):
        """Handle ShowOnOff event for text layer control."""

        if event.state:
            if self.text_layer:
                self.pyslip.ShowLayer(self.text_layer)
            if self.sel_text_layer:
                self.pyslip.ShowLayer(self.sel_text_layer)
        else:
            if self.text_layer:
                self.pyslip.HideLayer(self.text_layer)
            if self.sel_text_layer:
                self.pyslip.HideLayer(self.sel_text_layer)

    def textSelectOnOff(self, event):
        """Handle SelectOnOff event for text layer control."""

        layer = self.text_layer
        if event.state:
            self.add_select_handler(layer, self.textSelect)
            self.pyslip.SetLayerSelectable(layer, True)
        else:
            self.del_select_handler(layer)
            self.pyslip.SetLayerSelectable(layer, False)


    def textSelect(self, event):
        """Map-relative text select event from the widget.

        event  the event that contains these attributes:
                   type       the type of point selection: single or box
                   selection  [list of] tuple (xgeo,ygeo) of selected point
                              (if None then no point(s) selected)

        The selection could be a single or box select.

        The selection mode here is more standard: empty select turns point(s)
        off, selected points reselection leaves points selected.
        """

        selection = event.selection

        if self.sel_text_layer:
            # turn previously selected point(s) off
            self.pyslip.DeleteLayer(self.sel_text_layer)
            self.sel_text_layer = None

        if selection:
            # get selected points into form for display layer
            points = []
            for (x, y, t, d) in selection:
                del d['colour']     # remove point attributes, want different
                del d['radius']
                del d['offset_x']   # remove offsets, we want point not text
                del d['offset_y']
                points.append((x, y, d))

            self.sel_text_layer = \
                self.pyslip.AddPointLayer(points, map_rel=True,
                                          colour='#0000ff',
                                          radius=5, visible=True,
                                          show_levels=MRTextShowLevels,
                                          name='<sel_text_layer>')
            self.pyslip.PlaceLayerBelowLayer(self.sel_text_layer,
                                             self.text_layer)

        return True

##### view-relative text layer

    def textViewOnOff(self, event):
        """Handle OnOff event for view-relative text layer control."""

        if event.state:
            self.text_view_layer = \
                self.pyslip.AddTextLayer(TextViewData, map_rel=False,
                                         name='<text_view_layer>',
                                         delta=DefaultTextViewDelta,
                                         placement=TextViewDataPlace,
                                         visible=True,
                                         fontsize=24, textcolour='#0000ff',
                                         offset_x=TextViewDataOffX,
                                         offset_y=TextViewDataOffY)
        else:
            self.pyslip.DeleteLayer(self.text_view_layer)
            self.text_view_layer = None
            if self.sel_text_view_layer:
                self.pyslip.DeleteLayer(self.sel_text_view_layer)
                self.sel_text_view_layer = None

    def textViewShowOnOff(self, event):
        """Handle ShowOnOff event for view text layer control."""

        if event.state:
            self.pyslip.ShowLayer(self.text_view_layer)
            if self.sel_text_view_layer:
                self.pyslip.ShowLayer(self.sel_text_view_layer)
        else:
            self.pyslip.HideLayer(self.text_view_layer)
            if self.sel_text_view_layer:
                self.pyslip.HideLayer(self.sel_text_view_layer)

    def textViewSelectOnOff(self, event):
        """Handle SelectOnOff event for view text layer control."""

        layer = self.text_view_layer
        if event.state:
            self.add_select_handler(layer, self.textViewSelect)
            self.pyslip.SetLayerSelectable(layer, True)
        else:
            self.del_select_handler(layer)
            self.pyslip.SetLayerSelectable(layer, False)

    def textViewSelect(self, event):
        """View-relative text select event from the widget.

        event  the event that contains these attributes:
                   type       the type of point selection: single or box
                   selection  [list of] tuple (xgeo,ygeo) of selected point
                              (if None then no point(s) selected)

        The selection could be a single or box select.

        The selection mode here is more standard: empty select turns point(s)
        off, selected points reselection leaves points selected.
        """

        selection = event.selection

        # turn off any existing selection
        if self.sel_text_view_layer:
            self.pyslip.DeleteLayer(self.sel_text_view_layer)
            self.sel_text_view_layer = None

        if selection:
            # get selected points into form for point display layer
            points = []
            for (x, y, t, d) in selection:
                del d['colour']     # want to override colour, radius
                del d['radius']
                points.append((x, y, d))

            self.sel_text_view_layer = \
                self.pyslip.AddPointLayer(points, map_rel=False,
                                          colour='black',
                                          radius=5, visible=True,
                                          show_levels=MRTextShowLevels,
                                          name='<sel_text_view_layer>')
            self.pyslip.PlaceLayerBelowLayer(self.sel_text_view_layer,
                                             self.text_view_layer)

        return True

##### map-relative polygon layer

    def polyOnOff(self, event):
        """Handle OnOff event for map-relative polygon layer control."""

        if event.state:
            self.poly_layer = \
                self.pyslip.AddPolygonLayer(PolyData, map_rel=True,
                                            visible=True,
                                            delta=DefaultPolygonMapDelta,
                                            show_levels=MRPolyShowLevels,
                                            name='<poly_layer>')
        else:
            self.pyslip.DeleteLayer(self.poly_layer)
            self.poly_layer = None

            if self.sel_poly_layer:
                self.pyslip.DeleteLayer(self.sel_poly_layer)
                self.sel_poly_layer = None
                self.sel_poly_point = None

    def polyShowOnOff(self, event):
        """Handle ShowOnOff event for polygon layer control."""

        if event.state:
            self.pyslip.ShowLayer(self.poly_layer)
            if self.sel_poly_layer:
                self.pyslip.ShowLayer(self.sel_poly_layer)
        else:
            self.pyslip.HideLayer(self.poly_layer)
            if self.sel_poly_layer:
                self.pyslip.HideLayer(self.sel_poly_layer)

    def polySelectOnOff(self, event):
        """Handle SelectOnOff event for polygon layer control."""

        layer = self.poly_layer
        if event.state:
            self.add_select_handler(layer, self.polySelect)
            self.pyslip.SetLayerSelectable(layer, True)
        else:
            self.del_select_handler(layer)
            self.pyslip.SetLayerSelectable(layer, False)

    def polySelect(self, event):
        """Map- and view-relative polygon select event from the widget.

        event  the event that contains these attributes:
                   type       the type of point selection: single or box
                   selection  [list of] tuple (xgeo,ygeo) of selected point
                              (if None then no point(s) selected)

        The selection could be a single or box select.

        Select a polygon to turn it on, any other polygon selection turns
        it off, unless previous selection again selected.
        """

        # .seletion: [(poly,attr), ...]
        selection = event.selection

        # turn any previous selection off
        if self.sel_poly_layer:
            self.pyslip.DeleteLayer(self.sel_poly_layer)
            self.sel_poly_layer = None

        # box OR single selection
        if selection:
            # get selected polygon points into form for point display layer
            points = []
            for (poly, d) in selection:
                try:
                    del d['colour']
                except KeyError:
                    pass
                try:
                    del d['radius']
                except KeyError:
                    pass
                for (x, y) in poly:
                    points.append((x, y, d))

            self.sel_poly_layer = \
                self.pyslip.AddPointLayer(points, map_rel=True,
                                          colour='#ff00ff',
                                          radius=5, visible=True,
                                          show_levels=[3,4],
                                          name='<sel_poly>')

        return True

##### view-relative polygon layer

    def polyViewOnOff(self, event):
        """Handle OnOff event for map-relative polygon layer control."""

        if event.state:
            self.poly_view_layer = \
                self.pyslip.AddPolygonLayer(PolyViewData, map_rel=False,
                                            delta=DefaultPolygonViewDelta,
                                            name='<poly_view_layer>',
                                            placement='cn', visible=True,
                                            fontsize=24, colour='#0000ff')
        else:
            self.pyslip.DeleteLayer(self.poly_view_layer)
            self.poly_view_layer = None

            if self.sel_poly_view_layer:
                self.pyslip.DeleteLayer(self.sel_poly_view_layer)
                self.sel_poly_view_layer = None
                self.sel_poly_view_point = None

    def polyViewShowOnOff(self, event):
        """Handle ShowOnOff event for polygon layer control."""

        if event.state:
            self.pyslip.ShowLayer(self.poly_view_layer)
            if self.sel_poly_view_layer:
                self.pyslip.ShowLayer(self.sel_poly_view_layer)
        else:
            self.pyslip.HideLayer(self.poly_view_layer)
            if self.sel_poly_view_layer:
                self.pyslip.HideLayer(self.sel_poly_view_layer)

    def polyViewSelectOnOff(self, event):
        """Handle SelectOnOff event for polygon layer control."""

        layer = self.poly_view_layer
        if event.state:
            self.add_select_handler(layer, self.polyViewSelect)
            self.pyslip.SetLayerSelectable(layer, True)
        else:
            self.del_select_handler(layer)
            self.pyslip.SetLayerSelectable(layer, False)

    def polyViewSelect(self, event):
        """View-relative polygon select event from the widget.

        event  the event that contains these attributes:
                   type       the type of point selection: single or box
                   selection  tuple (sel, udata, None) defining the selected
                              polygon (if None then no point(s) selected)

        The selection could be a single or box select.
        """

        selection = event.selection

        # point select, turn any previous selection off
        if self.sel_poly_view_layer:
            self.pyslip.DeleteLayer(self.sel_poly_view_layer)
            self.sel_poly_view_layer = None

        # for box OR single selection
        if selection:
            # get selected polygon points into form for point display layer
            points = []
            for (poly, d) in selection:
                try:
                    del d['colour']
                except KeyError:
                    pass
                try:
                    del d['radius']
                except KeyError:
                    pass
                for (x, y) in poly:
                    points.append((x, y, d))

            self.sel_poly_view_layer = \
                self.pyslip.AddPointLayer(points, map_rel=False,
                                          colour='#ff00ff',
                                          radius=5, visible=True,
                                          show_levels=[3,4],
                                          name='<sel_view_poly>')

        return True

##### map-relative polyline layer

    def polylineOnOff(self, event):
        """Handle OnOff event for map-relative polyline layer control."""

        if event.state:
            self.polyline_layer = \
                self.pyslip.AddPolylineLayer(PolylineData, map_rel=True,
                                             visible=True,
                                             delta=DefaultPolylineMapDelta,
                                             show_levels=MRPolyShowLevels,
                                             name='<polyline_layer>')
        else:
            self.pyslip.DeleteLayer(self.polyline_layer)
            self.polyline_layer = None

            if self.sel_polyline_layer:
                self.pyslip.DeleteLayer(self.sel_polyline_layer)
                self.sel_polyline_layer = None
                self.sel_polyline_point = None
            if self.sel_polyline_layer2:
                self.pyslip.DeleteLayer(self.sel_polyline_layer2)
                self.sel_polyline_layer2 = None

    def polylineShowOnOff(self, event):
        """Handle ShowOnOff event for polycwlinegon layer control."""

        if event.state:
            self.pyslip.ShowLayer(self.polyline_layer)
            if self.sel_polyline_layer:
                self.pyslip.ShowLayer(self.sel_polyline_layer)
            if self.sel_polyline_layer2:
                self.pyslip.ShowLayer(self.sel_polyline_layer2)
        else:
            self.pyslip.HideLayer(self.polyline_layer)
            if self.sel_polyline_layer:
                self.pyslip.HideLayer(self.sel_polyline_layer)
            if self.sel_polyline_layer2:
                self.pyslip.HideLayer(self.sel_polyline_layer2)

    def polylineSelectOnOff(self, event):
        """Handle SelectOnOff event for polyline layer control."""

        layer = self.polyline_layer
        if event.state:
            self.add_select_handler(layer, self.polylineSelect)
            self.pyslip.SetLayerSelectable(layer, True)
        else:
            self.del_select_handler(layer)
            self.pyslip.SetLayerSelectable(layer, False)

    def polylineSelect(self, event):
        """Map- and view-relative polyline select event from the widget.

        event  the event that contains these attributes:
                   type       the type of point selection: single or box
                   selection  [list of] tuple (xgeo,ygeo) of selected point
                              (if None then no point(s) selected)
                   relsel     a tuple (p1,p2) of polyline segment

        The selection could be a single or box select.

        Select a polyline to turn it on, any other polyline selection turns
        it off, unless previous selection again selected.
        """

        # .seletion: [(poly,attr), ...]
        selection = event.selection
        relsel = event.relsel

        # turn any previous selection off
        if self.sel_polyline_layer:
            self.pyslip.DeleteLayer(self.sel_polyline_layer)
            self.sel_polyline_layer = None
        if self.sel_polyline_layer2:
            self.pyslip.DeleteLayer(self.sel_polyline_layer2)
            self.sel_polyline_layer2 = None

        # box OR single selection
        if selection:
            # show segment selected first, if any
            if relsel:
                self.sel_polyline_layer2 = \
                    self.pyslip.AddPointLayer(relsel, map_rel=True,
                                              colour='#40ff40',
                                              radius=5, visible=True,
                                              show_levels=[3,4],
                                              name='<sel_polyline2>')

            # get selected polygon points into form for point display layer
            points = []
            for (poly, d) in selection:
                try:
                    del d['colour']
                except KeyError:
                    pass
                try:
                    del d['radius']
                except KeyError:
                    pass
                for (x, y) in poly:
                    points.append((x, y, d))

            self.sel_polyline_layer = \
                self.pyslip.AddPointLayer(points, map_rel=True,
                                          colour='#ff00ff',
                                          radius=3, visible=True,
                                          show_levels=[3,4],
                                          name='<sel_polyline>')
        return True

##### view-relative polyline layer

    def polylineViewOnOff(self, event):
        """Handle OnOff event for map-relative polyline layer control."""

        if event.state:
            self.polyline_view_layer = \
                self.pyslip.AddPolylineLayer(PolylineViewData, map_rel=False,
                                             delta=DefaultPolylineViewDelta,
                                             name='<polyline_view_layer>',
                                             placement='cn', visible=True,
                                             fontsize=24, colour='#0000ff')
        else:
            self.pyslip.DeleteLayer(self.polyline_view_layer)
            self.polyline_view_layer = None

            if self.sel_polyline_view_layer:
                self.pyslip.DeleteLayer(self.sel_polyline_view_layer)
                self.sel_polyline_view_layer = None
                self.sel_polyline_view_point = None

            if self.sel_polyline_view_layer2:
                self.pyslip.DeleteLayer(self.sel_polyline_view_layer2)
                self.sel_polyline_view_layer2 = None

    def polylineViewShowOnOff(self, event):
        """Handle ShowOnOff event for polyline layer control."""

        if event.state:
            self.pyslip.ShowLayer(self.polyline_view_layer)
            if self.sel_polyline_view_layer:
                self.pyslip.ShowLayer(self.sel_polyline_view_layer)
            if self.sel_polyline_view_layer2:
                self.pyslip.ShowLayer(self.sel_polyline_view_layer2)
        else:
            self.pyslip.HideLayer(self.polyline_view_layer)
            if self.sel_polyline_view_layer:
                self.pyslip.HideLayer(self.sel_polyline_view_layer)
            if self.sel_polyline_view_layer2:
                self.pyslip.HideLayer(self.sel_polyline_view_layer2)

    def polylineViewSelectOnOff(self, event):
        """Handle SelectOnOff event for polyline layer control."""

        layer = self.polyline_view_layer
        if event.state:
            self.add_select_handler(layer, self.polylineViewSelect)
            self.pyslip.SetLayerSelectable(layer, True)
        else:
            self.del_select_handler(layer)
            self.pyslip.SetLayerSelectable(layer, False)

    def polylineViewSelect(self, event):
        """View-relative polyline select event from the widget.

        event  the event that contains these attributes:
                   type       the type of point selection: single or box
                   selection  tuple (sel, udata, None) defining the selected
                              polyline (if None then no point(s) selected)

        The selection could be a single or box select.
        """

        selection = event.selection
        relsel = event.relsel

        # point select, turn any previous selection off
        if self.sel_polyline_view_layer:
            self.pyslip.DeleteLayer(self.sel_polyline_view_layer)
            self.sel_polyline_view_layer = None
        if self.sel_polyline_view_layer2:
            self.pyslip.DeleteLayer(self.sel_polyline_view_layer2)
            self.sel_polyline_view_layer2 = None

        # for box OR single selection
        if selection:
            # first, display selected segment
            if relsel:
                # get original polyline attributes, get placement and offsets
                (_, attributes) = PolylineViewData[0]
                place = attributes.get('placement', None)
                offset_x = attributes.get('offset_x', 0)
                offset_y = attributes.get('offset_y', 0)

                self.sel_polyline_view_layer2 = \
                    self.pyslip.AddPointLayer(relsel, map_rel=False,
                                              placement=place,
                                              offset_x=offset_x,
                                              offset_y=offset_y,
                                              colour='#4040ff',
                                              radius=5, visible=True,
                                              show_levels=[3,4],
                                              name='<sel_view_polyline2>')

            # get selected polyline points into form for point display layer
            points = []
            for (poly, d) in selection:
                try:
                    del d['colour']
                except KeyError:
                    pass
                try:
                    del d['radius']
                except KeyError:
                    pass
                for (x, y) in poly:
                    points.append((x, y, d))

            self.sel_polyline_view_layer = \
                self.pyslip.AddPointLayer(points, map_rel=False,
                                          colour='#ff00ff',
                                          radius=3, visible=True,
                                          show_levels=[3,4],
                                          name='<sel_view_polyline>')

        return True

    def level_change_event(self, event):
        """Handle a "level change" event from the pySlipQt widget.
        
        event.type  the type of event
        event.level  the new map level
        """

        self.map_level.SetValue(str(event.level))

    def mouse_posn_event(self, event):
        """Handle a "mouse position" event from the pySlipQt widget.
       
        The 'event' object has these attributes:
            event.etype  the type of event
            event.mposn  the new mouse position on the map (xgeo, ygeo)
            event.vposn  the new mouse position on the view (x, y)
        """

        if event.mposn:
            (lon, lat) = event.mposn
            # we clamp the lon/lat to zero here since we don't want small
            # negative values displaying as "-0.00"
            if abs(lon) < 0.01:
                lon = 0.0
            if abs(lat) < 0.01:
                lat = 0.0
            self.mouse_position.SetValue('%.2f/%.2f' % (lon, lat))
        else:
            self.mouse_position.SetValue('')

    def select_event(self, event):
        """Handle a single select click, any mouse button.

        event.type       the event type number
        event.mposn      select point tuple in map (geo) coordinates: (xgeo, ygeo)
        event.vposn      select point tuple in view coordinates: (xview, yview)
        event.layer_id   the ID of the layer containing the selected object (or None)
        event.selection  a tuple (x,y,attrib) defining the position of the object selected (or [] if no selection)
        event.data       the user-supplied data object for the selected object (or [] if no selection)
        event.relsel     relative selection point inside a single selected image (or [] if no selection)
        event.button     one of pyslip.MopuseLeft, pyslip.MouseMiddle or pyslip.MouseRight

        Just look at 'event.layer_id' to decide what handler to call and pass
        'event' through to the handler.
        """

        self.demo_select_dispatch.get(event.layer_id, self.null_handler)(event)

    ######
    # Small utility routines
    ######

    def unimplemented(self, msg):
        """Issue an "Sorry, ..." message."""

        self.pyslip.warn('Sorry, %s is not implemented at the moment.' % msg)

    def dump_event(self, msg, event):
        """Dump an event to the log.

        Print attributes and values for non_dunder attributes.
        """

        log('dump_event: %s' % msg)
        for attr in dir(event):
            if not attr.startswith('__'):
                log('    event.%s=%s' % (attr, getattr(event, attr)))

    ######
    # Finish initialization of data, etc
    ######

    def initData(self):
        global PointData, PointDataColour, PointViewDataPlacement
        global PointViewData, PointViewDataColour
        global ImageData
        global ImageViewData
        global TextData
        global TextViewData
        global TextViewDataPlace, TextViewDataOffX, TextViewDataOffY
        global PolyData, PolyViewData
        global PolylineData, PolylineViewData
        global CR_Width, CR_Height

        # create PointData - lots of it to test handling
        PointData = []
        for lon in range(-70, 290+1, 5):
            for lat in range(-65, 65+1, 5):
                udata = 'point(%s,%s)' % (str(lon), str(lat))
                PointData.append((lon, lat, {'data': udata}))
        PointDataColour = '#ff000080'	# semi-transparent

        # create PointViewData - a point-rendition of 'PYSLIP'
        PointViewData = [(-66,-14),(-66,-13),(-66,-12),(-66,-11),(-66,-10),
                         (-66,-9),(-66,-8),(-66,-7),(-66,-6),(-66,-5),(-66,-4),
                         (-66,-3),(-65,-7),(-64,-7),(-63,-7),(-62,-7),(-61,-8),
                         (-60,-9),(-60,-10),(-60,-11),(-60,-12),(-61,-13),
                         (-62,-14),(-63,-14),(-64,-14),(65,-14),            # P
                         (-59,-14),(-58,-13),(-57,-12),(-56,-11),(-55,-10),
                         (-53,-10),(-52,-11),(-51,-12),(-50,-13),(-49,-14),
                         (-54,-9),(-54,-8),(-54,-7),(-54,-6),(-54,-5),
                         (-54,-4),(-54,-3),                                 # Y
                         (-41,-13),(-42,-14),(-43,-14),(-44,-14),(-45,-14),
                         (-46,-14),(-47,-13),(-48,-12),(-48,-11),(-47,-10),
                         (-46,-9),(-45,-9),(-44,-9),(-43,-9),(-42,-8),
                         (-41,-7),(-41,-6),(-41,-5),(-42,-4),(-43,-3),
                         (-44,-3),(-45,-3),(-46,-3),(-47,-3),(-48,-4),      # S
                         (-39,-14),(-39,-13),(-39,-12),(-39,-11),(-39,-10),
                         (-39,-9),(-39,-8),(-39,-7),(-39,-6),(-39,-5),
                         (-39,-4),(-39,-3),(-38,-3),(-37,-3),(-36,-3),
                         (-35,-3),(-34,-3),(-33,-3),(-32,-3),               # L
                         (-29,-14),(-29,-13),(-29,-12),
                         (-29,-11),(-29,-10),(-29,-9),(-29,-8),(-29,-7),
                         (-29,-6),(-29,-5),(-29,-4),(-29,-3),               # I
                         (-26,-14),(-26,-13),(-26,-12),(-26,-11),(-26,-10),
                         (-26,-9),(-26,-8),(-26,-7),(-26,-6),(-26,-5),(-26,-4),
                         (-26,-3),(-25,-7),(-24,-7),(-23,-7),(-22,-7),(-21,-8),
                         (-20,-9),(-20,-10),(-20,-11),(-20,-12),(-21,-13),
                         (-22,-14),(-23,-14),(-24,-14),(25,-14)]            # P
        PointViewDataColour = '#00000040'	# transparent
        PointViewDataPlacement = 'se'

        # create image data - shipwrecks off the Australian east coast
        ImageData = [# Agnes Napier - 1855
                     (160.0, -30.0, ShipImg, {'placement': 'cc'}),
                     # Venus - 1826
                     (145.0, -11.0, ShipImg, {'placement': 'ne'}),
                     # Wolverine - 1879
                     (156.0, -23.0, ShipImg, {'placement': 'nw'}),
                     # Thomas Day - 1884
                     (150.0, -15.0, ShipImg, {'placement': 'sw'}),
                     # Sybil - 1902
                     (165.0, -19.0, ShipImg, {'placement': 'se'}),
                     # Prince of Denmark - 1863
                     (158.55, -19.98, ShipImg),
                     # Moltke - 1911
                     (146.867525, -19.152185, ShipImg)
                    ]
        ImageData2 = []
        ImageData3 = []
        ImageData4 = []
        ImageData5 = []
        ImageData6 = []
        self.map_level_2_img = {0: ImageData2,
                                1: ImageData3,
                                2: ImageData4,
                                3: ImageData5,
                                4: ImageData6}
        self.map_level_2_selimg = {0: SelGlassyImg2,
                                   1: SelGlassyImg3,
                                   2: SelGlassyImg4,
                                   3: SelGlassyImg5,
                                   4: SelGlassyImg6}
        self.current_layer_img_layer = None

        ImageViewData = [(0, 0, CompassRoseGraphic, {'placement': 'ne',
                                                     'data': 'compass rose'})]

        text_placement = {'placement': 'se'}
        transparent_placement = {'placement': 'se', 'colour': '#00000040'}
        capital = {'placement': 'se', 'fontsize': 14, 'colour': 'red',
                   'textcolour': 'red'}
        capital_sw = {'placement': 'sw', 'fontsize': 14, 'colour': 'red',
                      'textcolour': 'red'}
        TextData = [
                    (151.20, -33.85, 'Sydney', text_placement),
                    (144.95, -37.84, 'Melbourne', {'placement': 'ce'}),
                    (153.08, -27.48, 'Brisbane', text_placement),
                    (115.86, -31.96, 'Perth', transparent_placement),
                    (138.30, -35.52, 'Adelaide', text_placement),
                    (130.98, -12.61, 'Darwin', text_placement),
                    (147.31, -42.96, 'Hobart', text_placement),
                    (174.75, -36.80, 'Auckland', text_placement),
                    (174.75, -41.29, 'Wellington', capital),
                    (172.61, -43.51, 'Christchurch', text_placement),
                    (168.74, -45.01, 'Queenstown', text_placement),
                    (147.30, -09.41, 'Port Moresby', capital),
                    (143.1048, -5.4646, 'Porgera', text_placement),
                    (103.833333, 1.283333, 'Singapore', capital),
                    (101.683333, 3.133333, 'Kuala Lumpur', capital_sw),
                    (106.822922, -6.185451, 'Jakarta', capital),
                    (110.364444, -7.801389, 'Yogyakarta', text_placement),
                    (121.050, 14.600, 'Manila', capital),
                    (271.74, +40.11, 'Champaign', text_placement),
                    (160.0, -30.0, 'Agnes Napier - 1855',
                        {'placement': 'cw', 'offset_x': 20, 'colour': 'green'}),
                    (145.0, -11.0, 'Venus - 1826',
                        {'placement': 'sw', 'colour': 'green'}),
                    (156.0, -23.0, 'Wolverine - 1879',
                        {'placement': 'ce', 'colour': 'green'}),
                    (150.0, -15.0, 'Thomas Day - 1884',
                        {'colour': 'green'}),
                    (165.0, -19.0, 'Sybil - 1902',
                        {'placement': 'cw', 'colour': 'green'}),
                    (158.55, -19.98, 'Prince of Denmark - 1863',
                        {'placement': 'nw', 'offset_x': 20, 'colour': 'green'}),
                    (146.867525, -19.152182, 'Moltke - 1911',
                        {'placement': 'ce', 'offset_x': 20, 'colour': 'green'}),
                   ]
        if sys.platform != 'win32':
            # TODO: check if this works under Windows
            TextData.extend([
                    (110.490, 24.780, '阳朔县 (Yangshuo)', {'placement': 'sw'}),
                    (117.183333, 39.133333, '天津市 (Tianjin)', {'placement': 'sw'}),
                    (106.36, +10.36, 'Mỹ Tho', {'placement': 'ne'}),
                    (105.85, +21.033333, 'Hà Nội', capital),
                    (109.18333, 12.25, 'Nha Trang', {'placement': 'sw'}),
                    (106.681944, 10.769444, 'Thành phố Hồ Chí Minh',
                        {'placement': 'sw'}),
                    (132.47, +34.44, '広島市 (Hiroshima City)',
                        {'placement': 'nw'}),
                    (114.000, +22.450, '香港 (Hong Kong)', text_placement),
                    (98.392, 7.888, 'ภูเก็ต (Phuket)', text_placement),
                    ( 96.16, +16.80, 'ရန်ကုန် (Yangon)', capital),
                    (104.93, +11.54, ' ភ្នំពេញ (Phnom Penh)', capital),
                    (100.49, +13.75, 'กรุงเทพมหานคร (Bangkok)', capital),
                    ( 77.56, +34.09, 'གླེ་(Leh)', text_placement),
                    (84.991275, 24.695102, 'बोधगया (Bodh Gaya)', text_placement)
                        ])

        TextViewData = [(0, 0, '%s %s' % (DemoName, DemoVersion))]
        TextViewDataPlace = 'cn'
        TextViewDataOffX = 0
        TextViewDataOffY = 3

        PolyData = [(((150.0,10.0),(160.0,20.0),(170.0,10.0),(165.0,0.0),(155.0,0.0)),
                      {'width': 3, 'colour': 'blue', 'closed': True}),
                    (((165.0,-35.0),(175.0,-35.0),(175.0,-45.0),(165.0,-45.0)),
                      {'width': 10, 'colour': '#00ff00c0', 'filled': True,
                       'fillcolour': '#ffff0040'}),
                    (((190.0,-30.0),(220.0,-50.0),(220.0,-30.0),(190.0,-50.0)),
                      {'width': 3, 'colour': 'green', 'filled': True,
                       'fillcolour': 'yellow'}),
                    (((190.0,+50.0),(220.0,+65.0),(220.0,+50.0),(190.0,+65.0)),
                      {'width': 10, 'colour': '#00000040'})]

        PolyViewData = [(((230,0),(230,40),(-230,40),(-230,0)),
                        {'width': 3, 'colour': '#00ff00ff', 'closed': True,
                         'placement': 'cn', 'offset_y': 1})]

        PolylineData = [(((150.0,10.0),(160.0,20.0),(170.0,10.0),(165.0,0.0),(155.0,0.0)),
                          {'width': 3, 'colour': 'blue'}),
                        (((185.0,10.0),(185.0,20.0),(180.0,10.0),(175.0,0.0),(185.0,0.0)),
                          {'width': 3, 'colour': 'red'})]

        PolylineViewData = [(((50,100),(100,50),(150,100),(100,150)),
                            {'width': 3, 'colour': '#00ffffff', 'placement': 'cn'}),
                            (((100,250),(50,300),(100,350),(150,300)),
                            {'width': 3, 'colour': '#0000ffff', 'placement': 'cn'})]

        # define layer ID variables & sub-checkbox state variables
        self.point_layer = None
        self.sel_point_layer = None
        self.sel_point = None

        self.point_view_layer = None
        self.sel_point_view_layer = None
        self.sel_point_view = None

        self.image_layer = None
        self.sel_image_layer = None
        self.sel_image = None

        self.image_view_layer = None
        self.sel_image_view_layer = None
        self.sel_image_view = None
        self.sel_imagepoint_view_layer = None

        self.text_layer = None
        self.sel_text_layer = None
        self.sel_text = None

        self.text_view_layer = None
        self.sel_text_view_layer = None

        self.poly_layer = None
        self.sel_poly_layer = None
        self.sel_poly = None

        self.poly_view_layer = None
        self.sel_poly_view_layer = None
        self.sel_poly = None

        self.polyline_layer = None
        self.sel_polyline_layer = None
        self.sel_polyline_layer2 = None
        self.sel_polyline = None

        self.polyline_view_layer = None
        self.sel_polyline_view_layer = None
        self.sel_polyline_view_layer2 = None
        self.sel_polyline = None

        # get width and height of the compass rose image
        cr_img = wx.Image(CompassRoseGraphic, wx.BITMAP_TYPE_ANY)
        cr_bmap = cr_img.ConvertToBitmap()
        (CR_Width, CR_Height) = cr_bmap.GetSize()

        # force pyslip initialisation
        self.pyslip.OnSize()    # required?

        # set initial view position
        self.map_level.SetLabel('%d' % InitViewLevel)
        wx.CallLater(25, self.final_setup, InitViewLevel, InitViewPosition)

    def final_setup(self, level, position):
        """Perform final setup.

        level     zoom level required
        position  position to be in centre of view

        We do this in a CallLater() function for those operations that
        must not be done while the GUI is "fluid".
        """

        self.pyslip.GotoLevelAndPosition(level, position)

    ######
    # Exception handlers
    ######

    def null_handler(self, event):
        """Routine to handle unexpected events."""

        print('ERROR: null_handler!?')
        log('ERROR: null_handler!?')

    ######
    # Handle adding/removing select handler functions.
    ######

    def add_select_handler(self, id, handler):
        """Add handler for select in layer 'id'."""

        self.demo_select_dispatch[id] = handler

    def del_select_handler(self, id):
        """Remove handler for select in layer 'id'."""

        del self.demo_select_dispatch[id]

    ######
    # Popup a small window with some text.
    ######

    def show_popup(self, text, posn):
        """Display a popup with some text.
        
        text  the text to display
        posn  position (x, y) of the top-left corner of the popup, view coords

        Tries to always draw the popup fully on the widget.
        """

        # create popup window, get size
        popup = DemoPopup(self.GetTopLevelParent(), wx.SIMPLE_BORDER, text)
        (pop_width, pop_height) = popup.GetSize()

        # get pySlip widget size and app position on screen
        (pyslip_width, pyslip_height) = self.pyslip.GetSize()
        screen_posn = self.ClientToScreen((0, 0))

        # assume the popup is displayed in the top-left quarter of the view
        # we want the top-left popup corner over the click point
        x_adjusted = posn.x                     # assume popup displays to right
        y_adjusted = posn.y                     # assume popup displays down

        if posn.x >= pyslip_width//2:
            # click in right half of widget, popup goes to the left
            x_adjusted = posn.x - pop_width
        if posn.y >= pyslip_height//2:
            # click in bottom half of widget, popup goes up
            y_adjusted = posn.y - pop_height

        popup.Position(screen_posn, (x_adjusted, y_adjusted))

        # move popup to final position and show it
        popup.Show(True)

###############################################################################
# Main code
###############################################################################

def usage(msg=None):
    if msg:
        print(('*'*80 + '\n%s\n' + '*'*80) % msg)
    print(__doc__)

# our own handler for uncaught exceptions
def excepthook(type, value, tback):
    msg = '\n' + '=' * 80
    msg += '\nUncaught exception:\n'
    msg += ''.join(traceback.format_exception(type, value, tback))
    msg += '=' * 80 + '\n'
    log(msg)
    print(msg)
    sys.exit(1)

# plug our handler into the python system
sys.excepthook = excepthook

# parse the CLI params
argv = sys.argv[1:]

try:
    (opts, args) = getopt.getopt(argv, 'd:hx',
                                 ['debug=', 'help', 'inspector'])
except getopt.error:
    usage()
    sys.exit(1)

debug = 10
inspector = False

for (opt, param) in opts:
    if opt in ['-d', '--debug']:
        debug = param
    elif opt in ['-h', '--help']:
        usage()
        sys.exit(0)
    elif opt == '-x':
        inspector = True

# convert any symbolic debug level to a number
try:
    debug = int(debug)
except ValueError:
    # possibly a symbolic debug name
    try:
        debug = LogSym2Num[debug.upper()]
    except KeyError:
        usage('Unrecognized debug name: %s' % debug)
        sys.exit(1)
log.set_level(debug)

# start wxPython app
app = wx.App()
app_frame = AppFrame()
app_frame.Show()

if inspector:
    import wx.lib.inspection
    wx.lib.inspection.InspectionTool().Show()

app.MainLoop()

