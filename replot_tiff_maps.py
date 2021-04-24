# -*- coding: utf-8 -*-
"""
Created on Fri Feb  5 16:06:15 2021

@author: Mike
"""
#%% import
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import glob
from pathlib import Path
import re

#%% init

height_mm = 24.133
width_mm = 44.958

orig_sample_name = 'PKP-T-01-3-U'

#%% processing

pattern = re.compile('_([A-z][a-z]?)')
filelist = glob.glob("*.tif")

print ('Found {} TIF files, processing...'.format(len(filelist)))

for full_name in filelist:
    import_file = Path(full_name).stem
    print ('Processing {} file...'.format(import_file),end='')
    r= pattern.search(import_file)
    element = r.group(1)
    export_filename = '{}_map_{}'.format(orig_sample_name,element)

    im = Image.open(full_name)
    im_gray = im.convert("L")
    n_im_gray = np.array(im_gray)
    norm_img = (n_im_gray - np.min(n_im_gray))/np.ptp(n_im_gray)
    
    plt.imshow(norm_img, extent = (0,width_mm,0,height_mm))
    plt.colorbar()
    plt.xlabel('x, mm')
    plt.ylabel('y, mm')
    plt.title(element)

    plt.savefig(export_filename,dpi=300)
    plt.close()
    
    print ('done.')

