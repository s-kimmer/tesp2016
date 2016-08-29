# -*- coding: cp1252 -*-
# Autor: Gregor Lingl
# Datum: 17. 9. 2006
# moorhuhn - Spiel

from turtle import Screen, Turtle # title, mainloop
import turtle
import random, time
import numpy as np
import cv2
import win32api, win32con

try:
    import winsound
    _SOUND = True
except:
    _SOUND = False
    print("NO SOUND!")

SHOTS = 100
VELOCITY = 0.3
WINWIDTH, WINHEIGHT = 1920, 1080-10 #size projector
HIT = "getroffen.wav"
MISSED = "daneben.wav"
GOOD = "gameover.wav"
MODERATE = "applaus.wa v"

## Homography
imgLayer0Path = "./original.png"
cameraDeviceIndex = 0 #choose camera device [0,N-1], 0 for first device, 1 for second device etc.
minimumMatchCount = 8
homographyThreshold = 10
minKeypoints = 10
# For H feasability check
margin = (1800, 1600) #(x,y) x=>width, y=>height

#calculate Keypoints
imgLayer0 = cv2.imread(imgLayer0Path, 1)
#imgLayer0 = cv2.resize(imgLayer0, (WINWIDTH, WINHEIGHT))
if imgLayer0 is None:
    print("errror")
#cv2.imshow("bg", imgLayer0)

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
 
#rotation detection       
RotIndOrig = np.array([[320,320],[0,480],[1,1]])
Rot = 0
mode = 0 #mode
numOfH = 0 #number of 'high' states
counter = 0 #noise toleration 

# Kalman filter
kalman = cv2.KalmanFilter(4,2)
kalman.measurementMatrix = np.array([[1,0,0,0],[0,1,0,0]],np.float32)
kalman.transitionMatrix = np.array([[1,0,1,0],[0,1,0,1],[0,0,1,0],[0,0,0,1]],np.float32)
kalman.processNoiseCov = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]],np.float32) * 0.002


def proj(H, p):
    ph = np.array([p[0], p[1], 1])
    pw = np.dot(H, ph)
    pt = np.array([pw[0], pw[1]]) 
    return pt
    
import ctypes
def click(x,y):
# see http://msdn.microsoft.com/en-us/library/ms646260(VS.85).aspx for details
    ctypes.windll.user32.SetCursorPos(x, y)
    ctypes.windll.user32.mouse_event(2, 0, 0, 0,0) # left down
#    time.sleep(0.1)
    ctypes.windll.user32.mouse_event(4, 0, 0, 0,0) # left up
#    time.sleep(0.1)
#    win32api.SetCursorPos((x,y))
#    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
#    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x+10,y+10,0,0)
    
RotIndOrig = np.array([[320,320],[0,480],[1,1]])
Rot = 0
cc = 0
    
def rotation(H, RotIndOrig, cc):        #Rotation dection
    RotIndProj = np.dot(H, RotIndOrig)

    RotIndx1 = RotIndProj[0,0]/RotIndProj[2,0] 
    RotIndx2 = RotIndProj[0,1]/RotIndProj[2,1]
    RotIndy1 = RotIndProj[1,0]/RotIndProj[2,0]
    RotIndy2 = RotIndProj[1,1]/RotIndProj[2,1]
    tanAngle = np.abs(RotIndx1-RotIndx2)/max(0.1,np.abs(RotIndy1-RotIndy2))
    
    if tanAngle < 0.57:# tan30
        Roti = 0
    elif tanAngle > 1.707: #tan30
        Roti = 1
    else:
        Roti = 2
        
    if cc == 0:
        Rot = Roti
        cc = 3
    else:
        Rot = 0
        cc = cc - 1

    return Rot, cc


