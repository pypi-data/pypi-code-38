import os
import zipfile
import glob


class BadDirectoryException(Exception):
    pass


class Bundle(object):

    def __init__(self, directory_path=None, options=None):
        self.__set_directory_path(directory_path=directory_path)
        self.options = options

    def __set_directory_path(self, directory_path):
        if directory_path:
            if directory_path in ['.', './']:
                self.directory_path = os.getcwd()
            else:
                self.directory_path = os.path.normpath(directory_path)
        else:
            self.directory_path = os.getcwd()

    def __get_last_directory(self):
        if os.path.isdir(self.directory_path):
            return os.path.basename(self.directory_path)
        else:
            raise BadDirectoryException

    def __get_last_file(self, path):
        return os.path.basename(path)

    def zip(self):
        zip_name = '{0}.zip'.format(self.__get_last_directory())
        with zipfile.ZipFile(zip_name, 'w') as bundle:
            for file in glob.glob(self.directory_path + '/*.tf'):
                print('adding {0}'.format(file))
                bundle.write(
                    file,
                    arcname=self.__get_last_file(path=file)
                )
        print('completed bundling {0}'.format(zip_name))
        return zip_name

    def info(self, zip_file):
        zf = zipfile.ZipFile(zip_file)
        return zf.infolist()


