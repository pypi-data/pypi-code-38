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
from quarchpy.user_interface import *

def load_meas_volt(load):

    # measaureLoadVoltage returns volts, we convert these to mV and return
    return load.measureLoadVoltage()*1000

def load_set_cur(load,value):

    #set load current, parameter is uA, the keithley needs amps
    response = load.setReferenceCurrent(value/1000000)
    return response

def load_meas_cur(load):

    #get load current, the keithley returns amps, we use uA
    return load.measureLoadCurrent()*1000000

'''
Coefficient Class

This class holds a floating point value, and the precision at which it will be stored (in the FPGA)

    The constructor will throw an OverFlowError if the integer value overflows the specified integer width

    Value() returns the original value

    storedValue() returns the reduced precision value as would be stored in the FPGA

    hexString() returns an appropriate length hex string of the stored Value

'''

class Coefficient:
    def __init__(self, value, signed, int_width, frac_width):
        # set overflow flag if the value can't fit in the assigned integer range
        if (signed == True and abs(value) >= (2**(int_width-1))) or (signed == False and abs(value) >= (2**(int_width))):
            self.overflow = True
        else:
            self.overflow = False

        self.value = value
        self.signed = signed
        self.int_width = int_width
        self.frac_width = frac_width

    def originalValue(self):
        return self.value

    def storedValue(self):
        #shift left by required number of fractional bits, round it (to nearest integer), then shift right again
        return round(self.value*(2**self.frac_width)) / (2**self.frac_width)

    '''
    hexString(hex_chars)

    returns a hex string begining 0x with the number of hex characters specified
    '''
    #def hexString(self,hex_chars):
    #    #shift left by required number of fractional bits, round it (to nearest integer), then and with 1's to truncate it to required length
    #    return "{:#0{hex_chars}x}".format(round(self.value*(2**self.frac_width)) & (2**(hex_chars*4)-1),hex_chars=(hex_chars+2))

    def hexString(self,hex_chars):
        #shift left by required number of fractional bits, round it (to nearest integer), then and with total bits to get correct 2's compliment value, then and with characters to truncate as necessary
        return "{:#0{hex_chars}x}".format(round(self.value*(2**self.frac_width)) & (2**(self.int_width+self.frac_width)-1) & ((2**(hex_chars*4))-1),hex_chars=(hex_chars+2))

'''
Calibration Class

This class holds a multiplier and offset coefficient as instances of the Coefficient class

    The constructor will generate multiplier and offset from a set of points in the form of a list of coordinates, using the x axis for ADC value and the y axis for reference value
    shift is an integer providing the size of the shift left that is applied to the result after multiplication and offset are applied

    Calibration(points,shift,abs_error,rel_error)

        shift is the binary left shift that takes place inside the FPGA


                LOW_12V = Calibration("uA",init_cmd,read_cmd,multiplier_cmd,offset_cmd,
                              MULTIPLIER = Coefficient(multiplier_int_width,multiplier_frac_width,multiplier_shift)
                              OFFSET = Coefficient(offset_int_width,offset_frac_width,offset_shift)

'''
class Calibration:

    def __init__(self):
        self.powerModule = None
        self.absErrorLimit = None
        self.relErrorLimit = None
        self.test_min = None
        self.test_max = None
        self.test_steps = None
        self.units = None
        self.scaling = None
        self.multiplier_signed = None
        self.multiplier_int_width = None
        self.multiplier_frac_width  = None
        self.offset_signed = None
        self.offset_int_width  = None
        self.offset_frac_width  = None

    '''
    generate(points)

        generates a multiplier and offset from a set of coordinates

        points  -   a list of x and y values in form [(x0,y0),(x1,y1),(x2,y2)]

    '''        
    def generate(self,points):

        (thisMultiplier,thisOffset) = bestFit(points)
        # divide the offset by the hardware shift
        thisOffset /= self.scaling
        self.multiplier = Coefficient(thisMultiplier,self.multiplier_signed,self.multiplier_int_width,self.multiplier_frac_width)
        self.offset = Coefficient(-thisOffset,self.offset_signed,self.offset_int_width,self.offset_frac_width)            # offsets are subtracted in the hw, so we flip the sign of the offset

    '''
    getResult(adc_value)

        takes in a value and applies the current calibration to it    

    '''
    def getResult(self,value):
        return round( ( (float(value)/self.scaling ) * self.multiplier.storedValue() - self.offset.storedValue() ) * self.scaling )

    '''
    getStepMultiplier()

        works out the multiplier to apply on each step to get from test_min to test_max in test_steps

    '''
    def getStepMultiplier(self):
        return (self.test_max/self.test_min)**(1/(self.test_steps-1))


