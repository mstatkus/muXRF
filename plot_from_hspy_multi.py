# -*- coding: utf-8 -*-
"""
Created on Wed Apr 21 10:32:44 2021

@author: Михаил

script for plotting several projections on single figure
"""

import hyperspy.api as hs
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib_scalebar.scalebar import ScaleBar
import re
import glob
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

def plot_map(elt,image_size_mm=None,
             caption=None,vmax=None):
    if not image_size_mm:
        image_size_mm = elt.image_size_mm
    
    if vmax:
        plt.imshow(elt.data, 
                   vmax=vmax,
                   extent = (0,image_size_mm[0],0,image_size_mm[1]))
        plt.colorbar(extend='max',label = 'Intensity,cps')
    else:
        plt.imshow(elt.data, 
                   extent = (0,image_size_mm[0],0,image_size_mm[1]))
        plt.colorbar(label ='Intensity,cps')
    
    # plt.xlabel('x, mm')
    # plt.ylabel('y, mm')
    if caption:
        plt.title(caption)
#%%
def load_hspy(filename,element_name,side=None,rot=None):
    
    hmap = hs.load(filename)
    
    stem = Path(filename).stem
    
    if not rot:
        sr = re.search(r'(\d{3})deg',stem)
        rot = int(sr.group(1))
        
    if not side:
        ss = re.search('(top|btm)', stem)
        side = ss.group(1)
    
    
    image_size_mm = hmap.metadata.image_size_mm
    intensity_maps = hmap.get_lines_intensity()
    
    elements = hmap.metadata.Sample.elements
    
    elt_index = elements.index(element_name)
    elt = intensity_maps[elt_index]
    
    elt.filename = filename
    elt.element_name = element_name
    elt.side = side
    elt.rot = rot
    elt.image_size_mm = image_size_mm
    
    return elt




#%%
def subplot_map(map_data,ax,vmin,vmax):
    ims = map_data.image_size_mm
    image = ax.imshow(map_data.data,
              extent = (0,ims[0],0,ims[1]),
              vmin = vmin,
              vmax = vmax)
    # ax.set_title('Side: {}, rotation {} deg'.format(map_data.side,map_data.rot))
    ax.set_title(u'Rotation {}\u00b0 CW'.format(map_data.rot))
    ax.axis('off')
    
    scalebar = ScaleBar(1, "mm", length_fraction=0.25)
    ax.add_artist(scalebar)
    
    return image
    


#%%

def pad_maps(maps):

    x = 0
    y = 0
    
    x_mm = 0
    y_mm = 0
    for m in maps:
        x = max (m.data.shape[0],x)
        y = max (m.data.shape[1],y)
        
        x_mm = max(m.image_size_mm[0],x_mm)
        y_mm = max(m.image_size_mm[1],y_mm)
    
    maps_padded = []
    for m in maps:
        m_padded = np.zeros((x,y))
        
        dx = x - m.data.shape[0]
        dy = y - m.data.shape[1]
        
        x0 = int(np.floor(dx/2))
        y0 = int(np.floor(dy/2))
        
        m_padded[x0:x0+m.data.shape[0], y0:y0+m.data.shape[1]] = m.data
        
        m.data = m_padded
        m.image_size_mm = [x_mm,y_mm]
        maps_padded.append(m)
        
    return maps_padded
    

#%% load fe maps
maps = []
filelist = glob.glob("*.hspy")
for filename in filelist:
    elt = load_hspy(filename, 'Fe')
    maps.append(elt)
#%%
maps_btm = pad_maps(maps[0:4])
maps_top = pad_maps(maps[4:])


#%% subplots - bottom
fig, axes = plt.subplots(2, 2,figsize =(6.5,8))
fig.subplots_adjust(top=0.9)

fig.suptitle(u'Fe K\u03b1 intensity map, bottom side',y=0.98)
k = 0
for i in range(2):
    for j in range(2):
        image = subplot_map(maps_btm[k], axes[j,i], vmin=0, vmax=110)
        k+=1
        

fig.subplots_adjust(right=0.9)
cbar_ax = fig.add_axes([0.98, 0.12, 0.035, 0.8])

plt.colorbar(image, extend='max',label = 'Intensity,cps',cax=cbar_ax)

plt.savefig('fe-btm.png',dpi=300,bbox_inches='tight')

#%% subplots - top
fig, axes = plt.subplots(2, 2,figsize =(6.5,8))
fig.subplots_adjust(top=0.9)

fig.suptitle('Fe K\u03b1 intensity map, top side',y=0.98)
k = 0
for i in range(2):
    for j in range(2):
        image = subplot_map(maps_top[k], axes[j,i], vmin=0, vmax=110)
        k+=1
        

fig.subplots_adjust(right=0.9)
cbar_ax = fig.add_axes([0.98, 0.12, 0.035, 0.8])

plt.colorbar(image, extend='max',label = 'Intensity,cps',cax=cbar_ax)

plt.savefig('fe-top.png',dpi=300,bbox_inches='tight')