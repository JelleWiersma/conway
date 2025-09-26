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
staticMenuCache = {}
layoutCache = {}

def loadMenus(w, h, startHeight, settings, colors):
	settings = settings.copy()
	for key, value in colors.items():
		
		settings["color"] = key
		getMenu(w, h, startHeight, settings, value)
	return list(menuCache.values())[0][1]


def getMenu(w, h, startHeight, settings, primColor=(255,255,255)):
	global menuCache
	cacheKey = (str(settings.items()), str(primColor))
	if cacheKey in menuCache:
		return menuCache[cacheKey][0]
	
	cachedScreen, layout = getStaticMenu(w, h, startHeight, primColor)
	screen = cachedScreen.copy()
	
	buttons = [] #text, rect, active
	buttons.append((CLEAREDTEXT if settings["cleared"] else CLEARTEXT, layout['clearRect'], settings["cleared"])) #clear
	buttons.append((POSTEXT, layout['posRect'], settings["pos"])) #reset pos
	buttons.append((settings["color"], layout['colorRect'], False)) #color
	buttons.append(("Animations off" if not settings["anims"] else "Animations on", layout['animRect'], settings["anims"])) #animations
	buttons.append(("Pixels", layout['modeRect'], False)) #mode
	buttons.append((PAUSETEXT, layout['pauseRect'], settings["still"])) #pause when still
	buttons.append((LOADTEXT, layout['loadRect'], settings["load"])) #load first turn
	buttons.append((GITHUBTEXT, layout['gitRect'], False))#github
	buttons.append((PYDROIDTEXT, layout['pyRect'], False))#pydroid	

	buttonRects = []
	for text, rect, active in buttons:
		border = layout['borders'] if not active else 0
		btnRect = drawButton(screen, rect, text, layout['smallFont'], border, primColor).copy()
		btnRect.top += startHeight
		buttonRects.append(btnRect)

	menuCache[cacheKey] = (screen, buttonRects)
	return screen

def getStaticMenu(w, h, startHeight, primColor=(255,255,255)):
	global staticMenuCache
	cacheKey = (w, h, startHeight, str(primColor))
	if cacheKey in staticMenuCache:
		return staticMenuCache[cacheKey]
	
	layout = getLayout(w, h, startHeight, primColor)
	screen = pygame.Surface((w, h - startHeight))

	#general
	bigFont = layout['bigFont']
	smallFont = layout['smallFont']
	borders = layout['borders']
	halfW = layout['halfW']
	spacing = layout['spacing']

	#lines
	pygame.draw.rect(screen, primColor, layout["borderRect"], borders) #outer border
	for line in [layout['introLine'], layout['vertLine'], layout['resetLine'], layout['rulesLine'], layout['optionsLine'], layout['moreLine']]:
		pygame.draw.line(screen, primColor, line[0], line[1], borders)
	
	#texts
	titleSurf = drawText(TITLETEXT, primColor, w-4*spacing, bigFont)
	screen.blit(titleSurf, layout['titleRect'])
	introSurf = drawText(INTTEXT, primColor, w-4*spacing, smallFont)
	screen.blit(introSurf, layout['introRect'])
	rulesSurf = drawText(RULESTEXT, primColor, halfW-spacing*4, layout['smallFont'])
	screen.blit(rulesSurf, layout['rulesRect'])
	moreSurf = drawText(MORETEXT, primColor, halfW-spacing*4, smallFont)
	screen.blit(moreSurf, layout['moreRect'])
	footerSurf = drawText(FOOTERTEXT, primColor, halfW-spacing*4, smallFont)
	screen.blit(footerSurf, layout['footerRect'])

	staticMenuCache[cacheKey] = (screen, layout)
	return screen, layout


