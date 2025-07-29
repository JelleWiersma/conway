import pygame
import sys
from util import drawText, drawButton

pygame.init()

BFONT = pygame.font.SysFont("Arial", 64)
SFONT = pygame.font.SysFont("Arial", 48)

TITLETEXT = "Welcome to Conway's Game of Life!"
INTTEXT = "This so called 'zero-player game' was created in 1970 by mathematician John Conway. It contains an infinite grid, where each turn cells will turn alive or dead based on the status of their 8 neighbours."
RULESTEXT = "The rules are as follows:"
R1TEXT = "- If a cell is alive and has 2 or 3 alive neighbours, it stays alive"
R2TEXT = "- If a cell is dead but has exactly 3 alive neighbours, it turns to life"
CLEARTEXT = "Clear"
CLEAREDTEXT = "Cleared"
POSTEXT = "Reset pos"
PAUSETEXT = "Pause when still"
LOADTEXT = "Load turn 0"
GITHUBTEXT = "GitHub"
PYDROIDTEXT = "Pydroid 3"
MORETEXT = "Why is this interesting?"
MOREBODY = "Apart from drawing something and watching the resulting chaos or patterns emerge, you can draw specific configurations that behave consistently. This makes it possible to make complex systems or beautiful drawings. Make sure you try out some googled figures!"
FOOTERTEXT = "This app was made by me, Jelle. It was made on my phone, using pygame in the Pydroid 3 IDE. I decided to make this during the quiet and/or connectionless moments of 4 months travelling."

#creates a surface with menu
def getMenu(w, h, settings, menu=None, primColor = (255,255,255), 
secColor = (0,0,0)):
	screen = menu if menu else pygame.Surface((w, h))
	screenRect = screen.get_rect()
	
	screen, buttonRects = drawButtons(screen, w, h, settings, menu, primColor)
	
	if menu:
		return screen, buttonRects
	
	pygame.draw.rect(screen, primColor, screenRect, 5) #outer
	pygame.draw.line(screen, primColor,(0, 400), (w, 400), 5) #below intro
	pygame.draw.line(screen, primColor, (w/2, 400), (w/2, h), 5) #vertical
	pygame.draw.line(screen, primColor, (w/2, 720), (w, 720), 5) #below reset options
	pygame.draw.line(screen, primColor, (0, 870), (w/2, 870),5) #below rules
	pygame.draw.line(screen, primColor, (0, 1610), (w/2, 1610), 5) #below options
	
	#Texts
	drawText(screen, TITLETEXT, primColor, (40, 40, w-80, 75), BFONT)
	drawText(screen, INTTEXT, primColor, (40, 120,w-80, 240), SFONT)
	drawText(screen, RULESTEXT, primColor, (40, 440, w/2-80, 60), SFONT)
	drawText(screen, R1TEXT, primColor, (40, 500, w/2-80, 170), SFONT)
	drawText(screen, R2TEXT, primColor, (40, 670, w/2-80, 200), SFONT)
	drawText(screen, MORETEXT, primColor, (w/2+40, 760, w/2-80, 60), SFONT)
	drawText(screen, MOREBODY, primColor, (w/2+40, 820, w/2-80, h-800), SFONT)
	drawText(screen, FOOTERTEXT, primColor, (40, 1650, w/2 - 80, h-1650), SFONT)
	
	return screen, buttonRects
	
	
def drawButtons(screen, w, h, settings, initial=False, primColor=(255,255,255)):
	buttonRects = []
	btnWidth = w/2 - 160
	redraw = True if initial or settings["changed"] else False

	#clear
	clearText = CLEAREDTEXT if settings["cleared"] else CLEARTEXT
	clearRect = pygame.Rect(w - btnWidth - 40, 440, btnWidth, 100)
	buttonRects.append(drawButton(screen, clearRect, clearText, SFONT, settings["cleared"], True, primColor))
	
	#reset pos
	posRect = pygame.Rect(w/2+40, 580, btnWidth, 100)
	buttonRects.append(drawButton(screen, posRect, POSTEXT, SFONT, settings["pos"], True, primColor))

	#color
	colorText = settings["color"]
	colorRect = pygame.Rect(40, 910, btnWidth, 100)
	buttonRects.append(drawButton(screen,colorRect, colorText, SFONT, False, redraw, primColor))
	
	#animations
	animText = "Animations off" if not settings["anims"] else "Animations on"
	animRect = pygame.Rect(w/2 - btnWidth - 40, 1050, btnWidth, 100)
	buttonRects.append(drawButton(screen,animRect, animText, SFONT, settings["anims"], redraw, primColor))
	
	#draw mode
	modeText = "Pixels" #settings["mode"]
	modeRect = pygame.Rect(40,1190,btnWidth, 100)
	buttonRects.append(drawButton(screen, modeRect, modeText, SFONT, False, redraw, primColor))
	
	#pause when still
	pauseRect = pygame.Rect(w/2 - btnWidth - 40, 1330, btnWidth, 100)
	buttonRects.append(drawButton(screen, pauseRect, PAUSETEXT, SFONT, settings["still"], redraw, primColor))
	
	#load first turn	
	loadRect = pygame.Rect(40,1470,btnWidth, 100)
	buttonRects.append(drawButton(screen, loadRect, LOADTEXT, SFONT, settings["load"], True, primColor))
	

	#links left
#	gitRect = pygame.Rect(40, 910, btnWidth, 100)
#	buttonRects.append(drawButton(gitRect, GITHUBTEXT, SFONT))#github
#	pyRect = pygame.Rect(w/2-(btnWidth+40), 1050, btnWidth, 100)
#	buttonRects.append(drawButton(pyRect, PYDROIDTEXT, SFONT))#pydroid
	
	#full reset

	return screen, buttonRects