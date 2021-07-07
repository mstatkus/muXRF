# -*- coding: utf-8 -*-
"""
Created on Wed Jul  7 09:01:59 2021

@author: Михаил

Plot eight simple element maps as a 4x2 montage
"""


#%% init 
import hyperspy.api as hs
# import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys
# import scipy.ndimage as nd
# import os
# import matplotlib.colors as colors
# from matplotlib import cm

# from matplotlib_scalebar.scalebar import ScaleBar

hmap_file = 'IRK-66.hspy' #TODO replace with sys.argv


# "short" list of elements for ceramics
full_element_list = ['Si','K', 'Ca', 'Ti', 'Mn', 'Fe', 'Sr','Ba']

#set true to replace original elements with full list above
replace_element_list = True 

#%% load hspy

hmap = hs.load(hmap_file)

#%% process hspy

if replace_element_list:
    print ('Replacing original elements with custom list...',end='')
   
    hmap.set_elements([])
    hmap.set_lines([])
    
    hmap.set_elements(full_element_list)
    hmap.add_lines()
    print ('done.')

intensity_maps = hmap.get_lines_intensity()
elements = hmap.metadata.Sample.elements
image_size_mm = hmap.metadata.image_size_mm
extent = (0,image_size_mm[0],0,image_size_mm[1])
aspect_ratio = image_size_mm[0] / image_size_mm[1]
print ('Image aspect ratio = {}'.format(aspect_ratio))
orig_filename = hmap.metadata.General.original_filename
export_filename_stem = Path(orig_filename).stem
print ('These elements are marked in hypermap:')
print (elements)

#%%
if len(intensity_maps)!=8: #TODO replace with propoer handling of !=8
    print ('Should be 8 elements to plot montage, quitting')
    sys.exit()

fig, axes = plt.subplots(2,4,dpi=300)
plt.suptitle('{} Intensity Maps'.format(export_filename_stem))
for i, elt in enumerate(intensity_maps):
    elt_name = elt.metadata.Sample.elements[0]
    data = elt.data
    # print (i //4, i % 4)
    row = i//4
    column = i % 4
    
    ax = axes[row][column]
    img = ax.imshow(data,extent=extent)
    if aspect_ratio <= 1:
        fig.colorbar(img, ax = ax,location='left')
    else:
        fig.colorbar(img, ax = ax,location='bottom')
    ax.set_title(elt_name)

    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    
fig.tight_layout()
plt.savefig('{}_maps_montage.png'.format(export_filename_stem))