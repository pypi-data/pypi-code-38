'''
Quarch Power Module Calibration Functions
Written for Python 3.6 64 bit

M Dearman April 2019
'''

'''
Calibration Flow
    Connect to PPM
    Connect to Keithley
    step through a set of values and get ADC vs Reference Value
    evaluate results vs defined limits


'''

#Imports QuarchPy library, providing the functions needed to use Quarch modules
#from quarchpy import quarchDevice #, scanDevices

# Import other libraries used in the examples
from functools import reduce
#from quarchpy.calibration import *
from quarchpy.calibration.deviceHelpers import sendAndVerifyCommand,returnMeasurement
import quarchpy.calibration.calibrationConfig
import types
from time import sleep,time
from math import ceil
from quarchpy.calibration.PowerModuleCalibration import *
import threading
from quarchpy.user_interface import *

class HDPowerModule (PowerModule):

    V5_VOLT_OFFSET_ADDR         = '0xF002'
    V5_VOLT_MULTIPLIER_ADDR     = '0xF003'
    V5_LOW_OFFSET_ADDR          = '0xF004'
    V5_LOW_MULTIPLIER_ADDR      = '0xF005'
    V5_LEAKAGE_MULTIPLIER_ADDR  = '0xF006'
    V5_HIGH_OFFSET_ADDR         = '0xF007'
    V5_HIGH_MULTIPLIER_ADDR     = '0xF008'
    V12_VOLT_OFFSET_ADDR        = '0xF009'
    V12_VOLT_MULTIPLIER_ADDR    = '0xF00A'
    V12_LOW_OFFSET_ADDR         = '0xF00B'
    V12_LOW_MULTIPLIER_ADDR     = '0xF00C'
    V12_LEAKAGE_MULTIPLIER_ADDR = '0xF00D'
    V12_HIGH_OFFSET_ADDR        = '0xF00E'
    V12_HIGH_MULTIPLIER_ADDR    = '0xF00F'
    V5_OUTPUT_OFFSET_ADDR       = '0xF010'
    V12_OUTPUT_OFFSET_ADDR      = '0xF011'

    def open_module(self):

        # get output mode
        self.voltageMode = self.dut.sendCommand("conf:out:mode?")

    def close_module(self):
            
        # write 0xaa55 to register 0xf012 to tell module it is calibrated
        sendAndVerifyCommand(self.dut,"write 0xf012 0xaa55")
        # change voltage mode back to original setting
        currentMode = self.dut.sendCommand("conf:out:mode?")
        if self.voltageMode != None and currentMode != self.voltageMode:
            sendAndVerifyCommand(self.dut,"conf:out:mode " + self.voltageMode)
            sleep(4)
        # reset the module
        #TODO: (this will crash as there is no response )self.dut.sendCommand("*rst")

    class HDCalibration (Calibration):

        def __init__(self): 
            super().__init__()



        def init_cal(self,voltage):

            # get output mode
            mode = self.powerModule.dut.sendCommand("conf:out:mode?")

            #if output mode is not 5v, set it
            while mode != "5V":
                sendAndVerifyCommand(self.powerModule.dut,"conf:out:mode 5v")
                #wait for module to change mode
                sleep(4)
                mode = self.powerModule.dut.sendCommand("conf:out:mode?")

            # power up
            sendAndVerifyCommand(self.powerModule.dut,"power up")

            # disable pull down fets
            sendAndVerifyCommand(self.powerModule.dut,"CONFig:OUTput:12v:PULLdown OFF")
            sendAndVerifyCommand(self.powerModule.dut,"CONFig:OUTput:5v:PULLdown OFF")

            # check averaging and set to max
            if (self.powerModule.dut.sendCommand("rec:ave?").find("32k") != 0):
                sendAndVerifyCommand(self.powerModule.dut,"rec:ave 32k")

            # set module into calibration mode (again?)
            self.powerModule.dut.sendCommand("write 0xf000 0xaa55")   # will not verify
            self.powerModule.dut.sendCommand("write 0xf000 0x55aa")   # will not verify

            #check we are connected to the right channel
            if voltage.upper() == "12V":
                lower_limit = 11
                upper_limit = 13
                sendAndVerifyCommand(self.powerModule.dut,"sig:12v:volt 12000")
            elif voltage.upper() == "5V":
                lower_limit = 4
                upper_limit = 6
                sendAndVerifyCommand(self.powerModule.dut,"sig:5v:volt 5000")
            else:
                raise ValueError ("Invalid voltage specified")

            result = self.powerModule.load.measureNoLoadVoltage()

            while (result < lower_limit or result > upper_limit):

                if voltage.upper() == "12V":
                    lower_limit = 11
                    upper_limit = 13
                    sendAndVerifyCommand(self.powerModule.dut,"sig:12v:volt 12000")
                elif voltage.upper() == "5V":
                    lower_limit = 4
                    upper_limit = 6
                    sendAndVerifyCommand(self.powerModule.dut,"sig:5v:volt 5000")

                showDialog("Check load connection","please connect the Keithley to the " + voltage + " channel")
                result = self.powerModule.load.measureNoLoadVoltage()

            # check temperature
            minTemp = 32    # this is the minimum internal temperature we require before we will do a calibration
            tempTimeout = 0
            rotateChar = '-'
            unitTemp = self.powerModule.dut.sendCommand('meas:temp unit?')
            if (int(unitTemp[0:2]) < minTemp):
                printText("unit is cold, waiting for it to warm up")
                printText("")

                # heat up unit
                if voltage.upper() == "12V":
                    sendAndVerifyCommand(self.powerModule.dut,"sig:12v:volt 10000") # 15V - 10V = 5V FET Voltage
                    self.powerModule.load.setReferenceCurrent(1) # 5V * 1A = 5W
                elif voltage.upper() == "5V":
                    sendAndVerifyCommand(self.powerModule.dut,"sig:5v:volt 1000") # 6V - 1V = 5V FET Voltage
                    self.powerModule.load.setReferenceCurrent(1) #1A * 1A = 5W

                while(int(unitTemp[0:2]) < minTemp):
                    printText(rotateChar + " required internal temperature: " + str(minTemp) + "C, current internal temperature: " + unitTemp,end = '\r')
                    sleep(1)
                    tempTimeout += 1
                    # rotate the icon to show we're still alive
                    if rotateChar == '-':
                        rotateChar = '\\'
                    elif rotateChar == '\\':
                        rotateChar = '|'
                    elif rotateChar == '|':
                        rotateChar = '/'
                    elif rotateChar == '/':
                        rotateChar = '-'
                    unitTemp = self.powerModule.dut.sendCommand('meas:temp unit?')
                    if tempTimeout == 600:
                        raise Exception('Timeout waiting for module to reach working temperature')

                                # heat up unit
                if voltage.upper() == "12V":
                    sendAndVerifyCommand(self.powerModule.dut,"sig:12v:volt 12000")
                    self.powerModule.load.setReferenceCurrent(0)
                elif voltage.upper() == "5V":
                    sendAndVerifyCommand(self.powerModule.dut,"sig:5v:volt 5000")
                    self.powerModule.load.setReferenceCurrent(0)

        def set_12v_volt(self,value):

            #set source voltage
            sendAndVerifyCommand(self.powerModule.dut,"sig:12v:volt " + str(value))

            # this sleep is necessary to allow the output to update before taking more measurements
            # affects voltage calibration and leakage calibration
            sleep(0.2)

        def get_12v_volt(self):
        
            response = returnMeasurement(self.powerModule.dut,"sig:12v:volt?")
            return int(response[0])

        def meas_12v_volt(self):

            response = returnMeasurement(self.powerModule.dut,"meas:volt:12v?")

            # returnMeasurement() returns [value,units] we only need the value, which is actually ADC levels * 2^shift
            return int(response[0])

        def meas_12v_cur(self):

            response = returnMeasurement(self.powerModule.dut,"meas:cur 12v?")
            return float(response[0])*1000

        def set_5v_volt(self,value):

            #set source voltage
            sendAndVerifyCommand(self.powerModule.dut,"sig:5v:volt " + str(value))

            # this sleep is necessary to allow the output to update before taking more measurements
            # affects voltage calibration and leakage calibration
            sleep(0.2)

        def get_5v_volt(self):

            #set source voltage
            response = returnMeasurement(self.powerModule.dut,"sig:5v:volt?")

            return int(response[0])

        def meas_5v_volt(self):

            response = returnMeasurement(self.powerModule.dut,"meas:volt:5v?")

            # returnMeasurement() returns [value,units] we only need the value, which is actually ADC levels * 2^shift
            return int(response[0])

        def meas_5v_cur(self):

            response = returnMeasurement(self.powerModule.dut,"meas:cur 5v?")
            return float(response[0])*1000

        def finish_cal(self):

            #turn off load
            self.powerModule.load.setReferenceCurrent(0)
            self.powerModule.load.disable()

            #turn off dut
            sendAndVerifyCommand(self.powerModule.dut,"power down")
            # set power rails to nominal voltage
            sendAndVerifyCommand(self.powerModule.dut,"sig:12v:volt 5000")
            sendAndVerifyCommand(self.powerModule.dut,"sig:12v:volt 12000")
            # turn dut to autoranging
            sendAndVerifyCommand(self.powerModule.dut,"write 0xf001 0x0100")

        def report(self,action,data):

            report = []

            # check errors and generate report
            report.append('\n')

            if action == "calibrate":
               report.append("\t" + '{0:>11}'.format('Reference') + '   ' + '{0:>10}'.format('Raw Value') + '   ' + '{0:>10}'.format('Result') + '   ' + '{0:>10}'.format('Error') + '   ' + '{0:>13}'.format('+/-(Abs Error,% Error)') + '   ' + '{0:>10}'.format('Pass'))
            elif action == "verify":
                report.append("\t" + '{0:>11}'.format('Reference') + '   ' + '{0:>10}'.format('Result') + '   ' + '{0:>10}'.format('Error') + '   ' + '{0:>13}'.format('+/-(Abs Error,% Error)') + '   ' + '{0:>10}'.format('Pass'))

            report.append("========================================================================================")        

            # zero worst case error vars
            worstAbsError = 0
            worstRelError = 0
            worstRef = None
            overallResult = True

            # for each calibration reference
            for thisLine in data:
                reference = thisLine[1]
                value = thisLine[0]

                # for calibration, replace value with calibrated result
                if action =="calibrate":
                    value = self.getResult(value)

                # work out errors
                (actError,errorSign,absError,relError,result) = getError(reference,value,self.absErrorLimit,self.relErrorLimit)
            
                # compare/replace with running worst case
                if absError >= worstAbsError:
                    if relError >= worstRelError:
                        worstAbsError = absError
                        worstRelError = relError
                        worstCase = errorSign + "(" + str(absError) + self.units + "," + "{:.3f}".format(relError) + "%) @ " + '{:.3f}'.format(reference) + self.units

                # update overall pass/fail
                if result != True:
                    overallResult = False

                #generate report
                passfail = lambda x: "Pass" if x else "Fail"
                if action == "calibrate":
                    report.append("\t" + '{:>11.3f}'.format(reference) + '   ' + '{:>10.1f}'.format(value) + '   ' + '{:>10.1f}'.format(value) + '   ' + "{:>10.3f}".format(actError) + '   ' + '{0:>16}'.format(errorSign + "(" + str(absError) + self.units + "," + "{:.3f}".format(relError) + "%)") + '   ' + '{0:>10}'.format(passfail(result)))
                elif action == "verify":
                    report.append("\t" + '{:>11.3f}'.format(reference) + '   ' + '{:>10.1f}'.format(value) + '   ' + "{:>10.3f}".format(actError) + '   ' + '{0:>16}'.format(errorSign + "(" + str(absError) + self.units + "," + "{:.3f}".format(relError) + "%)") + '   ' + '{0:>10}'.format(passfail(result)))
 
            report.append("========================================================================================")  
            report.append('\n')

            if action == "calibrate":
                report.append("Calculated Multiplier: " + str(self.multiplier.originalValue()) + ", Calculated Offset: " + str(self.offset.originalValue()))
                report.append("Stored Multiplier: " + str(self.multiplier.storedValue()) + ", Stored Offset: " + str(self.offset.storedValue()))
                report.append("Multiplier Register: " + self.multiplier.hexString(4) + ", Offset Register: " + self.offset.hexString(4))

            return {"result":overallResult,"worst case":worstCase,"report":('\n'.join(report))}

    class HD12VOffsetCalibration (HDCalibration):

        def __init__(self,powerModule):

            self.powerModule = powerModule
            self.absErrorLimit = 120     # the output can be within 1% of 12000mV = 120
            self.relErrorLimit = 0
            self.test_min = 10800
            self.test_max = 13200
            self.test_steps = 20
            self.units = "mV"
            self.scaling = 3.538305666
            self.multiplier_signed = False
            self.multiplier_int_width = 16
            self.multiplier_frac_width = 16
            self.offset_signed = False
            self.offset_int_width = 13
            self.offset_frac_width = 0

        def init(self):
 
            # Initialise the module
            super().init_cal("12v")
            # clear the output offset register by setting it to zero
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V12_OUTPUT_OFFSET_ADDR + " 0x0000")

        def setRef(self,value):

            super().set_12v_volt(value)

        def readRef(self):

            return load_meas_volt(self.powerModule.load)-11998   # this is the difference in mV between the current measured voltage and the nominal voltage

        def readVal(self):

            return (int(self.powerModule.dut.sendCommand("read 0x0006"),16)-0xD3F)*self.scaling  # this is the difference in mV between the current set point and the nominal voltage

        def setCoefficients(self):

            # set 12v output offset
            self.powerModule.dut.sendCommand("write " + HDPowerModule.V12_OUTPUT_OFFSET_ADDR + " " + self.offset.hexString(4))
            #sendAndVerifyCommand(self.powerModule.dut,"write 0xf011 " + self.offset.hexString(4)) # negative offsets don't read back in 1.5 and below

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get 12v output offset
            coefficients["offset"] = self.powerModule.dut.sendCommand("read " + HDPowerModule.V12_OUTPUT_OFFSET_ADDR)
            return coefficients

        def writeCoefficients(self,coefficients):

            # write 12v output offset
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V12_OUTPUT_OFFSET_ADDR + " " + coefficients["offset"])

    class HD12VVoltageCalibration (HDCalibration):

        def __init__(self,powerModule):

            self.powerModule = powerModule
            self.absErrorLimit = 1
            self.relErrorLimit = 1
            self.test_min = 40
            self.test_max = 14400
            self.test_steps = 20
            self.units = "mV"
            self.scaling = 2
            self.multiplier_signed = False
            self.multiplier_int_width = 1
            self.multiplier_frac_width = 16
            self.offset_signed = True
            self.offset_int_width = 10
            self.offset_frac_width = 6

        def init(self):

            super().init_cal("12v")

            # set module into calibration mode (again?)
            self.powerModule.dut.sendCommand("write 0xf000 0xaa55")   # will not verify
            self.powerModule.dut.sendCommand("write 0xf000 0x55aa")   # will not verify
            # clear the multiplier and offset registers by setting them to zero
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V12_VOLT_MULTIPLIER_ADDR + " 0x0000")
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V12_VOLT_OFFSET_ADDR + " 0x0000")

            #set voltage to zero and wait 1 second to settle
            sendAndVerifyCommand(self.powerModule.dut,"sig:12v:volt 0")
            sleep(1)

        def setRef(self,value):

            super().set_12v_volt(value)

        def readRef(self):

            return load_meas_volt(self.powerModule.load)

        def readVal(self):
        
            return super().meas_12v_volt()

        def setCoefficients(self):

            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V12_VOLT_MULTIPLIER_ADDR + " " + self.multiplier.hexString(4))
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V12_VOLT_OFFSET_ADDR + " " + self.offset.hexString(4))

        def finish(self):
        
            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get 12v voltage multiplier
            coefficients["multiplier"] = self.powerModule.dut.sendCommand("read " + HDPowerModule.V12_VOLT_MULTIPLIER_ADDR)
            # get 12v voltage offset
            coefficients["offset"] = self.powerModule.dut.sendCommand("read " + HDPowerModule.V12_VOLT_OFFSET_ADDR)
            return coefficients

        def writeCoefficients(self,coefficients):

            # write 12v voltage multiplier
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V12_VOLT_MULTIPLIER_ADDR + " " + coefficients["multiplier"])
            # write 12v voltage offset
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V12_VOLT_OFFSET_ADDR + " " + coefficients["offset"])

    class HD12VLowCurrentCalibration (HDCalibration):

        def __init__(self,powerModule):

            self.powerModule = powerModule
            self.absErrorLimit = 2      # 2uA
            self.relErrorLimit = 2      # 2%
            self.test_min = 10      # 10uA
            self.test_max = 10000   # 1mA
            self.test_steps = 20
            self.units = "uA"
            self.scaling = 16
            self.multiplier_signed = False
            self.multiplier_int_width = 1
            self.multiplier_frac_width = 16
            self.offset_signed = True
            self.offset_int_width = 10
            self.offset_frac_width = 6

        def init(self):

            super().init_cal("12v")

            #set low current mode
            sendAndVerifyCommand(self.powerModule.dut,"write 0xf001 0x0101")
            # clear the multiplier and offset registers by setting them to zero
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V12_LOW_MULTIPLIER_ADDR + " 0x0000")
            #sendAndVerifyCommand(ppm,"write 0xf00b 0x0000")
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V12_LOW_OFFSET_ADDR + " 0x0000")
            #sendAndVerifyCommand(ppm,"write 0xf00c 0x0000")

        def setRef(self,value):
        
            load_set_cur(self.powerModule.load,value)

        def readRef(self):
        
            return load_meas_cur(self.powerModule.load)

        def readVal(self):
        
            return super().meas_12v_cur()

        def setCoefficients(self):
        
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V12_LOW_MULTIPLIER_ADDR + " " + self.multiplier.hexString(4))
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V12_LOW_OFFSET_ADDR + " " + self.offset.hexString(4))

        def finish(self):

            super().finish_cal()

        def report(self,data):
        
            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get 12v low current multiplier
            coefficients["multiplier"] = self.powerModule.dut.sendCommand("read " + HDPowerModule.V12_LOW_MULTIPLIER_ADDR)
            # get 12v low current offset
            coefficients["offset"] = self.powerModule.dut.sendCommand("read " + HDPowerModule.V12_LOW_OFFSET_ADDR)
            return coefficients

        def writeCoefficients(self,coefficients):

            # write 12v low current multiplier
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V12_LOW_MULTIPLIER_ADDR + " " + coefficients["multiplier"])
            # write 12v low current offset
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V12_LOW_OFFSET_ADDR + " " + coefficients["offset"])

    class HD12VHighCurrentCalibration (HDCalibration):

        def __init__(self,powerModule):

            self.powerModule = powerModule
            self.absErrorLimit = 2000   # 2mA
            self.relErrorLimit = 1      # 1%
            self.test_min = 1000    # 1mA
            self.test_max = 4000000 # 4A
            self.test_steps = 20
            self.units = "uA"
            self.scaling = 2048
            self.multiplier_signed = False
            self.multiplier_int_width = 1
            self.multiplier_frac_width = 16
            self.offset_signed = True
            self.offset_int_width = 10
            self.offset_frac_width = 6

        def init(self):

            super().init_cal("12v")

            #set high current mode
            sendAndVerifyCommand(self.powerModule.dut,"write 0xf001 0x0102")
            # clear the multiplier and offset registers by setting them to zero
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V12_HIGH_MULTIPLIER_ADDR + " 0x0000")
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V12_HIGH_OFFSET_ADDR + " 0x0000")

        def setRef(self,value):
        
            load_set_cur(self.powerModule.load,value)

        def readRef(self):
        
            return load_meas_cur(self.powerModule.load)

        def readVal(self):
        
            return super().meas_12v_cur()

        def setCoefficients(self):
        
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V12_HIGH_MULTIPLIER_ADDR + " " + self.multiplier.hexString(4))
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V12_HIGH_OFFSET_ADDR + " " + self.offset.hexString(4))

        def finish(self):
        
            super().finish_cal()

        def report(self,data):
        
            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get 12v high current multiplier
            coefficients["multiplier"] = self.powerModule.dut.sendCommand("read " + HDPowerModule.V12_HIGH_MULTIPLIER_ADDR)
            # get 12v high current offset
            coefficients["offset"] = self.powerModule.dut.sendCommand("read " + HDPowerModule.V12_HIGH_OFFSET_ADDR)
            return coefficients

        def writeCoefficients(self,coefficients):

            # write 12v high current multiplier
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V12_HIGH_MULTIPLIER_ADDR + " " + coefficients["multiplier"])
            # write 12v high current offset
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V12_HIGH_OFFSET_ADDR + " " + coefficients["offset"])

    class HD12VLeakageCalibration (HDCalibration):

        def __init__(self,powerModule):

            self.powerModule = powerModule
            self.absErrorLimit = 50                 # 1% of 5000 uA
            self.relErrorLimit = 0                  # 
            self.test_min = 1000                    # 1000mV
            self.test_max = 14400                   # 14.4V
            self.test_steps = 20
            self.units = "mA"
            self.scaling = 1
            self.multiplier_signed = False
            self.multiplier_int_width = 1
            self.multiplier_frac_width = 16
            self.offset_signed = False               # offset is not stored, don't care
            self.offset_int_width = 16               # offset is not stored, don't care
            self.offset_frac_width = 16              # offset is not stored, don't care

        def init(self):

            super().init_cal("12v")

            #set low current mode
            sendAndVerifyCommand(self.powerModule.dut,"write 0xf001 0x0101")
            # clear the multiplier register by setting it to zero
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V12_LEAKAGE_MULTIPLIER_ADDR + " 0x0000")
            #set load current to 5mA
            self.powerModule.load.setReferenceCurrent(0.005)
            #set voltage to test_min and wait for it to settle
            super().set_12v_volt(self.test_min)
            sleep(1)

        def setRef(self,value):
        
            super().set_12v_volt(value)

        def readRef(self):
        
            # return test current (5mA) - current measured by PPM
            # this is the correction we need to make to the measured current at the given voltage
            return 5000-(float(returnMeasurement(self.powerModule.dut,"meas:cur 12v?")[0])*1000)

        def readVal(self):
        
            # return the difference between nominal voltage and the current voltage
            # we use raw DAC values as it slightly more accurate (12v nominal voltage = 0xD3F = 11.9984 V
            # this is the value we will multiply to correct the current measurement
            return 0xD3F-int(self.powerModule.dut.sendCommand("read 0x0006"),16)

        def setCoefficients(self):

            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V12_LEAKAGE_MULTIPLIER_ADDR + " " + self.multiplier.hexString(4))

        def finish(self):
        
            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get 12v leakage multiplier
            coefficients["multiplier"] = self.powerModule.dut.sendCommand("read " + HDPowerModule.V12_LEAKAGE_MULTIPLIER_ADDR)
            return coefficients

        def writeCoefficients(self,coefficents):

            # write 12v leakage multiplier
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V12_LEAKAGE_MULTIPLIER_ADDR + " " + coefficents["multiplier"])


    class HD5VOffsetCalibration (HDCalibration):

        def __init__(self,powerModule):

            self.powerModule = powerModule
            self.absErrorLimit = 50     # the output can be within 1% of 5000mV = 50
            self.relErrorLimit = 0
            self.test_min = 4500
            self.test_max = 5500
            self.test_steps = 20
            self.units = "mV"
            self.scaling = 3.538305666
            self.multiplier_signed = False
            self.multiplier_int_width = 16
            self.multiplier_frac_width = 16
            self.offset_signed = True
            self.offset_int_width = 13
            self.offset_frac_width = 0

        def init(self):

            super().init_cal("5v")

            # clear the output offset register by setting it to zero
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V5_OUTPUT_OFFSET_ADDR + " 0x0000")

        def setRef(self,value):

            super().set_5v_volt(value)

        def readRef(self):

            return load_meas_volt(self.powerModule.load)-5000   # this is the difference in mV between the current measured voltage and the nominal voltage

        def readVal(self):

            return (int(self.powerModule.dut.sendCommand("read 0x0005"),16)-0x585)*self.scaling  # this is the difference in DAC levels between the current set point and the nominal voltage

        def setCoefficients(self):

            self.powerModule.dut.sendCommand("write " + HDPowerModule.V5_OUTPUT_OFFSET_ADDR + " " + self.offset.hexString(4))
            #sendAndVerifyCommand(self.powerModule.dut,"write 0xf010 " + self.offset.hexString(4))    # negative offsets don't read back in 1.5 and below

        def finish(self):
        
            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get 5v output offset
            coefficients["offset"] = self.powerModule.dut.sendCommand("read " + HDPowerModule.V5_OUTPUT_OFFSET_ADDR)
            return coefficients

        def writeCoefficients(self,coefficients):

            # write 5v output offset
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V5_OUTPUT_OFFSET_ADDR + " " + coefficients["offset"])

    class HD5VVoltageCalibration (HDCalibration):

        def __init__(self,powerModule):

            self.powerModule = powerModule
            self.absErrorLimit = 1
            self.relErrorLimit = 1
            self.test_min = 40
            self.test_max = 6000
            self.test_steps = 20
            self.units = "mV"
            self.scaling = 2
            self.multiplier_signed = False
            self.multiplier_int_width = 1
            self.multiplier_frac_width = 16
            self.offset_signed = True
            self.offset_int_width = 10
            self.offset_frac_width = 6

        def init(self):

            super().init_cal("5v")

            # clear the multiplier and offset registers by setting them to zero
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V5_VOLT_MULTIPLIER_ADDR + " 0x0000")
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V5_VOLT_OFFSET_ADDR + " 0x0000")

            #set voltage to zero and wait 1 second to settle
            sendAndVerifyCommand(self.powerModule.dut,"sig:5v:volt 0")
            sleep(1)

        def setRef(self,value):
        
            super().set_5v_volt(value)

        def readRef(self):
        
            return load_meas_volt(self.powerModule.load)

        def readVal(self):
        
            return super().meas_5v_volt()

        def setCoefficients(self):

            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V5_VOLT_MULTIPLIER_ADDR + " " + self.multiplier.hexString(4))
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V5_VOLT_OFFSET_ADDR + " " + self.offset.hexString(4))

        def finish(self):
        
            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get 5v voltage multiplier
            coefficients["multiplier"] = self.powerModule.dut.sendCommand("read " + HDPowerModule.V5_VOLT_MULTIPLIER_ADDR)
            # get 5v voltage offset
            coefficients["offset"] = self.powerModule.dut.sendCommand("read " + HDPowerModule.V5_VOLT_OFFSET_ADDR)
            return coefficients

        def writeCoefficients(self,coefficients):

            # write 5v voltage multiplier
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V5_VOLT_MULTIPLIER_ADDR + " " + coefficients["multiplier"])
            # write 5v voltage offset
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V5_VOLT_OFFSET_ADDR + " " + coefficients["offset"])

    class HD5VLowCurrentCalibration (HDCalibration):

        def __init__(self,powerModule):

            self.powerModule = powerModule
            self.absErrorLimit = 2
            self.relErrorLimit = 2
            self.test_min = 10
            self.test_max = 1000
            self.test_steps = 20
            self.units = "uA"
            self.scaling = 16
            self.multiplier_signed = False
            self.multiplier_int_width = 1
            self.multiplier_frac_width = 16
            self.offset_signed = True
            self.offset_int_width = 10
            self.offset_frac_width = 6

        def init(self):

            super().init_cal("5v")

            #set low current mode
            sendAndVerifyCommand(self.powerModule.dut,"write 0xf001 0x0101")
            # clear the multiplier and offset registers by setting them to zero
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V5_LOW_MULTIPLIER_ADDR + " 0x0000")
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V5_LOW_OFFSET_ADDR + " 0x0000")

        def setRef(self,value):
        
            load_set_cur(self.powerModule.load,value)

        def readRef(self):
        
            return load_meas_cur(self.powerModule.load)

        def readVal(self):

            return super().meas_5v_cur()

        def setCoefficients(self):
        
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V5_LOW_MULTIPLIER_ADDR + " " + self.multiplier.hexString(4))
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V5_LOW_OFFSET_ADDR + " " + self.offset.hexString(4))

        def finish(self):
        
            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get 5v low current multiplier
            coefficients["multiplier"] = self.powerModule.dut.sendCommand("read " + HDPowerModule.V5_LOW_MULTIPLIER_ADDR)
            # get 5v low current offset
            coefficients["offset"] = self.powerModule.dut.sendCommand("read " + HDPowerModule.V5_LOW_OFFSET_ADDR)
            return coefficients

        def writeCoefficients(self,coefficients):

            # write 5v low current multiplier
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V5_LOW_MULTIPLIER_ADDR + " " + coefficients["multiplier"])
            # write 5v low current offset
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V5_LOW_OFFSET_ADDR + " " + coefficients["offset"])

    class HD5VHighCurrentCalibration (HDCalibration):

        def __init__(self,powerModule):

            self.powerModule = powerModule
            self.absErrorLimit = 2000
            self.relErrorLimit = 1
            self.test_min = 1000
            self.test_max = 4000000
            self.test_steps = 20
            self.units = "uA"
            self.scaling = 2048
            self.multiplier_signed = False
            self.multiplier_int_width = 1
            self.multiplier_frac_width = 16
            self.offset_signed = True
            self.offset_int_width = 10
            self.offset_frac_width = 6

        def init(self):

            super().init_cal("5v")

            #set high current mode
            sendAndVerifyCommand(self.powerModule.dut,"write 0xf001 0x0102")
            # clear the multiplier and offset registers by setting them to zero
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V5_HIGH_MULTIPLIER_ADDR + " 0x0000")
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V5_HIGH_OFFSET_ADDR + " 0x0000")

        def setRef(self,value):
        
            load_set_cur(self.powerModule.load,value)

        def readRef(self):
        
            return load_meas_cur(self.powerModule.load)

        def readVal(self):
        
            return super().meas_5v_cur()

        def setCoefficients(self):
        
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V5_HIGH_MULTIPLIER_ADDR + " " + self.multiplier.hexString(4))
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V5_HIGH_OFFSET_ADDR + " " + self.offset.hexString(4))

        def finish(self):
        
            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get 5v high current multiplier
            coefficients["multiplier"] = self.powerModule.dut.sendCommand("read " + HDPowerModule.V5_HIGH_MULTIPLIER_ADDR)
            # get 5v high current offset
            coefficients["offset"] = self.powerModule.dut.sendCommand("read " + HDPowerModule.V5_HIGH_OFFSET_ADDR)
            return coefficients

        def writeCoefficients(self,coefficients):

            # write 5v high current multiplier
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V5_HIGH_MULTIPLIER_ADDR + " " + coefficients["multiplier"])
            # write 5v high current offset
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V5_HIGH_OFFSET_ADDR + " " + coefficients["offset"])

    class HD5VLeakageCalibration (HDCalibration):

        def __init__(self,powerModule):

            self.powerModule = powerModule
            self.absErrorLimit = 50
            self.relErrorLimit = 0
            self.test_min = 1000
            self.test_max = 6000
            self.test_steps = 20
            self.units = "mA"
            self.scaling = 1
            self.multiplier_signed = False
            self.multiplier_int_width = 1
            self.multiplier_frac_width = 16
            self.offset_signed = True                # offset is not stored, don't care
            self.offset_int_width = 16               # offset is not stored, don't care
            self.offset_frac_width = 16              # offset is not stored, don't care

        def init(self):

            super().init_cal("5v")

            #set low current mode
            sendAndVerifyCommand(self.powerModule.dut,"write 0xf001 0x0101")
            # clear the multiplier register by setting it to zero
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V5_LEAKAGE_MULTIPLIER_ADDR + " 0x0000")
            #set load current to 5mA
            self.powerModule.load.setReferenceCurrent(0.005)

            #set voltage to test_min and wait for it to settle
            super().set_5v_volt(self.test_min)
            sleep(1)

        def setRef(self,value):
        
            super().set_5v_volt(value)

        def readRef(self):

            #return test current (5mA) - current measured by PPM
            return 5000-(float(returnMeasurement(self.powerModule.dut,"meas:cur 5v?")[0])*1000)

        def readVal(self):

            #return the difference between nominal voltage and the current voltage
            # we use raw DAC values as it slightly more accurate (12v nominal voltage = 0xD3F = 11.9984V not 12000mV
            # return nominal voltage - current set voltage
            return 0xD3F-int(self.powerModule.dut.sendCommand("read 0x0005"),16)

        def setCoefficients(self):

            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V5_LEAKAGE_MULTIPLIER_ADDR + " " + self.multiplier.hexString(4))

        def finish(self):
        
            super().finish_cal()

        def report(self,data):
        
            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get 5v leakage multiplier
            coefficients["multiplier"] = self.powerModule.dut.sendCommand("read " + HDPowerModule.V5_LEAKAGE_MULTIPLIER_ADDR)
            return coefficients

        def writeCoefficients(self,coefficients):

            # write 5v leakage multiplier
            sendAndVerifyCommand(self.powerModule.dut,"write " + HDPowerModule.V5_LEAKAGE_MULTIPLIER_ADDR + " " + coefficients["multiplier"])

    class HD12VOffsetVerification (HDCalibration):

        def __init__(self,powerModule):

            self.powerModule = powerModule
            self.absErrorLimit = 0      # no absolute tolerance
            self.relErrorLimit = 1      # 1% tolerance
            self.test_min = 10800       # 12v - 10%
            self.test_max = 13200       # 12v + 10%
            self.test_steps = 20
            self.units = "mV"

        def init(self):

            super().init_cal("12V")

        def setRef(self,value):

            super().set_12v_volt(value)

        def readRef(self):

            return super().get_12v_volt()

        def readVal(self):

            return load_meas_volt(self.powerModule.load)

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)

    class HD12VVoltageVerification (HDCalibration):

        def __init__(self,powerModule):

            self.powerModule = powerModule
            self.absErrorLimit = 1      # 1mV
            self.relErrorLimit = 1      # 1% tolerance
            self.test_min = 40          # 40mV
            self.test_max = 14400       # 14.4V
            self.test_steps = 20
            self.units = "mV"

        def init(self):

            super().init_cal("12V")

        def setRef(self,value):

            super().set_12v_volt(value)

        def readRef(self):

            return load_meas_volt(self.powerModule.load)

        def readVal(self):

            return super().meas_12v_volt()

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)

    class HD12VLowCurrentVerification (HDCalibration):

        def __init__(self,powerModule):

            self.powerModule = powerModule
            self.absErrorLimit = 2      # 2uA
            self.relErrorLimit = 2      # 2% tolerance
            self.test_min = 100         # 100uA
            self.test_max = 1000        # 1mA
            self.test_steps = 20
            self.units = "uA"

        def init(self):

            super().init_cal("12V")

        def setRef(self,value):

            load_set_cur(self.powerModule.load,value)

        def readRef(self):

            return load_meas_cur(self.powerModule.load)

        def readVal(self):

            return super().meas_12v_cur()

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)

    class HD12VHighCurrentVerification (HDCalibration):

        def __init__(self,powerModule):

            self.powerModule = powerModule
            self.absErrorLimit = 2000       # 2mA
            self.relErrorLimit = 1          # 1% tolerance
            self.test_min = 1000            # 1mA
            self.test_max = 4000000         # 4A
            self.test_steps = 20
            self.units = "uA"

        def init(self):

           super().init_cal("12v")

        def setRef(self,value):

            load_set_cur(self.powerModule.load,value)

        def readRef(self):

            return load_meas_cur(self.powerModule.load)

        def readVal(self):

            return super().meas_12v_cur()

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)

    class HD12VLeakageVerification (HDCalibration):

        def __init__(self,powerModule):

            self.powerModule = powerModule
            self.absErrorLimit = 0      # no absolute tolerance
            self.relErrorLimit = 1      # 1% tolerance
            self.test_min = 10000       # 1V
            self.test_max = 14400       # 14.4V
            self.test_steps = 20
            self.units = "mV"

        def init(self):

            super().init_cal("12v")

            #set load current to 5mA
            self.powerModule.load.setReferenceCurrent(0.005)

            #set voltage to test_min and wait for it to settle
            super().set_12v_volt(self.test_min)
            sleep(1)

        def setRef(self,value):

            super().set_12v_volt(value)

        def readRef(self):

            return load_meas_cur(self.powerModule.load)

        def readVal(self):

            return super().meas_12v_cur()

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)

    class HD5VOffsetVerification (HDCalibration):

        def __init__(self,powerModule):

            self.powerModule = powerModule
            self.absErrorLimit = 0      # no absolute tolerance
            self.relErrorLimit = 1      # 1% tolerance
            self.test_min = 4500        # 5v - 10%
            self.test_max = 5500        # 5v + 10%
            self.test_steps = 20
            self.units = "mV"

        def init(self):

           super().init_cal("5v")

        def setRef(self,value):

            super().set_5v_volt(value)

        def readRef(self):

            return super().get_5v_volt()

        def readVal(self):

            return load_meas_volt(self.powerModule.load)

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)

    class HD5VVoltageVerification (HDCalibration):

        def __init__(self,powerModule):

            self.powerModule = powerModule
            self.absErrorLimit = 1      # 1mV
            self.relErrorLimit = 1      # 1%
            self.test_min = 40          # 40mV
            self.test_max = 6000        # 6V
            self.test_steps = 20
            self.units = "mV"

        def init(self):

           super().init_cal("5v")

        def setRef(self,value):

            super().set_5v_volt(value)

        def readRef(self):

            return load_meas_volt(self.powerModule.load)

        def readVal(self):

            return super().meas_5v_volt()

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)

    class HD5VLowCurrentVerification (HDCalibration):

        def __init__(self,powerModule):

            self.powerModule = powerModule
            self.absErrorLimit = 2      # 2uA
            self.relErrorLimit = 2      # 2%
            self.test_min = 100         # 100uA
            self.test_max = 1000        # 1mA
            self.test_steps = 20
            self.units = "uA"

        def init(self):

           super().init_cal("5v")

        def setRef(self,value):

            load_set_cur(self.powerModule.load,value)

        def readRef(self):

            return load_meas_cur(self.powerModule.load)

        def readVal(self):

            return super().meas_5v_cur()

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)

    class HD5VHighCurrentVerification (HDCalibration):

        def __init__(self,powerModule):

            self.powerModule = powerModule
            self.absErrorLimit = 2000       # 2mA
            self.relErrorLimit = 1          # 1% tolerance
            self.test_min = 1000            # 1mA
            self.test_max = 4000000         # 4A
            self.test_steps = 20
            self.units = "uA"

        def init(self):

           super().init_cal("5v")

        def setRef(self,value):

            load_set_cur(self.powerModule.load,value)

        def readRef(self):

            return load_meas_cur(self.powerModule.load)

        def readVal(self):

            return super().meas_5v_cur()

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)

    class HD5VLeakageVerification (HDCalibration):

        def __init__(self,powerModule):

            self.powerModule = powerModule
            self.absErrorLimit = 50      # 1% of 5000 uA
            self.relErrorLimit = 0          
            self.test_min = 1000         # 1V
            self.test_max = 6000         # 6V
            self.test_steps = 20
            self.units = "mV"

        def init(self):

            super().init_cal("5v")

            #set load current to 5mA
            self.powerModule.load.setReferenceCurrent(0.005)

            #set voltage to test_min and wait for it to settle
            super().set_5v_volt(self.test_min)
            sleep(1)

        def setRef(self,value):

            super().set_5v_volt(value)

        def readRef(self):

            return load_meas_cur(self.powerModule.load)

        def readVal(self):

            return super().meas_5v_cur()

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)

    def __init__(self,dut):

        # set the name of this module
        self.name = "HD Programmable Power Module"
        self.dut = dut

        self.calibrations = {}
        # populate 12V channel with calibrations
        self.calibrations["12V"] = {
            "Output Offset":self.HD12VOffsetCalibration(self),
            "Voltage":self.HD12VVoltageCalibration(self),
            "Low Current":self.HD12VLowCurrentCalibration(self),
            "High Current":self.HD12VHighCurrentCalibration(self),
            "Leakage":self.HD12VLeakageCalibration(self)
            }
        # populate 5V channel with calibrations
        self.calibrations["5V"] = {
            "Output Offset":self.HD5VOffsetCalibration(self),
            "Voltage":self.HD5VVoltageCalibration(self),
            "Low Current":self.HD5VLowCurrentCalibration(self),
            "High Current":self.HD5VHighCurrentCalibration(self),
            "Leakage":self.HD5VLeakageCalibration(self)
            }

        self.verifications = {}
        # populate 12V channel with verifications
        self.verifications["12V"] = {
            "Output Offset":self.HD12VOffsetVerification(self),
            "Voltage":self.HD12VVoltageVerification(self),
            "Low Current":self.HD12VLowCurrentVerification(self),
            "High Current":self.HD12VHighCurrentVerification(self),
            "Leakage":self.HD12VLeakageVerification(self)
            }
        # populate 5V channel with verifications
        self.verifications["5V"] = {
            "Output Offset":self.HD5VOffsetVerification(self),
            "Voltage":self.HD5VVoltageVerification(self),
            "Low Current":self.HD5VLowCurrentVerification(self),
            "High Current":self.HD5VHighCurrentVerification(self),
            "Leakage":self.HD5VLeakageVerification(self)
            }

if __name__== "__main__":
 main()

