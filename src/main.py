# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 08:43:04 2016

@author: ROMANMUELLER

automatically finding matching points, calculate H, process images to compare, plots
"""
import cv2
import numpy as np

######################
# SETTIGNS

option = 0 #choose 0 for files, 1 for webcam

#images
imgLayer0Path = "./src/original.png"
imgLayer1Path = "./src/muscles.png"
imgLayer2Path = "./src/originalred.png"
imgLayer3Path = "./src/originalgreen.png"
imgLayer4Path = "./src/originalred.png"

imgMaskPath = "./src/maskRound.png"

cameraDeviceIndex = 0 #choose camera device [0,N-1], 0 for first device, 1 for second device etc.

# For captured camera images:
imgSourceDir = "./src/imgs5"
imgFileNameDesc = "img%03d.png"
imgStartIndex = 0
imgEndIndex = 200

### Parameters
minimumMatchCount = 8
homographyThreshold = 10



#########################
# Functions
  
    
#rotation detection
# if no rotation, Rot = 0; if anticlockwise rotation(90+-30), Rot = 1, if 
#clockwise rotation(90+-30), Rot = 2; else Rot = 3 

def rotation(H, RotIndOrig):        #Rotation dection
    RotIndProj = np.dot(np.linalg.inv(H), RotIndOrig)
    RotDis = RotIndProj[1,0] - RotIndProj[1,1]
    if np.abs(RotDis) < 240:#240 = 480*sin30
        if RotIndProj[0,0] < RotIndProj[0,1]:
            Rot = 1 #anticlockwise rotation
        else:
            Rot = 2 #clockwise rotation
    elif np.abs(RotDis) > 339:#339 = 480*cos30
        Rot = 0
    else:
        Rot = 3
#    print Rot
    return Rot
    
    
# mode switch
def switch(Rot, counter, numOfH, mode):
    if Rot == 1:
        counter = 3
    elif counter > 0 :
        counter = counter - 1
                
    if counter > 0:
        numOfH = numOfH + 1
    else:
        numOfH = 0
       
    print "Rot = %d" % Rot
    print "numOfH = %d"%numOfH        
    
    if numOfH >= 15:        
        if mode >= 3:# 3 modes
            mode = 0
        else:
            mode = mode + 1
        numOfH = 0
        counter = 0            

    print "mode = %d\n" % mode
    return (mode,counter,numOfH)        

    

#########################
# Do IT


imgLayer0 = cv2.imread(imgLayer0Path, 1)
imgLayer1 = cv2.imread(imgLayer1Path, 1)
imgLayer2 = cv2.imread(imgLayer2Path, 1)
imgLayer3 = cv2.imread(imgLayer3Path, 1)
imgLayer4 = cv2.imread(imgLayer4Path, 1)

imgMaskOrig = cv2.imread(imgMaskPath, 1)
if imgMaskOrig is None:
    print("The mas image " + imgMaskPath + " could not be read")

heightImgLayer2, widthImgLayer2 = imgLayer2.shape[:2]

threshhold = 125
imgMask = imgMaskOrig.copy()
imgMask[imgMaskOrig >= threshhold] = 0
imgMask[imgMaskOrig < threshhold] = 1


maskSize = (imgMask.shape[1],imgMask.shape[0])
maskCenter = np.array([maskSize[0] / 2, maskSize[1] / 2, 1])

#Mask initialization
#wMask = heightImgLayer2 
#hMask = widthImgLayer2
#imgMask = np.zeros_like(imgLayer0)
#yMin = maskCenter[1] - 0.5 * hMask
#yMax = maskCenter[1] + 0.5 * hMask
#xMin = maskCenter[0] - 0.5 * wMask
#xMax = maskCenter[0] + 0.5 * wMask
#imgMask[yMin:yMax, xMin:xMax] = 1 


#Init ORB detector and feature matcher
cv2.ocl.setUseOpenCL(False) #bugfix
orb = cv2.ORB_create()

bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True) #create BFMatcher object

keyPoints = orb.detect(imgLayer0, None)
keyPoints, descriptorKeyPoints = orb.compute(imgLayer0, keyPoints)

if option == 1:
    #cam initialzation
    cap = cv2.VideoCapture(cameraDeviceIndex)
    
    if cap.isOpened(): # try to get the first frame
        print("Opened camera stream!")
        ret, frame = cap.read()
        if ret == True:
            wframe = cap.get(3)
            hframe = cap.get(4)
            print("Frame width x height: {} x {} ".format( wframe, hframe ))
    else:
        ret = False
        
    if ret: 
        cv2.imshow("webcam", frame)
else:
    frame = 0


# Create Window for fullscreen display
#cv2.namedWindow("projector", cv2.WND_PROP_FULLSCREEN)          
#cv2.setWindowProperty("projector", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
#cv2.moveWindow("projector", 1920, 0)

cv2.imshow("projector", imgLayer0)    


#Loop initialization
imgProj = imgLayer0
imgIndex = imgStartIndex
doLoop = True


RotIndOrig = np.array([[320,320],[0,480],[1,1]])
Rot = 0
mode = 0 #mode
numOfH = 0 #number of 'high' states
counter = 0 #noise toleration 


while doLoop:
 
    
    if option == 1:
        # Web cam
        ret, capturedImg = cap.read()
        if ret == False:
            print("Img capture failed")
            break
    else:
        if imgIndex > imgEndIndex:
            break
        # File Source
        imgFileName = imgFileNameDesc % (imgIndex)
        imgFilePath = imgSourceDir + "/" + imgFileName
        print("Loading: " + imgFilePath)
        capturedImg = cv2.imread(imgFilePath, 1)
        imgIndex = imgIndex + 1
        
    
    # Find features in projector img
    kpProjImg = orb.detect(imgProj, None) 
    kpProjImg, desProjImg = orb.compute(imgProj, kpProjImg)    
    keyPoints = kpProjImg
    descriptorKeyPoints = desProjImg
    
    # Find features in curent captured img
    kpCapturedImg = orb.detect(capturedImg, None) 
    kpCapturedImg, desCapturedImg = orb.compute(capturedImg, kpCapturedImg)
    
    #find matching points
    matches = bf.match(descriptorKeyPoints, desCapturedImg) # Match descriptors
        
    if len(matches) > minimumMatchCount:
        print(len(matches))
        src_pts = np.float32([ keyPoints[m.queryIdx].pt for m in matches ])
        dst_pts = np.float32([ kpCapturedImg[m.trainIdx].pt for m in matches ])
    else:
        print("Error: less than four matching points")
        continue

    H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, homographyThreshold)
   
    # Rotation detection
    Rot = rotation(H, RotIndOrig)
    mode,counter,numOfH = switch(Rot,counter,numOfH,mode)
    
    #flashlight Overlay
    imgMaskProj = cv2.warpPerspective(imgMask, np.linalg.inv(H), maskSize)
    
    
    if mode == 0:    
        currentLayerImg = imgLayer1        
    elif mode == 1:
        currentLayerImg = imgLayer2
    elif mode == 2:
        currentLayerImg = imgLayer3
    else:        
        currentLayerImg = imgLayer4

    imgProj = np.multiply(currentLayerImg, imgMaskProj) + np.multiply(imgLayer0, (1-imgMaskProj))


    # Display stuff
    cv2.imshow("projector", imgProj)
    cv2.imshow("webcam", capturedImg)

    #cancelation criteria
    # note: waitkey does the event procesing of e.g. the imshow function
    key = cv2.waitKey(2)
    if (key == 27) | (imgIndex == imgEndIndex):
        cv2.destroyAllWindows()
        
        if option == 1:
            print("Releasing image capture device")
            cap.release
            cap.release
            
        doLoop = False
        break
    
  
    
    
    
    
#    UV = np.dot(np.linalg.inv(H), maskCenter)
    
#    #Pikachu Overlay
#    UVconv = np.array([[0], [0]])
#    UVconv[0] = max(1 + 0.5 * widthImgLayer2, UV[0])
#    UVconv[1] = max(1 + 0.5 * heightImgLayer2, UV[1])
#    UVconv[0] = min(UV[0], 640 - 0.5 * widthImgLayer2 -1)
#    UVconv[1] = min(UV[1], 480 - 0.5 * heightImgLayer2 -1)
#    
# 
#    #imgProj = np.zeros(h1, w1, np.uint8)
#    imgProj = imgLayer0.copy()
#    imgProj[(np.int(UVconv[1] - 0.5 * heightImgLayer2)):np.int((UVconv[1] + 0.5 * heightImgLayer2)), np.int((UVconv[0] - 0.5 * widthImgLayer2)):np.int((UVconv[0] + 0.5 * widthImgLayer2))] = imgLayer2
   