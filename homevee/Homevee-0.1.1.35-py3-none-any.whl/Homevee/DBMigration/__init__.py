import os
from os import listdir
from os.path import isfile, join

from Homevee.Utils import Constants


class DBMigration():
    def __init__(self):
        self.scripts_dir = os.path.join(Constants.HOMEVEE_DIR, "DBMigration", "scripts")

    def get_scripts(self):
        """
        Get all migration scripts in alphabetical order
        :return: list of filenames as strings
        """
        try:
            files = [f for f in listdir(self.scripts_dir) if isfile(join(self.scripts_dir, f))]
            return sorted(files)
        except:
            return []

    def get_filecontent_version_map(self):
        """
        Get a map of versions and script content
        :return: a map of the format version(int) => content(string)
        """
        files = self.get_scripts()
        version_map = {}
        for file in files:
            script_version = int(file.split("_")[0])
            script_content = self.read_script_content(file)
            version_map[script_version] = script_content
        return version_map

    def read_script_content(self, file_name: str):
        """
        Get the script content
        :param file_name: the filename as a string
        :return: the script content
        """
        with open(os.path.join(self.scripts_dir, file_name), 'r') as file:
            return file.read().replace('\n', '')

if __name__ == "__main__":
    migration = DBMigration()
    print(migration.get_filecontent_version_map())