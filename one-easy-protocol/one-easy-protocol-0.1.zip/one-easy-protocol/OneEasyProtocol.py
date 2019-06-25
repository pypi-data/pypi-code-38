
# coding: utf-8

# In[5]:


import serial
import time
import sys
import glob
    
class Protocol(object):
    
    def __init__(self):
        self.gripperopen =  'GRIPPEROPEN'
        self.gripperclose = 'GRIPPERCLOSE'
        self.lighton =      'LIGHTON'
        self.lightoff =     'LIGHTOFF'
        self.lightred =     'RED'
        self.lightgreen =   'GREEN'
        self.lightblue =    'BLUE'
        self.lightyellow =  'YELLOW'
        self.lightmagenta = 'MAGENTA'
        self.lightcyan =    'CYAN'
        self.lightwhite =   'WHITE'
        self.extmotoron =   'EXTMOTORON'
        self.extmotoroff =  'EXTMOTOROFF'
        
class Color(object):
    
    def __init__(self):
        self.__protocol = Protocol()
        self.red =     self.__protocol.lightred
        self.green =   self.__protocol.lightgreen
        self.blue =    self.__protocol.lightblue
        self.yellow =  self.__protocol.lightyellow
        self.magenta = self.__protocol.lightmagenta
        self.cyan =    self.__protocol.lightcyan
        self.white =   self.__protocol.lightwhite
        
class Pos(object):
    
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

class ServoData(object):
    
    def __init__(self):
        self.a = 0.0
        self.b = 0.0
        self.c = 0.0
        
class Utils (object):
    
    def __init__(self,info = False):
        self._info = info
    
    def valueToString(self,value):
        
        if(value>-1000.0 and value<1000.0):
            
            upvalue = value * 10.0
            tempstr = int(upvalue)
            string = str(tempstr)
            
            if (value > -1.0 and value < 1.0):
                string = '000' + string
                
            elif(value> -10.0 and value < 10.0):
                string = '00' + string
                
            elif(value> -100.0 and value < 100.0):
                string = '0' + string
            
            elif (value > -1000.0 and value < 1000.0):
                string = string 
            else:
                return '0000'
                
            if(value>=0.0):
                string = '+' + string
            else:
                string = string.replace('-','')
                string = '-' + string
            return string
        
        else:
            if (self._info == True): print("Values not valid! Please check you values. Valid numbers are between -999.9 and 999.9")
            return None
        
    def posToString(self,pos):
        strX=self.valueToString(pos.x)
        strY=self.valueToString(pos.y)
        strZ=self.valueToString(pos.z)
        return strX,strY,strZ
    
    def fillData(self,txString,length=22):
        i=0
        if len(txString) < length:
            i=len(txString)
            while(i<length):
                txString = txString +'#' 
                i+=1
        return txString

class Basic(object):
    
    def __init__(self, connection=None, robotid=None, deviceid=None,info = False):
        self._info = info
        self._robotid = robotid
        self._deviceid = deviceid
        self._connection = connection
        self._protocol = Protocol()
        self._utils = Utils()
        
    def _printInfo(self,status):
        self._info=status
        return 0
        
    def _checkParameters(self):
        if( self._robotid==None and self._deviceid==None and self._connection==None):
            return 1
        else:
            return 0
        
    def _sendData(self,txString):
        txBytes = str.encode(txString)
        self._connection.reset_output_buffer()
        time.sleep(0.01)
        self._connection.write(txBytes)
        if (self._info == True):print('One easy protocol: ' + txString)
        self._connection.reset_input_buffer()
        time.sleep(0.01)
        while True:
            line = self._connection.read(1)
            if line == self._robotid.encode():
                break
        return 0        

class Functions(Basic):  
    
    def waitFor(self,milliseconds):
        if(self._checkParameters()==0):
            seconds = milliseconds/1000.0
            time.sleep(int(seconds))
        return 0
    
