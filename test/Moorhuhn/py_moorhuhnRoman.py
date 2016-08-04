# -*- coding: cp1252 -*-
# Autor: Gregor Lingl
# Datum: 17. 9. 2006
# moorhuhn - Spiel

from turtle import Screen, Turtle # title, mainloop
import turtle
import random, time
import numpy as np
try:
    import winsound
    _SOUND = True
except:
    _SOUND = False
    print("NO SOUND!")

SHOTS = 10
VELOCITY = 0.3
WINWIDTH, WINHEIGHT = 1280, 800-10 #size projector
HIT = "getroffen.wav"
MISSED = "daneben.wav"
GOOD = "gameover.wav"
MODERATE = "applaus.wav"

import win32api, win32con
def click(x,y):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)


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
        self.game = game
        self.penup()
        self.speed(0)
        self.onclick(self.hit)
        self.start()
    def start(self):
        self.hideturtle()
        self.setpos(-WINWIDTH//2-20, random.randint(-WINHEIGHT//3,WINHEIGHT//3))
        self.vx = random.randint(6,11) * VELOCITY
        self.vy = random.randint(-3,3) * VELOCITY
        self.getroffen = False
        self.tot = False
        self.showturtle()
        self.ausdemspiel = False
    def hit(self, x, y):
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
        if x > WINWIDTH//2 + 20 or abs(y) > WINHEIGHT//2 + 10: 
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
        mhm.screen.bgpic("moon1280x790config.gif")
        mhm.message("Press spacebar to start game!")

        mhm.screen.register_shape("huhn01.gif")
        mhm.screen.register_shape("huhn02.gif")
        mhm.screen.register_shape("crosshair3.gif")
        #Add more huehner below
        self.huehner = [Huhn("huhn01.gif", self), Huhn("huhn02.gif", self), Huhn("huhn02.gif", self)]
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
        self.screenWidth = 1280 #width laptop screen
#        self.screenHeight = 745 
#        print("crosshairint")


    def step(self):

#        print("stepcrosshair")

        if self.rot == 1:
            click(np.int(self.u + self.screenWidth+642),np.int(self.v+22)) 

        else:
            win32api.SetCursorPos((0,0))

        if self.goon:
            turtle.ontimer(self.getpos, 200)

        self.setposition((self.u - WINWIDTH/2), -(self.v - WINHEIGHT/2))
        
    def getpos(self):
        
        self.u = np.float((random.random()-0.5) * 400 + 640)
        self.v = np.float((random.random()-0.5) * 400 + 400)
        
        if random.random() < 0.05:
            self.rot = 1
        else:
            self.rot = 0
        self.step()
#        print("getpos")


def main():  # for xturtleDemo
    MoorhuhnGame()
    return "EVENTLOOP"
        
if __name__ == "__main__":
    msg = main()
    print(msg)
    turtle.mainloop()