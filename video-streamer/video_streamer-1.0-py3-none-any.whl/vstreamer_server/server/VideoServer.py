import urllib.parse

import gi
from PySide2 import QtCore

import vstreamer_utils

gi.require_version("GstRtspServer", "1.0")
from gi.repository import GstRtspServer


class VideoServer(QtCore.QObject):
    def __init__(self, port, directory_tree, parent=None):
        super().__init__(parent)
        self.port = int(port)
        self.server = GstRtspServer.RTSPServer.new()
        self.server.set_service(str(self.port))

        for _, directory_info in directory_tree.directories.items():
            for file_entry in directory_info.entries:
                if file_entry.is_video():
                    self._add_media(file_entry.path, directory_tree.directory_root)
        vstreamer_utils.log_info("Initialized video server")

    def _add_media(self, file_path, directory_root):
        file = directory_root / file_path[1:]
        if not vstreamer_utils.is_video_file(file):
            raise ValueError("'%s' is not a valid video file" % str(file))

        demuxer = VideoServer._corresponding_demuxer(file)
        pipeline = "filesrc location=\"%s\" ! %s name=dmux " \
                   "dmux.video_0 ! queue ! rtph264pay name=pay0 pt=96 " \
                   "dmux.audio_0 ! queue ! rtpmp4apay name=pay1" % (file, demuxer)
        factory = GstRtspServer.RTSPMediaFactory()
        factory.set_launch(pipeline)
        factory.set_shared(True)
        encoded = urllib.parse.quote(file_path)
        self.server.get_mount_points().add_factory(encoded, factory)
        vstreamer_utils.log_info("Added '%s' to video server mount points" % str(file_path))

    def start(self, context=None):
        self.server.attach(context)
        vstreamer_utils.log_info("Started listening for rtsp connections on port %d" % self.port)

    @staticmethod
    def _corresponding_demuxer(file):
        if file.suffix == ".mkv":
            return "matroskademux"
        if file.suffix == ".mp4":
            return "qtdemux"
        raise ValueError("'%s' is not a valid container" % str(file))
