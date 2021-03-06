"""
   Impedance Analyzer 
   Author:  Lars Lindner
   Interpreter: 3.9.5
   Revision:  08/05/2021

   -> This programm does a linear frequency sweep from 'freq_start' to 'freq_end' with 'freq_delta' using a GUI interface
   -> It prints the numerical values of frequency [Hz], impedance [Ohm] and phase [deg] as a txt-file
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
hdwf = c_int()
szerr = create_string_buffer(512)
sts = c_byte()
impedance = c_double()
phase = c_double()

# Default values for Parameters
freq_start = int(3.5e6)
freq_end = int(4.5e6)
freq_delta = int(100)
amp_start = int(100)
amp_end = int(1000)
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




# region Window Functions
def connectFunction():
    connectButton.update()
    dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

    if hdwf.value == hdwfNone.value:
        dwf.FDwfGetLastErrorMsg(szerr)
        infoOutput.insert(tk.INSERT, str(szerr.value) + "\n")
        infoOutput.see("end")
    else:
        connectButton["state"] = tk.DISABLED
        disconnectButton["state"] = tk.NORMAL
        startButton["state"] = tk.NORMAL
        setButton["state"] = tk.NORMAL
        infoOutput.insert(tk.INSERT, "AD2 connected\n")
        infoOutput.see("end")


def disconnectFunction():
    disconnectButton.update()
    dwf.FDwfDeviceClose(hdwf)
    connectButton["state"] = tk.NORMAL
    disconnectButton["state"] = tk.DISABLED
    startButton["state"] = tk.DISABLED
    setButton["state"] = tk.DISABLED
    infoOutput.insert(tk.INSERT, "AD2 disconnected\n")
    infoOutput.see("end")


def setFunction():
    setButton.update()  # So the button 'Set Parameters' doesn't get blocked
    global freq_start
    global freq_end
    global freq_delta
    global amp_start
    global amp_end
    global amp_delta
    global resistance
    freq_start = int(startFreqInput.get())
    freq_end = int(endFreqInput.get())
    freq_delta = int(deltaFreqInput.get())
    amp_start = int(startAmpInput.get())
    amp_end = int(endAmpInput.get())
    amp_delta = int(deltaAmpInput.get())
    resistance = int(resistanceInput.get())
    
    dwf.FDwfDeviceAutoConfigureSet(hdwf, c_int(3))                          # Enabling dynamic adjustment of analog out settings like: frequency, amplitude...
    dwf.FDwfAnalogImpedanceReset(hdwf)
    dwf.FDwfAnalogImpedanceModeSet(hdwf, c_int(8))                          # 0 = W1-C1-DUT-C2-R-GND, 1 = W1-C1-R-C2-DUT-GND, 8 = AD IA adapter
    dwf.FDwfAnalogImpedanceReferenceSet(hdwf, c_double(resistance))         # Sets the reference resistor value in Ohms
    time.sleep(1)

    if (dec.get() == False):
        infoOutput.insert(tk.INSERT, "All Parameters set\n")
    elif (dec.get() == True):
        infoOutput.insert(tk.INSERT, "All Parameters set + DECREASE\n")
    else:
        infoOutput.insert(tk.INSERT, "Something went wrong!\n")

    infoOutput.see("end")


def startFunction():
    win.update()
    initial = time.time()                               # Take time stamp

    # region Measurement
    dwf.FDwfAnalogImpedanceConfigure(hdwf, c_int(1))    # Measurement Start

    # region For-loop Increasing
    # ut.measurementFunction(hdwf, sts, infoOutput, amp_start, amp_end, amp_delta, freq_start, freq_end, freq_delta, resistance)
    for amp in range(amp_start, amp_end + 1, amp_delta):                    # Runs all the amplitude range
        infoOutput.insert(tk.INSERT, "Start Measurement Inc: " + str(amp) + "mV \n")
        infoOutput.update()                                                 # Forces the GUI to update the text box
        infoOutput.see('end')                                               # Allows scrolling in text widget 

        extfile = open("impedance_" + str(amp) + "mV_" + str(resistance) + "Ohm_Inc.txt", "w")  # Open text-file to write measurement values
        dwf.FDwfAnalogImpedanceAmplitudeSet(hdwf, c_double(float(amp/1000)))                    # Sets the stimulus amplitude (0V to peak signal)

        for freq in range(freq_start, freq_end + 1, freq_delta):            # Runs all the frequency range increasing
            dwf.FDwfAnalogImpedanceFrequencySet(hdwf, c_double(freq))       # Sets the stimulus frequency
            time.sleep(0.01)                                                # Settle time of device under test (DUT), this value depends on the device!
            dwf.FDwfAnalogImpedanceStatus(hdwf, None)                       # Ignore last capture since we changed the frequency

            while True:
                if dwf.FDwfAnalogImpedanceStatus(hdwf, byref(sts)) == 0:
                    dwf.FDwfGetLastErrorMsg(szerr)
                    print(str(szerr.value))
                    quit()
                if sts.value == 2:
                    break

            dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceImpedance, byref(impedance))   # Read the DUT impedance value
            dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceImpedancePhase, byref(phase))  # Read the DUT phase value
            extfile.write(str(freq) + "\t" + str(abs(impedance.value)) + "\t" + str((phase.value / math.pi) * 180.0) + "\n")    # Write frequency, impedance and phase value to file

        extfile.close()
    # endregion

    # region For-loop Decreasing
    if(dec.get() == True):       
        for amp in range(amp_start, amp_end + 1, amp_delta):                    # Runs all the amplitude range
            infoOutput.insert(tk.INSERT, "Start Measurement Dec: " + str(amp) + "mV \n")
            infoOutput.update()                                                 # Forces the GUI to update the text box
            infoOutput.see('end')                                               # Allows scrolling in text widget 

            extfile = open("impedance_" + str(amp) + "mV_" + str(resistance) + "Ohm_Dec.txt", "w")  # Open text-file to write measurement values
            dwf.FDwfAnalogImpedanceAmplitudeSet(hdwf, c_double(float(amp/1000)))                    # Sets the stimulus amplitude (0V to peak signal)

            for freq in range(freq_end, freq_start - 1, -freq_delta):               # Runs all the frequency range decreasing
                dwf.FDwfAnalogImpedanceFrequencySet(hdwf, c_double(freq))       # Sets the stimulus frequency
                time.sleep(0.01)                                                # Settle time of device under test (DUT), this value depends on the device!
                dwf.FDwfAnalogImpedanceStatus(hdwf, None)                       # Ignore last capture since we changed the frequency

                while True:
                    if dwf.FDwfAnalogImpedanceStatus(hdwf, byref(sts)) == 0:
                        dwf.FDwfGetLastErrorMsg(szerr)
                        print(str(szerr.value))
                        quit()
                    if sts.value == 2:
                        break

                dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceImpedance, byref(impedance))   # Read the DUT impedance value
                dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceImpedancePhase, byref(phase))  # Read the DUT phase value
                extfile.write(str(freq) + "\t" + str(abs(impedance.value)) + "\t" + str((phase.value / math.pi) * 180.0) + "\n")    # Write frequency, impedance and phase value to file

            extfile.close()
    # endregion

    dwf.FDwfAnalogImpedanceConfigure(hdwf, c_int(0))    # Measurement End
    # endregion

    final = time.time()                                 # Take time stamp
    infoOutput.insert(tk.INSERT, "Finished: " + str(round(final - initial, 2)) + "s\n")
    infoOutput.update()
    infoOutput.see("end")                               # Allows scrolling in text widget


def clearFunction():
    clearButton.update()
    infoOutput.delete("1.0", END)


def quitFunction():
    dwf.FDwfDeviceClose(hdwf)
    win.quit()
# endregion




# region Window Layout

# region Main Window
w = 560  # width for the Tk root
h = 425  # height for the Tk root
ws = win.winfo_screenwidth()  # width of the screen
hs = win.winfo_screenheight()  # height of the screen
x = (ws / 2) - (w)
y = (hs / 2) - (h)
# set the dimensions of the screen and where it is placed
win.geometry("%dx%d+%d+%d" % (w, h, x, y))
win.configure(background="#F0F8FF")
win.title("Impedance Analyzer")
# endregion

# region Labels
startFreqLabel = Label(win, text="Start Freq [Hz]", bg="#F0F8FF", font=("arial", 12, "normal"))
startFreqLabel.grid(row=1, column=1, sticky=W)

endFreqLabel = Label(win, text="End Freq [Hz]", bg="#F0F8FF", font=("arial", 12, "normal"))
endFreqLabel.grid(row=2, column=1, sticky=W)

deltaFreqLabel = Label(win, text="Delta Freq [Hz]", bg="#F0F8FF", font=("arial", 12, "normal"))
deltaFreqLabel.grid(row=3, column=1, sticky=W)

startAmpLabel = Label(win, text="Start Amp [mV]", bg="#F0F8FF", font=("arial", 12, "normal"))
startAmpLabel.grid(row=4, column=1, sticky=W)

endAmpLabel = Label(win, text="End Amp [mV]", bg="#F0F8FF", font=("arial", 12, "normal"))
endAmpLabel.grid(row=5, column=1, sticky=W)

deltaAmpLabel = Label(win, text="Delta Amp [mV]", bg="#F0F8FF", font=("arial", 12, "normal"))
deltaAmpLabel.grid(row=6, column=1, sticky=W)

resistorLabel = Label(win, text="Resistor [Ohm]", bg="#F0F8FF", font=("arial", 12, "normal"))
resistorLabel.grid(row=7, column=1, sticky=W)

infoLabel = Label(win, text="Info", bg="#F0F8FF", font=("arial", 12, "normal"))
infoLabel.grid(row=9, column=1, sticky=W)
# endregion

# region Text Boxes
# Input Boxes
startFreqInput = Entry(win)
startFreqInput.insert(END, str(freq_start))
startFreqInput.grid(row=1, column=2, padx=20, ipadx=20, sticky=W+E)

endFreqInput = Entry(win)
endFreqInput.insert(END, str(freq_end))
endFreqInput.grid(row=2, column=2, padx=20, ipadx=20, sticky=W+E)

deltaFreqInput = Entry(win)
deltaFreqInput.insert(END, str(freq_delta))
deltaFreqInput.grid(row=3, column=2, padx=20, ipadx=20, sticky=W+E)

startAmpInput = Entry(win)
startAmpInput.insert(END, str(amp_start))
startAmpInput.grid(row=4, column=2, padx=20, ipadx=20, sticky=W+E)

endAmpInput = Entry(win)
endAmpInput.insert(END, str(amp_end))
endAmpInput.grid(row=5, column=2, padx=20, ipadx=20, sticky=W+E)

deltaAmpInput = Entry(win)
deltaAmpInput.insert(END, str(amp_delta))
deltaAmpInput.grid(row=6, column=2, padx=20, ipadx=20, sticky=W+E)

resistanceInput = ttk.Combobox(win, values = [10, 100, 1000, 10000, 100000, 1000000])
resistanceInput.set(1000)
resistanceInput.state(["readonly"])
resistanceInput.grid(row=7, column=2, padx=20, ipadx=20, sticky=W+E)

decreaseButton = Checkbutton(win, text = "Decrease (optional)", state=NORMAL, bg="#F0F8FF", font=("arial", 12, "normal"), variable = dec)
# decreaseButton = Radiobutton(win, text = "Decrease (optional)", state=NORMAL, bg="#F0F8FF", font=("arial", 12, "normal"), variable = dec)
decreaseButton.grid(row=8, column=2, sticky=W+E)

# Output boxes
infoOutput = Text(win, width=54, height=10)
infoOutput.grid(row=9, column=2, columnspan = 2, sticky=W)
# endregion

# region Buttons
connectButton = Button(
    win,
    text="Connect",
    state=NORMAL,
    bg="#F0F8FF",
    font=("arial", 12, "normal"),
    command=connectFunction,)
connectButton.grid(row=1, column=3, padx=40, sticky=W+E, ipadx=25)

disconnectButton = Button(
    win,
    text="Disconnect",
    state=DISABLED,
    bg="#F0F8FF",
    font=("arial", 12, "normal"),
    command=disconnectFunction,)
disconnectButton.grid(row=2, column=3, padx=40, sticky=W+E, ipadx=25)

setButton = Button(
    win,
    text="Set Parameters",
    state=DISABLED,
    bg="#F0F8FF",
    font=("arial", 12, "normal"),
    command=setFunction,)
setButton.grid(row=4, column=3, padx=40, sticky=W+E, ipadx=25)

startButton = Button(
    win,
    text="Start",
    state=DISABLED,
    bg="#F0F8FF",
    font=("arial", 12, "normal"),
    command=startFunction,)
startButton.grid(row=5, column=3, padx=40, sticky=W+E, ipadx=25)

clearButton = Button(
    win,
    text="Info Clear",
    state=NORMAL,
    bg="#F0F8FF",
    font=("arial", 12, "normal"),
    command=clearFunction,)
clearButton.grid(row=6, column=3, padx=40, sticky=W+E, ipadx=25)

quitButton = Button(
    win,
    text="Quit",
    state=NORMAL,
    bg="#F0F8FF",
    font=("arial", 12, "normal"),
    command=quitFunction,)
quitButton.grid(row=7, column=3, padx=40, sticky=W+E, ipadx=25)
# endregion

# endregion




# Runs the event loop of Tkinter
win.mainloop()
