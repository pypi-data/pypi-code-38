import xml.etree


'''
Class to define a test point to be executed
'''
class testLine:

    '''
    Init function taking all parameters
    '''
    def __init__(self):
        #self.idNumber=None
        self.lineType=None
        self.testName=None
        self.moduleName=None
        self.paramList={}

    '''
    Use an XML tree to init the testLine object.  Throws an exception of the required
    elements are not available.  Additional elements will be ignored
    '''
    def initFromXml (self, xmlTree):        
        # Verify expected root node
        if (xmlTree.tag != "RemoteCommand"):
            raise ValueError ("XML tree does not contain the required root value (RemoteCommand)")

        

        # Get main command details
        #self.idNumber = xmlTree.find('LineNumber').text
        self.lineType = xmlTree.find('LineType').text
        self.testName = xmlTree.find('Function').text
        self.moduleName = xmlTree.find('Module').text

        # Get parameter list
        newItem = xmlTree.iter()
        newItem2 = []
        for elem in newItem:
            if 'key' in elem.tag or 'value' in elem.tag:
                newItem2.append(elem.text)
                #print (elem.text)

        skipElement = ""
        #if there's any entries in the list
        if newItem2:
            for x, elem in enumerate(newItem2):
                if (skipElement == x):
                    continue
                self.paramList.update({elem: newItem2[x + 1]})
                skipElement = x + 1


        #for k, v in self.paramList.items():
        #    print(k, v)

        # Validate command data
        #if (self.idNumber == None):
        #    raise ValueError ("Remote command 'ID' not set")
        if (self.lineType == None):
            raise ValueError ("Remote command 'type' not set")
        if (self.testName == None):
            raise ValueError ("Remote command 'name' not set")
        if (self.moduleName == None):
            raise ValueError ("Remote command 'module' not set")
        #if (self.moduleName == None):
        #    raise ValueError ("Remote command 'module' not set")
        #if (len(self.paramList) == 0):
        #    raise ValueError ("Remote command 'parameters' not set")

