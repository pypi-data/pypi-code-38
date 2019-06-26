from openProduction.common import Constants

class Version:
    def __init__(self, version, revision, url, isDirty=False):
        if Constants.isValidStr(version) == False:
            raise RuntimeError("version string may not contain any charachter of '%s'"%Constants.invalidChars())
        
        self.version = version
        self.revision = int(revision)
        self.isDirty = isDirty
        self.url = url
        
    @staticmethod
    def fromString(myStr):
        url = ""
        if len(myStr.split(Constants.URL_SEPARATOR)) == 2:
            url, versStr = myStr.split(Constants.URL_SEPARATOR)
        elif len(myStr.split(Constants.URL_SEPARATOR)) == 1:
            versStr = myStr
        else:
            return None
        
        if len(versStr.split(Constants.VERSION_SEPARATOR)) == 2:
            version, revStr = versStr.split(Constants.VERSION_SEPARATOR)
        else:
            return None
        
        if Constants.isValidStr(version) == False:
            return None
        
        idxDirty = revStr.find("-dirty")
        if idxDirty != -1:
            revStr = revStr[:revStr.find("-dirty")]
            isDirty = True
        else:
            isDirty = False

        try:
            rev = int(revStr)
            return Version(version, rev, url, isDirty)
        except:
            pass
            
        return None
            
    def toString(self):
        vers = str(self.version) + Constants.VERSION_SEPARATOR + str(self.revision)
        if self.isDirty:
            vers = vers + "-dirty"
        return vers
        
    def toFullString(self):
        if self.url == "" or self.url == None:
            urlStr = ""
        else:
            urlStr = str(self.url) + Constants.URL_SEPARATOR
        return  urlStr + self.toString()
    
if __name__ == "__main__":
    v0 = Version.fromString("AA.34-dirty")
    v1 = Version.fromString("AA.34")
    v2 = Version.fromString("myUrlsfdsdf///.git|AA.34-dirty")