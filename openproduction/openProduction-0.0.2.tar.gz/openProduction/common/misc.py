from enum import Enum
import appdirs
import pkg_resources
import sys
import os
import getpass

class License(Enum):
    Type = 1

class Links(Enum):
    Documentation = 1
    SourceCode = 2
    
def getAppName():
    return pkg_resources.require("openProduction")[0].project_name
    
def getAuthorName():
    return "pieye"
    
def getDefaultAppFolder():
    appname = getAppName()
    appauthor = getAuthorName()
    return appdirs.user_data_dir(appname, appauthor)
    
def getVersion():
    version = pkg_resources.require("openProduction")[0].version
    return version

def getLink(link):
    rv = ""
    if link == Links.SourceCode:
        rv = "https://github.com/Coimbra1984/openProduction"
    elif link == Links.Documentation:
        rv = "https://readthedocs.org/projects/openProduction/"
    return rv

def getLicense(lic):
    rv = ""
    if lic == License.Type:
        rv = "GPLv3"
    return rv

def queryYesNo(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")
         
def queryFile(question):
    while True:
        sys.stdout.write(question)
        file = input().lower()
        file = os.path.abspath(file)
        if os.path.isfile(file):
            break
        else:
            print("File %s doesn't exist, please give an existing file"%file)
            continue
                
            break
    return file            
            
def queryFolder(question):
    while True:
        sys.stdout.write(question)
        path = input().lower()
        path = os.path.abspath(path)
        if os.path.exists(path):
            break
        else:
            try:
                os.makedirs(path)
            except Exception as e:
                print ("could not create folder %s, error message: %s"%(path, str(e)))
                continue
                
            break
    return path

def queryString(question, cb=None):
    while True:
        sys.stdout.write(question)
        value = input().lower()
        if cb != None:
            if cb(value):
                break
            else:
                continue
        break
    return value

def queryInteger(question, minVal=None, maxVal=None):
    if minVal != None and maxVal != None:
        if minVal > maxVal:
            raise ValueError("maxVal must be equal-or-greater than minVal")
        prompt = "[%d..%d]: "%(minVal,maxVal)
    else:
        minVal = None
        maxVal = None
        prompt = ""
        
    while True:
        sys.stdout.write(question+prompt)
        value = input().lower()
        try:
            value=int(value)
            ok = True
        except:
            ok = False
        
        if ok:
            if minVal == None:
                break
            else:
                if value>=minVal and value<=maxVal:
                    break
        
        if minVal != None:
            inRange = "in range [%d..%d]"%(minVal, maxVal)        
        else:
            inRange = ""
        sys.stdout.write("Please give a number %s.\n"%inRange)
        
    return value


def queryPassword(question, cb=None):
    while True:
        pw1 = getpass.getpass(question)
        pw2 = getpass.getpass("Type in the same pasword again: ")
        if pw1 == pw2:
            break
        else:
            print("Passwords did not match, please try again")
    return pw1

def queryChoice(question, choice, default=None, typ=str):
    if default not in choice:
        raise ValueError("invalid default answer: '%s'" % str(default))
    for c in choice:
        if type(c) != typ:
            raise ValueError("choice contains invalid types")
        
    while True:
        sys.stdout.write(question)
        inp = input().lower()
        if default is not None and inp == '':
            rv = default
            break
        else:
            try:
                rv = typ(inp)
                if rv in choice:
                    break
            except:
                pass
            
            sys.stdout.write("Invalid choice, use one of %s\n"%str(choice))
    
    return rv