class Move(Basic):

    def ptp(self,positionX,positionY,positionZ,speed=50.0):
        pos = Pos()
        if(self._checkParameters()==0):
            pos.x = positionX
            pos.y = positionY
            pos.z = positionZ
            x,y,z = self._utils.posToString(pos)
            
            v = self._utils.valueToString(speed)
            v = v.replace('+','')
            v = v.replace('-','')
            
            txString = self._robotid + self._deviceid +'M'+ x + y + z + v
            txString = self._utils.fillData(txString)
            self._sendData(txString)
        return 0
        
    def home(self):
        if(self._checkParameters()==0):
            self.ptp(0.0,0.0,85.0,50.0)
        return 0
    
class Gripper(Basic):
    
    def open(self):
        if(self._checkParameters()==0):
            txString = self._robotid + self._deviceid + self._protocol.gripperopen
            txString = self._utils.fillData(txString)
            self._sendData(txString)
        return 0
    
    def close(self):
        if(self._checkParameters()==0):
            txString = self._robotid + self._deviceid + self._protocol.gripperclose
            txString = self._utils.fillData(txString)
            self._sendData(txString)
        return 0
        
class ExtMotor(Basic):
        
    def start(self,speed=100.0):
        if(self._checkParameters()==0):
            v = self._utils.valueToString(speed)
            v = v.replace('+','')
            v = v.replace('-','')
            txString = self._robotid + self._deviceid + self._protocol.extmotoron
            txString = self._utils.fillData(txString,18)
            txString = txString + v
            self._sendData(txString)
        return 0
        
    def stop(self):
        if(self._checkParameters()==0):
            txString = self._robotid + self._deviceid + self._protocol.extmotoroff
            txString = self._utils.fillData(txString)
            self._sendData(txString)
        return 0
        
    def setSpeed(self,speed):
        if(self._checkParameters()==0):
            v = self._utils.valueToString(speed)
            v = v.replace('+','')
            v = v.replace('-','')
            txString = self._robotid + self._deviceid + self._protocol.extmotoron
            txString = self._utils.fillData(txString,18)
            txString = txString + v
            self._sendData(txString)
        return 0
        
class Light(Basic):
    
    def on(self, intensity=100.0):
        if(self._checkParameters()==0):
            i = self._utils.valueToString(intensity)
            i = i.replace('+','')
            i = i.replace('-','')
            txString = self._robotid + self._deviceid + self._protocol.lighton
            txString = self._utils.fillData(txString,18)
            txString = txString + i
            self._sendData(txString)
        return 0
        
    def off(self):
        if(self._checkParameters()==0):
            txString = self._robotid + self._deviceid + self._protocol.lightoff
            txString = self._utils.fillData(txString)
            self._sendData(txString)
        return 0
        
    def setColour(self, colour, intensity = 100.0):
        if(self._checkParameters()==0):
            i = self._utils.valueToString(intensity)
            i = i.replace('+','')
            i = i.replace('-','')
            txString = self._robotid + self._deviceid + self._protocol.lighton + '#' + colour
            txString = self._utils.fillData(txString,18)
            txString = txString + i
            self._sendData(txString)
        return 0
             
