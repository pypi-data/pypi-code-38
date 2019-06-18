## binhoHostAdapter Python Library
##
## Jonathan Georgino <jonathan@binho.io>
## Binho LLC
## www.binho.io

import threading
import queue
import signal
import sys
import serial
from time import sleep

class SerialPortManager(threading.Thread):

        serialPort = None
        txdQueue = None
        rxdQueue = None
        intQueue = None
        stopper = None
        inBridgeMode = False

        def __init__(self, serialPort, txdQueue, rxdQueue, intQueue, stopper):
            super().__init__()
            self.serialPort = serialPort
            self.txdQueue = txdQueue
            self.rxdQueue = rxdQueue
            self.intQueue = intQueue
            self.stopper = stopper
            self.exception = None

        def run(self):

            try:
                comport = serial.Serial(self.serialPort, baudrate=1000000, timeout=0.025, write_timeout=0.05)
            except:
                self.stopper.set()

            while not self.stopper.is_set():

                try:
                    if self.inBridgeMode:

                        if comport.in_waiting > 0:
                            receivedData = comport.read().decode("utf-8")
                            self.rxdQueue.put(receivedData)

                        if self.txdQueue.empty() == False:
                            serialData = self.txdQueue.get()
                            comport.write(serialData.encode('utf-8'))
                    else:

                        if comport.in_waiting > 0:
                            receivedData = comport.readline().strip().decode("utf-8")

                            if(len(receivedData) > 0):

                                if receivedData[0] == '!':
                                    self.intQueue.put(receivedData)
                                elif receivedData[0] == '-':
                                    self.rxdQueue.put(receivedData)

                        if self.txdQueue.empty() == False:
                            serialCommand = self.txdQueue.get() + '\n'
                            comport.write(serialCommand.encode("utf-8"))

                except Exception as e:
                    self.stopper.set()
                    self.exception = e
                    # print('Comm Error!')

        def get_exception(self):
            return self.exception

        def startUartBridge(self):
            self.inBridgeMode = True

        def stopUartBridge(self):
            self.inBridgeMode = False


class SignalHandler:
    """
    The object that will handle signals and stop the worker threads.
    """

    #: The stop event that's shared by this handler and threads.
    stopper = None

    #: The pool of worker threads
    workers = None

    def __init__(self, stopper, manager):
        self.stopper = stopper
        self.manager = manager

    def __call__(self, signum, frame):
        """
        This will be called by the python signal module
        https://docs.python.org/3/library/signal.html#signal.signal
        """
        self.stopper.set()

        self.manager.join()

        sys.exit(0)

    def sendStop(self):

        self.stopper.set()

        self.manager.join()

