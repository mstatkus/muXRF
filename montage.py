# -*- coding: utf-8 -*-
"""
Created on Sat Aug 14 21:34:56 2021

@author: Михаил
"""
#TODO add file checks
#TODO add logging

from PIL import Image, ImageOps

import glob
from pathlib import Path

#%% defaults
dpi = 300
page_w_cm = 16
page_h_cm = 25

columns = 3

#%% load PNGs to dict
images = {}
heights_px = []
widths_px = []

for file in glob.glob('*.png'):
    name = Path(file).stem
    im = Image.open(file)
    images[name]=im
    heights_px.append(im.height)
    widths_px.append(im.width)
    
#%% padding to max h and w
max_w_px = max(widths_px)
max_h_px = max(heights_px)

for im in images:
    images[im] = ImageOps.pad(images[im],
                              size=(max_w_px,max_h_px),
                              color='white')

#%% calculate image sizes with respect to columns and pagesize
page_w_px = int(dpi * page_w_cm // 2.54)
page_h_px = int(dpi * page_h_cm // 2.54)

max_allowed_w_px = page_w_px // columns
scale = max_allowed_w_px / max_w_px

for im in images:
    images[im] = ImageOps.scale(images[im], scale)
    images[im].save(im+'.png')

