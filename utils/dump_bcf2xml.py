# -*- coding: utf-8 -*-
"""
Created on Sat Jul  3 09:56:12 2021

@author: Mike
"""
#%% init

import hyperspy.io_plugins.bruker as bru


import_file = 'fang-A.bcf'
#%% load file
bcf=bru.BCF_reader(import_file)

header_file = bcf.get_file('EDSDatabase/HeaderData')

header_byte_str = header_file.get_as_BytesIO_string().getvalue()
hd_bt_str = bru.fix_dec_patterns.sub(b'\\1.\\2', header_byte_str)
#%% dump xml file
h_file = open('h_file.xml','wb')
h_file.write(hd_bt_str)
h_file.close()
