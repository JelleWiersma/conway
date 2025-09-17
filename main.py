import pygame
import math
from collections import defaultdict
from menu import getMenu
from util import drawButton

pygame.init()
pygame.display.set_caption('Conway\'s Game of Life')

#Calculate size for pc, this is ignored on mobile devices
screen_height = pygame.display.Info().current_h
scale_factor = 0.9
window_height = int(screen_height * scale_factor)
window_width = int(window_height * 51 / 80)

screen = pygame.display.set_mode((window_width, window_height))

#constants
WIDTH, HEIGHT = screen.get_width(), screen.get_height()
WHITE = (255,255,255)
BLACK = (0,0,0)
GREEN = pygame.Color("green2")
RED = pygame.Color("red1")
YELLOW = pygame.Color("yellow1")
BLUE = pygame.Color("dodgerblue")
ORANGE = pygame.Color("orange1")
PURPLE =pygame.Color("purple")
CYAN = pygame.Color("cyan1")
FONT = pygame.font.SysFont("Arial", int(HEIGHT * 0.04), True)
UPDATEEVENT = pygame.USEREVENT + 1
UPDATESP1 = 1000 #ms
UPDATESP2 = 500 #ms
UPDATESP3 = 250 #ms
UPDATESP4 = 100 #ms
UPDATESP6 = 50 #ms
UPDATESP8 = 25 #ms



#sizes
BORDERSIZE = int(HEIGHT * 0.005)
SPACING = int(HEIGHT * 0.01)
CTRLBTNHEIGHT = int(HEIGHT * 0.07)
CTRLBTNWIDTH = (WIDTH - (BORDERSIZE * 2) - (SPACING * 2)) // 3

#rects
TITLERECT = pygame.Rect(0, 0, WIDTH, int(HEIGHT * 0.05))
FIELDRECT = pygame.Rect(BORDERSIZE, TITLERECT.bottom, WIDTH - (BORDERSIZE * 2), HEIGHT-TITLERECT.height - CTRLBTNHEIGHT - (2*SPACING))
MBUTTONRECT = pygame.Rect(TITLERECT.right - BORDERSIZE - int(TITLERECT.width * 0.25), TITLERECT.top + BORDERSIZE, int(TITLERECT.width * 0.25), TITLERECT.height)
PBUTTONRECT = pygame.Rect(FIELDRECT.left, FIELDRECT.bottom + SPACING, CTRLBTNWIDTH, CTRLBTNHEIGHT)
SBUTTONRECT = pygame.Rect(PBUTTONRECT.right+SPACING, FIELDRECT.bottom + SPACING, CTRLBTNWIDTH, CTRLBTNHEIGHT)
DBUTTONRECT = pygame.Rect(SBUTTONRECT.right+SPACING, FIELDRECT.bottom + SPACING, FIELDRECT.right - (SBUTTONRECT.right + SPACING), CTRLBTNHEIGHT)

#texts
PLAYTEXT = "Play"
PAUSETEXT = "Pause"
SP1TEXT = "1X"
SP2TEXT = "2X"
SP3TEXT = "3X"
SP4TEXT = "4X"
SP6TEXT = "6X"
SP8TEXT = "8X"
DRAWTEXT = "Drawing"
DRAGTEXT = "Dragging"
MENUTEXT = "Menu"
CLOSETEXT = "Close"

#buttons
def drawPauseButton():
	global paused
	if paused:
		drawButton(screen, PBUTTONRECT, PLAYTEXT, FONT, 0, True, primColor)
	else:
		drawButton(screen, PBUTTONRECT, PAUSETEXT, FONT, BORDERSIZE, True, primColor)
		
def drawSpeedButton():
	global speedText
	drawButton(screen, SBUTTONRECT, speedText, FONT, BORDERSIZE, primColor)
		
def drawDragButton():
	global draw
	if draw:
		drawButton(screen, DBUTTONRECT, DRAWTEXT, FONT, 0, True, primColor)
	else:
		drawButton(screen, DBUTTONRECT, DRAGTEXT, FONT, BORDERSIZE, True, primColor)