def getLayout(w, h, startHeight, primColor=(255,255,255)):
	global layoutCache
	cacheKey = (w, h, startHeight, str(primColor))
	if cacheKey in layoutCache:
		return layoutCache[cacheKey]
	
	layout = {}
	layout['bigFont'] = pygame.font.SysFont("arial", int(h * 0.03), True)
	layout['smallFont'] = pygame.font.SysFont("arial", int(h * 0.02))
	layout['borders'] = int(h * 0.002)
	layout['spacing'] = int(h * 0.006)

	layout["borderRect"] = pygame.Rect(0, 0, w, h - startHeight).inflate(0-layout['borders']*2, 0)
	screenRect = layout["borderRect"].copy().inflate(0-layout['borders']*2, 0-layout['borders']*2) #inner
	left, top, right, bottom, centerX, w = screenRect.left, screenRect.top, screenRect.right, screenRect.bottom, screenRect.centerx, screenRect.width
	layout['halfW'] = (w - layout['borders'])//2
	btnWidth = (layout['halfW'] - 8*layout['spacing'])//1.25
	btnHeight = layout['smallFont'].get_height()+layout['spacing']*2
	
	#get rects
	title = drawText(TITLETEXT, primColor, w-layout['spacing']*4, layout['bigFont'], False)
	layout['titleRect'] = pygame.Rect(left + layout['spacing']*2, top+layout['spacing'], title[0], title[1])

	intro = drawText(INTTEXT, primColor, w-layout['spacing']*4, layout['smallFont'], False)
	layout['introRect'] = pygame.Rect(left+layout['spacing']*2, layout['titleRect'].bottom, intro[0], intro[1])

	rules = drawText(RULESTEXT, primColor, layout['halfW']-layout['spacing']*4, layout['smallFont'], False)
	layout['rulesRect'] = pygame.Rect(left+layout['spacing']*2, layout['introRect'].bottom+layout['spacing']*2 + layout['borders'], rules[0], rules[1])

	layout['clearRect'] = pygame.Rect(right - btnWidth - 4*layout['spacing'], layout['introRect'].bottom+3*layout['spacing']+layout['borders'], btnWidth, btnHeight)
	layout['posRect'] = pygame.Rect(centerX + 4*layout['spacing'], layout['clearRect'].bottom+2*layout['spacing'], btnWidth, btnHeight)
	layout['colorRect'] = pygame.Rect(left+4*layout['spacing'], layout['rulesRect'].bottom+4*layout['spacing']+layout['borders'], btnWidth, btnHeight)
	layout['animRect'] = pygame.Rect(centerX - btnWidth - 4*layout['spacing'], layout['colorRect'].bottom+2*layout['spacing'], btnWidth, btnHeight)
	layout['modeRect'] = pygame.Rect(left+4*layout['spacing'],layout['animRect'].bottom+2*layout['spacing'],btnWidth, btnHeight)
	layout['pauseRect'] = pygame.Rect(centerX - btnWidth - 4*layout['spacing'], layout['modeRect'].bottom+2*layout['spacing'], btnWidth, btnHeight)
	layout['loadRect'] = pygame.Rect(left+4*layout['spacing'],layout['pauseRect'].bottom+2*layout['spacing'],btnWidth, btnHeight)

	more = drawText(MORETEXT, primColor, layout['halfW']-layout['spacing']*4, layout['smallFont'],False)
	layout['moreRect'] = pygame.Rect(centerX + layout['spacing']*2, layout['posRect'].bottom+layout['spacing']*4 + layout['borders'], more[0], more[1])

	footer = drawText(FOOTERTEXT, primColor, layout['halfW']-layout['spacing']*4, layout['smallFont'], False)
	layout['footerRect'] = pygame.Rect(left + layout['spacing']*2, layout['loadRect'].bottom+layout['spacing']*4 + layout['borders'], footer[0], footer[1])

	layout['gitRect'] = pygame.Rect(right - btnWidth - 4*layout['spacing'], layout['moreRect'].bottom + 4*layout['spacing'] + layout['borders'], btnWidth, btnHeight)
	layout['pyRect'] = pygame.Rect(centerX + 4*layout['spacing'], layout['gitRect'].bottom + 2*layout['spacing'], btnWidth, btnHeight)
	
	layout['introLine'] = ((left, layout['introRect'].bottom+layout['spacing']), (right, layout['introRect'].bottom+layout['spacing'])) #below intro
	layout['vertLine'] = ((centerX, layout['introRect'].bottom+layout['spacing']), (centerX, bottom)) #vertical
	layout['resetLine'] = ((centerX, layout['posRect'].bottom+2*layout['spacing']), (right, layout['posRect'].bottom+2*layout['spacing'])) #below reset options
	layout['rulesLine'] = ((left, layout['rulesRect'].bottom+2*layout['spacing']), (centerX, layout['rulesRect'].bottom+2*layout['spacing'])) #below rules
	layout['optionsLine'] = ((left, layout['loadRect'].bottom + layout['spacing']*2), (centerX, layout['loadRect'].bottom + layout['spacing']*2))#below options
	layout['moreLine'] = ((centerX, layout['moreRect'].bottom + 2*layout['spacing']), (right, layout['moreRect'].bottom + 2*layout['spacing'])) #below more

	layoutCache[cacheKey] = layout
	return layout