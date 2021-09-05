# -*- coding: utf-8 -*-
"""
Created on Sat Aug 14 21:34:56 2021

@author: Михаил
"""
#TODO add file checks
#TODO add logging

from PIL import Image, ImageDraw

import glob
from pathlib import Path

#%% defaults
r = 10
lw_px = 2
color = 'red'


for file in glob.glob('*.jpg'):
    name = Path(file).stem
    im = Image.open(file)
    
    x, y =  im.size
    x0, y0 = x/2, y/2
    bbox = (x0-r,y0-r,x0+r,y0+r)
    
    draw = ImageDraw.Draw(im)
    
    draw.ellipse(bbox,
                 fill=None,
                 outline = color,
                 width = lw_px)
    # del draw
    
    im.save(name+'_point.png')
    # im.show()

    


