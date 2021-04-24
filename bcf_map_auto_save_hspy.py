# -*- coding: utf-8 -*-
"""
Created on Fri Apr  9 22:07:17 2021

@author: Михаил
"""
#%% init
print ('Init... ',end='')

import hyperspy.api as hs
import numpy as np
# import matplotlib.pyplot as plt
from pathlib import Path
import glob

print(' done.')


filelist = glob.glob("*.bcf")

print ('Found {} .BCF files, processing...'.format(len(filelist)))

def get_image_size_mm(hmap):
    omd = hmap.original_metadata

    dx = omd.Microscope.DX
    dy = omd.Microscope.DY
    
    
    ny = omd.DSP_Configuration.ImageHeight
    nx = omd.DSP_Configuration.ImageWidth
    
    w_mm = (nx) * np.round(dx,decimals=3) /1000
    h_mm = (ny+1) * np.round(dy,decimals=3) /1000
    
    return (w_mm, h_mm)



#%% bcf load, extract hmap

for import_file in filelist:
# import_file = filelist[0]

    print ('Processing file: {} ...'.format(import_file), end='')
    bcf=hs.load(import_file)
    hmap=bcf[4]
    print (' done.')
    print ('Extracting hypermap data... ',end='')
    hmap.metadata.Acquisition_instrument.SEM.beam_energy=80
    # intensity_maps = hmap.get_lines_intensity()
    image_size_mm = get_image_size_mm(hmap)
    hmap.metadata.image_size_mm = image_size_mm
    
    
    orig_filename = hmap.metadata.General.original_filename
    export_filename = Path(orig_filename).stem + '.hspy'
    print (' done.')
    print ('Saving as {} file...'.format(export_filename),end='')
    hmap.save(export_filename)
    print (' done.')