class EasyProtocol(object):
    def __init__(self, info = False):
        self.__info = info
        self.__timeout = 1
        self.__port = ""
        self.__baudrate = 9600
        self.__connection = serial.Serial()
        self.__robotid = ''
        
        self.move = Move()
        self.gripper = Gripper()
        self.extmotor = ExtMotor()
        self.light = Light()
        self.functions = Functions()
    
    def printInfo(self,status):
        self.__info = status
        self.move._printInfo(status)
        self.gripper._printInfo(status)
        self.extmotor._printInfo(status)
        self.light._printInfo(status)
        self.functions._printInfo(status)
        
    def setPort(self,port,baudrate = 9600,timeout = 1):
        self.__timeout = timeout
        self.__port = port
        self.__baudrate = baudrate
        return 0
    
    def __setCommunication(self):
        if (self.__info == True):print("Try to connect robot...")
        if (self.__info == True):print("ID: "+ self.__robotid+" / "+"Port: "+self.__port+" / "+"Baudrate: "+str(self.__baudrate))
        traffic=None
        try:
            self.__connection = serial.Serial(port=self.__port,baudrate=self.__baudrate,timeout=self.__timeout)
            time.sleep(0.25)
            for i in range(10):
                traffic = self.__connection.read(1)
                time.sleep(0.25)
                if traffic == self.__robotid.encode():
                    if (self.__info == True):print("...connection sucessfully etablished!")
                    break
                if (self.__info == True):print("...searching for robot ("+str(i+1)+'/'+str(10)+')')
                traffic = None
        except:
            if (self.__info == True):print("...no robot available. Please check your parameters!")
            
        if traffic == None:
            if (self.__info == True):print("...no robot available. Please connect your robot and activate serial communication software!")
            if (self.__info == True):print("Dont't forget to activate the USB Control Mode (Ctrl) using the switch on the circuit board!")
        elif traffic!=None:
            self.move = Move(self.__connection,self.__robotid,self.__deviceid,self.__info)
            self.gripper = Gripper(self.__connection,self.__robotid,self.__deviceid,self.__info)
            self.extmotor = ExtMotor(self.__connection,self.__robotid,self.__deviceid,self.__info)
            self.light = Light(self.__connection,self.__robotid,self.__deviceid,self.__info)
            self.functions = Functions(self.__connection,self.__robotid,self.__deviceid,self.__info)
        return 0
    
    def __find_ports(self):
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i+1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            portsUSB = glob.glob('/dev/ttyUSB*')
            portsACM = glob.glob('/dev/ttyACM*')
            ports = portsUSB + portsACM
        else:
            if (self.__info == True):print("Can' finding ports on your operating system")
            ports = ""
        return ports
    
    def find_robot(self):
        ports = self.__find_ports()
        if ports != "":
            traffic=None
            portname=""
            for port in ports:
                try:
                    self.__connection = serial.Serial(port,baudrate=self.__baudrate,timeout=self.__timeout)
                    if (self.__info == True):print("Checking port: " + port +"...")
                    check = ""
                    time.sleep(0.25)
                    self.__connection.reset_input_buffer()
                    time.sleep(0.25)
                    traffic = self.__connection.read(1)
                    time.sleep(0.25)
                    if traffic != None and str(traffic.decode()) != "":
                        check = str(traffic.decode())
                        
                    time.sleep(0.25)
                    self.__connection.reset_input_buffer()
                    time.sleep(0.25)
                    traffic = self.__connection.read(1)
                    time.sleep(0.25)
                    if traffic != None and str(traffic.decode()) == check and check != "":
                        if (self.__info == True):print("...found robot with ID: " + str(traffic.decode()) + " on port: "+ port)
                        self.__connection.close()
                        self.__robotid = traffic.decode()
                        self.__port = port
                        break
                    self.__robotid = None
                    self.__connection.close()
                except:
                    if (self.__info == True):print("...error while checking port: "+ port) 
            else:
                self.__port = None
                if (self.__info == True):print("...no robot available. Please connect your robot and activate serial communication software!")
                if (self.__info == True):print("Dont't forget to activate the USB Control Mode (Ctrl) using the switch on the circuit board!")
        return 
    
    def start(self,robotid=1,deviceid=0):
        robotidstr = str(robotid)
        deviceidstr = str(deviceid)
        if len(robotidstr)==1 and len(deviceidstr)==1:
            self.__robotid = robotidstr
            self.__deviceid = deviceidstr
            if self.__port != None:
                self.__setCommunication()
        else:
            if (self.__info == True):print("Please enter only one symbol to set the Robot-ID and Device-ID") 
        return 0
    
    def stop(self):
        self.__connection.close()
        
    def __del__(self):
        self.stop()
        
    def __waitForRobot(self):
        if (self.__info == True):print("Robot executes a command...")
        for i in range(60):
            line = self.__connection.read(1)
            if line == self.__robotid.encode():
                break
            if (self.__info == True):print("...")
        if i+1==60:
            if (self.__info == True):print("Timout! Please check the connection to the robot!")
        else:   
            if (self.__info == True):print("Robot is waiting for signals...")
        return 0

