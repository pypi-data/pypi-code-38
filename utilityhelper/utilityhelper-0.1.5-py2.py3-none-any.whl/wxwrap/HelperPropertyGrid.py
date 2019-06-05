import wx

WX_VERSION = wx.__version__

if WX_VERSION >= '4':
    from ._wx4PropertyGrid import *
else:
    from ._wx3PropertyGrid import *


if __name__ == '__main__':
    class MyApp(wx.App):
        def OnInit(self):
            self.frame = Frame(None)
            self.SetTopWindow(self.frame)
            self.frame.Show()

            return True


    class Frame(wx.Frame):
        def __init__(self, parent):
            wx.Frame.__init__(self, parent, size = wx.Size( 800,600 ), style = wx.DEFAULT_FRAME_STYLE|wx.MAXIMIZE|wx.TAB_TRAVERSAL)

            bSizer23 = wx.BoxSizer(wx.VERTICAL)

            bSizer24 = wx.BoxSizer(wx.VERTICAL)

            self.m_textCtrl25 = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE)

            #test panel
            self.m_panel1 = TestPanel(self, self.m_textCtrl25)

            bSizer24.Add(self.m_panel1, 1, wx.EXPAND | wx.ALL, 5)

            bSizer23.Add(bSizer24, 1, wx.EXPAND, 5)

            bSizer26 = wx.BoxSizer(wx.VERTICAL)

            bSizer26.Add(self.m_textCtrl25, 1, wx.ALL | wx.EXPAND, 5)

            bSizer23.Add(bSizer26, 1, wx.EXPAND, 5)

            self.SetSizer(bSizer23)
            self.Layout()

            self.Centre(wx.BOTH)
            self.Show()

    app = MyApp()
    app.MainLoop()

