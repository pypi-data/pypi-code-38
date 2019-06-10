from quarchpy import *
import pkg_resources
from pkg_resources import parse_version, get_distribution
import os
import platform

def main ():

    print("Quarchpy Version : " + pkg_resources.get_distribution("quarchpy").version)
    print("Python Version : " + sys.version)
    print("OS Name : " + os.name)
    print("Platform System : " + platform.system())
    print("Platfrom Release :  " + platform.release())




if __name__ == "__main__":
    main()