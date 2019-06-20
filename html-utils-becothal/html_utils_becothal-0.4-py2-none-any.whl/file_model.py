
class file_model:
    rootDir = ""
    sourceFileName = ""
    content = ""

    def __init__(self):
        self.rootDir = ""
        self.sourceFileName = ""
        self.content = ""

    def readFile(self, fileName):
        if fileName == "":
            return
        self.extractFileNameAndRoot(fileName)
        fileHandler = file
        try:
            fileHandler = open(self.rootDir + self.sourceFileName)
            self.content = fileHandler.read()
            fileHandler.close()
        except (OSError, IOError) as e:
            fileHandler.close()
            raise IOError(e.errno + e.errmessage)

    def toString(self):
        """
        Returns the content of Object as String.
        :returns: Content of the Object as String
        :rtype: str
        """
        return self.content

    def extractFileNameAndRoot(self, fileName):
        if fileName == "":
            print "getRootPath: FileName was empty!"
            return
        fileName.replace("\\", "/")
        self.sourceFileName = fileName[fileName.rfind('/'):]
        self.rootDir = fileName[:fileName.rfind('/') + 1]