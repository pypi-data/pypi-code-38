import time, sys, os ,logging

from quarchpy.connection import QISConnection, PYConnection, QPSConnection


class quarchDevice:

    def __init__(self, ConString, ConType="PY", timeout="5", forceFind=0, controllerType="DIRECT"):
        self.ConString = ConString.lower()
        self.ConType = ConType
        self.ControllerType = controllerType

        try:
            self.timeout = int(timeout)
        except:
            raise Exception("Invalid value for timeout, must be a numeric value")
        self.forceFind = forceFind

        if checkModuleFormat(self.ConString) == False:
            raise Exception("Module format is invalid!")

        # Initializes the object as a python or QIS connection
        ## Python
        if self.ConType.upper() == "PY":

            # replacing colons
            numb_colons = self.ConString.count(":")
            if numb_colons == 2:
                self.ConString = self.ConString.replace('::', ':')

            # Create the connection object
            self.connectionObj = PYConnection(self.ConString)
            self.ConCommsType = self.connectionObj.ConnTypeStr

            # Exposes the connection type and module for later use.
            self.connectionName = self.connectionObj.ConnTarget
            self.connectionTypeName = self.connectionObj.ConnTypeStr

            time.sleep(0.1)
            item = None
            item = self.connectionObj.connection.sendCommand("*tst?")
            if "OK" in item:
                pass
            elif "FAIL" in item:
                pass
            elif item is not None:
                pass
            else:
                raise Exception("No module responded to *tst? command!")
            time.sleep(0.1)

        ## QIS
        # ConType may be QIS only or QIS:ip:port [:3] checks if the first 3 letters are QIS.
        elif self.ConType[:3].upper() == "QIS":
            # If host and port are specified.
            try:
                # Extract QIS, host and port.
                QIS, host, port = self.ConType.split(':')
                # QIS port should be an int.
                port = int(port)
            # If host and port are not specified.
            except:
                host = '127.0.0.1'
                port = 9722

            numb_colons = self.ConString.count(":")
            if numb_colons == 1:
                self.ConString = self.ConString.replace(':', '::')

            # Creates the connection object.
            self.connectionObj = QISConnection(self.ConString, host, port)

            if self.forceFind != 0:
                self.connectionObj.qis.sendAndReceiveCmd(cmd="$scan " + self.forceFind)
                time.sleep(0.1)

            list = self.connectionObj.qis.getDeviceList()
            list_str = "".join(list).lower()

            # check for device in list, has a timeout
            while 1:
                if (self.timeout == 0):
                    raise ValueError("Search timeout - no Quarch module found.")

                elif (self.ConString in list_str):
                    break

                else:
                    time.sleep(1)
                    self.timeout -= 1
                    list = self.connectionObj.qis.getDeviceList()
                    list_str = "".join(list).lower()

            self.connectionObj.qis.sendAndReceiveCmd(cmd="$default " + self.ConString)

        ## QPS
        elif self.ConType[:3].upper() == "QPS":
            try:
                # Extract QIS, host and port.
                QIS, host, port = self.ConType.split(':')
                # QIS port should be an int.
                port = int(port)
            # If host and port are not specified.
            except:
                host = '127.0.0.1'
                port = 9822

            numb_colons = self.ConString.count(":")
            if numb_colons == 1:
                self.ConString = self.ConString.replace(':', '::')

            # Creates the connection object.
            self.connectionObj = QPSConnection(host, port)

            ## Neither PY or QIS, connection cannot be created.
        else:
            raise ValueError("Invalid connection type. Acceptable values [PY,QIS,QPS]")

        logging.debug(os.path.basename(__file__) + " ConString : " + str(self.ConString) + " ConType : " + str(self.ConType) + " controllerType : " + str(self.ControllerType))


    # def setCanStream(self):
    # ask module name if = name in list

    def sendCommand(self, CommandString):

        # send command to log
        logging.debug(os.path.basename(__file__) + ": sending command: " + CommandString)

        if self.ConType[:3] == "QIS":

            numb_colons = self.ConString.count(":")
            if numb_colons == 1:
                self.ConString = self.ConString.replace(':', '::')

            response = self.connectionObj.qis.sendCmd(self.ConString, CommandString)
            # send response to log
            logging.debug(os.path.basename(__file__) + ": received: " + response)
            return response

        elif self.ConType == "PY":
            time.sleep(0.015)
            response = self.connectionObj.connection.sendCommand(CommandString)
            # send response to log
            logging.debug(os.path.basename(__file__) + ": received: " + response)
            return response

        elif self.ConType[:3] == "QPS":
            # checking if the command string passed has a $ as first char
            if CommandString[0] != '$':
                CommandString = self.ConString + " " + CommandString

            response = self.connectionObj.qps.sendCmdVerbose(CommandString)
            # send response to log
            logging.debug(os.path.basename(__file__) + ": received: " + response)
            return response

    # Only works for usb
    def sendBinaryCommand(self, cmd):
        self.connectionObj.connection.Connection.SendCommand(cmd)
        return self.connectionObj.connection.Connection.BulkRead()

    def openConnection(self):
        if self.ConType[:3] == "QIS":
            self.connectionObj.qis.connect()

        elif self.ConType == "PY":
            del self.connectionObj
            self.connectionObj = PYConnection(self.ConString)
            return self.connectionObj

        elif self.ConType[:3] == "QPS":
            self.connectionObj.qps.connect(self.ConString)

    def closeConnection(self):
        if self.ConType[:3] == "QIS":
            self.connectionObj.qis.disconnect()
        elif self.ConType == "PY":
            self.connectionObj.connection.close()

        elif self.ConType[:3] == "QPS":
            self.connectionObj.qps.disconnect(self.ConString)


def checkModuleFormat(ConString):
    ConnectionTypes = ["USB", "SERIAL", "TELNET", "REST", "TCP"]  # acceptable conTypes

    conTypeSpecified = ConString[:ConString.find(':')]

    correctConType = False
    for value in ConnectionTypes:
        if value.lower() == conTypeSpecified.lower():
            correctConType = True

    if not correctConType:
        raise Exception("Invalid connection type specified in Module string, use one of [USB|SERIAL|TELNET|REST|TCP]")
        return False

    numb_colons = ConString.count(":")
    if numb_colons > 2 or numb_colons <= 0:
        raise Exception("Invalid number of colons in module string")
        return False

    return True
