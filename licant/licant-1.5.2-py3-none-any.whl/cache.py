import os


class FileCache:
    def __init__(self):
        self.cache = dict()

    class fileinfo:
        def __init__(self, path):
            self.exist = os.path.exists(path)
            if self.exist:
                self.mtime = os.stat(path).st_mtime
            else:
                self.mtime = None

    def update_info(self, path):
        self.cache[path] = self.fileinfo(path)

    def get_info(self, path):
        if not path in self.cache:
            self.update_info(path)
        return self.cache[path]


fcache = FileCache()
