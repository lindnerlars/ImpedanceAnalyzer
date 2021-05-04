import tkinter as tk
from tkinter import ttk
from tkinter import *

# This variable must be defined AFTER definition of the Tk() window!
dec = tk.BooleanVar()

# Variables Definitons
win = Tk()

# # This variable must be defined AFTER definition of the Tk() window!
# dec = tk.BooleanVar()


decreaseButton = Checkbutton(win, text = "Decrease (optional)", variable = dec)
decreaseButton.grid(row=1, column=1, sticky='W')


# Runs the event loop of Tkinter
win.mainloop()
