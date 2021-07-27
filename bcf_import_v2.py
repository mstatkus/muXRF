# -*- coding: utf-8 -*-
"""
Created on Sun Jul 25 13:40:28 2021

@author: Михаил
"""

import hyperspy.api as hs
import hyperspy.io_plugins.bruker as bru
import xml.etree.ElementTree as ET
from PIL import Image
import codecs
import re
import numpy as np

def load_bruker_bcf_as_xml(import_file):
    """
    Loads Bruker BCF file as XML,
    useful for mosaic extraction
    
    Returns root xml tree object
    """


    # for mosaic extraction
    bcf=bru.BCF_reader(import_file)
    
    header_file = bcf.get_file('EDSDatabase/HeaderData')
    
    header_byte_str = header_file.get_as_BytesIO_string().getvalue()
    hd_bt_str = bru.fix_dec_patterns.sub(b'\\1.\\2', header_byte_str)
    
    root = ET.fromstring(hd_bt_str)
    root = root.find("./ClassInstance[@Type='TRTSpectrumDatabase']")
    
    return root

def extract_mosaic_from_xml(root):
        
    """
    Extracts mosaic RGB and calibration data from xml tree
    """
    node = root.find(
        ".//ClassInstance[@Type='TRTImageData'][@Name='Default']")
    
    
    width = int(node.find('./Width').text)  # in pixels
    height = int(node.find('./Height').text)  # in pixels
    # image datatype in bytes ('u1','u2','u4')
    dtype = 'u' + node.find('./ItemSize').text
    
    # calibration data: x_cal [um in 1 px]
    x_cal = float(node.find('./XCalibration').text)  
    y_cal = float(node.find('./YCalibration').text)

    plane_count = 3 #assuming RGB image
    
    planes = []
    for i in range(plane_count):
        img = node.find("./Plane" + str(i))
        raw = codecs.decode(
            (img.find('./Data').text).encode('ascii'), 'base64')
        array1 = np.frombuffer(raw, dtype=dtype)
        if any(array1):
            data = array1.reshape((height, width))
            planes.append(data)
            
    rgb_image_np = np.stack(planes,axis=-1)
    pil_image = Image.fromarray(rgb_image_np)
    
    calibration = [x_cal,y_cal]
    size_px = [width, height]
    
    return pil_image, size_px, calibration

def extract_map_description(root):
    """
    Extracts map txt description data (crop coordinates for mosaic)
    """
    xpath = ".//ClassInstance[@Name='OverviewImageDescription']"
    node = root.find(xpath)
    node_txt = node.find('Text')
    txt_raw = node_txt.text
    txt_enc = codecs.decode(txt_raw.encode('ascii'), 'base64')
    txt = txt_enc.decode('ascii')
    return txt

def get_crop_mosaic_coords_mm(txt_map_descr):
    map_rect_regex = re.compile(
        "MapRectMM=([0-9.E]+),([0-9.E]+),([0-9.E]+),([0-9.E]+)")
    coords_str = re.findall(map_rect_regex,txt_map_descr)[0]
    x1,y1,w,h = [float(c) for c in coords_str] #x1, y1. w, h in mm
    coords_mm = [x1,y1,x1+w,y1+h] #x1,y1, x2,y2
    return coords_mm

# =============================================================================
# def mosaic_origin(txt_map_descr):
#     """
#     Get MapStartPosMM coordinates: 
#         origin X,Y,Z in _mosaic_ coordinate system,
#     
# 
#     Parameters
#     ----------
#     txt_map_descr : TYPE
#         DESCRIPTION.
# 
#     Returns
#     -------
#     coords_mm : TYPE
#         DESCRIPTION.
# 
#     """
#     map_rect_regex = re.compile(
#         "MapStartPosMM=([0-9.E]+),([0-9.E]+),([0-9.E]+)")
#     coords_str = re.findall(map_rect_regex,txt_map_descr)[0]
#     coords_mm = [float(c) for c in coords_str] #x,y,z in mm
#     return coords_mm
# =============================================================================

def stage_origin(root):
    """
    Get TRTSEMStageData coordinates:
        origin X,Y,Z in _stage_ coordinate system

    Parameters
    ----------
    root : TYPE
        DESCRIPTION.

    Returns
    -------
    coords : TYPE
        DESCRIPTION.

    """
    xpath = ".//ClassInstance[@Type='TRTSEMStageData']"
    node = root.find(xpath)
    coords = []
    for L in list('XYZ'):
        c = float(node.find('./{}'.format(L)).text)
        coords.append(c)
    return coords
        
    
    

def mm2px(x_mm,cal):
    x_px = round(x_mm / cal *1000)
    return x_px

def px2mm(x_px,cal):
    x_mm = x_px * cal / 1000
    return x_mm

def coords_mm2px(coords,calibrations):
    coords_mm = []
    for i,c in enumerate(coords):
        coords_mm.append(mm2px(coords[i],calibrations[i%2]))
    return coords_mm

def coords_px2mm(coords,calibrations,round_place = 3):
    coords_px = []
    for i,c in enumerate(coords):
        coords_px.append(np.round(px2mm(coords[i],calibrations[i%2]),
                                  round_place))
    return coords_px

  
def extent_from_coords(coords):
    x1,y1,x2,y2 = coords
    extent = (x1,x2,y2,y1)
    return extent

def stage2mosaic_coords(stage_zero,
                        crop_coords,
                        stage_coords):
    mosaic_coords = []
    for i in range(2):
        q = stage_zero[i]+crop_coords[i]-stage_coords[i]
        mosaic_coords.append(q)
    return mosaic_coords

    
    
   
#%% test run
if __name__ == "__main__":
    print ('Test run')
    import_file = 'fang-A.bcf'
    
    root_xml = load_bruker_bcf_as_xml(import_file)
    mosaic_full, size_px, calibration = extract_mosaic_from_xml(root_xml)
    
    stage_origin_mm = stage_origin(root_xml)
    
    txt_map_descr = extract_map_description(root_xml)
    crop_coords_mm = get_crop_mosaic_coords_mm(txt_map_descr)
    # mosaic_origin_mm = mosaic_origin(txt_map_descr)
    
    full_coords_px =[0,0] + size_px
    full_coords_mm = coords_px2mm(full_coords_px, calibration,
                                  round_place = 2)
    
    
    crop_coords_px = coords_mm2px(crop_coords_mm, calibration)
    
    import matplotlib.pyplot as plt


    extent = extent_from_coords(full_coords_mm)
    plt.imshow(mosaic_full,extent = extent)
    x = [99.149, 93.108, 81.709, 74.138] #coords from spx files
    y = [61.348, 59.679, 56.652, 66.077]
    
    for p in zip(x,y):
        pm = stage2mosaic_coords(stage_origin_mm,
                                 crop_coords_mm,
                                 p)
        plt.scatter(pm[0],pm[1],color='white')
  

    
    

