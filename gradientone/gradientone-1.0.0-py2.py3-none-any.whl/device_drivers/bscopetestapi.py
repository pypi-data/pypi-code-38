"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited 
without the express permission of GradientOne Inc.

"""

'''Test the BitScope Library by connecting with the first available device
and performing a capture and dump. Requires BitLib 2.0 and Python Bindings'''

from bitlib import *

MY_DEVICE = 0 # one open device only
MY_CHANNEL = 0 # channel to capture and display
MY_PROBE_FILE = "" # default probe file if unspecified 
MY_MODE = BL_MODE_FAST # preferred capture mode
MY_RATE = 1000000 # default sample rate we'll use for capture.
MY_SIZE = 5 # number of samples we'll capture (simply a connectivity test)
TRUE = 1

MODES = ("FAST","DUAL","MIXED","LOGIC","STREAM")
SOURCES = ("POD","BNC","X10","X20","X50","ALT","GND")

class BitScope:

    def main(argv=None):
    
        print("Starting: Attempting to open one device...")
        if BL_Open(MY_PROBE_FILE,1):
        
            print(" Library: %s (%s)" % (
                BL_Version(BL_VERSION_LIBRARY),
                BL_Version(BL_VERSION_BINDING)))
        
            BL_Select(BL_SELECT_DEVICE,MY_DEVICE)

            print("    Link: %s" % BL_Name(0))
            print("BitScope: %s (%s)" % (BL_Version(BL_VERSION_DEVICE),BL_ID()))
            print("Channels: %d (%d analog + %d logic)" % (
                BL_Count(BL_COUNT_ANALOG)+BL_Count(BL_COUNT_LOGIC),
                BL_Count(BL_COUNT_ANALOG),BL_Count(BL_COUNT_LOGIC)))

            print("   Modes:" + "".join(["%s" % (
                (" " + MODES[i]) if i == BL_Mode(i) else "") for i in range(len(MODES))]))

            BL_Mode(BL_MODE_LOGIC) == BL_MODE_LOGIC or BL_Mode(BL_MODE_FAST)
            print(" Capture: %d @ %.0fHz = %fs (%s)" % (
                BL_Size(),BL_Rate(),
                BL_Time(),MODES[BL_Mode()]))

            BL_Range(BL_Count(BL_COUNT_RANGE))
            if BL_Offset(-1000) != BL_Offset(1000):
                print("  Offset: %+.4gV to %+.4gV" % (
                    BL_Offset(1000), BL_Offset(-1000)))

            for i in range(len(SOURCES)):
                if i == BL_Select(2,i):
                    print("     %s: " % SOURCES[i] + " ".join(["%5.2fV" % BL_Range(n) for n in range(BL_Count(3)-1,-1,-1)]))
   
            BL_Mode(MY_MODE) # prefered capture mode
            BL_Intro(BL_ZERO) # optional, default BL_ZERO
            BL_Delay(BL_ZERO) # optional, default BL_ZERO
            BL_Rate(MY_RATE) # optional, default BL_MAX_RATE
            BL_Size(MY_SIZE) # optional default BL_MAX_SIZE
            BL_Select(BL_SELECT_CHANNEL,MY_CHANNEL) # choose the channel
            BL_Trigger(BL_ZERO,BL_TRIG_RISE) # optional when untriggered */
            BL_Select(BL_SELECT_SOURCE,BL_SOURCE_POD) # use the POD input */
            BL_Range(BL_Count(BL_COUNT_RANGE)) # maximum range
            BL_Offset(BL_ZERO) # optional, default 0
            BL_Enable(TRUE) # at least one channel must be initialised 

            BL_Trace()
  
            DATA = BL_Acquire()
            print(" Data(%d): " % MY_SIZE + ", ".join(["%f" % DATA[n] for n in range(len(DATA))]))
  
            BL_Close()
            print("Finished: Library closed, resources released.")
        else:
            print("  FAILED: device not found (check your probe file).")
    
if __name__ == "__main__":
    import sys
    sys.exit(main())
