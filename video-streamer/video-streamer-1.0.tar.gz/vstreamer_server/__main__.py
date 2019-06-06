import sys

import dbus
import dbus.bus
import dbus.mainloop.glib
import gi

import vstreamer_utils
from vstreamer_server import application, server

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst


def main():
    Gst.init(None)
    Gst.debug_set_active(True)
    Gst.debug_set_default_threshold(3)

    glib_loop = GLib.MainLoop()
    dbus_loop = dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    app = application.VideoStreamerServerApplication(sys.argv)

    session_bus = dbus.SessionBus()
    if session_bus.request_name(
            vstreamer_utils.DBUS_NAME) != dbus.bus.REQUEST_NAME_REPLY_PRIMARY_OWNER:
        app.logger.error("Application already running")
        return 1
    server_controller = server.ServerController(session_bus)

    server_controller.start()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
