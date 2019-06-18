import tarfile
import zipfile


class DecompressHelper(object):
    valid_extensions = ('tar.gz', 'tar.bz2', 'zip', 'tar')

    def __init__(self, filename):
        self.fobject = self.get_decompress_object(filename)

    @property
    def support_methods(self):
        suport_method = {
            "tar.gz": lambda fname: tarfile.open(fname, mode='r:gz'),
            "tar.bz2": lambda fname: tarfile.open(fname, mode='r:bz2'),
            "tar": lambda fname: tarfile.open(fname, mode='r:'),
            "zip": lambda fname: zipfile.ZipFile(fname, mode='r')
        }
        return suport_method

    def extractall(self, dest_folder):
        self.fobject.extractall(dest_folder)

    def name_list(self):
        values = []
        if isinstance(self.fobject, tarfile.TarFile):
            values = [i.name for i in self.fobject.getmembers()]
        if isinstance(self.fobject, zipfile.ZipFile):
            values = self.fobject.namelist()
        return values

    def get_decompress_object(self, filename):
        for ext in self.valid_extensions:
            if filename.endswith(ext):
                return self.support_methods[ext](filename)
        return False
