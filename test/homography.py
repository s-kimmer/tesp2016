# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 08:43:04 2016

@author: ROMANMUELLER

automatically finding matching points, calculate H, process images to compare, plots
"""
import cv2 
import numpy as np

#load images
img0_path = "./photo.png"
img1_path = "./original.png"
img0 = cv2.imread(img0_path,0)
img1 = cv2.imread(img1_path,0)

# Initiate ORB detector
cv2.ocl.setUseOpenCL(False) #bugfix
orb = cv2.ORB_create()

kp0 = orb.detect(img0,None) #find the keypoints with ORB
kp1 = orb.detect(img1,None)

kp0, des0 = orb.compute(img0, kp0) # compute the descriptors with ORB
kp1, des1 = orb.compute(img1, kp1)

cv2.ocl.setUseOpenCL(True) #endoffix

#find matching points
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True) #create BFMatcher object
matches = bf.match(des0,des1) # Match descriptors

MIN_MATCH_COUNT = 4       
if len(matches)>MIN_MATCH_COUNT:
    src_pts = np.float32([ kp0[m.queryIdx].pt for m in matches ])
    dst_pts = np.float32([ kp1[m.trainIdx].pt for m in matches ])
    
#homography    
H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)

#img-processin
img2 = cv2.warpPerspective(img1, np.linalg.inv(H), (img1.shape[1],img1.shape[0]))
img3 = cv2.warpPerspective(img0, H, (img1.shape[1],img1.shape[0]))

#plots
cv2.imshow("original", img0)
cv2.imshow("photo", img1)
cv2.imshow("transform", img2)
cv2.imshow("transfom2", img3)

#close windows
while True:
    key = cv2.waitKey(20)
    if key == 27:
        cv2.destroyAllWindows()
        break