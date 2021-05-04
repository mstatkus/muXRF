# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 12:57:19 2021

@author: Mike

script for plotting all maps and histograms from a dir of hspy files
"""


import hyperspy.api as hs
# import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import glob

# "full" list of elements for ceramics
full_element_list = ['Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'K', 'Ca', 
                     'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu',
                     'Zn', 'Rb', 'Sr', 'Y', 'Zr', 'Ba', 'La', 'Ce', 'W']

#set true to replace original elements with full list above
replace_element_list = True 

#%%
def plot_hist(elt,caption=None):
    flat = elt.data.flatten()
    plt.hist(flat,bins=50,
             log=True,density=True,
             histtype='step')
    
    plt.xlabel('Line intensity, cps')
    plt.ylabel('Probability Density')
    if caption:
        plt.title(caption)

def plot_map(elt,image_size_mm,
             caption=None,vmax=None):
    if vmax:
        plt.imshow(elt.data, 
                   vmax=vmax,
                   extent = (0,image_size_mm[0],0,image_size_mm[1]))
        plt.colorbar(extend='max',label = 'Intensity,cps')
    else:
        plt.imshow(elt.data, 
                   extent = (0,image_size_mm[0],0,image_size_mm[1]))
        plt.colorbar(label = 'Intensity,cps')
    
    plt.xlabel('x, mm')
    plt.ylabel('y, mm')
    if caption:
        plt.title(caption)
        
def plot_mosaic_lowres(mosaic_lowres, image_size_mm, caption=None):
    plt.imshow(mosaic_lowres,
               extent = (0,image_size_mm[0],0,image_size_mm[1]),
               cmap='gray')
    plt.xlabel('x, mm')
    plt.ylabel('y, mm')
    if caption:
        plt.title(caption)
    
    

#%%

filelist = glob.glob("*.hspy")

print ('Found {} .HSPY files, processing...'.format(len(filelist)))
print ('')

for import_file in filelist:
    print ('Loading file: {} ...'.format(import_file), end='')

    hmap = hs.load(import_file)
    print ('done')
    
    if replace_element_list:
        print ('Replacing original elements with custom list...',end='')
        #%% test - clear elements and lines
        hmap.set_elements([]) #TODO - check whether clearing is necessary
        hmap.set_lines([])
        
        hmap.set_elements(full_element_list)
        hmap.add_lines()
        print ('done.')
    
    
    print('Extracting data...')
    intensity_maps = hmap.get_lines_intensity()
    
    elements = hmap.metadata.Sample.elements
    
    image_size_mm = hmap.metadata.image_size_mm
    
    orig_filename = hmap.metadata.General.original_filename
    export_filename_stem = Path(orig_filename).stem
    print('done')
    print ('These elements are marked in hypermap:')
    print (' '.join(elements))
    
    # processing lowres
    
    print ('Extracting lowres mosaic...',end='')
    mosaic_lowres = hmap.metadata.mosaic_lowres
    export_name_mosaic = '{}_MSC.png'.format(export_filename_stem)
    plot_mosaic_lowres(mosaic_lowres,
                       image_size_mm = image_size_mm,
                       caption = 'Lowres Mosaic {}'.format(export_filename_stem))
    plt.savefig(export_name_mosaic,dpi=300)
    plt.close()
    print ('done.')
   
    
    for i, elt in enumerate(intensity_maps):
        elt_name = elements[i]
        print('Processing {} data...'.format(elt_name),end='')
        
        plot_map(elt, image_size_mm,caption=elt_name+'\n'+ orig_filename)
        export_name_map = '{}_{}_MAP.png'.format(export_filename_stem, elt_name)
        export_name_hist = '{}_{}_HST.png'.format(export_filename_stem, elt_name)
        plt.savefig(export_name_map,dpi=300)
        plt.close()
    
        plot_hist(elt,caption=elt_name+'\n'+ orig_filename)
        plt.savefig(export_name_hist,dpi=300)
        plt.close()
        
        print(' done.')


