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

import csv

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
        

def np_skew(elt_map):
    median = np.ma.median(elt_map)
    mean = np.ma.mean(elt_map)
    std = np.ma.std(elt_map)
    
    skew = (mean - median)/ std
    
    return (mean,median,std,skew)


def plot_si_figure(si_f,si_f_masked,mosaic_lowres,export_filename_stem=None,save=False):
    vmax = si_f_masked.max()
    # vmin = si_f_masked.min()
    
    fig, axes = plt.subplots(2,2,dpi=300)
    
    plt.suptitle('Original datafile: {0} Plotted on: {1.year}-{1.month:02d}-{1.day:02d} {1.hour:02d}:{1.minute:02d}:{1.second:02d}'.format(orig_filename,datetime.now()),
                 size='x-small',
                 x=0.01,y=0,ha='left')
    
    img00 = axes[0,0].imshow(si_f,extent=extent,vmax=vmax,vmin=0)
    fig.colorbar(img00,ax=axes[0,0],label='Intensity, cps',shrink=0.8,location='left')
    axes[0,0].set_title('Si K\u03b1 Line Map')
    
    axes[0,0].get_xaxis().set_visible(False)
    axes[0,0].get_yaxis().set_visible(False)
    
    scalebar_white = ScaleBar(1, "mm", length_fraction=0.25,
                              frameon=False,color='white',
                              location='lower left',
                              font_properties = {'size':'x-small'})
    axes[0,0].add_artist(scalebar_white)
    
    img10 = axes[1,0].imshow(si_f_masked,extent=extent,vmax=vmax,vmin=0)
    fig.colorbar(img10,ax=axes[1,0],label='Intensity, cps',shrink = 0.8,location='left')
    
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
    
    fig.tight_layout(w_pad=2.0, h_pad=2.0)
    
    export_filename = '{}_Si_cutoff.png'.format(export_filename_stem)
    if save:
        plt.savefig(export_filename,bbox_inches='tight')
        plt.close(fig)

def process_single_element(elt_name, intensity_maps, mask, 
                           writer, export_filename_stem,
                           landscape = True):
    
    elt_map = get_element_map(elt_name, intensity_maps).data
    elt_map_masked = np.ma.array(elt_map,mask=mask)
    
    (mean,median,std,skew) = np_skew(elt_map_masked)
    ratio = (mean-median)/mean
    
    # csv_header = ['Sample', 'Element', 'Mean', 'Median', 'STD', 'Skew', 'Ratio']
    
    row = [export_filename_stem, elt_name, mean, median, std, skew, ratio]
    
    writer.writerow(row)
    
    cmap = cm.coolwarm
    vmin = elt_map_masked.min()
    vmax = elt_map_masked.max()
    
    divnorm = colors.TwoSlopeNorm(vmin=vmin, vcenter=median, vmax=vmax)

    # landscape = True #2 cols, 1 row
    # landscape = False #1 col, 2 rows

    if landscape:
        fig, axes = plt.subplots(2,1,dpi=300)
    else:
        fig, axes = plt.subplots(1,2,dpi=300)
    
    
    plt.suptitle('Original datafile: {0} Plotted on: {1.year}-{1.month:02d}-{1.day:02d} {1.hour:02d}:{1.minute:02d}:{1.second:02d}'.format(orig_filename,datetime.now()),
                 size='x-small',
                 x=0.01,y=0,ha='left')
    
    img00 = axes[0].imshow(elt_map_masked,norm=divnorm,cmap=cmap,extent=extent)
    fig.colorbar(img00,ax=axes[0],label='Intensity, cps',shrink=1,location='left')
    axes[0].set_title('{} Intensity Map'.format(elt_name))
    
    axes[0].get_xaxis().set_visible(False)
    axes[0].get_yaxis().set_visible(False)
    
    scalebar_black = ScaleBar(1, "mm", length_fraction=0.25,
                              frameon=False,color='black',
                              location='lower left',
                              font_properties = {'size':'x-small'})
    axes[0].add_artist(scalebar_black)
    
    axes[1].hist(elt_map_masked.flatten(),
                   bins=50,
                   density=True,
                   histtype='step')
    axes[1].set_xlabel('Line Intensity, cps')
    axes[1].set_ylabel('Probability Density')
    axes[1].set_title('{} Intensity Histogram'.format(elt_name))
    
    
    axes[1].axvline(median,color='r',label='Median')
    axes[1].axvline(mean,color='g',label='Mean')
    axes[1].legend()
    
    fig.tight_layout(w_pad=2.0, h_pad=2.0)
    
    export_filename = '{}_{}.png'.format(export_filename_stem,elt_name)
    
    plt.savefig(export_filename,bbox_inches='tight')
    plt.close(fig)
#%% load hspy
hmap_file = 'IRK-66.hspy'
hmap = hs.load(hmap_file)

# process hspy
intensity_maps = hmap.get_lines_intensity()
elements = hmap.metadata.Sample.elements
image_size_mm = hmap.metadata.image_size_mm
extent = (0,image_size_mm[0],0,image_size_mm[1])
orig_filename = hmap.metadata.General.original_filename
export_filename_stem = Path(orig_filename).stem
print ('These elements are marked in hypermap:')
print (elements)

mosaic_lowres = hmap.metadata.mosaic_lowres

# create csv for export of stat data

csv_filename = export_filename = '{}_stats.csv'.format(export_filename_stem)

csv_file = open(csv_filename, 'w', newline='')
writer = csv.writer(csv_file, delimiter=';')
csv_header = ['Sample', 'Element', 'Mean', 'Median', 'STD', 'Skew', 'Ratio']
writer.writerow(csv_header)

# plot Si map and hist and select cutoff value
si = get_element_map('Si',intensity_maps)
si_f = nd.gaussian_filter(si, 1) #blur si map

# plot temp histogram for selection of cutoff
plot_hist(si_f,log=False)
#%% set cutoff value
cutoff = 20

si_f_masked = np.ma.masked_less(si_f,cutoff)

mask = si_f_masked.mask

plot_si_figure(si_f, si_f_masked,mosaic_lowres,save=False)
#%%
plot_si_figure(si_f, si_f_masked,mosaic_lowres, export_filename_stem, save=True)



for elt_name in elements:
    print ('Processing {} element...'.format(elt_name),end='')

    process_single_element(elt_name, intensity_maps, mask, writer, export_filename_stem)
    
    print ('done')
    
csv_file.close()
#%%

