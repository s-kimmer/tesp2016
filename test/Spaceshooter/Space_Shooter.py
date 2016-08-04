#!/usr/bin/env python
'''Space Shooter Game modified by Michael Langeder'''
'''based on Raspberry Pi shooter game written by Liam Fraser for RaspberryPiTutorials (runtime environment and basic movement/cursor)'''

'''Import pygame for graphics, import sys for exit function, random for random numbers
os is used for environment variables to set the position to centre'''
import pygame, sys, random, os


'''import constants used by pygame such as event type = QUIT'''
from pygame.locals import *

'''initial definitions'''


	
	
'''Declare our classes and functions'''

def initPyGame():
	
	'''Initialize pygame components'''
	pygame.init()
	
	'''
	Centres the pygame window. Note that the environment variable is called 
	SDL_VIDEO_WINDOW_POS because pygame uses SDL (standard direct media layer)
	for it's graphics, and other functions
	'''
	os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'

	'''Set the window title'''
	pygame.display.set_caption("Space Shooter")
	
	'''hide the mouse cursor'''
	pygame.mouse.set_visible(False)
	
	
	
class musicClass():
	def __init__(self):
		musicfile="DST-Darko(Boss).wav"
		pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
		self.music = pygame.mixer.Sound(musicfile)
		self.musiclength = pygame.mixer.Sound.get_length(self.music)
		self.loopcounter = 0
		self.secondcounter = 0
		self.play()
		'''for menu'''
		self.state = 1
		'''set a font, default font size 36'''
		self.font = pygame.font.Font(None, 36)
	
	def play(self):
		pygame.mixer.Sound.play(self.music)
	'''endless loop of music'''
	def update(self):
		self.loopcounter += 1
		if self.loopcounter == framesPerSecond:
			self.loopcounter = 0
			self.secondcounter +=1
			if self.secondcounter >= self.musiclength:
				self.secondcounter = 0
				self.play()
		if self.state == 0:
			self.music.set_volume(0)
		else:
			self.music.set_volume(1)
		'''for menu'''
		self.text = self.font.render("Music:%s" % self.state, True, (255, 255, 255))
		self.textRect = self.text.get_rect()
		self.screenrect = screen.get_rect()
		self.textRect.centerx = 200
		screen.blit(self.text, self.textRect)	
		
class restartClass():
	'''Class to hold the score and update the score to the screen'''
	def __init__(self):
		self.value = ''
		'''set a font, default font size 36'''
		self.font = pygame.font.Font(None, 36)
		
	def update(self):
		'''Font.renderer(text, fontSmoothing, colour(r, g, b))'''
		self.text = self.font.render("Restart %s" % self.value, True, (255, 255, 255))
		self.textRect = self.text.get_rect()
		screenrect = screen.get_rect()
		self.textRect.centerx = screenrect.width/2
		self.textRect.centery = screenrect.height/2 + 50
		screen.blit(self.text, self.textRect)
		
class backgroundClass():
	
	'''Class containing properties and methods for our background'''
	def __init__(self):
		'''Variable to store what our background image is called'''
		backgroundfile = "background.png"
		
		'''Create a pygame surface called image with our background image'''
		self.image = pygame.image.load(backgroundfile).convert()
		
	def draw(self):
		'''Code to draw the background to screen surface'''
		screen.blit(self.image, (0,0))

class crosshairsClass(pygame.sprite.Sprite):
	'''This class inherits functions from pygame.sprite.Sprite
	   containing methods and properties for our crosshairs'''
	   
	def __init__(self):
	   '''Initialize a sprite, passing this instance as a parameter'''
	   pygame.sprite.Sprite.__init__(self)
	   
	   '''Variable to store what our image is called'''
	   crosshairsfile = "crosshairsmouse.png"
	   
	   '''get our image from crosshairs file and rectangle from our image'''
	   self.image = pygame.image.load(crosshairsfile).convert_alpha()
	   self.rect = self.image.get_rect()
	   pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
	   self.lasersound = pygame.mixer.Sound("laser1.wav")	
	   self.lasersound.set_volume(0.5)
	def update(self):
		'''move the crosshairs to where the mouse is'''
		
		'''get the mouse position'''
		position = pygame.mouse.get_pos()
		
		'''assign it to the centre of our rectangle'''
		self.rect.center = position
		
	
	def playsound(self):
		
		pygame.mixer.Sound.play(self.lasersound)
		
