import copy
import pathlib

import vstreamer_utils
from vstreamer_utils import model


class DirectoryInfo:
    def __init__(self, path, directory_root):
        path = pathlib.Path(path)
        directory_root = pathlib.Path(directory_root)
        if not path.is_dir():
            raise ValueError("'%s' is not a directory" % str(path))
        self.name = str(path.name)
        self.path = "/" + str(path.relative_to(directory_root))
        self.entries = sorted([model.FileEntry(x, directory_root) for x in path.iterdir()
                               if x.is_dir() or vstreamer_utils.is_video_file(x)],
                              key=DirectoryInfo._sort_key)
        if path != directory_root:
            back_dir = model.FileEntry(path.parent, directory_root)
            back_dir.filename = back_dir.properties["Filename"] = ".."
            self.entries.insert(0, back_dir)
        vstreamer_utils.log_info("Created DirectoryInfo for '%s'" % self.path)

    def __len__(self):
        return len(self.entries)

    def __getitem__(self, key):
        return self.entries[key]

    def light_copy(self):
        light = copy.copy(self)
        light.entries = list(map(lambda e: e.light_copy(), self.entries))
        return light

    def add_additional_properties(self, file, properties):
        for entry in self.entries:
            if entry.path == file:
                entry.apply_additional_properties(properties)
                self.entries.sort(key=DirectoryInfo._sort_key)
                return
        raise RuntimeError("'%s' not found in directory tree" % file)

    @staticmethod
    def _sort_key(file_entry):
        return file_entry.is_video(), file_entry.properties["Filename"]
