import pkg_resources
from pkg_resources import parse_version, get_distribution
import re

def getQuarchPyVersion ():
    return pkg_resources.get_distribution("quarchpy").version

def requiredQuarchpyVersion (requiredVersion):
    currentVersion =getQuarchPyVersion ()

    # S.B Debugging
    #print ("ReqVer: "+requiredVersion + "CurVer: "+ currentVersion)
    #print ("Old if: " + str(parse_version(getQuarchPyVersion ())) < str(parse_version(requiredVersion)))
    #print ("New if: " + str(currentVersion) < str(requiredVersion))
    #if (parse_version(getQuarchPyVersion ()) < parse_version(requiredVersion)): #old if not working

    if (str(currentVersion) < str(requiredVersion)): #takes into account .dev* endings as they are larger that .0 or nothing.
        raise ValueError ("Current quarchpy version " + str(currentVersion) + " is not high enough, upgrade to " + str(requiredVersion) + " or above.")
    else:
        return True