# -*- coding: utf-8 -*-
"""
Created on Sat Jul  3 09:56:12 2021

@author: Mike
"""
#%% init
# import hyperspy.api as hs
import hyperspy.io_plugins.bruker as bru
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np
import codecs
from matplotlib_scalebar.scalebar import ScaleBar
import re
from PIL import Image

import_file = 'd:/Google Drive/археология/PLT-1/C/PLT-1-C.bcf'
#%% funcs

def load_bruker_bcf_as_xml(import_file):
    bcf=bru.BCF_reader(import_file)
    
    header_file = bcf.get_file('EDSDatabase/HeaderData')
    
    header_byte_str = header_file.get_as_BytesIO_string().getvalue()
    hd_bt_str = bru.fix_dec_patterns.sub(b'\\1.\\2', header_byte_str)
    
    root = ET.fromstring(hd_bt_str)
    root = root.find("./ClassInstance[@Type='TRTSpectrumDatabase']")
    
    return root

def extract_mosaic_as_rgb(root):
    node = root.find(
        ".//ClassInstance[@Type='TRTImageData'][@Name='Default']")
    
    
    width = int(node.find('./Width').text)  # in pixels
    height = int(node.find('./Height').text)  # in pixels
    # in bytes ('u1','u2','u4')
    dtype = 'u' + node.find('./ItemSize').text
    
    x_cal = float(node.find('./XCalibration').text)  
    y_cal = float(node.find('./YCalibration').text)
    
    metadata = {'w_px'  :   width,
                'h_px'  :   height,
                'x_cal' :   x_cal,
                'y_cal' :   y_cal}
    
    plane_count = 3
    
    planes = []
    for i in range(plane_count):
        img = node.find("./Plane" + str(i))
        raw = codecs.decode(
            (img.find('./Data').text).encode('ascii'), 'base64')
        array1 = np.frombuffer(raw, dtype=dtype)
        if any(array1):
            data = array1.reshape((height, width))
            planes.append(data)
            
    rgb_image = np.stack(planes,axis=-1)
    return rgb_image, metadata

def extract_encoded_text_from_node(root,xpath):
    desc_node = root.find(xpath)         
        
    desc_text = desc_node.find('Text')
    
    t_raw =desc_text.text
    
    txt = codecs.decode(t_raw.encode('ascii'), 'base64')
    
    t1=txt.decode('ascii')
    
    return t1

def extract_map_description(root):
    xpath = ".//ClassInstance[@Name='OverviewImageDescription']"
    txt = extract_encoded_text_from_node(root,xpath)
    return txt

def get_coords_px(coords_mm,metadata):
    x_cal = metadata['x_cal'] # um in px
    y_cal = metadata['y_cal'] # um in px
    
    x1_mm = coords_mm[0]
    y1_mm = coords_mm[1]
    w_mm = coords_mm[2]
    h_mm = coords_mm[3]
    
    x2_mm = x1_mm + w_mm
    y2_mm = y1_mm + h_mm
    
    x1_px = round(x1_mm / x_cal *1000)
    x2_px = round(x2_mm / x_cal *1000)
    
    y1_px = round(y1_mm / y_cal *1000)
    y2_px = round(y2_mm / y_cal *1000)
    
    return (x1_px,y1_px,x2_px,y2_px)


    
#%% load file
root = load_bruker_bcf_as_xml(import_file)

# extract image and image metadata
rgb_image, metadata = extract_mosaic_as_rgb(root)

#%% extract description
desc_txt = extract_map_description(root)

map_rect_regex = re.compile(
    "MapRectMM=([0-9.E]+),([0-9.E]+),([0-9.E]+),([0-9.E]+)")

coords_str = re.findall(map_rect_regex,desc_txt)[0]
coords_mm = [float(c) for c in coords_str] #x1, y1. w, h in mm

crop_coords = get_coords_px(coords_mm, metadata) # coords in px


#%% crop and save

msc_full = Image.fromarray(rgb_image)
msc_full.save('mosaic_full.jpg')

msc_crop = msc_full.crop(crop_coords)
msc_crop.save('mosaic_crop.jpg')

#%% plot full mosaic with scalebar


w_mm = metadata['w_px'] * metadata['x_cal'] / 1000 
h_mm = metadata['h_px'] * metadata['y_cal'] / 1000 


extent = (0,w_mm,0,h_mm)
fig, ax = plt.subplots()

ax.imshow(rgb_image,extent = extent)

# scalebar 
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)
scalebar_black = ScaleBar(1, "mm", length_fraction=0.25,
                          frameon=False,color='white',
                          location='lower right',
                          font_properties = {'size':'x-small'})
ax.add_artist(scalebar_black)


plt.savefig('mosaic_full_scalebar.png',dpi=300)
plt.close()

#%% plot cropped mosaic with scalebar

w_mm = coords_mm[2]
h_mm = coords_mm[3]

extent = (0,w_mm,0,h_mm)
fig, ax = plt.subplots()

ax.imshow(msc_crop,extent = extent)

# scalebar 
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)
scalebar_black = ScaleBar(1, "mm", length_fraction=0.25,
                          frameon=False,color='white',
                          location='lower right',
                          font_properties = {'size':'x-small'})
ax.add_artist(scalebar_black)


plt.savefig('mosaic_cropped_scalebar.png',dpi=300)
plt.close()