#title
def drawTitle(force=False):
	global lastTRender, lastLoc, lastLRender, locPos

	if update or force:
		lastTRender = FONT.render(f"Turns: {turns}", 1, primColor)
		
	if lastLoc != (firstX, firstY) or force:
		lastLoc = (firstX, firstY)
		lastLRender = FONT.render(f"{firstX},{firstY}", 1, primColor)
		locPos = (TITLERECT.width-345-lastLRender.get_width(), tTextTop)
		
	screen.blit(lastTRender, (TITLERECT.left + 30, tTextTop))
	screen.blit(lastLRender, locPos)
	
	if ingame:
		drawButton(screen, MBUTTONRECT, MENUTEXT, FONT, BORDERSIZE, True, primColor)
	else:
		drawButton(screen, MBUTTONRECT, CLOSETEXT, FONT, 0, True, primColor)
	

#field
def drawField():
	field.fill(secColor)
	pygame.draw.rect(field, primColor, field.get_rect(), BORDERSIZE)
	
	#draw cells
	for (x, y) in currentGrid:
		if x in range(firstX-1, columns+firstX) and y in range(firstY-1, rows+firstY):
			posX=((x-firstX)*cellSize)+offsX
			posY=((y-firstY)*cellSize)+offsY 
			pygame.draw.rect(field, primColor, (posX,posY, cellSize, cellSize))
			
	screen.blit(field, FIELDRECT.topleft)

#Logic
def updateCells():
	global currentGrid, still, lastGrid
	
	newAlive = set()
	neighbourCounts = defaultdict(int)
	#for every alive cell, add one alive cell to the count of all the neighbours
	for cell in currentGrid:
		for dx in [-1, 0, 1]:
			for dy in [-1,0,1]:
				if not (dx == 0 and dy == 0):
					currentNb = (cell[0] + dx, cell[1] + dy)
					neighbourCounts[currentNb] += 1
	
	#Take every relevant cell and check if they live
	for cell, count in neighbourCounts.items():
		if count == 3 or (count == 2 and cell in currentGrid):
			newAlive.add(cell)
	
	still = newAlive == currentGrid or newAlive == lastGrid
	currentGrid = set(newAlive)

#update grid size and offset
def updateGrid(dX, dY, dDist, zoomcenter=None):
	global firstX, firstY, offsX, offsY, cellSize
	
	#add offset to total
	offsX += dX
	offsY += dY

	zoomFactor = 1 + (dDist / 300)
	newCellSize = max(10, int(cellSize * zoomFactor))
	
	if cellSize != newCellSize and zoomcenter:
		cx, cy = zoomcenter
		
		#convert center px to coords
		gx = (cx - offsX) / cellSize + firstX
		gy = (cy - offsY) / cellSize + firstY
		
		#center offset
		offsX = cx - (gx - firstX) * newCellSize
		offsY = cy - (gy - firstY) * newCellSize
		
	cellSize = newCellSize
	
	# shift coords
	shiftX = int(offsX / cellSize)
	shiftY = int(offsY / cellSize)
	firstX -= shiftX
	firstY -= shiftY
		
	# remove whole cells from the offset
	offsX -= shiftX * cellSize
	offsY -= shiftY * cellSize
	
#cycle through colors
def cycleColor():
	global colors, color, colorNames, primColor, menu
	color = color + 1 if color < 7 else 0
	settings["changed"] = True
	settings["color"] = colorNames[color]
	primColor = colors[color]
	menu = getMenu(WIDTH-10, HEIGHT-100, settings, None, primColor)[0]
	drawTitle(True)

