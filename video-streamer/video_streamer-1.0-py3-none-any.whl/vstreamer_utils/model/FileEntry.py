import abc
import collections
import copy
import datetime
import pathlib
import time

import pymediainfo

import vstreamer_utils
from vstreamer_utils import model


class FileEntry(abc.ABC):
    def __new__(cls, file=None, directory_root=None):
        # if called from subclass call default implementation
        if cls is not FileEntry:
            return super().__new__(cls)

        # if called from FileEntry class return selected subclass (factory)
        if pathlib.Path(file).is_dir():
            return super().__new__(DirectoryEntry)
        return super().__new__(VideoFileEntry)

    def __init__(self, file, directory_root):
        file = pathlib.Path(file)
        directory_root = pathlib.Path(directory_root)
        stat = file.stat()

        self.filename = str(file.name)
        self.path = "/" + str(file.relative_to(directory_root))
        self.size = stat.st_size
        self.creation_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_ctime))
        self.modification_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime))

        # additional
        self.description = None
        self.image = None

        self.properties = collections.OrderedDict()
        self.other_properties = collections.OrderedDict()

        self.properties["Filename"] = self.filename
        self.properties["Path"] = self.path
        self.properties["Size"] = vstreamer_utils.size_to_string(self.size)
        self.properties["Creation Time"] = self.creation_time
        self.properties["Modification Time"] = self.modification_time

    @abc.abstractmethod
    def is_video(self):
        ...

    def light_copy(self):
        copied = copy.copy(self)
        copied.description = None
        copied.image = None
        return copied

    def additional_properties(self):
        return model.AdditionalEntryProperties.from_file_entry(self)

    def apply_additional_properties(self, additional_properties):
        if additional_properties.title is None:
            self.properties["Filename"] = self.filename
        else:
            self.properties["Filename"] = additional_properties.title
        self.description = additional_properties.description
        self.image = additional_properties.image


class DirectoryEntry(FileEntry):
    def __init__(self, file, directory_root):
        super().__init__(file, directory_root)
        file = pathlib.Path(file)
        if not file.is_dir():
            raise ValueError("'%s' is not a directory" % str(file))

        # zero size for directories
        self.size = 0
        self.properties["Size"] = "0B"

        self.properties["Type"] = "Directory"

        subdirectories, video_files = DirectoryEntry._file_count(file)
        self.other_properties["File Count"] = str(subdirectories + video_files)
        self.other_properties["Subdirectories"] = str(subdirectories)
        self.other_properties["Video Files"] = str(video_files)
        vstreamer_utils.log_info("Created DirectoryEntry for '%s'" % self.path)

    def is_video(self):
        return False

    @staticmethod
    def _file_count(directory):
        directories = 0
        video_files = 0
        for file in directory.iterdir():
            if file.is_dir():
                directories += 1
            elif vstreamer_utils.is_video_file(file):
                video_files += 1
        return directories, video_files


class VideoFileEntry(FileEntry):
    def __init__(self, file, directory_root):
        super().__init__(file, directory_root)
        file = pathlib.Path(file)
        if not vstreamer_utils.is_video_file(file):
            raise ValueError("'%s' is not a video file" % str(file))

        self.properties["Type"] = "Video"

        media_info = pymediainfo.MediaInfo.parse(file)
        for track in media_info.tracks:
            if track.track_type == "General":
                if track.format is not None:
                    self.other_properties["Container"] = track.format
                if track.duration is not None:
                    self.other_properties["Duration"] = str(datetime.timedelta(seconds=track.duration//1000))
                if track.overall_bit_rate is not None:
                    self.other_properties["Overall Bitrate"] = vstreamer_utils.size_to_string(track.overall_bit_rate, "b/s")
            elif track.track_type == "Video":
                if track.format_info is not None:
                    self.other_properties["Video Format"] = track.format_info
                if track.width is not None and track.height is not None:
                    self.other_properties["Resolution"] = "%dx%d" % (track.width, track.height)
            elif track.track_type == "Audio":
                if track.format_info is not None:
                    self.other_properties["Audio Format"] = track.format_info
        vstreamer_utils.log_info("Created VideoFileEntry for '%s'" % self.path)

    def is_video(self):
        return True
