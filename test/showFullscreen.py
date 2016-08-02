# -*- coding: utf-8 -*-
"""
Created on Mon Aug 01 07:06:50 2016

@author: Stefan Kimmer
"""
import numpy as np
import cv2

cv2.destroyAllWindows()

imgPath = "../src/layerImgs/original.png"
imgMaskPath = "../src/layerImgs/maskRound.png"


img = cv2.imread(imgPath,0)
imgMask = cv2.imread(imgMaskPath,0)


#M = np.array([[ 111, 112, 113, 114 ], [ 121, 122, 123, 124 ]])
#N = np.array([[ 211, 212, 213, 214 ], [ 221, 222, 223, 224 ]])
#P = np.array([[ 311, 312, 313, 314 ], [ 321, 322, 323, 324 ]])

#img = np.dstack((M,N,P))

img2 = np.zeros_like(img)
img2[200:300,200:300] = 1L

img3 = np.multiply(img, img2)

#cv2.namedWindow("test", cv2.WND_PROP_FULLSCREEN)          
#cv2.setWindowProperty("test", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
cv2.imshow("img", img)
cv2.imshow("mask", img2)
cv2.imshow("multi", img3)


key = cv2.waitKey(0)
cv2.destroyAllWindows()