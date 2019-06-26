#!/usr/bin/env python
'''
This contains useful functions to help with disk target selection

Ensure installation of wmi and pywin32

########### VERSION HISTORY ###########

13/08/2018 - Andy Norrie    - First version, based on initial work from Pedro Leao
'''

from iometerDiskFinder import iometerDiskFinder

def getDiskTargetSelection (purpose = "iometer"):

    driveInfo = {}

    """
    device will be a dictionary including the following parameters
        NAME
        DRIVE
        //Any additional that others use
    """
    """
    if purpose.lower() is "fio":

        fioObject = fioDiskFinder()
        disk = fioObject.returnDisk()
        print (driveInfo)
    """

    if purpose.lower() == "iometer":
        iometerObject = iometerDiskFinder()
        disk = iometerObject.returnDisk()
        driveInfo = disk

    return driveInfo