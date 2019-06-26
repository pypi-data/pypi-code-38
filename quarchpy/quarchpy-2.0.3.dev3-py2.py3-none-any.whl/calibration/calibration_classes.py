import pkg_resources
import datetime
import xml.etree.ElementTree
import quarchpy

'''
Contains basic information for populating the header section of a calibration file and similar
'''
class CalibrationHeaderInformation ():
    def __init__(self):
        self.quarchEnclosureSerial = None
        self.quarchInternalSerial = None
        self.idnStr = None
        self.quarchFirmware = None
        self.quarchFpga = None
        self.calInstrumentId = None
        self.quarchpyVersion = None
        self.calCoreVersion = None
        self.calTime = None
        self.calTemperature = None
        self.calNotes = None
        self.calFileVersion = "1.0"
        self.calibrationType = None
        self.result = None
        
    '''
    Convert to standard XML text
    '''
    def toXmlText(self):
        # Header node
        headerObject = ElementTree.Element("Header")
        # Quarch module information
        quarchModuleObject = ElementTree.SubElement(headerObject, "QuarchModule")
        ElementTree.SubElement(quarchModuleObject, "EnclosureSerial").text = self.quarchEnclosureSerial
        ElementTree.SubElement(quarchModuleObject, "InternalSerial").text = self.quarchInternalSerial
        ElementTree.SubElement(quarchModuleObject, "ModuleFirmware").text = self.quarchFirmware
        ElementTree.SubElement(quarchModuleObject, "ModuleFpga").text = self.quarchFpga
        # Calibration instrument information
        calInstrumentObject = ElementTree.SubElement(headerObject, "CalInstrument")
        ElementTree.SubElement(calInstrumentObject, "Identity").text = self.calInstrumentId
        # Calibration software information
        CalSoftwareObject = ElementTree.SubElement(headerObject, "CalSoftware")
        ElementTree.SubElement(CalSoftwareObject, "QuarchPy").text = self.quarchpyVersion
        ElementTree.SubElement(CalSoftwareObject, "CalCoreVersion").text = self.calCoreVersion
        ElementTree.SubElement(CalSoftwareObject, "CalFileVersion").text = self.calFileVersion
        # General information        
        ElementTree.SubElement(headerObject, "CalTime").text = self.calTime
        ElementTree.SubElement(headerObject, "CalTemperature").text = self.calTemperature
        ElementTree.SubElement(headerObject, "calNotes").text = self.calNotes
        
        return ElementTree.tostring(headerObject)

    '''
    Convert to standard report text
    '''
    def toReportText(self):
        reportText = ""
        reportText += "CALIBRATION REPORT\n"
        reportText += "---------------------------------\n"
        reportText += "\n"
        reportText += "Quarch Enclosure#: "
        reportText += self.quarchEnclosureSerial + "\n"
        reportText += "Quarch Serial#: "
        reportText += self.quarchInternalSerial + "\n"
        reportText += "Quarch Versions: "
        reportText += "FW:" + self.quarchFirmware + ", FPGA: " + self.quarchFpga + "\n"
        reportText += "\n"
        reportText += "Calibration Instrument#:\n"
        reportText += self.calInstrumentId + "\n"
        reportText += "\n"
        reportText += "Calibration Versions:\n"
        reportText += "QuarchPy Version: " + str(self.quarchpyVersion) + "\n"
        reportText += "Calibration Version: " + str(self.calCoreVersion) + "\n"
        reportText += "\n"
        reportText += "Calibration Details:\n"
        reportText += "Calibration Type: " + str(self.calibrationType) + "\n"
        reportText += "Calibration Time: " + str(self.calTime) + "\n"
        reportText += "Calibration Temperature: " + str(self.calTemperature) + "\n"
        reportText += "Calibration Notes: " + str(self.calNotes) + "\n"
        reportText += "\n"
        reportText += "---------------------------------\n"
        reportText += "\n"
        return reportText
        
        
        

'''
Populates the header with Keithley specific information
'''       
def populateCalHeader_Keithley (calHeader, myCalInstrument):
    calHeader.calInstrumentId = myCalInstrument.sendCommandQuery ("*IDN?")
    
'''
Populates the header with PPM specific information
'''       
def populateCalHeader_HdPpm (calHeader, myDevice, calAction):
    # Serial numbers (ensure QTL at start)
    calHeader.quarchEnclosureSerial = myDevice.sendCommand("*ENCLOSURE?")
    if (calHeader.quarchEnclosureSerial.find ("QTL") == -1):
        calHeader.quarchEnclosureSerial = "QTL" + calHeader.quarchEnclosureSerial
    # fetch the enclosure position
    calHeader.quarchEnclosurePosition = myDevice.sendCommand("*POSITION?")
    calHeader.quarchInternalSerial = myDevice.sendCommand ("*SERIAL?")
    if (calHeader.quarchInternalSerial.find ("QTL") == -1):
        calHeader.quarchInternalSerial = "QTL" + calHeader.quarchInternalSerial
    # Code version (FPGA)
    calHeader.idnStr = myDevice.sendCommand ("*IDN?")
    pos = calHeader.idnStr.upper().find ("FPGA 1:")
    if (pos != -1):
        versionStr = calHeader.idnStr[pos+7:]
        pos = versionStr.find ("\n")
        if (pos != -1):
            versionStr = versionStr[:pos].strip()
        else:
            pass
    else:
        versionStr = "NOT-FOUND"    
    calHeader.quarchFpga = versionStr.strip()
    
    # Code version (FW)    
    pos = calHeader.idnStr.upper().find ("PROCESSOR:")
    if (pos != -1):
        versionStr = calHeader.idnStr[pos+10:]
        pos = versionStr.find ("\n")
        if (pos != -1):
            versionStr = versionStr[:pos].strip()            
        else:
            pass
    else:
        versionStr = "NOT-FOUND"    
    calHeader.quarchFirmware = versionStr.strip()
    calHeader.calibrationType = calAction
    
'''
Populates the header with system specific information
'''       
def populateCalHeader_System (calHeader):
    # Calibration core version
    calHeader.calCoreVersion = quarchpy.calibration.calCodeVersion
    # Quarchpy version
    calHeader.quarchpyVersion = pkg_resources.get_distribution("quarchpy").version
    # Calibration time
    calHeader.calTime = datetime.datetime.now()

'''
Class to hold result/status of a module's calibration process
'''
class ModuleResultsInformation ():
    def __init__(self):        
        self.calibrationStatus = False
        self.channelResults = []
        self.calibrationHeader = None

    '''
    Outputs the main (text form) report to file
    '''
    def saveTextReport (self, outputPath):
        # Setup the standard filename format
        fileName = calibrationHeader.quarchEnclosureSerial + " - " + self.calibrationType + " - " + self.calTime + ".txt"
        # Open the file        
        f = open (fileName, "w")
        # Write the cal header
        f.write (calibrationHeader.toReportText())
        # TODO: Loop through the calibrations and summarise the results here
        # TODO: Loop through the calibrations and print the detailed results here
        

        
'''
Class to hold result/status of a calibration on a single channel
'''
class CalibrationResultsInformation ():
    def __init__(self):
        self.calibrationName = None
        self.calibrationStatus = None
        self.calibrationSummary = None
        self.reportText = None
        self.reportXml = None
    
