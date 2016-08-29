# -*- coding: utf-8 -*-
"""
Created on Thu Aug 04 10:18:54 2016

@author: Stefan Kimmer
"""

import numpy as np
import cv2


def proj(H, p):
    ph = np.array([p[0], p[1], 1])
    pw = np.dot(H, ph)
    pt = np.array([pw[0], pw[1]]) 
    return pt




## Homography
#imgLayer0Path = "../src/layerImgs/original.png"
imgLayer0Path = "./Moorhuhn/uschi1920x1070.png"
cameraDeviceIndex = 0 #choose camera device [0,N-1], 0 for first device, 1 for second device etc.
minimumMatchCount = 8
homographyThreshold = 10
minKeypoints = 10


imgMatchesVisu = 0


#calculate Keypoints
imgLayer0 = cv2.imread(imgLayer0Path, 1)
#imgLayer0 = cv2.resize(imgLayer0, (WINWIDTH, WINHEIGHT))
if imgLayer0 is None:
    print("errror")
    
cv2.namedWindow("bg", cv2.WND_PROP_FULLSCREEN) 
cv2.namedWindow("bg") 
cv2.moveWindow("bg", 1920, 0)         
cv2.setWindowProperty("bg", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

cv2.imshow("bg", imgLayer0)

#Init ORB detector and feature matcher
cv2.ocl.setUseOpenCL(False) #bugfix
orb = cv2.ORB_create()

bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True) #create BFMatcher object

keyPoints = orb.detect(imgLayer0, None)
keyPoints, desPoints = orb.compute(imgLayer0, keyPoints)
print("keypoints precalcualted")



#initialize camera
cap = cv2.VideoCapture(cameraDeviceIndex)
    
if cap.isOpened(): # try to get the first frame
    print("Opened camera stream!")
    ret, frame = cap.read()
    if ret == False:
        print("Test capture failed!")
        quit()
else:
    print("Open capture failed!!!")
 
while True:
    
    # Web cam
    ret, capturedImg = cap.read()
    if ret == False:
        print("Img capture failed")
        
    cv2.imshow("webcam", capturedImg)
    # Find features in curent captured img
    kpCapturedImg = orb.detect(capturedImg, None) 
    kpCapturedImg, desCapturedImg = orb.compute(capturedImg, kpCapturedImg)
    
    
    if len(kpCapturedImg) > minKeypoints:
       
        #find matching points
        matches = bf.match(desPoints, desCapturedImg) # Match descriptors
        
        if len(matches) > minimumMatchCount:
            #print(len(matches))
            ptsOriginal = np.float32([ keyPoints[m.queryIdx].pt for m in matches ])
            ptsCaptured = np.float32([ kpCapturedImg[m.trainIdx].pt for m in matches ])
            
            
            if (len(keyPoints) > minKeypoints) & (len(kpCapturedImg) > minKeypoints) \
                & (len(matches) > minimumMatchCount) \
                & (len(kpCapturedImg) >= len(keyPoints)):
                # Note that  matchesMask from 
                # cv2.drawMatches() does not seem to work with the mask
                
                imgMatchesVisu = cv2.drawMatches(capturedImg.copy(), kpCapturedImg, \
                    imgLayer0, keyPoints, matches, imgMatchesVisu)
                        
                
                cv2.imshow("Matches", imgMatchesVisu)            
            
            
            H, mask = cv2.findHomography(ptsCaptured, ptsOriginal, cv2.RANSAC, homographyThreshold)
            if True: #checkH(H, imgSize, margin) == True:
                # Rotation detection
                #Rot = rotation(H, RotIndOrig)
                #mode,counter,numOfH = switch(Rot, counter, numOfH, mode)
                 pt = proj(H, np.array([320, 240]))
                 print(pt)
            else:
                print("H is NOT feasable")
        else:
            print("To few matching points")
    else:
        print("Not enough keypoints")

    key = cv2.waitKey(2)
    if (key == 27):
        cv2.destroyAllWindows()
        break