# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 08:43:04 2016

@author: Stefan Kimmer
"""

import cv2 
import numpy as np

def proj(H, p):
    ph = np.array([p[0], p[1], 1])
    pw = np.dot(H, ph)
    pt = np.array([pw[0] / pw[2], pw[1] / pw[2]])
    return pt

def checkH(H, size, margin):
    # size = (width, height)
    width = size[0] - 1
    height = size[1] - 1
    
    #  ----> x (width)
    # |
    # |  p0m ---------- p1m
    # v
    # y     p0 --- p1
    #       |      |
    #       p3 --- p2
    #
    #    p3m ---------- p2m
    
    p0 = np.array([0, 0])    
    p1 = np.array([width, 0])
    p2 = np.array([width, height])
    p3 = np.array([0, height])

    p0m = p0 - margin   
    p2m = p2 + margin
    
    # Projected points
    p0w = proj(H, p0)
    p1w = proj(H, p1)
    p2w = proj(H, p2)
    p3w = proj(H, p3)
    
    isInside = False  
    isConvex = False  
    
    # Check if point projections are inside margin
    if all(p0w > p0m) & all(p0w < p2m) & \
        all(p1w > p0m) & all(p1w < p2m) & \
        all(p2w > p0m) & all(p2w < p2m) & \
        all(p3w > p0m) & all(p3w < p2m):
        isInside = True        
    
    # Check if points are convex
    cp0 = np.cross(p1w - p0w, p2w - p1w)
    cp1 = np.cross(p2w - p1w, p3w - p2w)
    cp2 = np.cross(p3w - p2w, p0w - p3w)
    cp3 = np.cross(p0w - p3w, p1w - p0w)
    if (cp0 > 0) & (cp1 > 0) & (cp2 > 0) & (cp3 > 0):
        isConvex = True
        print("isConvex")
        
    isFeasable = isInside & isConvex
    
    return isFeasable  
    
    
def boundingBox(p0, p1, p2, p3):
    xl = min(p0[0], p3[0])
    xr = max(p1[0], p2[0])
    yt = min(p0[1], p1[1])
    yb = max(p2[1], p3[1])
    return (xl, xr, yt, yb)

def overlayWarp(H, backgroundImg, overlayImg, mask):
    
#    maskSize = (imgMask.shape[1], imgMask.shape[0])
#    maskCenter = np.array([maskSize[0] / 2, maskSize[1] / 2, 1])    
        
    imgSize = (backgroundImg.shape[1], backgroundImg.shape[0])
    overlayImgMasked = overlayImg * mask
    imgProjected = cv2.warpPerspective(overlayImgMasked, H, imgSize)

    validIndex = imgProjected != 0
    
    overlaidImg = backgroundImg.copy()

    overlaidImg[validIndex] = overlayImg[validIndex]
    
    return overlaidImg


def overlay(H, backgroundImg, overlayImg, overlaySize):
    
    imgSize = (backgroundImg.shape[1], backgroundImg.shape[0])
    # size = (width, height)
    imgWidth = imgSize[0] - 1
    imgHeight = imgSize[1] - 1
    
    w = overlaySize[0]
    h = overlaySize[1]
    
    center = np.array([imgWidth / 2, imgHeight / 2])    

    c = proj(H, center)
    xl = max(0, c[0] - w/2)
    xr = min(imgWidth, c[0] + w/2)
    yt = max(0, c[1] - h/2)
    yb = min(imgHeight, c[1] + h/2)
    
    overlaidImg = backgroundImg.copy()
    
    if (xl < xr) & (yt < yb):
        overlaidImg[yt:yb, xl:xr] = overlayImg[yt:yb, xl:xr]
    
    return overlaidImg

def overlayBB(H, backgroundImg, overlayImg):
    
    size = (backgroundImg.shape[1], backgroundImg.shape[0])
    # size = (width, height)
    width = size[0] - 1
    height = size[1] - 1
    
    p0 = np.array([0, 0])    
    p1 = np.array([width, 0])
    p2 = np.array([width, height])
    p3 = np.array([0, height])
    
    # Projected points
    p0w = proj(H, p0)
    p1w = proj(H, p1)
    p2w = proj(H, p2)
    p3w = proj(H, p3)
    
    (xl, xr, yt, yb) = boundingBox(p0w, p1w, p2w, p3w)
    xl = max(0, xl)
    xr = min(width, xr)
    yt = max(0, yt)
    yb = min(height, yb)
    
    overlaidImg = backgroundImg.copy()
    
    if (xl < xr) & (yt < yb):
        overlaidImg[yt:yb, xl:xr] = overlayImg[yt:yb, xl:xr]
    
    return overlaidImg


def prepareMask(imgMask):
    threshhold = 125
    imgMaskBin = imgMask.copy()
    imgMaskBin[imgMask >= threshhold] = 0
    imgMaskBin[imgMask < threshhold] = 1
    return imgMaskBin

## Settings
imgCapturedPath = "../src/imgs3/img103.png"
imgOriginalPath = "../src/layerImgs/original.png"

imgOverlayPath = "../src/layerImgs/muscles.png"
imgMaskPath = "../src/layerImgs/maskRoundBig.png"


MIN_MATCH_COUNT = 4


imgCaptured = cv2.imread(imgCapturedPath, cv2.IMREAD_COLOR)
imgOriginal = cv2.imread(imgOriginalPath, cv2.IMREAD_COLOR)
imgOverlay = cv2.imread(imgOverlayPath, cv2.IMREAD_COLOR)

### Load an prepare mask
imgMaskOrig = cv2.imread(imgMaskPath, cv2.IMREAD_COLOR)
if imgMaskOrig is None:
    print("The mas image " + imgMaskPath + " could not be read")

imgMask = prepareMask(imgMaskOrig)





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


size = (imgCaptured.shape[1], imgCaptured.shape[0])
if checkH(H, size, (1000,1000)) == True:
    print("H is feasable")

# init out image
imgMatchesVisu = 0
# Note that  matchesMask from 
# cv2.drawMatches() does not seem to work with the mask
imgMatchesVisu = cv2.drawMatches(imgCaptured, kpCaptured, \
    imgOriginal, kpOriginal, matches, imgMatchesVisu)



overlaySize = (800, 60)

#imgReprojected = overlay(H, imgOriginal, imgOverlay, overlaySize)
imgReprojected = overlayBB(H, imgOriginal, imgOverlay)
#imgReprojected = overlayWarp(H, imgOriginal, imgOverlay, imgMask)

#plots
cv2.imshow("Matches", imgMatchesVisu)

cv2.imshow("Original", imgOriginal)
cv2.imshow("Captured", imgCaptured)
cv2.imshow("Reprojected", imgReprojected)


# Process gui events (e.g. for image display)
key = cv2.waitKey(0) # 0 waits forever
if key == 27: # Escape button pressed
    cv2.destroyAllWindows()