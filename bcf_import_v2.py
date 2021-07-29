# -*- coding: utf-8 -*-
"""
Created on Sun Jul 25 13:40:28 2021

@author: Михаил
"""
#%% init
import hyperspy.api as hs
import hyperspy.io_plugins.bruker as bru
import xml.etree.ElementTree as ET
from PIL import Image
import codecs
import re
import numpy as np
import struct
import matplotlib.pyplot as plt
from pathlib import Path


import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

class XRF_Project():
    def load_from_bcf_file(self,bcf_file):
        bcf = BCF_data()
        bcf.load_BCF(bcf_file)
        bcf_hs = hs.load(bcf_file) #TODO remove redundant loading
        
        _logger.info('Load BCF file {} OK'.format(bcf_file))
        
        self.hmap = bcf_hs[4] # first four bcf elements are images
        instrument_type = self.hmap.metadata.Acquisition_instrument
        if instrument_type.has_item('SEM'):
            self.hmap.metadata.Acquisition_instrument.SEM.beam_energy = 100
        elif instrument_type.has_item('TEM'):
            self.hmap.metadata.Acquisition_instrument.TEM.beam_energy = 100
        else:
            _logger.warning('Error setting beam energy in metadata')
                
        
        
        self.bcf_file = bcf_file
        self.stem_filename = Path(bcf_file).stem
        self.mosaic_full = bcf.extract_mosaic()
        self.crop_coords_mm = bcf.extract_crop_coords()
        self.stage_origin_mm = bcf.extract_stage_origin()
        self.delta_coords = [x+y for x,y in zip(self.stage_origin_mm[:2],
                                                self.crop_coords_mm)]
    
        self.mosaic_cropped = self.mosaic_full.crop(self.crop_coords_mm)
        _logger.info('Process BCF file OK')
        
    def save_mosaic_files_as_jpeg(self,**kwargs):
        self.mosaic_full.save_as_image('{}_mosaic_full.jpg'.format(
            self.stem_filename), **kwargs)
        self.mosaic_cropped.save_as_image('{}_mosaic_cropped.jpg'.format(
            self.stem_filename), **kwargs)
        
        

