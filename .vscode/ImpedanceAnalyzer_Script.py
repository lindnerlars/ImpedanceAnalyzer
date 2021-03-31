"""
   Impedance Analyzer 
   Author:  Lars Lindner
   Revision:  15/03/2021

   -> This programm does a frequency sweep from 'freq_start' to 'freq_end' in 'freq_steps'
   -> It prints the impedance [kOhm] and phase [deg] as an image and the numerical values as .txt file
"""

from ctypes import *
from dwfconstants import *
import math
import time
import sys
import numpy as np
import matplotlib.pyplot as plt

freq_start = 3.8e6
freq_end = 4.2e6
freq_steps = 100
resistance_ref = 1000
amplitude = 1

sts = c_byte()
impedance = c_double()
phase = c_double()
rgHz = [0.0]*freq_steps
rgIm = [0.0]*freq_steps
rgPh = [0.0]*freq_steps



if sys.platform.startswith("win"):
    dwf = cdll.LoadLibrary("dwf.dll")
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

hdwf = c_int()
szerr = create_string_buffer(512)
print("Opening first device")
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

if hdwf.value == hdwfNone.value:
    dwf.FDwfGetLastErrorMsg(szerr)
    print(str(szerr.value))
    print("failed to open device")
    quit()


dwf.FDwfDeviceAutoConfigureSet(hdwf, c_int(3)) # this option will enable dynamic adjustment of analog out settings like: frequency, amplitude...
dwf.FDwfAnalogImpedanceReset(hdwf)
dwf.FDwfAnalogImpedanceModeSet(hdwf, c_int(8)) # 0 = W1-C1-DUT-C2-R-GND, 1 = W1-C1-R-C2-DUT-GND, 8 = AD IA adapter
dwf.FDwfAnalogImpedanceReferenceSet(hdwf, c_double(resistance_ref)) # reference resistor value in Ohms
dwf.FDwfAnalogImpedanceFrequencySet(hdwf, c_double(freq_start)) # frequency in Hertz
dwf.FDwfAnalogImpedanceConfigure(hdwf, c_int(1)) # Measurement start
time.sleep(1)

print("Reference: " + str(resistance_ref) + " Ohm \t Frequency: " + str(freq_start/1000) + " kHz ... " + str(freq_end/1000) + " kHz")
extfile = open("impedance_" + str(amplitude) + "V.txt", "w")
extfile.write("Frequency [hz]" + "\t" + "Impedance [kOhm]" + "\t" + "Phase [rad]" + "\n")

for i in range(freq_steps):
    hz = freq_end * pow(10.0, 1.0*(1.0*i/(freq_steps-1)-1)*math.log10(freq_end/freq_start)) # exponential frequency freq_steps
    rgHz[i] = hz
    dwf.FDwfAnalogImpedanceAmplitudeSet(hdwf, c_double(amplitude)) # Measurement amplitude, 0V to peak signal
    dwf.FDwfAnalogImpedanceFrequencySet(hdwf, c_double(hz)) # frequency in Hertz
    time.sleep(0.01)
    dwf.FDwfAnalogImpedanceStatus(hdwf, None) # ignore last capture since we changed the frequency
    while True:
        if dwf.FDwfAnalogImpedanceStatus(hdwf, byref(sts)) == 0:
            dwf.FDwfGetLastErrorMsg(szerr)
            print(str(szerr.value))
            quit()
        if sts.value == 2:
            break

    dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceImpedance, byref(impedance))
    impedance.value = (impedance.value / 1000)
    rgIm[i] = abs(impedance.value)

    dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceImpedancePhase, byref(phase))
    phase.value = (phase.value / math.pi) * 180.0
    rgPh[i] = phase.value

    extfile.write(str(hz) + "\t" + str(rgIm[i]) + "\t" + str(rgPh[i]) + "\n")


dwf.FDwfAnalogImpedanceConfigure(hdwf, c_int(0)) # Measurement end
dwf.FDwfDeviceClose(hdwf)



fig, (ax1, ax2) = plt.subplots(2, sharex=True)
fig.suptitle('Impedance [kOhm] and Phase [deg]')
ax1.plot(rgHz, rgIm)
ax2.plot(rgHz, rgPh)

ax1.set_xscale('log')
ax1.set_yscale('log')
# ax1.ylabel('Impedance')

ax2.plot(rgHz, rgPh)
ax2.set_xscale('log')
# ax2.set_yscale('log')
# ax2.ylim([-90, 90])
# ax2.ylabel('Phase')

plt.xlabel('Frequency [hz]')
# plt.ylabel('Phase')

plt.show()



## Usefull code
# plt.plot(rgHz, rgIm)

# ax2 = plt.gca() # get plot axis
# # Set x-axis
# ax2.set_xscale('log')
# # Set y-axis
# ax2.set_yscale('log')
# # plt.ylim([0, 16])
# plt.ylabel('Impedance [kOhm]')
