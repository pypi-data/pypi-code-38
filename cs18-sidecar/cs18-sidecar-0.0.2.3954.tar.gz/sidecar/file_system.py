import os
import shutil
import tempfile


class FileSystemService:
    def __init__(self):
        pass

    def create_temp_folder(self):
        """
        Create a temporary folder in the os tmp folder.
        :return: The path of the new folder.
        """
        return tempfile.mkdtemp()

    def create_folder(self, folder):
        """
        Create a folder.
        :param str folder: The path of the new folder.
        """
        if not os.path.exists(folder):
            os.makedirs(folder)

    def create_folders(self, path):
        os.makedirs(path)

    def exists(self, path):
        """
        Check if the path exists.
        :param str path: The path to examine
        :rtype bool
        """
        return os.path.exists(path)

    def delete_temp_folder(self, folder):
        """
        Delete a temporary folder from the os tmp folder.
        :param str folder: Folder path.
        """
        shutil.rmtree(folder, ignore_errors=True)

    def create_file(self, path, chmod=None, mode=None):
        """
        Create (or override) a new file.
        :param str path: The path of the new file (example: 'c:\tmp\file.txt}
        """

        if mode is None:
            mode = 'w'

        f = open(path, mode)
        if chmod:
            os.chmod(path, int(chmod))
        return f

    def get_working_dir(self):
        """
        Get the current working directory.
        :rtype: str
        """
        return os.getcwd()

    def get_entries(self, dir):
        """
           Return a list containing the names of the entries in the directory.
           :param str path: The path of of directory to list
           The list is in arbitrary order.  It does not include the special
           entries '.' and '..' even if they are present in the directory.
           """
        return os.listdir(dir)

    def set_working_dir(self, path):
        """
        Set new working directory.
        :type path: str
        """
        os.chdir(path)

    def write_lines_to_file(self, path, lines, chmod):
        with open(path, "w+") as f:
            f.writelines(lines)
        os.chmod(path, chmod)


class WorkingDirectoryScope:
    def __init__(self, file_system: FileSystemService):
        self.file_system = file_system

    def __enter__(self):
        self.folder = self.file_system.create_temp_folder()
        self.prev_working_dir = self.file_system.get_working_dir()
        self.file_system.set_working_dir(self.folder)
        return self.folder

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file_system.set_working_dir(self.prev_working_dir)
        self.file_system.delete_temp_folder(self.folder)
