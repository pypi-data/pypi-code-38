import sys

from PySide2 import QtCore

import vstreamer_utils
from vstreamer import application, client


def main():
    app = application.VideoStreamerApplication(sys.argv)

    error_handler = vstreamer_utils.ErrorHandler(vstreamer_utils.ErrorHandlerType.GUI_HANDLER, app)

    try:
        main_window = client.MainWindow()
    except Exception as exc:
        error_handler.handle_exception(exc)
        return 1

    QtCore.QTimer.singleShot(0, main_window.connect_to_server)
    app.exec_()


if __name__ == "__main__":
    sys.exit(main())
