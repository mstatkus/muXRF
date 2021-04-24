# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 22:30:26 2021

@author: Mike
"""

import hyperspy.api as hs
import os
import hyperspy.io_plugins.bruker as brk

bcf_file = 'kvr-btm-180deg-100ms-1det.bcf'

os.chdir(u'D:/Google Drive/археология/soft/test')
#%%
bcf=hs.load('kvr-btm-180deg-100ms-1det.bcf')
#%%
b1 = brk.BCF_reader(bcf_file) #brk.BCF_reader class

h=b1.header #brk.HyperHeader class instance

d2=h.estimate_map_channels() # incorrect map channels

# =============================================================================
# bruker_hv_range = self.spectra_data[index].amplification / 1000
# if self.hv >= bruker_hv_range:
#     return self.spectra_data[index].data.shape[0]
# else:
#     return self.spectra_data[index].energy_to_channel(self.hv)
# =============================================================================

h.spectra_data[0].amplification # line 768, = 40 000

s = h.spectra_data[0] # s - brk.EDXSpectrum class

s.energy_to_channel(0) # = 96, incorrect!

s.energy_to_channel(40) # =4096 , correct!


# =============================================================================
# 
# patched line 625 in bruker.py:
#     self.hv = self.sem_metadata.get('HV', 80.0)  # in kV
#     
#     instead of 
#     
#     self.hv = self.sem_metadata.get('HV', 0.0)  # in kV
#     
# =============================================================================
    