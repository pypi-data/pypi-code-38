#!python
import sys

import dbus
import dbus.bus

import vstreamer_utils


def main():
    if len(sys.argv) != 5:
        print("%s: invalid number of arguments (%d/%d)" % (sys.argv[0], len(sys.argv) - 1, 4),
              file=sys.stderr)
        return 1
    file = sys.argv[1]
    title = sys.argv[2]
    description = sys.argv[3]
    image_file = sys.argv[4]

    session_bus = dbus.SessionBus()
    if session_bus.request_name(
            vstreamer_utils.DBUS_NAME) == dbus.bus.REQUEST_NAME_REPLY_PRIMARY_OWNER:
        print("%s: video_streamer_server is not running" % sys.argv[0], file=sys.stderr)
        return 1

    remote_object = session_bus.get_object(vstreamer_utils.DBUS_NAME, "/ServerController")
    server_controller = dbus.Interface(remote_object, vstreamer_utils.DBUS_NAME)

    if server_controller.set_additional_properties(file, title, description, image_file):
        print("Operation succeeded")
        return 0
    else:
        print("Operation failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
