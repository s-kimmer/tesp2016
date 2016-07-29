# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 08:43:04 2016

@author: ROMANMUELLER

automatically finding matching points, calculate H, process images to compare, plots
"""
import cv2 
import numpy as np

option = 0 #choose 0 for static, 1 for webcam

#load images
imgOL_path = "./src/pikachu.jpg"
imgBG_path = "./src/original.png"
imgOL= cv2.imread(imgOL_path,0)
imgBG = cv2.imread(imgBG_path,0)

#ORB detector
cv2.ocl.setUseOpenCL(False) #bugfix
orb = cv2.ORB_create()

kpBG = orb.detect(imgBG,None) #find the keypoints with ORB
kpBG, desBG = orb.compute(imgBG, kpBG) # compute the descriptors with ORB
cv2.ocl.setUseOpenCL(True) #endoffix

if option == 1:
    #cam initialzation
    camera_device_index = 0 #choose camera device [0,N-1], 0 for first device, 1 for second device etc.
    cap = cv2.VideoCapture(camera_device_index)
    
    if cap.isOpened(): # try to get the first frame
        print("Opened camera stream!")
        ret, frame = cap.read()
        if ret == True:
            wframe = cap.get(3)
            hframe = cap.get(4)
            print("Frame width x height: {} x {} ".format( width, height ))
    else:
        ret = False
        
    if ret: 
        cv2.imshow("webcam", frame)
else:
    frame = cv2.imread("./src/photo.png",0)
    wframe = 640
    hframe = 480
    
imgProj = imgBG
#hframe, wframe = frame.shape[:2]
hOL, wOL = imgOL.shape[:2]
UVcenter = np.array([[320], [240], [1]])

while True:
    cv2.imshow("projector", imgProj)    
    
    if option == 1:
        frame = cap.read()
    else:
        frame = frame
        
    #ORB detector
    cv2.ocl.setUseOpenCL(False) #bugfix
    kpframe = orb.detect(frame,None) #find the keypoints with ORB
    kpframe, desframe = orb.compute(frame, kpframe) # compute the descriptors with ORB
    cv2.ocl.setUseOpenCL(True) #endoffix
    
    #find matching points
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True) #create BFMatcher object
    matches = bf.match(desBG,desframe) # Match descriptors
    
    MIN_MATCH_COUNT = 4       
    if len(matches)>MIN_MATCH_COUNT:
        src_pts = np.float32([ kpBG[m.queryIdx].pt for m in matches ])
        dst_pts = np.float32([ kpframe[m.trainIdx].pt for m in matches ])
    else:
        print("Error: less than four matching points")
        break


    #homography    
    H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
    
    UV = np.dot(H, UVcenter) #H or H^-1 ???
    UV[1] = max(0 + 0.5 * wOL, UV[1])
    UV[2] = max(0 + 0.5 * hOL, UV[2])
    UV[1] = min(UV[1], 640 - 0.5 * wOL)
    UV[2] = max(UV[2], 480 - 0.5 * hOL)
    
    
    #imgProj = np.zeros(h1, w1, np.uint8)
    imgProj = imgBG
    imgProj[(UV[2] - 0.5 * hOL):(UV[2] + 0.5 * hOL), (UV[1] - 0.5 * wOL):(UV[1] + 0.5 * wOL)] = imgOL
    imgProj = cv2.cvtColor(imgProj, cv2.COLOR_GRAY2BGR)
#    
    key = cv2.waitKey(2)
    if key == 27:
        cv2.destroyAllWindows()
        break

