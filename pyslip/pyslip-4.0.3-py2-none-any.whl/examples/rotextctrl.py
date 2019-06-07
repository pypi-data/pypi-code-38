"""
Overide the wxpython TextCtrl to provide our own "read only" style.
"""

import wx


class ROTextCtrl(wx.TextCtrl):
    """Override the wx.TextCtrl widget to get read-only text control which
    has a distinctive background colour.
    """

    # background colour for the 'read-only' text field
    ReadonlyBGColour = '#ffffcc'

    def __init__(self, parent, value, tooltip='', *args, **kwargs):
        wx.TextCtrl.__init__(self, parent, wx.ID_ANY, value=value,
                             style=wx.TE_READONLY, *args, **kwargs)
        self.SetBackgroundColour(ROTextCtrl.ReadonlyBGColour)
        self.SetToolTip(wx.ToolTip(tooltip))

