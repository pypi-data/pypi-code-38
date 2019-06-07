"""
Custom LayerControl widget.

This is used to control each type of layer, whether map- or view-relative.
The layout is:

    + Title text ------------------------------+
    |  +--+                                    |
    |  |  | Add layer                          |
    |  +--+                                    |
    |                                          |
    |       +--+          +--+                 |
    |       |  | Show     |  | Select          |
    |       +--+          +--+                 |
    |                                          |
    +------------------------------------------+

Constructor:

    lc = LayerControl(parent, title, selectable=False, tooltip=None):

Methods:

    lc.set_show(state)      set 'show' checkbox to 'state'
    lc.set_select(state)    set 'select' checkbox to 'state'

Events:

    .change_add      the "add layer" checkbox was toggled
    .change_show     the "show" checkbox was toggled
    .change_select   the "select" checkbox was toggled
"""

import wx
from appstaticbox import AppStaticBox
import pyslip
import pyslip.gmt_local as tiles
import pyslip.log as log

PackBorder = 1    # should come from wxpython?

###############################################################################
# Class for a LayerControl widget.
#
# This is used to control each type of layer, whether map- or view-relative.
###############################################################################

myEVT_ONOFF = wx.NewEventType()
myEVT_SHOWONOFF = wx.NewEventType()
myEVT_SELECTONOFF = wx.NewEventType()

EVT_ONOFF = wx.PyEventBinder(myEVT_ONOFF, 1)
EVT_SHOWONOFF = wx.PyEventBinder(myEVT_SHOWONOFF, 1)
EVT_SELECTONOFF = wx.PyEventBinder(myEVT_SELECTONOFF, 1)

class LayerControlEvent(wx.PyCommandEvent):
    """Event sent when a LayerControl is changed."""

    def __init__(self, eventType, id):
        wx.PyCommandEvent.__init__(self, eventType, id)


class LayerControl(wx.Panel):

    def __init__(self, parent, title, selectable=False, editable=False,
                 **kwargs):
        """Initialise a LayerControl instance.

        parent      reference to parent object
        title       text to ahow in static box outline
        selectable  True if 'selectable' checkbox is to be displayed
        editable    True if layer can be edited
        **kwargs    keyword args for Panel
        """

        # create and initialise the base panel
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY, **kwargs)
        self.SetBackgroundColour(wx.WHITE)

        self.selectable = selectable
        self.editable = editable

        box = AppStaticBox(self, title)
        sbs = wx.StaticBoxSizer(box, orient=wx.VERTICAL)
        gbs = wx.GridBagSizer(vgap=0, hgap=0)

        self.cbx_onoff = wx.CheckBox(self, wx.ID_ANY, label='Add layer')
        gbs.Add(self.cbx_onoff, (0,0), span=(1,4), border=PackBorder)

        self.cbx_show = wx.CheckBox(self, wx.ID_ANY, label='Show')
        gbs.Add(self.cbx_show, (1,1), border=PackBorder)
        self.cbx_show.Disable()

        if selectable:
            self.cbx_select = wx.CheckBox(self, wx.ID_ANY, label='Select')
            gbs.Add(self.cbx_select, (1,2), border=PackBorder)
            self.cbx_select.Disable()

        if editable:
            self.cbx_edit = wx.CheckBox(self, wx.ID_ANY, label='Edit')
            gbs.Add(self.cbx_edit, (1,3), border=PackBorder)
            self.cbx_edit.Disable()

        sbs.Add(gbs)
        self.SetSizer(sbs)
        sbs.Fit(self)

        # tie handlers to change events
        self.cbx_onoff.Bind(wx.EVT_CHECKBOX, self.onChangeOnOff)
        self.cbx_show.Bind(wx.EVT_CHECKBOX, self.onChangeShowOnOff)
        if selectable:
            self.cbx_select.Bind(wx.EVT_CHECKBOX, self.onChangeSelectOnOff)
#        if editable:
#            self.cbx_edit.Bind(wx.EVT_CHECKBOX, self.onChangeEditOnOff)

    def onChangeOnOff(self, event):
        """Main checkbox changed."""

        event = LayerControlEvent(myEVT_ONOFF, self.GetId())
        event.state = self.cbx_onoff.IsChecked()
        self.GetEventHandler().ProcessEvent(event)

        if self.cbx_onoff.IsChecked():
            self.cbx_show.Enable()
            self.cbx_show.SetValue(True)
            if self.selectable:
                self.cbx_select.Enable()
                self.cbx_select.SetValue(False)
            if self.editable:
                self.cbx_edit.Enable()
                self.cbx_edit.SetValue(False)
        else:
            self.cbx_show.Disable()
            if self.selectable:
                self.cbx_select.Disable()
            if self.editable:
                self.cbx_edit.Disable()

    def onChangeShowOnOff(self, event):
        """Show checkbox changed."""

        event = LayerControlEvent(myEVT_SHOWONOFF, self.GetId())
        event.state = self.cbx_show.IsChecked()
        self.GetEventHandler().ProcessEvent(event)

    def onChangeSelectOnOff(self, event):
        """Select checkbox changed."""

        event = LayerControlEvent(myEVT_SELECTONOFF, self.GetId())
        if self.selectable:
            event.state = self.cbx_select.IsChecked()
        else:
            event_state = False
        self.GetEventHandler().ProcessEvent(event)

