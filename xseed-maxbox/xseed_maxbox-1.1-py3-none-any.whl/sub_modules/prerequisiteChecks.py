# Prerequisite checks

import subprocess as sp
import sys

def checks():
    minCheckFail = 0
    minRAM = 4194304
    minOS = 18
    minFreeSpace = 32
    minProcessor = 3


    RAM = sp.getoutput('cat /proc/meminfo | grep MemTotal | cut -d\':\' -f2 | xargs| cut -d\' \' -f1')
    print("RAM is: ", RAM)
    if minRAM <= int(RAM):
       print('RAM check pass')
    else :
       print('RAM check fail')
       minCheckFail = 1

    OSVersion = sp.getoutput('cat /etc/lsb-release | grep DISTRIB_RELEASE | cut -d\'=\' -f2 | xargs| cut -d\'.\' -f1')
    print("OS Version is: ", OSVersion)
    if minOS <= int(OSVersion):
       print('OS Version check pass')
    else :
       print('OS Version check fail')
       minCheckFail = 1

    freeSpace = sp.getoutput('df -h --total | grep total| tr -s \' \'|cut -d \' \' -f4 |cut -d \'G\' -f1| xargs')
    print("Total free Space is: ", freeSpace)
    if minFreeSpace <= int(freeSpace):
       print('Free space check pass')
    else :
       print('Free space check fail')
       minCheckFail = 1

    processor = sp.getoutput('cat /proc/cpuinfo | grep \'model name\'|head -n 1|tr -s \' \'|cut -d \' \' -f5| cut -d \'-\' -f1|head -c 2|tail -c 1|xargs')
    print("Processor is: i", processor)
    if minProcessor <= int(processor):
       print('Processor check pass')
    else :
       print('Processor check fail')
       minCheckFail = 1

    if (minCheckFail == 1):
        print('Prerequisite checks failed')
        exit();
