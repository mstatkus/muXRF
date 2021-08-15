# -*- coding: utf-8 -*-
"""
Created on Fri Jul 30 14:53:21 2021

@author: Михаил
"""
#%% init

import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

import bcf_import_v2 as bcf
_logger.info('bcf_import_v2 import Ok')
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar


import os, sys
from pathlib import Path
#%%
try:
    filename = Path(sys.argv[1])
    filename.resolve(strict=True)
except IndexError:
    print ('No filename given')
    sys.exit()
except FileNotFoundError:
    print ('{} : No such file'.format(filename))
    sys.exit()
#%%
# filename = Path('KPV-74-map-Rh.bcf')
short_filename = filename.stem

p = bcf.XRF_Project()
p.load_from_bcf_file(filename)
p.get_intensity_maps()

Path('./maps').mkdir(parents=True, exist_ok=True)
os.chdir('./maps')
_logger.info('Created /maps dir Ok')
#%% save mosaic as jpeg

p.save_mosaic_files_as_jpeg(dpi=(300,300))
_logger.info('Saved raw mosaic images Ok')
#%% all maps
for elt in p.elements:
    fig, ax = plt.subplots(dpi=300)
    img = p.imshow(elt,ax=ax,plot_axes=False)
    ax.set_title(elt)
    
    scalebar = ScaleBar(1, "mm", length_fraction=0.25,
                          frameon=True,color='black',
                          location='upper right',
                          font_properties = {'size':'x-small'})
    ax.add_artist(scalebar)
    
    plt.colorbar(img)
    
    # plt.tight_layout()
    png_filename = '{}_{}.png'.format(elt,short_filename)
    plt.savefig(png_filename, bbox_inches='tight')
    _logger.info('Saved {} map Ok'.format(elt))
    

#%% Single map
# =============================================================================
# elt = 'Fe'
# vmax = 2000
# cbar_extend = 'max' #or 'neither'
# 
# fig, ax = plt.subplots(dpi=300)
# img = p.imshow(elt,ax=ax,plot_axes=False,vmax = vmax)
# ax.set_title(elt)
# 
# scalebar = ScaleBar(1, "mm", length_fraction=0.25,
#                       frameon=True,color='black',
#                       location='upper right',
#                       font_properties = {'size':'x-small'})
# ax.add_artist(scalebar)
# 
# plt.colorbar(img,extend = cbar_extend)
# 
# =============================================================================

#%% plot mosaic with title and scalebar
fig, ax = plt.subplots(dpi=300)
img = p.mosaic_cropped.imshow(ax=ax,plot_axes=False)
ax.set_title('Photo Mosaic')
scalebar = ScaleBar(1, "mm", length_fraction=0.25,
                          frameon=True,color='black',
                          location='upper right',
                          font_properties = {'size':'x-small'})
ax.add_artist(scalebar)

png_filename = '{}_{}.png'.format('mosaic',short_filename)
plt.savefig(png_filename, bbox_inches='tight')
_logger.info('Saved scalebar mosaic Ok')
_logger.info('Processing done, quitting')