def cycleSpeed():
	global speed, speedText
	settings["speed"] = settings["speed"] + 1 if settings["speed"] < 6 else 1
	if settings["speed"] == 1:
		speed = UPDATESP1
		speedText = SP1TEXT
	elif settings["speed"] == 2:
		speed = UPDATESP2
		speedText = SP2TEXT
	elif settings["speed"] == 3:
		speed = UPDATESP3
		speedText = SP3TEXT
	elif settings["speed"] == 4:
		speed = UPDATESP4
		speedText = SP4TEXT
	elif settings["speed"] == 5:
		speed = UPDATESP6
		speedText = SP6TEXT
	else:
		speed = UPDATESP8
		speedText = SP8TEXT
	pygame.time.set_timer(UPDATEEVENT, speed)

def loadFirst():
	global turns, currentGrid, firstGrid
	turns = 0
	currentGrid = firstGrid
	
#reset game
def reset(clear=True, pos=True, count=True):
	global currentGrid, turns, firstX, firstY, offsX, offsY, turns
	if clear:
		currentGrid = set()
	if pos:
		firstX, firstY, offsX, offsY = 0,0,0,0
	if count:
		turns = 0
			
def handleFDGame(x, y, finger_id):
	global ptouch, stouch, dtouch, paused, speed, draw, ingame, settings
	if PBUTTONRECT.collidepoint((x,y)):
		ptouch = finger_id
		paused = not paused
	elif SBUTTONRECT.collidepoint((x,y)):
		stouch = finger_id
		cycleSpeed()
	elif DBUTTONRECT.collidepoint((x,y)):
		dtouch = finger_id
		draw = not draw
	elif MBUTTONRECT.collidepoint((x,y)):
		ingame = False
		settings["cleared"] = False
		settings["pos"] = False
		settings["load"] = False
		paused = True
	else:
		#save fingers for drawing
		fingers[finger_id] = x, y
		
def handleFDMenu(x,y, finger_id):
		global settings, mtouch, ingame
		if MBUTTONRECT.collidepoint((x,y)):
			mtouch = finger_id
			ingame = True
		#clear
		if menuBtnRects[0].collidepoint((x,y)):
			settings["changed"] = True
			settings["cleared"] = True
			reset(True, False, False)
		#reset pos
		elif menuBtnRects[1].collidepoint((x,y)):
			settings["changed"] = True
			settings["pos"] = True
			reset(False, True, False)
		#color
		elif menuBtnRects[2].collidepoint((x,y)):
			settings["changed"] = True
			cycleColor()
		#animations
		elif menuBtnRects[3].collidepoint((x,y)):
			pass
		#mode
		elif menuBtnRects[4].collidepoint((x,y)):
			pass
		#still
		elif menuBtnRects[5].collidepoint((x,y)):
			settings["changed"] = True
			settings["still"] = not settings["still"]
		#load
		elif menuBtnRects[6].collidepoint((x,y)):
			settings["changed"] = True
			settings["load"] = True
			loadFirst()

def handleFMGame(x,y,dx,dy,finger_id):
#only draw pixel if finger didnt start by touching a button
	global fingers, ptouch, stouch, dtouch, draw
	if finger_id not in (ptouch, stouch, dtouch,mtouch):
		oldFingers[finger_id] = fingers[finger_id]
		fingers[finger_id] = (x,y)
		
		if not draw:
			ds = 0
			center = 0
			if len(oldFingers) > 1 and len(fingers) > 1:
				#calculate pinch distance and center
				fList = list(fingers.values())
				fdist = math.dist(fList[0], fList[1])
				centerX = (fList[0][0] + fList[1][0]) / 2
				centerY = (fList[0][1] + fList[1][1]) / 2
				center = (centerX, centerY)
				
				ofList = list(oldFingers.values())
				ofdist = math.dist(ofList[0], ofList[1])
				
				ds = fdist - ofdist
			updateGrid(dx, dy, int(ds), center)
		
def handleFU(finger_id):
	global ptouch, dtouch, stouch, mtouch, fingers
	if finger_id == ptouch:
		ptouch = None
	elif finger_id == dtouch:
		dtouch = None
	elif finger_id == stouch:
		stouch = None
	elif finger_id == mtouch:
		mtouch = None
	else:
		fingers.pop(finger_id, None)
		oldFingers.pop(finger_id, None)

