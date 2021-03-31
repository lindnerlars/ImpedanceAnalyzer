"""
   Impedance Plot
   Author:  Lars Lindner
   Revision:  13/03/2021

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
from dwfconstants import *
import math
import time
import sys
import numpy
import matplotlib.pyplot as plt

sts = c_byte()
impedance = c_double()
frequency = 22000
resistance_ref = 1000


if sys.platform.startswith("win"):
    dwf = cdll.LoadLibrary("dwf.dll")
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

# version = create_string_buffer(16)
# dwf.FDwfGetVersion(version)
# print("DWF Version: "+str(version.value))

hdwf = c_int()
szerr = create_string_buffer(512)
print("Opening first device")
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

if hdwf.value == hdwfNone.value:
    dwf.FDwfGetLastErrorMsg(szerr)
    print(str(szerr.value))
    print("failed to open device")
    quit()


print("Reference: " + str(resistance_ref) + " Ohm \t Frequency: " + str(frequency) +" Hz")
dwf.FDwfAnalogImpedanceReset(hdwf)
dwf.FDwfAnalogImpedanceModeSet(hdwf, c_int(8)) # 0 = W1-C1-DUT-C2-R-GND, 1 = W1-C1-R-C2-DUT-GND, 8 = AD IA adapter
dwf.FDwfAnalogImpedanceReferenceSet(hdwf, c_double(resistance_ref)) # reference resistor value in Ohms
dwf.FDwfAnalogImpedancePeriodSet(hdwf, c_double(16))
dwf.FDwfAnalogImpedanceFrequencySet(hdwf, c_double(frequency))
dwf.FDwfAnalogImpedanceAmplitudeSet(hdwf, c_double(1))
time.sleep(1)

dwf.FDwfAnalogImpedanceStatus(hdwf, None) # ignore last capture, force a new one

for i in range(10):
    while True:
        if dwf.FDwfAnalogImpedanceStatus(hdwf, byref(sts)) == 0:
            dwf.FDwfGetLastErrorMsg(szerr)
            print(str(szerr.value))
            quit()
        if sts.value == 2:
            break
    dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceImpedance, byref(impedance))
#    impedance.value = round(impedance.value / 1000, 2)
    print(str(i) + ": \t" + "Impedance = " + str(impedance.value) + " Ohm")
    time.sleep(0.2)


dwf.FDwfAnalogImpedanceConfigure(hdwf, c_int(0)) # stop
dwf.FDwfDeviceClose(hdwf)