class BCF_data():
    
    def load_BCF(self,bcf_file):
        self.bcf_file = bcf_file
        bcf=bru.BCF_reader(bcf_file)
        header_file = bcf.get_file('EDSDatabase/HeaderData')
        header_byte_str = header_file.get_as_BytesIO_string().getvalue()
        hd_bt_str = bru.fix_dec_patterns.sub(b'\\1.\\2', header_byte_str)  
        root = ET.fromstring(hd_bt_str)
        root = root.find("./ClassInstance[@Type='TRTSpectrumDatabase']")
        self.root = root

    def extract_mosaic(self):
        """
        Extracts mosaic RGB and calibration data from xml tree
        Returns MosaicImageArray instance
        """
        node = self.root.find(
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
        
        mosaic = MosaicImageArray(rgb_image_np)
        mosaic.set_calibration((x_cal,y_cal))
        return mosaic

    def extract_crop_coords(self):
        """
        Extracts crop coordinates for small mosaic
        """
        xpath = ".//ClassInstance[@Name='OverviewImageDescription']"
        node = self.root.find(xpath)
        node_txt = node.find('Text')
        txt_raw = node_txt.text
        txt_enc = codecs.decode(txt_raw.encode('ascii'), 'base64')
        txt = txt_enc.decode('ascii')
        
        map_rect_regex = re.compile(
            "MapRectMM=([0-9.E]+),([0-9.E]+),([0-9.E]+),([0-9.E]+)")
        coords_str = re.findall(map_rect_regex,txt)[0]
        x1,y1,w,h = [float(c) for c in coords_str] #x1, y1. w, h in mm
        coords_mm = [x1,y1,x1+w,y1+h] #x1,y1, x2,y2
        return coords_mm
    
    def extract_stage_origin(self):
        """
        Get TRTSEMStageData coordinates:
            origin X,Y,Z in _stage_ coordinate system
        """
        xpath = ".//ClassInstance[@Type='TRTSEMStageData']"
        node = self.root.find(xpath)
        coords = []
        for L in list('XYZ'):
            c = float(node.find('./{}'.format(L)).text)
            coords.append(c)
        return coords


class MosaicImageArray():
    def __init__(self, rgb_array):
        self.rgb_array = rgb_array #np array (Y,X,3) - RGB
        self.size_px = self.rgb_array.shape[0:2] # Y,X
        self.calibrated = False
    
    
    def set_calibration(self,calibration):
        x_cal, y_cal = calibration #tuple of (x_cal,y_cal)
        
        self.calibration = (y_cal, x_cal) 
        size_mm = []
        for x_px, cal in zip(self.size_px,self.calibration):
            x_mm = x_px * cal / 1000
            size_mm.append(x_mm)
        self.size_mm = tuple(size_mm) # Y, X
        self.calibrated = True
        self.extent = (0,size_mm[1], # X - left, right
                       size_mm[0],0) # Y - top, bottom
        
    def imshow(self, ax=None, plot_axes = True,
               **kwargs):
        if ax is None:
            ax = plt.gca()
        if self.calibrated:
            ax.imshow(X = self.rgb_array,
                      extent = self.extent,
                      **kwargs)
        else:
            _logger.info('Plotting uncalibrated image')
            ax.imshow(X = self.rgb_array, **kwargs)
        if plot_axes == False:
            ax.get_xaxis().set_visible(False)
            ax.get_yaxis().set_visible(False)
            
    def crop(self, crop_coords_mm):
        
        # crop_coords_mm = (x1,y1,x2,y2)
        # self.calibration = (y_cal,x_cal) #FIXME
        
        crop_coords_px = []
        for i,x in enumerate(crop_coords_mm):
            cal = self.calibration[i%2]
            x_px = round(x / cal *1000)
            crop_coords_px.append(x_px)
            
        full = self.rgb_array
        slice_y = slice(crop_coords_px[0],crop_coords_px[2])
        slice_x = slice(crop_coords_px[1],crop_coords_px[3])
        cropped = full[slice_x,slice_y,:]
        
        crop_mosaic = MosaicImageArray(cropped)
        crop_mosaic.set_calibration(self.calibration)
        
        return crop_mosaic
    
    def save_as_image(self, filename, **kwargs):
        img = Image.fromarray(self.rgb_array)
        img.save(filename, **kwargs)
        

def load_bcf_dump_xml(bcf_file,xml_file):
    '''
    Loads bcf file, dumps header contents to XML file
    s'''
    # hd_bt_str = _load_bruker_bcf_as_bytestream(bcf_file)
    
    bcf=bru.BCF_reader(import_file)
    header_file = bcf.get_file('EDSDatabase/HeaderData')
    header_byte_str = header_file.get_as_BytesIO_string().getvalue()
    hd_bt_str = bru.fix_dec_patterns.sub(b'\\1.\\2', header_byte_str)  

    xml_file = open(xml_file,'wb')
    xml_file.write(hd_bt_str)
    xml_file.close()

def extract_coords_from_spx_xml(xml_root):
    '''
    Extracts stage coords from SPX file (not BCF!)

    '''
    node = xml_root.find(
        ".//ClassInstance[@Type='TRTUnknownHeader'][@Name='RTREM']")

    txt_raw =node.find('./Data').text
    txt_enc = codecs.decode(txt_raw.encode('cp1252'), 'base64') # or ascii?
    t_list = txt_enc.split(b'\x00') #split by 'empty' bytes
    chunk=[x for x in t_list if len(x)==24][0] #get a chunk of 3*8 bytes - three floats
    coords = struct.unpack('<ddd', chunk) #<ddd - three double floats
    
    return coords

  
    
   
#%% test run
if __name__ == "__main__":
    _logger.info('Test run')
    import_file = 'fang-A.bcf'
    
    project = XRF_Project()
    project.load_from_bcf_file(import_file)
    project.save_mosaic_files_as_jpeg(dpi=(300,300))
    # project.mosaic_full.save_as_image('mosaic_full_test.jpg',dpi=(300,300))
    project
 

    fig, ax = plt.subplots()
    project.mosaic_full.imshow(ax=ax,plot_axes=True)
    ax.set_title('Full mosaic')

    fig, ax = plt.subplots()
    project.mosaic_cropped.imshow(ax=ax)
    ax.set_title('Cropped mosaic')
    
 

    fig, ax = plt.subplots()
    project.mosaic_full.imshow(ax=ax,plot_axes=True)
    ax.set_title('Full mosaic with points')
    x = [99.149, 93.108, 81.709, 74.138] #coords from spx files
    y = [61.348, 59.679, 56.652, 66.077]
    
    for p in zip(x,y):
        pm = tuple(map(lambda i, j: i - j, project.delta_coords, p))
        
        
        ax.scatter(pm[0],pm[1],color='white')
  
