# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 08:43:04 2016

@author: Stefan Kimmer
"""
import cv2 
import numpy as np

## Settings
imgCapturedPath = "../src/imgs3/img000.png"
imgOriginalPath = "../src/layerImgs/original.png"

MIN_MATCH_COUNT = 4


imgCaptured = cv2.imread(imgCapturedPath, cv2.IMREAD_COLOR)
imgOriginal = cv2.imread(imgOriginalPath, cv2.IMREAD_COLOR)

# Initiate ORB detector and BF matcher
cv2.ocl.setUseOpenCL(False) #bugfix
orb = cv2.ORB_create()

bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck = True)

 #find the keypoints and match them
kpCaptured = orb.detect(imgCaptured, None)
kpOriginal = orb.detect(imgOriginal, None)

kpCaptured, desCaptured = orb.compute(imgCaptured, kpCaptured)
kpOriginal, desOriginal = orb.compute(imgOriginal, kpOriginal)

#find matching points
matches = bf.match(desCaptured, desOriginal)

if len(matches) > MIN_MATCH_COUNT:
    ptsCaptured = np.float32([ kpCaptured[m.queryIdx].pt for m in matches ])
    ptsOriginal = np.float32([ kpOriginal[m.trainIdx].pt for m in matches ])


    
# Compute homography    
H, mask = cv2.findHomography(ptsOriginal, ptsCaptured, cv2.RANSAC, 5.0)


# init out image
imgMatchesVisu = 0
# Note that  matchesMask from 
# cv2.drawMatches() does not seem to work with the mask
imgMatchesVisu = cv2.drawMatches(imgCaptured, kpCaptured, \
    imgOriginal, kpOriginal, matches, imgMatchesVisu)


#img-processing
size = (imgCaptured.shape[1], imgCaptured.shape[0])
imgProjected = cv2.warpPerspective(imgOriginal, H, size)

# reproject the original image onto the camptured one
imgReprojected = imgCaptured.copy()
validIndex = imgProjected != 0
imgReprojected[validIndex] = imgProjected[validIndex]

#plots
cv2.imshow("Matches", imgMatchesVisu)

cv2.imshow("Original", imgOriginal)
cv2.imshow("Captured", imgCaptured)
cv2.imshow("Reprojected", imgReprojected)


# Process gui events (e.g. for image display)
key = cv2.waitKey(0) # 0 waits forever
if key == 27: # Escape button pressed
    cv2.destroyAllWindows()