class MHManager(Turtle):
    """Special Turtle, perform the task to manage the Moorhuhn-GUI.
    """
    def __init__(self, w, h):
        Turtle.__init__(self, visible=False)
        self.screen = Screen()
        self.screen.setup(w, h)
        self.speed(0)
        self.penup()
        self.goto(-WINWIDTH//2 + 50, -WINHEIGHT//2 + 20)
        self.pencolor("yellow")
    def message(self, txt):
        """Output text to graphics window.
        """
        self.clear()
        self.write(txt, font=("Courier", 18, "bold"))
#        print("message")

class Huhn(Turtle):
    def __init__(self, bilddatei, game):
        Turtle.__init__(self, bilddatei)
        self.onclick(self.hit)
        print("onclickset")
        self.game = game
        self.penup()
        self.speed(0)
        self.start()
    def start(self):
        self.hideturtle()
#        self.onclick(self.hit)
        self.setpos(-WINWIDTH//2-120, random.randint(-WINHEIGHT//3,WINHEIGHT//3))
        self.vx = random.randint(6,11) * VELOCITY
        self.vy = random.randint(-3,3) * VELOCITY
        self.getroffen = False
        self.tot = False
        self.showturtle()
        self.ausdemspiel = False
    def hit(self, x, y):
        print("hit")
        if self.tot or self.game.shots==SHOTS: # game over
            return
        self.getroffen = True
        self.tot = True
        self.game.score += 1


    def step(self):
        if self.ausdemspiel:
            time.sleep(0.01)  # 
            return
        if self.tot:
            self.vy = self.vy - 0.25 * VELOCITY
        x, y = self.position()
        x = x + self.vx
        y = y + self.vy
        self.goto(x,y)
        if x > WINWIDTH//2 + 120 or abs(y) > WINHEIGHT//2 + 120: 
            if self.game.shots != SHOTS:
                self.start()
            else:
                self.ausdemspiel = True

class MoorhuhnGame(object):
    """Combine elements of Moorhuhn game.
    """
    def __init__(self):
        self.mhm = mhm= MHManager(WINWIDTH, WINHEIGHT) # erzeugt
                                     # Grafik-Fenster
        mhm.screen.bgpic("uschi1920x1070.gif")
        mhm.message("Press spacebar to start game!")

        mhm.screen.register_shape("huhn01.gif")
        mhm.screen.register_shape("huhn02.gif")
        mhm.screen.register_shape("huhn03.gif")
        mhm.screen.register_shape("crosshair3.gif")
        #Add more huehner below
        self.huehner = [Huhn("huhn01.gif", self), Huhn("huhn03.gif", self), Huhn("huhn01.gif", self), Huhn("huhn01.gif", self), Huhn("huhn01.gif", self)]
        self.crosshair = crosshair("crosshair3.gif", self)        
        self.gameover = True   # now a new game can start
        mhm.screen.onclick(self.shot, 1)
        mhm.screen.onkey(self.game, "space")
        crosshair.goon = True
        mhm.screen.listen()
        mhm.screen.getcanvas().config(cursor="X_cursor") # get into Tkinter ;-)
        
    def game(self):
        if not self.gameover:
            return   # altes Spiel läuft noch
        self.mhm.message("GAME RUNNING")
        self.crosshair.step()
#        print("game")
        self.shots = 0
        self.score = 0
        self.gameover = False
        self.crosshair.goon = True
        for huhn in self.huehner:
            huhn.start()
        while not self.gameover:
            for huhn in self.huehner:
                huhn.step()

            gameover = self.shots == SHOTS
            for huhn in self.huehner:
                gameover = (gameover and huhn.ausdemspiel)
            self.gameover = gameover
            
        trefferrate = 1.0*self.score/self.shots
        self.mhm.message( ("Score: %1.2f" % trefferrate) +
                                        " - press spacebar!")
        if trefferrate > 0.55:
            self.sound(GOOD)
        else:
            self.sound(MODERATE)
            

        
        crosshair.getpos()
            
    def shot(self, x, y):
        if self.shots == SHOTS:
            return # Es läuft kein Spiel, also kein Schuss
        
        self.shots = self.shots + 1
        klangdatei = MISSED
        for huhn in self.huehner:
            if huhn.getroffen: 
                klangdatei = HIT
                huhn.getroffen = False
                break
        if self.shots == SHOTS:
            self.mhm.message("GAME OVER!")
            crosshair.goon = False
        else:        
            self.mhm.message("hits/shots: %d/%d" %(self.score, self.shots))
        self.sound(klangdatei)
#        print("shot")
        
    def sound(self, soundfile):
        if not _SOUND: return
        winsound.PlaySound(soundfile, winsound.SND_ASYNC) 

     
class crosshair(Turtle):
    def __init__(self, bilddatei, game):
        Turtle.__init__(self, bilddatei)
#        self.game = game
        self.penup()
        self.speed(0)
        self.u = 0.0
        self.v = 0.0
        self.goon = True
#        self.game = game
        self.rot = 0
        self.screenWidth = 1920 #width laptop screen
#        self.screenHeight = 745 
#        print("crosshairint")
        self.cc = 0

    def step(self):

#        print("stepcrosshair")


        if self.rot == 2:
            clickX = np.int(self.u + self.screenWidth+1)
            clickY = np.int(self.v+22)
        
            clickX = max(self.screenWidth + 10, clickX)
            clickX = min(clickX, self.screenWidth + WINWIDTH - 20)
            clickY = max(30, clickY)
            clickY = min(WINHEIGHT, clickY)
            click(clickX, clickY)
#            click(clickX, clickY)
#        else:
#            win32api.SetCursorPos((clickX,clickY))

        if self.goon:
            turtle.ontimer(self.getpos, 40)

        self.setposition((self.u - WINWIDTH/2), -(self.v - WINHEIGHT/2))
        
        
    def getpos(self):
        
        # Web cam
        ret, capturedImg = cap.read()
        if ret == False:
            print("Img capture failed")
#        cv2.imshow("webcam", capturedImg)
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
                
                H, mask = cv2.findHomography(ptsCaptured, ptsOriginal, cv2.RANSAC, homographyThreshold)
                if True: #checkH(H, imgSize, margin) == True:
                    # Rotation detection
                    #Rot = rotation(H, RotIndOrig)
                    #mode,counter,numOfH = switch(Rot, counter, numOfH, mode)
                     pt = proj(H, np.array([320, 240]))
#                     print(pt)
                     kalman.correct(np.array([[np.float32(pt[0])],[np.float32(pt[1])]]))
                     ptFil = kalman.predict()
#                     print("ptFil:")
#                     print(ptFil)
                     self.u = np.int(ptFil[0]*1920/640)#1100 #
                     self.v = np.int(ptFil[1]*1070/480)#600 #
                     
                else:
                    print("H is NOT feasable")
            else:
                print("To few matching points")
        else:
            print("Not enough keypoints")
        
            
        self.rot, self.cc = rotation(H,RotIndOrig,self.cc)
        self.step()
#        print("getpos")

            



def main():  # for xturtleDemo
    MoorhuhnGame()
    return "EVENTLOOP"
        
if __name__ == "__main__":
    msg = main()
    print(msg)
    turtle.mainloop()