"""
   Impedance Analyzer 
   Author:  Lars Lindner
   Revision:  15/03/2021

   -> This programm does a logarithmic frequency sweep from 'freq_start' to 'freq_end' in 'freq_steps' using a GUI interface
   -> It prints the impedance [kOhm] and phase [deg] as an image and the numerical values as .txt file
"""


import tkinter as tk
# from ttkthemes import themed_tk as tk
from tkinter import ttk
from tkinter import * 

from ctypes import *
from dwfconstants import *

import math
import time
import sys
import numpy as np
import matplotlib.pyplot as plt

# Default values for parameters
freq_start = 100
freq_end = 100000
steps = 100
resistance = 1000
amplitude = 1

# Variables Definitons
# win = tk.ThemedTk()
# win.set_theme("plastik")
win = Tk()
hdwf = c_int()
sts = c_byte()
impedance = c_double()
phase = c_double()


# Load .dll
if sys.platform.startswith("win"):
    dwf = cdll.LoadLibrary("dwf.dll")
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")


def connectFunction():
	szerr = create_string_buffer(512)
	# print("Opening first device")
	dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

	if hdwf.value == hdwfNone.value:
		dwf.FDwfGetLastErrorMsg(szerr)
		infoOutput.insert(tk.INSERT, str(szerr.value) + "\n")
		infoOutput.see('end')
		# infoOutput.insert(tk.INSERT, "ADS failed to open\n")		
	else:
		connectButton['state'] = tk.DISABLED
		disconnectButton['state'] = tk.NORMAL
		startButton['state'] = tk.NORMAL
		setButton['state'] = tk.NORMAL
		infoOutput.insert(tk.INSERT, "AD2 connected\n")
		infoOutput.see('end')


def disconnectFunction():
	dwf.FDwfDeviceClose(hdwf)
	connectButton['state'] = tk.NORMAL
	disconnectButton['state'] = tk.DISABLED
	startButton['state'] = tk.DISABLED
	setButton['state'] = tk.DISABLED
	infoOutput.insert(tk.INSERT, "AD2 disconnected\n")
	infoOutput.see('end')


def setFunction():
	global freq_start
	global freq_end
	global steps
	global resistance
	global amplitude	
	freq_start = float(startInput.get())
	freq_end = float(endInput.get())
	steps = int(stepsInput.get())
	resistance = int(resistanceInput.get())
	amplitude = float(amplitudeInput.get())

	dwf.FDwfDeviceAutoConfigureSet(hdwf, c_int(3)) # this option will enable dynamic adjustment of analog out settings like: frequency, amplitude...
	dwf.FDwfAnalogImpedanceReset(hdwf)
	dwf.FDwfAnalogImpedanceModeSet(hdwf, c_int(8)) # 0 = W1-C1-DUT-C2-R-GND, 1 = W1-C1-R-C2-DUT-GND, 8 = AD IA adapter
	dwf.FDwfAnalogImpedanceFrequencySet(hdwf, c_double(freq_start)) # frequency in Hertz
	dwf.FDwfAnalogImpedanceReferenceSet(hdwf, c_double(resistance)) # reference resistor value in Ohms
	dwf.FDwfAnalogImpedanceAmplitudeSet(hdwf, c_double(amplitude)) # Measurement amplitude, 0V to peak signal
	time.sleep(1)

	infoOutput.insert(tk.INSERT, "All parameters set\n")
	infoOutput.see('end')


def startFunction():
	extfile = open("impedance_" + str(amplitudeInput.get()) + "V.txt", "w")
	extfile.write("Frequency [hz]" + "\t" + "Impedance [kOhm]" + "\t" + "Phase [rad]" + "\n")
	# infoOutput.insert(tk.INSERT, "Start Measurement\n")
	# infoOutput.see('end')
	# time.sleep(1)

	dwf.FDwfAnalogImpedanceConfigure(hdwf, c_int(1)) # Measurement start

	for i in range(steps):
		hz = freq_end * pow(10.0, 1.0*(1.0*i/(steps-1)-1)*math.log10(freq_end/freq_start)) # exponential frequency freq_steps
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
		dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceImpedancePhase, byref(phase))
		# extfile.write(str(hz) + "\t" + str(abs(impedance.value / 1000)) + "\t" + str((phase.value / math.pi) * 180.0) + "\n")
		extfile.write(str(hz) + "\t" + str(abs(impedance.value / 1000)) + "\t" + str(phase.value) + "\n")
		
	dwf.FDwfAnalogImpedanceConfigure(hdwf, c_int(0)) # Measurement end

	infoOutput.insert(tk.INSERT, "Finished Measurement\n")
	infoOutput.see('end')


def clearFunction():
	infoOutput.delete('1.0', END)


def quitFunction():
	dwf.FDwfDeviceClose(hdwf)
	win.quit()




# This is the section of code which creates the main window
w = 540 # width for the Tk root
h = 300 # height for the Tk root
ws = win.winfo_screenwidth() # width of the screen
hs = win.winfo_screenheight() # height of the screen
x = (ws/2) - (w)
y = (hs/2) - (h)
# set the dimensions of the screen and where it is placed
win.geometry('%dx%d+%d+%d' % (w, h, x, y))
win.configure(background='#F0F8FF')
win.title('Impedance Analyzer')




