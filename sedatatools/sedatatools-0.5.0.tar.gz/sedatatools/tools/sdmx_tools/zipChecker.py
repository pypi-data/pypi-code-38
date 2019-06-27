import zipfile, os, sys


os.chdir('C:\\Canadian census downloaded files\\')

#check whats in it
filesInDirectory = os.listdir()
allFilesSizes = []


def chkZippStat():
    # get statistics for sorce files
    print("Cheking ziped files statistics!")
    for packedFile in filesInDirectory:
        if packedFile.endswith('.ZIP'):
            zippedData = zipfile.ZipFile(packedFile)
            filesInZip = zippedData.namelist()
            for fileName in filesInZip:
                fileInfo = zippedData.getinfo(fileName)
                print(("File: {} have original file size of {}b and compressed {}b".format(fileName, fileInfo.file_size,
                                                                                           fileInfo.compress_size)))
                allFilesSizes.append((fileName, fileInfo.file_size, fileInfo.compress_size))
    print('Total size when unpacked: {} b, total size when packed: {} b.'.format(
        sum(totalUnpackedSize[1] for totalUnpackedSize in allFilesSizes),
        sum(totalCompressedSize[2] for totalCompressedSize in allFilesSizes)))
    print('(Thats {} TB when unpacked and {} GB when packed.)'.format(
        sum(totalUnpackedSize[1] for totalUnpackedSize in allFilesSizes) / (1000 ** 4),
        sum(totalCompressedSize[2] for totalCompressedSize in allFilesSizes) / (1000 ** 3)))


chkZippStat()
####################################################################################################################
import ctypes
import os
import platform
import sys

def get_free_space_mb(dirname):
    """Return folder/drive free space (in megabytes)."""
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(dirname), None, None, ctypes.pointer(free_bytes))
        return free_bytes.value / (1024**3)
    else:
        st = os.statvfs(dirname)
        return st.f_bavail * st.f_frsize / (1024**3)

print('There is {} GB left on disk.'.format(round(get_free_space_mb('c:'),2)))