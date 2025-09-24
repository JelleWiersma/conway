import pygame
from util import drawText, drawButton

pygame.init()

TITLETEXT = "Welcome to Conway's Game of Life!"
INTTEXT = "This so called 'zero-player game' was created in 1970 by mathematician John Conway. It contains an infinite grid, where each turn cells will turn alive or dead based on the status of their 8 neighbours."
RULESTEXT = "The rules are as follows:\n- If a cell is alive and has 2 or 3 alive neighbours, it stays alive\n- If a cell is dead but has exactly 3 alive neighbours, it turns to life"
CLEARTEXT = "Clear"
CLEAREDTEXT = "Cleared"
POSTEXT = "Reset pos"
PAUSETEXT = "Pause when still"
LOADTEXT = "Load turn 0"
GITHUBTEXT = "GitHub"
PYDROIDTEXT = "Pydroid 3"
MORETEXT = "Why is this interesting?\nApart from drawing something and watching the resulting chaos or patterns emerge, you can draw specific configurations that behave consistently. This makes it possible to make complex systems or beautiful drawings. Make sure you try out some googled figures!"
FOOTERTEXT = "This app was made by me, Jelle. It was made on my phone, using pygame in the Pydroid 3 IDE. I decided to make this during the quiet and/or connectionless moments of 4 months travelling."

menuCache = {}
defaultSettings = {}
buttonsCache = {}

def loadMenus(w, h, startHeight, settings, colors):
	global menuCache, defaultSettings
	defaultSettings = settings.copy()
	for primColor in colors:
		getMenu(w, h, startHeight, settings, primColor)


def getMenu(w, h, startHeight, settings, primColor=(255,255,255)):
	global menuCache
	cacheKey = (settings.items(), str(primColor))
	if cacheKey in menuCache:
		return menuCache[cacheKey]
	#load color and redraw buttons if needed
	
	menu = drawMenu(w, h, startHeight, settings, primColor)
	menuCache[cacheKey] = menu
	return menu