'''
Class PowerModule

    Generic Class for a quarch module with measurement channels. The function holds a list of channels, and a channel holds a list of calibrations

'''
class PowerModule:

    def __init__(self):

        self.name = None            # this is the name of the product that will be displayed to the user
        self.dut = None             # this is a comms device for the module
        self.calibrations = {}      # a dictionary of calibrations supported by this module
        self.verifications = {}     # a dictionary of verifications supported by this module
        self.voltageMode = None

    def open_module(self):

        # stub method to be overidden
        pass

    def close_module(self):
            
        # stub method to be overidden
        pass

    def readCalibration(self):

        calValues = {}

        for channel in self.calibrations:

            calValues[channel] = {}

            for calibration in self.calibrations[channel]:

                calValues[channel][calibration] = self.calibrations[channel][calibration].readCoefficients()


        return calValues

    def writeCalibration(self,calValues):

        self.dut.sendCommand("write 0xf000 0xaa55")
        self.dut.sendCommand("write 0xf000 0x55aa")
        
        for channel in calValues:

            for calibration in calValues[channel]:

                self.calibrations[channel][calibration].writeCoefficients(calValues[channel][calibration])

    def calibrate(self,load,reportFile):

        return self.calibrateOrVerify("calibrate",load,reportFile)

    def verify(self,load,reportFile):

        return self.calibrateOrVerify("verify",load,reportFile)

    def calibrateOrVerify(self,action,load,reportFile):

        if action == 'calibrate':
            list = self.calibrations
        elif action == 'verify':
            list = self.verifications
        else:
            raise Exception('calibrateOrVerify() called with invalid action: ' + action)

        self.load = load

        self.open_module()

        passed = True

        # for each channel to be calibrated on the instrument
        for channel in list:

            # for each calibration/verification in the channel
            for calibration in list[channel]:

                thisItem = list[channel][calibration]
                    
                # print title
                if action == 'calibrate':
                    startTestBlock("Calibrating " + channel + " " + calibration)
                else:
                    startTestBlock("Verifying " + channel + " " + calibration)

                # Initialise this calibration/verification
                thisItem.init()

                # step through values and populate table
                iteration = 1
                data = []
                steps = thisItem.test_steps
                test_value = thisItem.test_min
                while test_value <= thisItem.test_max:

                    # set reference value
                    thisItem.setRef(int(test_value))

                    # get calibrated result
                    reference = thisItem.readRef()

                    # get DUT result
                    value = thisItem.readVal()

                    #store the results
                    data.append([value,reference])

                    # print progress bar
                    progressBar(iteration,steps)
                    iteration += 1

                    # increment the test value
                    test_value = int(test_value*thisItem.getStepMultiplier())

                #turn off the module and load
                thisItem.finish()

                if action == 'calibrate':

                    # generate coefficients
                    thisItem.generate(data)

                    #set coefficients
                    thisItem.setCoefficients()

                report = thisItem.report(data)

                if action == 'calibrate':

                    logCalibrationResult(channel + " " + calibration + " Calibration",report)
                    reportFile.write("\n\n" + channel + " " + calibration + " Calibration")

                else:

                    logCalibrationResult(channel + " " + calibration + " Verification",report)
                    reportFile.write("\n\n" + channel + " " + calibration + " Verification")

                # send to report file
                reportFile.write(report["report"])
                reportFile.flush()

                # if any test fails, we set passed to false
                if report["result"] == False:
                    passed = False

        # reset the unit
        self.close_module()

        #return overall result
        return passed

'''
bestFit(points)

takes in a list of x and y coordinates of ADC values (x value) and reference values (y value)
and returns offset and gradient for the best fit straight line approximation of those points
'''
def bestFit(points):

    # calculate the mean value of all x coordinates
    AveX = reduce(lambda sum,point : sum+point[0],points,0)/len(points)
    # calculate the mean value of all y coordinates
    AveY = reduce(lambda sum,point : sum+point[1],points,0)/len(points)
    # calculate the sum of (x-x'mean)*(y-y'mean) for all points
    SumXY = reduce(lambda sum,point : sum + ((point[0]-AveX)*(point[1]-AveY)), points, 0)
    # calculate the sum of (x-x'mean)*(x-x'mean) for all points
    SumX2 = reduce(lambda sum,point : sum + ((point[0]-AveX)*(point[0]-AveX)), points, 0)

    Slope = SumXY/SumX2
    Intercept = AveY-(Slope*AveX)
        
    return Slope,Intercept

'''
getError(reference_value,calculated_value,abs_error,rel_error)

    takes in a reference value and a calculated value
    returns a tuple with actual error (reference-calculated), absolute error, relative error and result

    abs_error is the absolute error allowance for this calibration, in the same units as the result
    rel_error is a percentage error allowance for this calibration, it is the percentage error between calibrated and reference value after the absolute error allowance is subtracted.

'''
def getError(reference_value,calculated_value,abs_error_limit,rel_error_limit):

    #the error at this point is reference value - test value
    error_value = calculated_value - reference_value

    #work out sign
    if error_value >= 0:
        error_sign = '+'
    else:
        error_sign = '-'

    #make error positive
    error_value = abs(error_value)
            
    # if error at this point is greater than absolute_error, set abs_error_val to absolute_error
    if error_value >= abs_error_limit:
        abs_error_val = abs_error_limit

        # calculate relative error after deduction of abolute error allowance, and as a percentage of the calculated value (not the reference value)
        # we return a positive percentage because the sign is always the same as abs_error_val so we display +/-(abs + pc)
        rel_error_val = abs(((error_value - abs_error_val) /  calculated_value) * 100)

    # else round up to the nearest integer 
    else:
        abs_error_val = ceil(error_value)
        rel_error_val = 0

    # set pass/fail
    if abs(rel_error_val) <= rel_error_limit:
        result = True;
    else:
        result = False;

    #  Actual Error, Absolute Error, Relative Error, Pass/Fail
    return([error_value,error_sign,abs_error_val,rel_error_val,result])

if __name__== "__main__":
 main()

