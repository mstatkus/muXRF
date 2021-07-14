# -*- coding: utf-8 -*-
"""
Created on Wed Jul 14 09:58:39 2021

@author: Михаил
"""

import hyperspy.api as hs
import hyperspy.io_plugins.bruker as bru
import xml.etree.ElementTree as ET
from PIL import Image
import codecs
import re
import numpy as np



class MuXRF_Project():
    def __init__(self):
        pass
    
    def import_from_BCF_file(self,import_file):
        """
        Load hypermap and mosaic from BCF file
        """
        print('Loading data from {}...'.format(import_file))
        self.import_file = import_file
        self.load_hypermap(import_file)
        print('Hypermap loading done')
        self.load_mosaic(import_file)
        print('Mosaic loading done.')
        
    def load_hypermap(self,import_file):
        """
        Load only hypermap from BCF file
        """
        bcf=hs.load(import_file)
        hmap=bcf[4]
        #TODO check SEM-TEM problem
        hmap.metadata.Acquisition_instrument.SEM.beam_energy=80 
        
        self.hmap = hmap
        self.metadata = hmap.metadata
        self.orig_metadata = hmap.original_metadata
        self.elements = mxrf.hmap.metadata.Sample.elements
        
    
    def load_mosaic(self,import_file):
        """
        Loads mosaic data from BCF file, creates full and cropped mosaic.

        """
        root = self._load_bruker_bcf_as_xml(import_file)
        self.mosaic_full = self._extract_mosaic_as_rgb(root)
        self.mosaic_full.calculate_size_mm()
        
        crop_coords_mm = self._get_crop_mosaic_coords_px(root)
        calibration = self.mosaic_full.calibration
        x1_mm = crop_coords_mm[0]
        y1_mm = crop_coords_mm[1]
        w_mm = crop_coords_mm[2]
        h_mm = crop_coords_mm[3]
        
        x2_mm = x1_mm + w_mm
        y2_mm = y1_mm + h_mm
        
        x1_px = round(x1_mm / calibration[0] *1000)
        x2_px = round(x2_mm / calibration[0] *1000)
        
        y1_px = round(y1_mm / calibration[1] *1000)
        y2_px = round(y2_mm / calibration[1] *1000)
        
        crop_coords_px = [x1_px,y1_px,x2_px,y2_px]
        
        cropped_image = self.mosaic_full.rgb_image.crop(crop_coords_px)
        
        new_coords_px = [0,0,x2_px-x1_px,y2_px-y1_px]
        
        self.mosaic_crop = Mosaic_Image(cropped_image,
                                        style='cropped',
                                        coords_px = new_coords_px,
                                        calibration = calibration)
        self.mosaic_crop.calculate_size_mm()
        
        
    
    def _load_bruker_bcf_as_xml(self,import_file):
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
    
    def _extract_encoded_text_from_node(self,root,xpath):
        """
        Extracts encoded text from xml tree node, returns decoded text
        """
        
        desc_node = root.find(xpath)
            
        desc_text = desc_node.find('Text')
        
        t_raw =desc_text.text
        
        txt = codecs.decode(t_raw.encode('ascii'), 'base64')
        
        t1=txt.decode('ascii')
        
        return t1

    def _extract_map_description(self,root):
        """
        Extracts map description data - crop coordinates for mosaic
        """
        xpath = ".//ClassInstance[@Name='OverviewImageDescription']"
        txt = self._extract_encoded_text_from_node(root,xpath)
        return txt
    
    def _get_crop_mosaic_coords_px(self,root):
        desc_txt = mxrf._extract_map_description(root)
        map_rect_regex = re.compile(
            "MapRectMM=([0-9.E]+),([0-9.E]+),([0-9.E]+),([0-9.E]+)")
        coords_str = re.findall(map_rect_regex,desc_txt)[0]
        coords_mm = [float(c) for c in coords_str] #x1, y1. w, h in mm
        return coords_mm
    
    def _extract_mosaic_as_rgb(self, root):
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
        rgb_image = Image.fromarray(rgb_image_np)
        
        msc = Mosaic_Image(rgb_image,
                           style='full',
                           coords_px = [0,0,width,height],
                           calibration = [x_cal, y_cal])
        
        return msc
    
    def replace_elements(self,new_elements_list):
        print ('Replacing original elements with custom list:')
        print (new_elements_list)
        hmap = self.hmap
        hmap.set_elements([]) 
        hmap.set_lines([])
        
        hmap.set_elements(new_elements_list)
        hmap.add_lines()
        
        self.elements = new_elements_list
        print ('...done.')
        

    




class Mosaic_Image():
    def __init__(self,
                 rgb_image,
                 style,
                 coords_px,
                 calibration):
        # image as PIL.Image
        self.rgb_image = rgb_image
        self.style = style
        self.coords_px = coords_px
        self.calibration = calibration
        

    def calculate_size_mm(self):
        coords_mm = []
        for i, c_px in enumerate(self.coords_px):
            cal = self.calibration[i%2] #x for i=0 and 2
            c_mm = c_px * cal / 1000
            coords_mm.append(c_mm)
        self.coords_mm = coords_mm

    def save_as_jpg(self, output_filename):
        self.rgb_image.save(output_filename)
    
#%% test
import_file = 'fang-A.bcf'
mxrf = MuXRF_Project()

mxrf.import_from_BCF_file(import_file)
# mxrf.replace_elements(['Al','Si'])
mxrf.mosaic_crop.save_as_jpg('msc_full.jpg')



