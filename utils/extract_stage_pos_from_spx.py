# -*- coding: utf-8 -*-
"""
Created on Sun Jul 25 16:18:07 2021

@author: Михаил
"""

#extract coordinates sdata from spx


import codecs
import struct


#%%
def extract_coords_from_spx_xml(xml_root):
    node = xml_root.find(
        ".//ClassInstance[@Type='TRTUnknownHeader'][@Name='RTREM']")

    txt_raw =node.find('./Data').text
    txt_enc = codecs.decode(txt_raw.encode('cp1252'), 'base64') # or ascii?
    t_list = txt_enc.split(b'\x00') #split by 'empty' bytes
    chunk=[x for x in t_list if len(x)==24][0] #get a chunk of 3*8 bytes - three floats
    coords = struct.unpack('<ddd', chunk) #<ddd - three double floats
    
    return coords

#%%
if __name__ == "__main__":
    import glob
    import xml.etree.ElementTree as ET
    import pandas as pd
    
    cdf = pd.DataFrame(columns = ['file','x_s','y_s','z_s'])
    spx_files = glob.glob("*.spx")
    for file in spx_files:

        tree = ET.parse(file)
        root = tree.getroot()
        
        x,y,z = extract_coords_from_spx_xml(root)
        row = [file,x,y,z]
        cdf.loc[len(cdf)] = row
    cdf.to_excel('coords.xlsx')