class piClass(pygame.sprite.Sprite):

	'''This class inherits functions from pygame.sprite.Sprite
	   containing methods and properties for our pi'''
	   
	def __init__(self, starty, speed):
	   '''Initialize a sprite, passing this instance as a parameter'''
	   pygame.sprite.Sprite.__init__(self)
	   
	   '''Variable to store what our image is called'''
	   pifile = "pi.png"
	   
	   '''get our image from pi file and rectangle from our image'''
	   self.image = pygame.image.load(pifile).convert_alpha()
	   self.rect = self.image.get_rect()
	   
	   '''set right of rectangle to our start x and y co ordinates'''
	   self.rect.right = 0
	   self.rect.centery = starty
	   
	   '''How many pixels to move the pi image across the screen'''
	   self.pispeed = speed
	   '''explotion sound on hit'''
	   pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
	   self.explodesound = pygame.mixer.Sound("boom2.wav")
	   self.explodesound.set_volume(0.3)	
	   
	def update(self):
		'''Add pispeed to current rectangle x value so it moves horizontaly across the screen'''
		self.rect.right += self.pispeed
		
		'''Get the rectangle for the screen'''
		screenrect = screen.get_rect()
		
		'''If the left edge of our pi is >= edge of our screen then...'''
		if self.rect.left >= screenrect.right:
			'''set our rectangle right x value back to zero'''
			self.rect.right = 0
			score.life-=1
			'''get a y value from our function, passing through screenrect
			so the function can work our the correct ranges. Then assign it
			to the y co ordinate top of our pi rectangle'''
			self.rect.top = self.randomYValue(screenrect)
			
	def randomYValue(self, screenrect):
		'''generate a random y value for the pi so that 
		it appears on a different 'row' of the screen'''
		
		'''work out the correct ranges so the whole logo is visible'''
		startrange = self.rect.height
		endrange = screenrect.height - self.rect.height
		
		randomY = random.randrange(startrange, endrange)
		
		'''returns a y co ordinate suitable for use at the top of the rectangle'''
		return randomY
		
	def reset(self):
		screenrect = screen.get_rect()
		self.rect.top = self.randomYValue(screenrect)
		self.rect.right=0
		
	def playsound(self):
		pygame.mixer.Sound.play(self.explodesound)	
		
class scoreClass:
	'''Class to hold the score and update the score to the screen'''
	def __init__(self):
		self.value = 0
		'''set a font, default font size 36'''
		self.font = pygame.font.Font(None, 36)
		self.lifeinit = 3
		self.life = self.lifeinit
		
	def update(self):
		'''Font.renderer(text, fontSmoothing, colour(r, g, b))'''
		text = self.font.render("Score: %s Lifes: %s" % (self.value ,self.life), True, (255, 255, 255))
		textRect = text.get_rect()
		screenrect = screen.get_rect()
		textRect.centerx = screenrect.width - textRect.width
		screen.blit(text, textRect)
		
		
class printClass:
	'''Class to hold the score and update the score to the screen'''
	def __init__(self):
		self.value = ''
		'''set a font, default font size 36'''
		self.font = pygame.font.Font(None, 80)
		
	def update(self):
		'''Font.renderer(text, fontSmoothing, colour(r, g, b))'''
		text = self.font.render("Game Over %s" % self.value, True, (255, 42, 42))
		textRect = text.get_rect()
		screenrect = screen.get_rect()
		textRect.centerx = screenrect.width/2
		textRect.centery = screenrect.height/2
		screen.blit(text, textRect)
		
		

