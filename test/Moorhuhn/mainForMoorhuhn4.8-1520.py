# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 08:43:04 2016

@author: ROMANMUELLER

automatically finding matching points, calculate H, process images to compare, plots
"""


######################
# SETTIGNS

option = 0 #choose 0 for files, 1 for webcam

#images



## For captured camera images:
#imgSourceDir = "./imgs2"
#imgFileNameDesc = "img%03d.png"
#imgStartIndex = 0
#imgEndIndex = 200

determineKeyPointsFromMergedImg = False




#########################
# Functions
  
    
#rotation detection
# if no rotation, Rot = 0; if anticlockwise rotation(90+-30), Rot = 1, if 
#clockwise rotation(90+-30), Rot = 2; else Rot = 3 


    
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
    else:
        print("is NOT Inside")
    
    # Check if points are convex
    cp0 = np.cross(p1w - p0w, p2w - p1w)
    cp1 = np.cross(p2w - p1w, p3w - p2w)
    cp2 = np.cross(p3w - p2w, p0w - p3w)
    cp3 = np.cross(p0w - p3w, p1w - p0w)
    if (cp0 > 0) & (cp1 > 0) & (cp2 > 0) & (cp3 > 0):
        isConvex = True
    else:
        print("is NOT Convex")
        
    isFeasable = isInside & isConvex
    
    return isFeasable  



def rotation(H, RotIndOrig):        #Rotation dection
    RotIndProj = np.dot(H, RotIndOrig)
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
       
    #print "Rot = %d" % Rot
    #print "numOfH = %d"%numOfH        
    
    if numOfH >= 15:        
        if mode >= 3:# 3 modes
            mode = 0
        else:
            mode = mode + 1
        numOfH = 0
        counter = 0            

    #print "mode = %d\n" % mode
    return (mode,counter,numOfH)        


#########################
# Do IT




if option == 1:
    #cam initialzation
    
else:
    # Read images
    frame = 0
  
#Loop initialization
imgProj = imgLayer0
imgIndex = imgStartIndex
doLoop = True
# init out image
imgMatchesVisu = 0




while doLoop:
 
    

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
    if determineKeyPointsFromMergedImg == True:
        kpProjImg = orb.detect(imgProj, None) 
        kpProjImg, desProjImg = orb.compute(imgProj, kpProjImg)    
        keyPoints = kpProjImg
        desPoints = desProjImg
    
    
    

    


    
