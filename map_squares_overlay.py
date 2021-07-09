# -*- coding: utf-8 -*-
"""
Created on Fri Jul  9 11:12:37 2021

@author: Михаил
"""

import matplotlib.pyplot as plt
import string
import numpy as np
import matplotlib.ticker as tk

mosaic_file = 'mosaic_full_scalebar_contour.png'

msc=plt.imread(mosaic_file)

y,x,c = np.shape(msc)

delta_px = 100 #step between gridlines

xlabels = list(string.ascii_uppercase)

#%%

def format_letter(tick_val, tick_pos):
    pos = int(tick_val/delta_px)
    return xlabels[pos]

def format_number(tick_val, tick_pos):
    return int(tick_val/delta_px)+1

fig, ax = plt.subplots()

ax.imshow(msc)
ax.xaxis.set_major_locator(tk.MultipleLocator(delta_px))
ax.xaxis.set_major_formatter(tk.NullFormatter())

ax.xaxis.set_minor_locator(tk.MultipleLocator(delta_px/2))
ax.xaxis.set_minor_formatter(format_number)

for tick in ax.xaxis.get_minor_ticks():
    tick.tick1line.set_markersize(0)
    tick.tick2line.set_markersize(0)
    tick.label1.set_horizontalalignment('center')

ax.yaxis.set_major_locator(tk.MultipleLocator(delta_px))
ax.yaxis.set_major_formatter(tk.NullFormatter())

ax.yaxis.set_minor_locator(tk.MultipleLocator(delta_px/2))
ax.yaxis.set_minor_formatter(format_letter)

for tick in ax.yaxis.get_minor_ticks():
    tick.tick1line.set_markersize(0)
    tick.tick2line.set_markersize(0)
    # tick.label1.set_horizontalalignment('center')


plt.grid(linestyle = 'dotted',color='black')

plt.savefig('msc.png', dpi=1200)
