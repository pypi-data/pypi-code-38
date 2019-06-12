# encoding: utf-8

import logging_helper
import pyperclip
import requests
import pickle
from uiutil.tk_names import NORMAL, W, EW, NSEW
from uiutil import RootWindow, BaseFrame, ChildWindow, Button, TextEntry, Label

logging = logging_helper.setup_logging()


class RequestPicklerFrame(BaseFrame):
    def __init__(self,
                 *args,
                 **kwargs):

        BaseFrame.__init__(self, *args, **kwargs)

        self.grid(sticky=EW)

        Label(text=u'Pickler:',
              width=10,
              sticky=W)

        Label(text=u'URI:',
              width=10,
              sticky=W,
              row=self.row.next())

        self.uri = TextEntry(frame=self,
                             width=50,
                             column=self.column.next(),
                             sticky=EW,
                             tooltip=u"Enter the url of the request you'd like to pickle")

        Button(state=NORMAL,
               text=u"Pickle",
               width=8,
               sticky=EW,
               column=self.column.next(),
               command=self.pickle_uri_and_copy_to_clipboard,
               tooltip=u'Pickle the request and\n'
                       u'copy the pickled string\n'
                       u'to the clipboard.')

        self.nice_grid()

    def pickle_uri_and_copy_to_clipboard(self):
        try:
            pyperclip.copy(pickle.dumps(requests.get(self.uri.value)))

        except Exception:
            pass
            # TODO: Show dialog

    def cancel(self):
        self.parent.master.exit()


class RequestPicklerWindow(ChildWindow):

    def __init__(self,
                 *args,
                 **kwargs):

        super(RequestPicklerWindow, self).__init__(*args, **kwargs)

    def _draw_widgets(self,
               *args,
               **kwargs):
        self.title(u"Request Pickler")

        self.config = RequestPicklerFrame(parent=self._main_frame)
        self.config.grid(sticky=NSEW)

    #def close(self):
    #    self.config.cancel()


class StandaloneRequestPicklerFrame(RootWindow):
    def __init__(self, *args, **kwargs):
        super(StandaloneRequestPicklerFrame, self).__init__(*args, **kwargs)

    def _draw_widgets(self):

        self.title(u"Test Pickler Frame")

        RequestPicklerFrame(parent=self._main_frame)


if __name__ == u'__main__':
    StandaloneRequestPicklerFrame()
