"""
Overide the wxpython StaticBox to provide our own style.
"""

import wx


class AppStaticBox(wx.StaticBox):
    def __init__(self, parent, label, *args, **kwargs):
        if 'style' not in kwargs:
            kwargs['style'] = wx.NO_BORDER
        wx.StaticBox.__init__(self, parent, wx.ID_ANY, label, *args, **kwargs)
