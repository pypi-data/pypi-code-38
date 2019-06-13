import time
import socket

'''
Sends a command to the device and verifies that the expexted response is returned
'''
def sendAndVerifyCommand (myDevice, commandString, responseExpected="OK", exception=True):
    responseStr = myDevice.sendCommand (commandString)
    if (responseStr != responseExpected):
        if (exception):
            raise ValueError ("Command response error: " + responseStr)
        else:
            return False
    else:
        return True
    
'''
Sends a measurement command to the device and decodes the response into a float and unit
component for return
'''
def returnMeasurement (myDevice, commandString):
    valueStr = None
    unitStr = None

    # Send the command
    responseStr = myDevice.sendCommand (commandString)
    # If a space is found, suggests xxx uu format
    pos = responseStr.find(" ")
    if (pos != -1):
        valStr = responseStr[pos:].strip()
        unitStr = responseStr[:pos].strip()
        try:
            floatVal = float(valStr)
        except:
            raise ValueError ("Response does not parse to a measurement value: " + responseStr)
    # If '0x' is found, looks like a register read value
    elif (responseStr.find("0x") != -1):
        unitStr = 'hex'
        try:
            unitVal = int(responseStr[2:].strip(),16)
        except:
            raise ValueError ("Response does not parse to a register measurement value: " + responseStr)
    # Otherwise may be a simple value (xxx format)       
    else:
        # Try to parse direct to float
        try:
            floatVal = float(responseStr)
        # If that failes, assumed to be xxxuu format
        except:
            for i, c in enumerate(responseStr):
                if c.isalpha():
                    pos = i
                    break
            if (i < len(responseStr)):
                valStr = responseStr[:pos].strip()
                unitStr = responseStr[pos:].strip()
                try:
                    floatVal = float(valStr)
                except:
                    raise ValueError ("Response does not parse to a measurement value: " + responseStr)
            else:
                raise ValueError ("Response does not parse to a measurement value: " + responseStr)
    
    # Return parsed values
    return valStr, unitStr
        
'''
Class to gather data from mDNS search system
'''
class MdnsListener:
    def __init__(self):
        self.deviceList = {}

    def remove_service(self, zeroconf, type, name):
        pass

    '''
    Add all located devices to the dictionary (IP:Name)
    '''
    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info:
            addr = socket.inet_ntoa(info.address)
            self.deviceList[addr] = info.name
            pass
            

'''
Function to locate a list of instruments matching the given name
'''
def locateMdnsInstr (instrName, scanTime=2):
    from zeroconf import ServiceBrowser, Zeroconf
    foundDevices = {}

    # Run the scan process
    zeroconf = Zeroconf()
    listener = MdnsListener()
    browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)
    time.sleep(scanTime)
    zeroconf.close()

    # Filter through the devices, looking for matching ones
    for k, v in listener.deviceList.items():
        if (instrName.upper() in v.upper()):
            foundDevices[k] = v

    # Sort the list by value to order the same way each time
    sortedFoundDevices = {}
    # get a sorted list of values
    for k in sorted(foundDevices.keys(),key=lambda x:x.lower()):
        sortedFoundDevices[k] = foundDevices[k]

    return sortedFoundDevices




