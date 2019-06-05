#coding:utf-8

from utilityhelper.loggingHelper import *

if __name__ == '__main__':
    import wx

    class MyFrame(wx.Frame):
        def __init__(self, parent, title):
            wx.Frame.__init__(self, parent, -1, title)
            self.textctrl = wx.TextCtrl(self, style=wx.TE_MULTILINE)
            self.Show()

        def write(self, s):
            self.textctrl.AppendText(s)


    app = wx.App(False)
    frame = MyFrame(None, 'logging demo')

    fmt = '[%(levelname)s] - %(asctime)s - %(name)s - %(message)s'

    log1 = LogManger.getLogger()
    log2 = LogManger.getLogger("XYZ")
    log3 = LogManger.getLogger("XYZT.MNT")

    LogManger.addHandler((log1,), HANDLER_TYPE_STREAM, "DEBUG", fmt)

    LogManger.addHandler((log2,), HANDLER_TYPE_WINDOW, "DEBUG", fmt, window=frame.textctrl)

    LogManger.addHandler((log3,), HANDLER_TYPE_FILE, "ERROR", fmt,
                         filename="log.txt", mode='a', backup_count=5, limit=20480, when=None)

    # LogManger.addHandler((log3,), HANDLER_TYPE_STREAM, "ERROR", fmt)
    # LogManger.addHandler("SMTP", "DEBUG", fmt,
    #                      mailhost="smtp.qiye.163.com",
    #                      fromaddr="",#'raAutosender@163.com',
    #                      toaddrs ='',
    #                      subject='',
    #                      credentials = ('emailaddr', 'password')
    #                      #credentials = ('raAutosender@163.com', 'password'))
    #                      )
    for log in g_logger:
        print("logger=", log, "logger.handers=", log.handlers)

    log1.info("log1 info")
    log2.info("log2 info")
    log1.error("log1 UNICODE中文")
    log2.warning("log2 waring")
    log2.error("log2 error")
    # log2.error(u"log2 UNICODE中文")
    log3.error("log3 error")
    log3.error("log3 UNICODE中文")
    log3.error("log3 GBK中文")

    app.MainLoop()