# -*- coding: utf-8 -*-
"""
Created on Sun May  2 10:57:05 2021

@author: Михаил

hmap processing script for neolithic ceramic
1. load hmap
2. plot Si map, select cutoff value
3. plot Si with cutoff
4. mask other elements
5. calculate mean,median,skew
6. plot histogram and coolwarm map

"""
#%% init 
import hyperspy.api as hs
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import scipy.ndimage as nd
import os
import matplotlib.colors as colors
from matplotlib import cm

from matplotlib_scalebar.scalebar import ScaleBar

from datetime import datetime

workdir = u'C:/Users/Михаил/Google Диск/археология/IRK/hspy' #vivo book
os.chdir(workdir)

#%% functions
def get_element_map(element_name,int_maps):
    # extract element int_map by name
    for im in int_maps:
        if element_name in im.metadata.Sample.elements:
            return im
    return None

def plot_hist(elt,caption=None,log=True,bins=50):
    flat = elt.flatten()

    plt.hist(flat,bins=bins,
             log=log,density=True,
             histtype='step')
    
    plt.xlabel('Line Intensity, cps')
    plt.ylabel('Probability Density')
    if caption:
        plt.title(caption)
#%% load hspy
hmap_file = 'IRK-31.hspy'
hmap = hs.load(hmap_file)

#%% process hspy
intensity_maps = hmap.get_lines_intensity()
elements = hmap.metadata.Sample.elements
image_size_mm = hmap.metadata.image_size_mm
extent = (0,image_size_mm[0],0,image_size_mm[1])
orig_filename = hmap.metadata.General.original_filename
export_filename_stem = Path(orig_filename).stem
print ('These elements are marked in hypermap:')
print (elements)

mosaic_lowres = hmap.metadata.mosaic_lowres

#%% plot Si map and hist and select cutoff value
si = get_element_map('Si',intensity_maps)
si_f = nd.gaussian_filter(si, 1) #blur si map

#%% plot temp histogram for selection of cutoff
plot_hist(si_f,log=False)

cutoff = 35

si_f_masked = np.ma.masked_less(si_f,cutoff)
#%% plot four subplots for export

vmax = si_f_masked.max()
vmin = si_f_masked.min()

fig, axes = plt.subplots(2,2,dpi=300)

plt.suptitle('Original datafile: {0}. Plotted on: {1.year}-{1.month}-{1.day} {1.hour}:{1.minute}:{1.second}'.format(orig_filename,datetime.now()),
             size='x-small',
             x=0.01,y=0,ha='left')

axes[0,0].imshow(si_f,extent=extent,vmax=vmax,vmin=vmin)
axes[0,0].set_title('Si K\u03b1 Line Map')

axes[0,0].get_xaxis().set_visible(False)
axes[0,0].get_yaxis().set_visible(False)

scalebar_white = ScaleBar(1, "mm", length_fraction=0.25,
                          frameon=False,color='white',
                          location='lower left',
                          font_properties = {'size':'x-small'})
axes[0,0].add_artist(scalebar_white)

axes[1,0].imshow(si_f_masked,extent=extent,vmax=vmax,vmin=vmin)
axes[1,0].set_title('Cutoff intensity = {} cps'.format(cutoff))

axes[1,0].get_xaxis().set_visible(False)
axes[1,0].get_yaxis().set_visible(False)

scalebar_black = ScaleBar(1, "mm", length_fraction=0.25,
                          frameon=False,color='black',
                          location='lower left',
                          font_properties = {'size':'x-small'})
axes[1,0].add_artist(scalebar_black)

axes[0,1].hist(si_f.flatten(),
               bins=50,
               density=True,
               histtype='step')
axes[0,1].set_xlabel('Line Intensity, cps')
axes[0,1].set_ylabel('Probability Density')
axes[0,1].set_title('Si K\u03b1 Intensity Histogram')


axes[0,1].axvline(cutoff,color='r',label='Cutoff')
axes[0,1].legend()

axes[1,1].imshow(mosaic_lowres,extent=extent,cmap='gray')
axes[1,1].set_title('Video Mosaic')

axes[1,1].get_xaxis().set_visible(False)
axes[1,1].get_yaxis().set_visible(False)

scalebar_white = ScaleBar(1, "mm", length_fraction=0.25,
                          location='lower left',
                          font_properties = {'size':'x-small'})
axes[1,1].add_artist(scalebar_white)

fig.tight_layout(pad=0.4, w_pad=3, h_pad=3.0)