#setup
running = ingame = paused = draw = True
still = mouseActive = False
ptouch = stouch = dtouch = mtouch = None
turns = color = offsX = offsY = firstX = firstY = 0
cellSize = max(10, FIELDRECT.width // 80, FIELDRECT.height // 60)
speed = UPDATESP1
fingers = {}
oldFingers = {}
primColor = WHITE
secColor = BLACK
field = pygame.Surface((FIELDRECT.width, FIELDRECT.height))
field.set_clip(field.get_rect())
clock = pygame.time.Clock()
rows, columns = FIELDRECT.height // cellSize, FIELDRECT.width // cellSize
currentGrid = set()
firstGrid = set()
lastGrid = set()
pygame.time.set_timer(UPDATEEVENT, UPDATESP1)
settings = {"changed": True, "speed": 1, "cleared": False, "pos": False, "color": "White", "anims": False, "mode": 1, "still": False, "load": False}
speedText = SP1TEXT
menu, menuBtnRects = getMenu(WIDTH-10, HEIGHT-100,settings) #clear, pos, color, animations, mode, still, load
lastTRender = FONT.render("Turns: 0", 1, primColor)
lastLRender = FONT.render("0,0", 1, primColor)
tTextTop = TITLERECT.height // 2 - lastTRender.get_height() // 2
lastLoc = (0,0)
locPos = (MBUTTONRECT.left-lastLRender.get_width() - 10,tTextTop)
colors = [WHITE,GREEN,RED,YELLOW,BLUE,ORANGE,PURPLE,CYAN]
colorNames = ["White","Green", "Red", "Yellow", "Blue", "Orange", "Purple","Cyan"]

#translate rect positions for menu placement
for rect in menuBtnRects:
	rect.move_ip(5,100)
	
#game loop
while running:
	update = False
	for event in pygame.event.get():
		
		#Process events
		if event.type == pygame.QUIT:
			running = False
			
		if event.type == pygame.FINGERDOWN or event.type == pygame.MOUSEBUTTONDOWN:

			x = event.x * WIDTH if event.type == pygame.FINGERDOWN else event.pos[0]
			y = event.y * HEIGHT if event.type == pygame.FINGERDOWN else event.pos[1]
			finger = event.finger_id if event.type == pygame.FINGERDOWN else -1
			if ingame:
				handleFDGame(x,y, finger)
			else:
				handleFDMenu(x,y, finger)
				
		if event.type == pygame.FINGERMOTION:
			x = event.x * WIDTH
			y = event.y * HEIGHT
			dx = event.dx*WIDTH
			dy = event.dy*HEIGHT
			
			if ingame:
				handleFMGame(x,y,dx,dy, event.finger_id)
					
		if event.type == pygame.FINGERUP:
			handleFU(event.finger_id)
		if event.type == pygame.MOUSEBUTTONUP:
			handleFU(-1)
		
		if event.type == UPDATEEVENT:
			update = True
	
	#draw stuff
	screen.fill(secColor)
	drawTitle()
		
	if ingame:

		#draw fingers
		if draw:
			for finger, pos in fingers.items():
				if FIELDRECT.collidepoint(pos):
					fx, fy = pos[0], pos[1]
					cx = int((fx - offsX) // cellSize + firstX)
					cy = int((fy - offsY - 70) // cellSize + firstY)
					currentGrid.add((cx,cy))
		
		#update cells
		if (not paused) & update:
			if settings["still"] and still:
				paused = True
				continue
			
			if turns == 0:
				firstGrid = currentGrid
			turns += 1
			updateCells()
	
		drawPauseButton()
		drawSpeedButton()
		drawDragButton()
		drawField()

	else:
		menu = getMenu(WIDTH-10, HEIGHT-100, settings, menu, primColor)[0]
		screen.blit(menu, (5,100))
		settings["changed"] = False
		
	pygame.display.flip()
	clock.tick(144)