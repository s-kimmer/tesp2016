# -*- coding: utf-8 -*-
"""
Created on Mon Aug 01 08:07:03 2016

@author: ROMANMUELLER
"""

import numpy as np

UV = np.array([[0], [10], [33]])
UVstack = np.array([[320,320,320],[240,240,240]])

while True:
    UV = UV + 1
    UVstack = np.roll(UVstack, 1)
    UVstack[0,0] = UV[0]
    UVstack[1,0] = UV[1]
    UVfilt = np.mean(UVstack, axis=1)
    
 