def eventHandling():
	restartwish=0
	'''The code below handles our event'''
	for event in pygame.event.get():
		
		'''Close the program when the X button is pressed'''
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
			
		if event.type == MOUSEBUTTONDOWN:
			'''The mouse has been clicked so see if the sprites rectangles collide
			The pygame.sprite.collide_rect returns either True or False.
			Note that in our case the collision detection isn't very accurate
			because there will be a collision even if the edge of the crosshairs
			is over the edge of the pi. This can be improved by testing collision 
			on specific pixels which I will do next week'''
			
			hit = pi.rect.collidepoint(crosshairs.rect.centerx, crosshairs.rect.centery)
			if hit == True:
				'''The crosshairs was over the pi sprite when mouse was clicked'''
				pi.playsound()
				score.value += 1
				pi.reset()
				
			hit2 = pi2.rect.collidepoint(crosshairs.rect.centerx, crosshairs.rect.centery)
			
			if hit2 == True:
				'''The crosshairs was over the pi sprite when mouse was clicked'''
				pi2.playsound()
				score.value += 1
				pi2.reset()
				
			hit3 = pi3.rect.collidepoint(crosshairs.rect.centerx, crosshairs.rect.centery)
			
			if hit3 == True:
				'''The crosshairs was over the pi sprite when mouse was clicked'''
				pi3.playsound()
				score.value += 1
				pi3.reset()	
			
			hit4 = pi4.rect.collidepoint(crosshairs.rect.centerx, crosshairs.rect.centery)
			
			if hit4 == True:
				'''The crosshairs was over the pi sprite when mouse was clicked'''
				pi4.playsound()
				score.value += 1
				pi4.reset()	
				
			musiconoff = music.textRect.collidepoint(crosshairs.rect.centerx, crosshairs.rect.centery)
			if musiconoff:
				if music.state == 1:
					music.state=0
				else:
					music.state=1	
			
			if score.life == 0:	
				restartwish = restart.textRect.collidepoint(crosshairs.rect.centerx, crosshairs.rect.centery)
				if restartwish:
					score.life=score.lifeinit
					score.value=0	
					pi.rect.right = 0
					pi2.rect.right = 0
					pi3.rect.right = 0
					pi4.rect.right = 0
			if not musiconoff and not restartwish:
				crosshairs.playsound()
				
				
'''Initialize pygame and set some environment variables'''


initPyGame()

'''Initialize a display with width 640 and height 480 with 32 bit colour'''
screen = pygame.display.set_mode((640, 480), 0, 32)

'''Used to manage how fast the screen updates'''
clock = pygame.time.Clock()

'''variable for how many loops a second'''
framesPerSecond = 20

'''Declare a global variable called score to hold the score'''
score = scoreClass()
'''Declare a clobal variable for Game-Over-Screen'''
printer = printClass()

'''Declare class instances to be used in game loop'''
background = backgroundClass()
crosshairs = crosshairsClass()
music = musicClass()
restart = restartClass()

'''Initialize an instance of pi class with start y = 70
and speed of 10'''
pi = piClass(70, 10)
pi2 = piClass(200,7)
pi3 = piClass(400,5)
pi4 = piClass(250,8)

'''create a sprite Group which will contain all our sprites
This sprite group can draw all the sprites it contains to the screen.
It is called RenderPlain because there are actually more advanced Render groups.
But for our game, we just need simple drawing.'''
allsprites = pygame.sprite.RenderPlain((crosshairs, pi, pi2, pi3, pi4))
menusprites = pygame.sprite.RenderPlain((crosshairs))


while True:
	'''We are now in our game loop'''
	
	'''Limit screen updates to 20 frames per second so we dont use 100% cpu time'''
	clock.tick(framesPerSecond)
	
	'''Runs the code in the event handling function'''
	eventHandling()

	'''Draws background to display surface'''
	background.draw()
	music.update()
	score.update()
	
	'''check if lifes are left'''
	if score.life > 0:
		'''run the update code in our sprites and then draw them to the screen'''
		allsprites.update()
		allsprites.draw(screen)
	else:
		'''Game-Over'''
		printer.update() 
		restart.update()
		crosshairs.update()
		menusprites.draw(screen)
		
	'''update the full display surface to the screen'''
	pygame.display.update()
