# -*- coding: utf-8 -*-
"""
Created on Thu Jul  1 10:37:31 2021

@author: Mike
"""



#%% init

import sys
from pathlib import Path

try:
    import_file = Path(sys.argv[1])
    import_file.resolve(strict=True)
except IndexError:
    print ('No filename given')
    sys.exit()
except FileNotFoundError:
    print ('{} : No such file'.format(import_file))
    sys.exit()

#%%
import hyperspy.api as hs
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib_scalebar.scalebar import ScaleBar


# "full" list of elements for ochre plates
full_element_list = ['Si', 'Ca', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Ba']

#set true to replace original elements with full list above
replace_element_list = True 

#%% funcs
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



#%% processing


bcf = hs.load(import_file)
hmap = bcf[4]
hmap.metadata.Acquisition_instrument.TEM.beam_energy=80

if replace_element_list:
    print ('Replacing original elements with custom list...',end='')
   
    hmap.set_elements([]) #TODO - check whether clearing is necessary
    hmap.set_lines([])
    
    hmap.set_elements(full_element_list)
    hmap.add_lines()
    print ('done.')

im = hmap.get_lines_intensity()

image_size_mm = get_image_size_mm(hmap)
extent = (0,image_size_mm[0],0,image_size_mm[1])
hmap.metadata.image_size_mm = image_size_mm

fe = im[3]

ca=im[1]

#%%

fe_low_cutoff = 100
fe_high_cutoff = 600


fe_masked = np.ma.masked_less(fe.data,fe_low_cutoff)

title = 'Part A'

#%% plot fe+ca


fig, ax = plt.subplots()

img_ca=ax.imshow(ca.data,cmap='Greys',extent=extent)
img_fe=ax.imshow(fe_masked,cmap='Reds',alpha=0.75,
                 vmin=0,vmax=fe_high_cutoff, extent=extent)
# fig.colorbar(img_ca,ax=ax,label = 'Ca K\u03B1 intensity,cps',
#                   shrink=0.8)
# fig.colorbar(img_fe,ax=ax,label = 'Fe K\u03B1 intensity,cps',
#                   extend='max',shrink=0.8)

# ax.set_title(title)

# fig.set_size_inches(6.4,4.8)

# scalebar 
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)
scalebar_black = ScaleBar(1, "mm", length_fraction=0.25,
                          frameon=False,color='black',
                          location='lower right',
                          font_properties = {'size':'x-small'})
ax.add_artist(scalebar_black)
# print(fig.get_size_inches())
plt.savefig('fe-ca_mask.png',dpi=300)

#%% plot fe - cmr -sqrt
fig, ax = plt.subplots()
# img_fe=ax.imshow(fe,cmap='viridis', vmax = fe_high_cutoff,
#                  extent=extent)
img_fe=ax.imshow(fe,cmap='CMRmap', norm=colors.PowerNorm(gamma=0.5),
                 extent=extent, vmax = fe_high_cutoff,)
fig.colorbar(img_fe,ax=ax,label = 'Fe K\u03B1 intensity,cps',
                  extend = 'max',shrink=0.8)

# scalebar 
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)
scalebar_black = ScaleBar(1, "mm", length_fraction=0.25,
                          frameon=False,color='white',
                          location='lower right',
                          font_properties = {'size':'x-small'})
ax.add_artist(scalebar_black)
plt.savefig('fe_sqrt.png',dpi=300)

#%% plot fe-reds
fig, ax = plt.subplots()
img_fe=ax.imshow(fe,cmap='Reds', vmax = fe_high_cutoff,
                 extent=extent)
fig.colorbar(img_fe,ax=ax,label = 'Fe K\u03B1 intensity,cps',
                  extend='max',shrink=0.8)

# scalebar 
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)
scalebar_black = ScaleBar(1, "mm", length_fraction=0.25,
                          frameon=False,color='black',
                          location='lower right',
                          font_properties = {'size':'x-small'})
ax.add_artist(scalebar_black)
plt.savefig('fe-reds.png',dpi=300)