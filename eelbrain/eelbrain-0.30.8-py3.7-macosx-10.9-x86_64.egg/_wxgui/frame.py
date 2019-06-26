import wx

from .._utils import IS_OSX
from . import ID

FOCUS_UI_UPDATE_FUNC_NAMES = {
    wx.ID_COPY: 'CanCopy',
    ID.COPY_AS_PNG: 'CanCopyPNG',
    wx.ID_CUT: 'CanCut',
    wx.ID_PASTE: 'CanPaste',
}


class EelbrainWindow:
    # Frame subclass to support UI Update

    def OnWindowIconize(self, event):
        self.Iconize()

    def OnWindowZoom(self, event):
        self.Maximize()

    def OnUpdateUIBackward(self, event):
        event.Enable(False)

    def OnUpdateUIClear(self, event):
        event.Enable(False)

    def OnUpdateUIClose(self, event):
        event.Enable(True)

    def OnUpdateUIDown(self, event):
        event.Enable(True)

    def OnUpdateUIDrawCrosshairs(self, event):
        event.Enable(False)
        event.Check(False)

    def OnUpdateUIForward(self, event):
        event.Enable(False)

    def OnUpdateUIFocus(self, event):
        func_name = FOCUS_UI_UPDATE_FUNC_NAMES[event.GetId()]
        win = self.FindFocus()
        func = getattr(win, func_name, None)
        if func is None:
            func = getattr(self, func_name, None)
            if func is None:
                event.Enable(False)
                return
        event.Enable(func())

    def OnUpdateUIOpen(self, event):
        event.Enable(False)

    def OnUpdateUIRedo(self, event):
        event.Enable(False)

    def OnUpdateUISave(self, event):
        event.Enable(False)

    def OnUpdateUISaveAs(self, event):
        event.Enable(False)

    def OnUpdateUISetLayout(self, event):
        event.Enable(False)

    def OnUpdateUISetMarkedChannels(self, event):
        event.Enable(False)

    def OnUpdateUISetVLim(self, event):
        event.Enable(False)

    def OnUpdateUISetTime(self, event):
        event.Enable(False)

    def OnUpdateUITools(self, event):
        event.Enable(hasattr(self, 'MakeToolsMenu'))

    def OnUpdateUIUndo(self, event):
        event.Enable(False)

    def OnUpdateUIUp(self, event):
        event.Enable(False)


class EelbrainFrame(wx.Frame, EelbrainWindow):
    _allow_user_set_title = False

    def __init__(self, parent=None, id=wx.ID_ANY, title="", pos=wx.DefaultPosition, *args, **kwargs):
        wx.Frame.__init__(self, parent, id, title, pos, *args, **kwargs)
        if not IS_OSX:
            from .app import get_app
            self.SetMenuBar(get_app().CreateMenu(self))
        self._title = self.GetTitle()

    def OnClear(self, event):
        raise RuntimeError(str(self))

    def OnCopy(self, event):
        win = wx.Window.FindFocus()
        if hasattr(win, 'CanCopy'):
            return win.Copy()
        elif hasattr(self, 'CanCopy'):
            return self.Copy()
        else:
            event.Skip()

    def OnDrawCrosshairs(self, event):
        raise RuntimeError(str(self))

    def OnOpen(self, event):
        raise RuntimeError(str(self))

    def OnRedo(self, event):
        raise RuntimeError(str(self))

    def OnSave(self, event):
        raise RuntimeError(str(self))

    def OnSaveAs(self, event):
        raise RuntimeError(str(self))

    def OnSetVLim(self, event):
        raise RuntimeError(str(self))

    def OnSetLayout(self, event):
        raise RuntimeError(str(self))

    def OnSetMarkedChannels(self, event):
        raise RuntimeError(str(self))

    def OnSetTime(self, event):
        raise RuntimeError(str(self))

    def OnSetWindowTitle(self, event):
        dlg = wx.TextEntryDialog(self, f"New title for '{self._title}':", "Set Window Title", value=self._title)
        if dlg.ShowModal() == wx.ID_OK:
            self._title = dlg.GetValue()
            self.SetTitle(self._title)
        dlg.Destroy()

    def OnUndo(self, event):
        raise RuntimeError(str(self))

    def OnWindowClose(self, event):
        self.Close()

    def SetTitleSuffix(self, suffix):
        self.SetTitle(self._title + suffix)


class EelbrainDialog(wx.Dialog, EelbrainWindow):

    pass
