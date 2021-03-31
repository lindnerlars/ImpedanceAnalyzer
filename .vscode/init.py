"""
   init.py
   Author:  Lars Lindner
   Revision:  31/03/2021

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


# Default values for parameters
freq_start = int(3.9e6)
freq_end = int(4.1e6)
freq_delta = int(10000)
resistance = int(1000)
amplitude = float(1)

# Variables Definitons
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