# This is the section of code which creates all labels
startLabel = Label(win, text='freq_start [Hz]', bg='#F0F8FF', font=('arial', 12, 'normal'))
startLabel.grid(row = 1, column = 1, sticky = "W")

endLabel = Label(win, text='frequ_end [Hz]', bg='#F0F8FF', font=('arial', 12, 'normal'))
endLabel.grid(row = 2, column = 1, sticky = "W")

stepsLabel = Label(win, text='steps [No.]', bg='#F0F8FF', font=('arial', 12, 'normal'))
stepsLabel.grid(row = 3, column = 1, sticky = "W")

resistorLabel = Label(win, text='Resistor [Ohm]', bg='#F0F8FF', font=('arial', 12, 'normal'))
resistorLabel.grid(row = 4, column = 1, sticky = "W")

amplitudeLabel = Label(win, text='Amplitude [V]', bg='#F0F8FF', font=('arial', 12, 'normal'))
amplitudeLabel.grid(row = 5, column = 1, sticky = "W")

infoLabel = Label(win, text='Info', bg='#F0F8FF', font=('arial', 12, 'normal'))
infoLabel.grid(row = 6, column = 1, sticky = "W")




# This is the section of code which creates all text input boxes
startInput = Entry(win)
startInput.insert(END, str(freq_start))
startInput.grid(row = 1, column = 2, padx = 20, ipadx = 20, sticky = "W")

endInput=Entry(win)
endInput.insert(END, str(freq_end))
endInput.grid(row = 2, column = 2, padx = 20, ipadx = 20)

stepsInput = Entry(win)
stepsInput.insert(END, str(steps))
stepsInput.grid(row = 3, column = 2, padx = 20, ipadx = 20)

resistanceInput = Entry(win)
resistanceInput.insert(END, str(resistance))
resistanceInput.grid(row = 4, column = 2, padx = 20, ipadx = 20)

amplitudeInput = Entry(win)
amplitudeInput.insert(END, str(amplitude))
amplitudeInput.grid(row = 5, column = 2, padx = 20, ipadx = 20)




# This is the section of code which creates all text output boxes
infoOutput = Text(win, height = 5, width = 25)
infoOutput.grid(row = 6, column = 2, sticky = "W")




# This is the section of code which creates all buttons
connectButton = Button(win, text='Connect', state=NORMAL, bg='#F0F8FF', font=('arial', 12, 'normal'), command=connectFunction)
# connectButton = ttk.Button(win, text = 'Connect')
connectButton.grid(row = 1, column = 3, padx = 40, sticky = "E", ipadx = 25)

disconnectButton = Button(win, text='Disconnect', state=DISABLED, bg='#F0F8FF', font=('arial', 12, 'normal'), command=disconnectFunction)
disconnectButton.grid(row = 2, column = 3, padx = 40, sticky = "E", ipadx = 25)

setButton = Button(win, text='Set Parameters', state=DISABLED, bg='#F0F8FF', font=('arial', 12, 'normal'), command=setFunction)
setButton.grid(row = 4, column = 3, padx = 40, sticky = "E", ipadx = 25)

startButton = Button(win, text='Start', state=DISABLED, bg='#F0F8FF', font=('arial', 12, 'normal'), command=startFunction)
startButton.grid(row = 5, column = 3, padx = 40, sticky = "E", ipadx = 25)

clearButton = Button(win, text='Info Clear', state=NORMAL, bg='#F0F8FF', font=('arial', 12, 'normal'), command=clearFunction)
clearButton.grid(row = 6, column = 3, padx = 40, sticky = "E", ipadx = 25)

quitButton = Button(win, text='Quit', state=NORMAL, bg='#F0F8FF', font=('arial', 12, 'normal'), command=quitFunction)
quitButton.grid(row = 7, column = 3, padx = 40, sticky = "E", ipadx = 25)




win.mainloop()










# from tkinter import *

# fenster = Tk()
# fenster.title("Impedance Analyzer")
# fenster.geometry("200x50")

# label = Label(fenster, text = "Este GUI analiza la Impedancia y Fase de una bipuerta")
# label.grid(row = 1, column = 1) #Anordnung durch Grid-Manager
# # label.pack() #Anordnung durch Pack-Manager
# # label.place(x = 10, y = 10) #Anordnung durch Place-Manager

# fenster.mainloop()




## tkinter using object-oriented approach (from English Wikipedia: https://en.wikipedia.org/wiki/Tkinter)
# import tkinter as tk

# class Application(tk.Frame):

#     def __init__(self, master=None):
#         tk.Frame.__init__(self, master)
#         self.grid()  
#         self.createWidgets()

#     def createWidgets(self):
#         self.mondialLabel = tk.Label(self, text='Este GUI analiza la Impedancia y Fase de una bipuerta')
#         # self.mondialLabel.config(bg="#00ffff")
#         self.mondialLabel.grid()
#         self.quitButton = tk.Button(self, text='Quit', command= self.quit)
#         self.quitButton.grid()

# app = Application()
# app.master.title('Impedance Analyzer')
# app.mainloop()