#creates a surface with menu
def drawMenu(totalWidth, totalHeight, startHeight, settings, primColor=(255,255,255)):
	screen = pygame.Surface((totalWidth, totalHeight - startHeight))
	
	bigFont = pygame.font.SysFont("arial", int(totalHeight * 0.03), True)
	smallFont = pygame.font.SysFont("arial", int(totalHeight * 0.02))
	borders = int(totalHeight * 0.002)
	spacing = int(totalHeight * 0.006)

	screenRect = screen.get_rect().inflate(0-borders*2, 0)
	pygame.draw.rect(screen, primColor, screenRect, borders) #outer
	screenRect = screenRect.inflate(0-borders*2, 0-borders*2) #inner
	left, top, right, bottom, centerX, w = screenRect.left, screenRect.top, screenRect.right, screenRect.bottom, screenRect.centerx, screenRect.width
	halfW = (w - borders)//2
	btnWidth = (halfW - 8*spacing)//1.25
	btnHeight = smallFont.get_height()+spacing*2
	
	#draw stuff
	titleSurf = drawText(TITLETEXT, primColor, w-spacing*4, bigFont)
	titleRect = pygame.Rect(left + spacing*2, top+spacing, titleSurf.get_width(), titleSurf.get_height())
	screen.blit(titleSurf, titleRect)

	introSurf = drawText(INTTEXT, primColor, w-spacing*4, smallFont)
	introRect = pygame.Rect(left+spacing*2, titleRect.bottom, introSurf.get_width(), introSurf.get_height())
	screen.blit(introSurf, introRect)

	rulesSurf = drawText(RULESTEXT, primColor, halfW-spacing*4, smallFont)
	rulesRect = pygame.Rect(left+spacing*2, introRect.bottom+spacing*2 + borders, rulesSurf.get_width(), rulesSurf.get_height())
	screen.blit(rulesSurf, rulesRect)

	buttons = [] #text, rect, active
	
	clearRect = pygame.Rect(right - btnWidth - 4*spacing, introRect.bottom+3*spacing+borders, btnWidth, btnHeight)
	buttons.append((CLEAREDTEXT if settings["cleared"] else CLEARTEXT, clearRect, settings["cleared"])) #clear
	
	posRect = pygame.Rect(centerX + 4*spacing, clearRect.bottom+2*spacing, btnWidth, btnHeight)
	buttons.append((POSTEXT, posRect, settings["pos"])) #reset pos

	colorRect = pygame.Rect(left+4*spacing, rulesRect.bottom+4*spacing+borders, btnWidth, btnHeight)
	buttons.append((settings["color"], colorRect, False)) #color
	
	animText = "Animations off" if not settings["anims"] else "Animations on"
	animRect = pygame.Rect(centerX - btnWidth - 4*spacing, colorRect.bottom+2*spacing, btnWidth, btnHeight)
	buttons.append((animText, animRect, settings["anims"])) #animations
	
	modeText = "Pixels" #settings["mode"]
	modeRect = pygame.Rect(left+4*spacing,animRect.bottom+2*spacing,btnWidth, btnHeight)
	buttons.append((modeText, modeRect, False)) #mode

	pauseRect = pygame.Rect(centerX - btnWidth - 4*spacing, modeRect.bottom+2*spacing, btnWidth, btnHeight)
	buttons.append((PAUSETEXT, pauseRect, settings["still"])) #pause when still
	
	loadRect = pygame.Rect(left+4*spacing,pauseRect.bottom+2*spacing,btnWidth, btnHeight)
	buttons.append((LOADTEXT, loadRect, settings["load"])) #load first turn

	moreSurf = drawText(MORETEXT, primColor, halfW-spacing*4, smallFont)
	moreRect = pygame.Rect(centerX + spacing*2, posRect.bottom+spacing*4 + borders, moreSurf.get_width(), moreSurf.get_height())
	screen.blit(moreSurf, moreRect)

	footerSurf = drawText(FOOTERTEXT, primColor, halfW-spacing*4, smallFont)
	footerRect = pygame.Rect(left + spacing*2, loadRect.bottom+spacing*4 + borders, footerSurf.get_width(), footerSurf.get_height())
	screen.blit(footerSurf, footerRect)

	gitRect = pygame.Rect(right - btnWidth - 4*spacing, moreRect.bottom + 4*spacing + borders, btnWidth, btnHeight)
	buttons.append((GITHUBTEXT, gitRect, False))#github
	pyRect = pygame.Rect(centerX + 4*spacing, gitRect.bottom + 2*spacing, btnWidth, btnHeight)
	buttons.append((PYDROIDTEXT, pyRect, False))#pydroid	

	buttonRects = []
	for text, rect, active in buttons:
		border = borders if not active else 0
		btnRect = drawButton(screen, rect, text, smallFont, border, primColor).copy()
		btnRect.top += startHeight
		buttonRects.append(btnRect)

	#lines
	pygame.draw.line(screen, primColor, (left, introRect.bottom+spacing), (right, introRect.bottom+spacing), borders) #below intro
	pygame.draw.line(screen, primColor, (centerX, introRect.bottom+spacing), (centerX, bottom), borders) #vertical
	pygame.draw.line(screen, primColor, (centerX, posRect.bottom+2*spacing), (right, posRect.bottom+2*spacing), borders) #below reset options
	pygame.draw.line(screen, primColor, (left, rulesRect.bottom+2*spacing), (centerX, rulesRect.bottom+2*spacing),borders) #below rules
	pygame.draw.line(screen, primColor, (left, loadRect.bottom + spacing*2), (centerX, loadRect.bottom + spacing*2), borders) #below options
	pygame.draw.line(screen, primColor, (centerX, moreRect.bottom + 2*spacing), (right, moreRect.bottom + 2*spacing), borders) #below more

	return screen, buttonRects

def updateButton(menu, rect, text, font, active, primColor, borders):
	border = borders if not active else 0
	pygame.draw.rect(menu, (0,0,0), rect) #clear
	drawButton(menu, rect, text, font, border, primColor)
	return menu