# -*- coding: utf-8 -*-
"""
Convertor of multiple Bruker muXRF BCF files to Hyperspy files

Created on Fri Apr  9 22:07:17 2021

@author: Mike Statkus

Suppress Hyperspy GUI warnings during first launch:
import hyperspy.api as hs
hs.preferences.GUIs.warn_if_guis_are_missing = False
hs.preferences.save()

"""
#%% init

import hyperspy.api as hs
import numpy as np
from pathlib import Path
import glob

def get_image_size_mm(hmap):
    
    omd = hmap.original_metadata
    
    # dx and dy are calculated scan steps in um
    dx = omd.Microscope.DX
    dy = omd.Microscope.DY
    
    # ny and nx are number of pixels in map
    ny = omd.DSP_Configuration.ImageHeight
    nx = omd.DSP_Configuration.ImageWidth
    
    # actual map dimensions in mm
    w_mm = (nx) * np.round(dx,decimals=3) /1000
    h_mm = (ny+1) * np.round(dy,decimals=3) /1000
    
    return (w_mm, h_mm)



#%% bcf load, extract hmap

# list of all files in CWD with .bcf extension
filelist = glob.glob("*.bcf")

print ('Found {} .BCF files, processing...'.format(len(filelist)))
print ('')

for import_file in filelist:

    print ('Processing file: {} ...'.format(import_file), end='')
    bcf=hs.load(import_file)
    # first 3 items in bcf are mosaic images, skipping them...
    #TODO: select hypermap by content, not by position 
    hmap=bcf[4] 
    print (' done.')
    print ('Extracting hypermap data... ',end='')
    
    
    # We need to set beam_energy to arbitrary high value, e.g. 80 kEv,
    # to work with SEM class with XRF data
    hmap.metadata.Acquisition_instrument.SEM.beam_energy=80
    
    image_size_mm = get_image_size_mm(hmap)
    hmap.metadata.image_size_mm = image_size_mm
    
    
    orig_filename = hmap.metadata.General.original_filename
    export_filename = Path(orig_filename).stem + '.hspy'
    print (' done.')
    
    print ('Saving as {} file...'.format(export_filename),end='')
    hmap.save(export_filename)
    print (' done.')



