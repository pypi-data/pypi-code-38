from synfo.system import System

# Windows only, get information on mounted drives
if System().os == 'Windows':
    from os import popen, path
    from re import findall, MULTILINE
    from string import ascii_uppercase
    from ctypes import windll

    # TODO: Make class cross platform compatible
    class Drives:
        def __init__(self):
            self._drives = None
            self._drives_local = None

        def __str__(self):
            return str(self.drives)

        def __iter__(self):
            return iter(self.drives)

        @property
        def drives(self):
            if not self._drives:
                self._drives = self._get_drives()
            return self._drives

        @property
        def drives_local(self):
            if not self._drives_local:
                self._drives_local = self._get_drives_local()
            return self._drives_local

        @staticmethod
        def _get_drives():
            """Get list of all network and locally mounted drives"""
            drives = []
            bitmask = windll.kernel32.GetLogicalDrives()
            for letter in ascii_uppercase:
                if bitmask & 1:
                    drives.append(letter)
                bitmask >>= 1

            return ['{0}:\\'.format(d) for d in drives]

        @staticmethod
        def _get_drives_local():
            """Get list of locally mounted drives"""
            return findall(r"[A-Z]+:.*$", popen("mountvol /").read(), MULTILINE)

        def find(self, test_path):
            """
            Retrieve the drive letter for a drive by attempting to find an existing path.

            :param test_path: Path to be joined with a drive letter to test validity
            :return: Drive letter for valid path
            """
            for drive in self.drives:
                if path.exists(path.join(drive, test_path)):
                    return drive
            else:
                print('Unable to find a valid path')


    def main():
        print(Drives())


    if __name__ == '__main__':
        main()


else:
    class Drives:
        def __init__(self):
            print("synfo.drives module is compatible with Windows platform's only")
            pass