class binhoHostAdapter:

    # Constructor, needs a serial port as a parameter

    def __init__(self, serialPort):

        self.serialPort = serialPort

        self.interrupts = set()

        self._stopper = threading.Event()
        self._txdQueue = queue.Queue()
        self._rxdQueue = queue.Queue()
        self._intQueue = queue.Queue()

        # we need to keep track of the workers but not start them yet
        #workers = [StatusChecker(url_queue, result_queue, stopper) for i in range(num_workers)]
        self.manager = SerialPortManager(self.serialPort, self._txdQueue, self._rxdQueue, self._intQueue, self._stopper)

        # create our signal handler and connect it
        self.handler = SignalHandler(self._stopper, self.manager)
        signal.signal(signal.SIGINT, self.handler)

        # start the threads!
        self.manager.daemon = True

        self.manager.start()

    # Destructor

    def __del__(self):

        self.handler.sendStop()

    # Private functions

    def _sendCommand(self, command):

        self._txdQueue.put(command)

    def _readResponse(self):

        result = '[ERROR]'

        if self.manager.is_alive():
            if not self.manager.get_exception():
                result = self._rxdQueue.get()
        else:
            print('Connection with Device Lost!')
            self.handler.sendStop()

        return result

    def _checkInterrupts(self):

        while self._intQueue.empty() == False:
            self.interrupts.add(self._intQueue.get())

    # Public functions

    # Communication Management

    def open(self):

        self.interrupts.clear()
        self.manager.start()

    def isConnected(self):

        return self.manager.is_alive()

    def isCommError(self):

        e = self.manager.get_exception()

        if e:
            return True
        else:
            return False

    def close(self):

        self.handler.sendStop()

    def interruptCount(self):

        self._checkInterrupts()

        return len(self.interrupts)

    def interruptCheck(self, interrupt):

        self._checkInterrupts()

        if interrupt in self.interrupts:
            return True
        else:
            return False

    def interruptClear(self, interrupt):

        self.interrupts.discard(interrupt)

    def interruptClearAll(self):

        self.interrupts.clear()

    def getInterrupts(self):

        self._checkInterrupts()

        return self.interrupts.copy()

    ## DEVICE COMMANDS

    def echo(self):

        self._sendCommand('+ECHO')
        result = self._readResponse()

        return result

    def ping(self):

        self._sendCommand('+PING')
        result = self._readResponse()

        return result

    ## GET/SET OperationMode
    ##
    ## parameters:
    ##  mode        I2C|IIC, SPI, IO

    def setOperationMode(self, coreIndex, mode):

        self._sendCommand('+MODE ' + str(coreIndex) + ' ' + mode)
        result = self._readResponse()

        return result

    def getOperationMode(self, coreIndex):

        self._sendCommand('+MODE ' + str(coreIndex) + ' ?')
        result = self._readResponse()

        return result

    def setNumericalBase(self, base):

        self._sendCommand('+BASE ' + str(base))
        result = self._readResponse()

        return result

    def getNumericalBase(self):

        self._sendCommand('+BASE ?')
        result = self._readResponse()

        return result

    def setLEDRGB(self, red, green, blue):

        self._sendCommand('+LED ' + str(red) + ' ' + str(green) + ' ' + str(blue))
        result = self._readResponse()

        return result

    def setLEDColor(self, color):

        self._sendCommand('+LED ' + color)
        result = self._readResponse()

        return result

    def getFirmwareVer(self):

        self._sendCommand('+FWVER')
        result = self._readResponse()

        return result

    def getHardwareVer(self):

        self._sendCommand('+HWVER')
        result = self._readResponse()

        return result

    def resetToBtldr(self):

        self._sendCommand('+BTLDR')
        result = self._readResponse()

        return result

    def reset(self):

        self._sendCommand('+RESET')
        result = self._readResponse()

        return result

    def getDeviceID(self):

        self._sendCommand('+ID')
        result = self._readResponse()

        return result

    ## BUFFER COMMANDS

    def clearBuffer(self, bufferIndex):

        self._sendCommand('BUF' + str(bufferIndex) + ' CLEAR')
        result = self._readResponse()

        return result

    def addByteToBuffer(self, bufferIndex, value):

        self._sendCommand('BUF' + str(bufferIndex) + ' ADD ' + str(value))
        result = self._readResponse()

        return result

    def readBuffer(self, bufferIndex, numBytes):

        self._sendCommand('BUF' + str(bufferIndex) + ' READ ' + str(numBytes))
        result = self._readResponse()

        return result

    def writeToBuffer(self, bufferIndex, startIndex, data):

        bufferData = ''

        for x in data:
            bufferData += ' ' + str(x)

        self._sendCommand('BUF' + str(bufferIndex) + ' WRITE ' + str(startIndex) + bufferData)
        result = self._readResponse()

        return result

    ## I2C COMMANDS

    def setClockI2C(self, i2cIndex, clock):

        self._sendCommand('I2C' + str(i2cIndex) + ' CLK ' + str(clock))
        result = self._readResponse()

        return result

    def getClockI2C(self, i2cIndex):

        self._sendCommand('I2C' + str(i2cIndex) + ' CLK ?')
        result = self._readResponse()

        return result

    def setPullUpStateI2C(self, i2cIndex, pullUpState):

        self._sendCommand('I2C' + str(i2cIndex) + ' PULL ' + str(pullUpState))
        result = self._readResponse()

        return result

    def getPullUpStateI2C(self, i2cIndex):

        self._sendCommand('I2C' + str(i2cIndex) + ' PULL ?')
        result = self._readResponse()

        return result

    def scanBusI2C(self, i2cIndex):

        self._sendCommand('I2C' + str(i2cIndex) + ' SCAN')
        result = self._readResponse()

        return result

    def scanAddrI2C(self, i2cIndex, address):

        self._sendCommand('I2C' + str(i2cIndex) + ' SCAN ' + str(address))
        result = self._readResponse()

        return result

    def writeI2C(self, i2cIndex, address, startingRegister, data):

        dataPacket = ''

        for x in data:
            dataPacket += ' ' + str(x)

        self._sendCommand('I2C' + str(i2cIndex) + ' WRITE ' + str(address) + ' ' + str(startingRegister) + dataPacket)
        result = self._readResponse()

        return result

    def writeByteI2C(self, i2cIndex, data):

        self._sendCommand('I2C' + str(i2cIndex) + ' WRITE ' + str(data))
        result = self._readResponse()

        return result

    def readByteI2C(self, i2cIndex, address):

        self._sendCommand('I2C' + str(i2cIndex) + ' REQ ' + str(address) + ' 1')
        result = self._readResponse()

        return result

    def readBytesI2C(self, i2cIndex, address, numBytes):

        self._sendCommand('I2C' + str(i2cIndex) + ' REQ ' + str(address) + ' ' + str(numBytes))
        result = self._readResponse()

        return result

    def readI2C(self, i2cIndex, address, startingRegister, numBytes):

        self._sendCommand('I2C' + str(i2cIndex) + ' READ ' + str(address) + ' ' + str(startingRegister) + ' ' + str(numBytes))
        result = self._readResponse()

        return result

    def getReceivedDataI2C(self, i2cIndex):

        self._sendCommand('I2C' + str(i2cIndex) + ' READ')
        result = self._readResponse()

        return result

    def writeFromBufferI2C(self, i2cIndex, numBytes):

        self._sendCommand('I2C' + str(i2cIndex) + ' WRITE BUF0 ' + str(numBytes))
        result = self._readResponse()

        return result

    def readToBufferI2C(self, i2cIndex, address, numBytes):

        self._sendCommand('I2C' + str(i2cIndex) + ' REQ ' + str(address) + ' BUF0 ' + str(numBytes))
        result = self._readResponse()

        return result

    def startI2C(self, i2cIndex, address):

        self._sendCommand('I2C' + str(i2cIndex) + ' START ' + str(address))
        result = self._readResponse()

        return result

    def endI2C(self, i2cIndex, repeat=False):

        if repeat == True:
            self._sendCommand('I2C' + str(i2cIndex) + ' END R')
        else:
            self._sendCommand('I2C' + str(i2cIndex) + ' END')

        result = self._readResponse()

        return result

    def setSlaveAddressI2C(self, i2cIndex, address):

        self._sendCommand('I2C' + str(i2cIndex) + ' SLAVE ' + str(address))
        result = self._readResponse()

        return result

    def getSlaveAddressI2C(self, i2cIndex):

        self._sendCommand('I2C' + str(i2cIndex) + ' SLAVE ?')
        result = self._readResponse()

        return result

    def getSlaveRequestInterruptI2C(self, i2cIndex):

        result = self.interruptCheck('!I2C' + str(i2cIndex) + ' SLAVE RQ')

        return result

    def clearSlaveRequestInterruptI2C(self, i2cIndex):

        self.interruptClear('!I2C' + str(i2cIndex) + ' SLAVE RQ')

    def getSlaveReceiveInterruptI2C(self, i2cIndex):

        result = self.interruptCheck('!I2C' + str(i2cIndex) + ' SLAVE RX')

        return result

    def clearSlaveReceiveInterruptI2C(self, i2cIndex):

        self.interruptClear('!I2C' + str(i2cIndex) + ' SLAVE RX')

    ## SPI COMMANDS

    def setClockSPI(self, spiIndex, clock):

        self._sendCommand('SPI' + str(spiIndex) + ' CLK ' + str(clock))
        result = self._readResponse()

        return result

    def getClockSPI(self, spiIndex):

        self._sendCommand('SPI' + str(spiIndex) + ' CLK ?')
        result = self._readResponse()

        return result

    def setOrderSPI(self, spiIndex, order):

        self._sendCommand('SPI' + str(spiIndex) + ' ORDER ' + order)
        result = self._readResponse()

        return result

    def getOrderSPI(self, spiIndex):

        self._sendCommand('SPI' + str(spiIndex) + ' ORDER ?')
        result = self._readResponse()

        return result

    def setModeSPI(self, spiIndex, mode):

        self._sendCommand('SPI' + str(spiIndex) + ' MODE ' + str(mode))
        result = self._readResponse()

        return result

    def getModeSPI(self, spiIndex):

        self._sendCommand('SPI' + str(spiIndex) + ' MODE ?')
        result = self._readResponse()

        return result

    def getCpolSPI(self, spiIndex):

        self._sendCommand('SPI' + str(spiIndex) + ' CPOL ?')
        result = self._readResponse()

        return result

    def getCphaSPI(self, spiIndex):

        self._sendCommand('SPI' + str(spiIndex) + ' CPHA ?')
        result = self._readResponse()

        return result

    def setBitsPerTransferSPI(self, spiIndex, bits):

        self._sendCommand('SPI' + str(spiIndex) + ' TXBITS ' + str(bits))
        result = self._readResponse()

        return result

    def getBitsPerTransferSPI(self, spiIndex):

        self._sendCommand('SPI' + str(spiIndex) + ' TXBITS ?')
        result = self._readResponse()

        return result

    def beginSPI(self, spiIndex):

        self._sendCommand('SPI' + str(spiIndex) + ' BEGIN')
        result = self._readResponse()

        return result

    def transferSPI(self, spiIndex, data):

        self._sendCommand('SPI' + str(spiIndex) + ' TXRX ' + str(data))
        result = self._readResponse()

        return result

    def transferBufferSPI(self, spiIndex, numBytes):
        self._sendCommand('SPI' + str(spiIndex) + ' TXRX BUF0 ' + str(numBytes))
        result = self._readResponse()

        return result

    def endSPI(self, spiIndex):

        self._sendCommand('SPI' + str(spiIndex) + ' END')
        result = self._readResponse()

        return result

    ## UART COMMANDS

    def setBaudRateUART(self, uartIndex, baud):

        self._sendCommand('UART' + str(uartIndex) + ' BAUD ' + str(baud))
        result = self._readResponse()

        return result

    def getBaudRateUART(self, uartIndex):

        self._sendCommand('UART' + str(uartIndex) + ' BAUD ?')
        result - self._readResponse()

        return result

    def setDataBitsUART(self, uartIndex, databits):

        self._sendCommand('UART' + str(uartIndex) + ' DATABITS ' + str(databits))
        result = self._readResponse()

        return result

    def getDataBitsUART(self, uartIndex):

        self._sendCommand('UART' + str(uartIndex) + ' DATABITS ?')
        result = self._readResponse()

        return result

    def setParityUART(self, uartIndex, parity):

        self._sendCommand('UART' + str(uartIndex) + ' PARITY ' + str(parity))
        result = self._readResponse()

        return result

    def getParityUART(self, uartIndex):

        self._sendCommand('UART' + str(uartIndex) + ' PARITY ?')
        result = self._readResponse()

        return result

    def setStopBitsUART(self, uartIndex, stopbits):

        self._sendCommand('UART' + str(uartIndex) + ' STOPBITS ' + str(stopbits))
        result = self._readResponse()

        return result

    def getStopBitsUART(self, uartIndex):

        self._sendCommand('UART' + str(uartIndex) + ' STOPBITS ?')
        result = self._readResponse()

        return result

    def setEscapeSequenceUART(self, uartIndex, escape):

        self._sendCommand('UART' + str(uartIndex) + ' ESC ' + escape)
        result = self._readResponse()

        return result

    def getEscapeSequenceUART(self, uartIndex):

        self._sendCommand('UART' + str(uartIndex) + ' ESC ?')
        result = self._readResponse()

        return result

    def beginBridgeUART(self, uartIndex):

        self._sendCommand('UART' + str(uartIndex) + ' BEGIN')
        result = self._readResponse()

        self.manager.startUartBridge()

        return result

    def stopBridgeUART(self, sequence):

        self.manager.stopUartBridge()
        self._txdQueue.put(sequence)
        result = self._readResponse()

        return result

    def writeBridgeUART(self, data):

        self._txdQueue.put(data)

    def readBridgeUART(self):

        return self._rxdQueue.get()

    ## 1WIRE COMMANDS

    def begin1WIRE(self, oneWireIndex, pin, pullup):

        if not pullup:
            self._sendCommand('1WIRE' + str(oneWireIndex) + ' BEGIN ' + str(pin))
        else:
            self._sendCommand('1WIRE' + str(oneWireIndex) + ' BEGIN ' + str(pin) + ' PULL')

        result = self._readResponse()

        return result

    def reset1WIRE(self, oneWireIndex):

        self._sendCommand('1WIRE' + str(oneWireIndex) + ' RESET')
        result = self._readResponse()

        return result

    def writeByte1WIRE(self, oneWireIndex, data, powered = False):

        if not powered:
            self._sendCommand('1WIRE' + str(oneWireIndex) + ' WRITE ' + str(data))
        else:
            self._sendCommand('1WIRE' + str(oneWireIndex) + ' WRITE ' + str(data) + ' POWER')

        result = self._readResponse()

        return result

    def readByte1WIRE(self, oneWireIndex):

        self._sendCommand('1WIRE' + str(oneWireIndex) + ' READ')
        result = self._readResponse()

        return result

    def select1WIRE(self, oneWireIndex):

        self._sendCommand('1WIRE' + str(oneWireIndex) + ' SELECT')
        result = self._readResponse()

        return result

    def skip1WIRE(self, oneWireIndex):

        self._sendCommand('1WIRE' + str(oneWireIndex) + ' SKIP')
        result = self._readResponse()

        return result

    def depower1WIRE(self, oneWireIndex):

        self._sendCommand('1WIRE' + str(oneWireIndex) + ' DEPOWER')
        result = self._readResponse()

        return result

    def getAddress1WIRE(self, oneWireIndex):

        self._sendCommand('1WIRE' + str(oneWireIndex) + ' ADDR ?')
        result = self._readResponse()

        return result

    def search1WIRE(self, oneWireIndex, normalSearch = True):

        if normalSearch:
            self._sendCommand('1WIRE' + str(oneWireIndex) + ' SEARCH')
        else:
            self._sendCommand('1WIRE' + str(oneWireIndex) + ' SEARCH COND')

        result = self._readResponse()

        return result

    def resetSearch1WIRE(self, oneWireIndex):

        self._sendCommand('1WIRE' + str(oneWireIndex) + ' SEARCH RESET')
        result = self._readResponse()

        return result

    def targetSearch1WIRE(self, oneWireIndex, target):

        self._sendCommand('1WIRE' + str(oneWireIndex) + ' SEARCH ' + str(target))
        result = self._readResponse()

        return result

    ## SWI COMMANDS

    def beginSWI(self, swiIndex, pin, pullup):

        if not pullup:
            self._sendCommand('SWI' + str(swiIndex) + ' BEGIN ' + str(pin))
        else:
            self._sendCommand('SWI' + str(swiIndex) + ' BEGIN ' + str(pin) + ' PULL')

        result = self._readResponse()

        return result

    def sendTokenSWI(self, swiIndex, token):

        self._sendCommand('SWI' + str(swiIndex) + ' TOKEN ' + str(token))
        result = self._readResponse()

        return result

    def sendFlagSWI(self, swiIndex, flag):

        self._sendCommand('SWI' + str(swiIndex) + ' FLAG ' + str(flag))
        result = self._readResponse()

        return result

    def sendCommandFlagSWI(self, swiIndex):

        self._sendCommand('SWI' + str(swiIndex) + ' FLAG COMMAND')
        result = self._readResponse()

        return result

    def sendTransmitFlagSWI(self, swiIndex):

        self._sendCommand('SWI' + str(swiIndex) + ' FLAG TRANSMIT')
        result = self._readResponse()

        return result

    def sendIdleFlagSWI(self, swiIndex):

        self._sendCommand('SWI' + str(swiIndex) + ' FLAG IDLE')
        result = self._readResponse()

        return result

    def sendSleepFlagSWI(self, swiIndex):

        self._sendCommand('SWI' + str(swiIndex) + ' FLAG SLEEP')
        result = self._readResponse()

        return result

    def transmitByteSWI(self, swiIndex, data):

        self._sendCommand('SWI' + str(swiIndex) + ' TX ' + str(data))
        result = self._readResponse()

        return result

    def receiveBytesSWI(self, swiIndex, count):

        self._sendCommand('SWI' + str(swiIndex) + ' RX ' + str(count))
        result = self._readResponse()

        return result

    def setPacketOpCodeSWI(self, swiIndex, opCode):

        self._sendCommand('SWI' + str(swiIndex) + ' PACKET OPCODE ' + str(opCode))
        result = self._readResponse()

        return result

    def setPacketParam1SWI(self, swiIndex, value):

        self._sendCommand('SWI' + str(swiIndex) + ' PACKET PARAM1 ' + str(value))
        result = self._readResponse()

        return result

    def setPacketParam2SWI(self, swiIndex, value):

        self._sendCommand('SWI' + str(swiIndex) + ' PACKET PARAM2 ' + str(value))
        result = self._readResponse()

        return result

    def setPacketDataSWI(self, swiIndex, index, value):

        self._sendCommand('SWI' + str(swiIndex) + ' PACKET DATA ' + str(index) + ' ' + str(value))
        result = self._readResponse()
        
        return result;

    def setPacketDataFromBufferSWI(self, swiIndex, byteCount, bufferName):

        self._sendCommand('SWI' + str(swiIndex) + ' PACKET DATA ' + str(byteCount) + ' ' + str(bufferName))
        result = self._readResponse();

        return result;

    def sendPacketSWI(self, swiIndex):

        self._sendCommand('SWI' + str(swiIndex) + ' PACKET SEND')
        result = self._readResponse()

        return result

    def clearPacketSWI(self, swiIndex):

        self._sendCommand('SWI' + str(swiIndex) + ' PACKET CLEAR')
        result = self._readResponse()

        return result

    ## IO COMMANDS

    ## GET/SET IOpinMode
    ##
    ## parameters:
    ##  ioNumber    0, 1, 2, 3, 4
    ##  mode        DIN, DOUT, AIN, AOUT, TOUCH, PWM
    ##
    ##  Note that not all modes are available on all pins

    def setIOpinMode(self, ioNumber, mode):

        self._sendCommand('IO' + str(ioNumber) + ' MODE ' + mode)
        result = self._readResponse()

        return result

    def getIOpinMode(self, ioNumber):

        self._sendCommand('IO' + str(ioNumber) + ' MODE ?')
        result = self._readResponse()

        return result

    ## GET/SET IOpinInterrupt
    ##
    ## parameters:
    ##  ioNumber    0, 1, 2, 3, 4
    ##  intMode     CHANGE|CHANGING, RISE|RISING, FALL|FALLING, NONE|OFF|0

    def setIOpinInterrupt(self, ioNumber, intMode):

        self._sendCommand('IO' + str(ioNumber) + ' INT ' + intMode)
        result = self._readResponse()

        return result

    def getIOpinInterrupt(self, ioNumber):

        self._sendCommand('IO' + str(ioNumber) + ' INT ?')
        result = self._readResponse()

        return result

    ## GET/SET IOpinValue
    ##
    ## parameters:
    ##  ioNumber    0, 1, 2, 3, 4
    ##  value       0|LOW, 1|HIGH, x%, Volts

    def setIOpinValue(self, ioNumber, value):

        self._sendCommand('IO' + str(ioNumber) + ' VALUE ' + str(value))
        result = self._readResponse()

        return result

    def getIOpinValue(self, ioNumber):

        self._sendCommand('IO' + str(ioNumber) + ' VALUE ?')
        result = self._readResponse()

        return result

    def getIOpinInterruptFlag(self, ioNumber):

        result = self.interruptCheck('!I0' + str(ioNumber))

        return result

    def clearIOpinInterruptFlag(self, ioNumber):

        self.interruptClear('!IO' + str(ioNumber))