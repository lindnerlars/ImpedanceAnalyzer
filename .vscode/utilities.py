"""
   Utilities 
   Author:  Lars Lindner
   Revision:  02/05/2021

   -> This module provides several functions for the main program
   (But until now, it is only a test and it doesn't work correct, I have to learn more about modules!)

"""

import tkinter as tk
from tkinter import ttk
from tkinter import *

from ctypes import *
from dwfconstants import *

import math
import time
import sys
import numpy as np
import matplotlib.pyplot as plt


# region Init
# Variables Definitons
win = Tk()
win.withdraw()                  # To surpress this window!
hdwf = c_int()
sts = c_byte()
impedance = c_double()
phase = c_double()

# Default values for Parameters
freq_start = int(3.5e6)
freq_end = int(4.5e6)
freq_delta = int(10000)
amp_start = int(100)
amp_end = int(100)
amp_delta = int(100)
resistance = int(1000)
dec = tk.BooleanVar()           # WICHTIG!: Diese Variable muss NACH der Fenster Definition 'win = Tk()' definiert werden!!

# Load .dll
if sys.platform.startswith("win"):
    dwf = cdll.LoadLibrary("dwf.dll")
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")
# endregion



# Performs the actual impedance and phase measurement
def measurementFunction(hdwf, sts, infoOutput, amp_start, amp_end, amp_delta, freq_start, freq_end, freq_delta, resistance):
    for amp in range(amp_start, amp_end + 1, amp_delta):                    # Runs all the amplitude range
        infoOutput.insert(tk.INSERT, "Start Measurement Inc: " + str(amp) + "mV \n")
        infoOutput.update()                                                 # Forces the GUI to update the text box
        infoOutput.see('end')                                               # Allows scrolling in text widget 

        extfile = open("impedance_" + str(amp) + "mV_" + str(resistance) + "Ohm_Inc.txt", "w")  # Open text-file to write measurement values
        dwf.FDwfAnalogImpedanceAmplitudeSet(hdwf, c_double(float(amp/1000)))                # Sets the stimulus amplitude (0V to peak signal)
        dwf.FDwfAnalogImpedanceReferenceSet(hdwf, c_double(resistance))                     # Sets the reference resistor value in Ohms

        for freq in range(freq_start, freq_end + 1, freq_delta):            # Runs all the frequency range increasing
            dwf.FDwfAnalogImpedanceFrequencySet(hdwf, c_double(freq))       # Sets the stimulus frequency
            time.sleep(0.01)                                                # Settle time of device under test (DUT), this value depends on the device!
            dwf.FDwfAnalogImpedanceStatus(hdwf, None)                       # Ignore last capture since we changed the frequency

            checkErrorsFunction(hdwf, sts)

            dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceImpedance, byref(impedance))   # Read the DUT impedance value
            dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceImpedancePhase, byref(phase))  # Read the DUT phase value
            extfile.write(str(freq) + "\t" + str(abs(impedance.value)) + "\t" + str((phase.value / math.pi) * 180.0) + "\n")    # Write frequency, impedance and phase value to file

        extfile.close()



# Checks if the AD2 reading throws an error
def checkErrorsFunction(hdwf, sts):
    while True:
        if dwf.FDwfAnalogImpedanceStatus(hdwf, byref(sts)) == 0:
            dwf.FDwfGetLastErrorMsg(szerr)
            print(str(szerr.value))
            quit()
        if sts.value == 2:
            break

