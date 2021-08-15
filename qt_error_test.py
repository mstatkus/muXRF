# -*- coding: utf-8 -*-
"""
Created on Sun Aug 15 14:31:01 2021

@author: Михаил
"""

#qt import error test
import os
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = r'C:\WinPython\WPy64-3870\python-3.8.7.amd64\Lib\site-packages\pyqt5_tools\Qt\plugins\platforms'

import matplotlib.pyplot as plt

import sys
print (sys.executable)

plt.plot([1,2,3],[4,5,6])
plt.show()