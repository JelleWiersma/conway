import pygame
import math
from collections import defaultdict
from menu import getMenu
from util import drawButton

pygame.init()
screen = pygame.display.set_mode((640, 480))

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
#SAND =pygame.Color.
FONT = pygame.font.SysFont("Arial", 64)
UPDATEEVENT = pygame.USEREVENT + 1
UPDATESP1 = 1000 #ms
UPDATESP2 = 500 #ms
UPDATESP3 = 250 #ms
UPDATESP4 = 100 #ms
UPDATESP6 = 50 #ms
UPDATESP8 = 25 #ms

#variables
running = True
ingame = True
paused = True
draw = True
still = False
turns = 0
ptouch = None
stouch = None
dtouch = None
mtouch = None
settings = None
cellSize = 10
speed = UPDATESP1
color = 0
fingers = {}
oldFingers = {}
offsY = 0
offsX = 0
firstX = 0
firstY = 0
primColor = WHITE
secColor = BLACK

#rects
FIELD = pygame.Surface((WIDTH-10, HEIGHT-300))
FIELDRECT = FIELD.get_rect()
PBUTTONRECT = pygame.Rect(5, HEIGHT-184, (WIDTH-40)/3, 168)
SBUTTONRECT = pygame.Rect(PBUTTONRECT.w+20, HEIGHT-184, PBUTTONRECT.w, 168)
DBUTTONRECT = pygame.Rect(PBUTTONRECT.w*2+35, HEIGHT-184, PBUTTONRECT.w, 168)
MBUTTONRECT = pygame.Rect(WIDTH - 305, 10, 300, 100)
CBUTTONRECT = pygame.Rect(WIDTH -305, 10, 300, 100)

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
MENUTEXT = "menu"
CLOSETEXT = "close"

#buttons
def drawPauseButton():
	if paused:
		drawButton(screen, PBUTTONRECT, PLAYTEXT, FONT, True, True, primColor)
	else:
		drawButton(screen, PBUTTONRECT, PAUSETEXT, FONT, False, True, primColor)
		
def drawSpeedButton():
	global speedText
	drawButton(screen, SBUTTONRECT, speedText, FONT, False, True, primColor)
		
def drawDragButton():
	if draw:
		drawButton(screen, DBUTTONRECT, DRAWTEXT, FONT, True, True, primColor)
	else:
		drawButton(screen, DBUTTONRECT, DRAGTEXT, FONT, False, True, primColor)

#title
def drawTitle(force=False):
	global lastTRender, lastLoc, lastLRender, locPos
	
	if update or force:
		lastTRender = FONT.render(f"Turns: {turns}", 1, primColor)
		
	if lastLoc != (firstX, firstY) or force:
		lastLoc = (firstX, firstY)
		lastLRender = FONT.render(f"{firstX},{firstY}", 1, primColor)
		locPos = (WIDTH-345-lastLRender.get_width(),20)
		
	screen.blit(lastTRender, (40,20))
	screen.blit(lastLRender, locPos)
	
	text = CLOSETEXT
	if ingame:
		text = MENUTEXT
	drawButton(screen, MBUTTONRECT, text, FONT, not ingame, True,   primColor)

def drawField():
	FIELD.fill(secColor)
	pygame.draw.rect(FIELD, primColor, FIELDRECT, 5)
	
	#draw cells
	for (x, y) in currentGrid:
		if x in range(firstX-1, columns+firstX) and y in range(firstY-1, rows+firstY):
			posX=((x-firstX)*cellSize)+offsX
			posY=((y-firstY)*cellSize)+offsY 
			pygame.draw.rect(FIELD, primColor, (posX,posY, cellSize, cellSize))
			
	screen.blit(FIELD, (5,100))

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
	
def reset(clear=True, pos=True, count=True):
	global currentGrid, turns, firstX, firstY, offsX, offsY, turns
	if clear:
		currentGrid = set()
	if pos:
		firstX, firstY, offsX, offsY = 0,0,0,0
	if count:
		turns = 0
			
def handleFDGame(x, y, finger_id):
	global ptouch, stouch, dtouch, cltouch, paused, speed, draw, lastPos1, lastPos2, ingame, settings
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
		fingers[event.finger_id] = x, y
		
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
	if event.finger_id not in (ptouch, stouch, dtouch,mtouch):
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
	if event.finger_id == ptouch:
		ptouch = None
	elif event.finger_id == dtouch:
		dtouch = None
	elif event.finger_id == stouch:
		stouch = None
	elif event.finger_id == mtouch:
		mtouch = None
	else:
		fingers.pop(finger_id, None)
		oldFingers.pop(finger_id, None)

#setup
FIELD.set_clip(FIELDRECT)
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
lastLoc = (0,0)
locPos = (WIDTH-345-lastLRender.get_width(),20)
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
			
		if event.type == pygame.FINGERDOWN:
			x = event.x * WIDTH
			y = event.y * HEIGHT
			if ingame:
				handleFDGame(x,y, event.finger_id)
			else:
				handleFDMenu(x,y, event.finger_id)
				
		if event.type == pygame.FINGERMOTION:
			x = event.x * WIDTH
			y = event.y * HEIGHT
			dx = event.dx*WIDTH
			dy = event.dy*HEIGHT
			
			if ingame:
				handleFMGame(x,y,dx,dy, event.finger_id)
					
		if event.type == pygame.FINGERUP:
			handleFU(event.finger_id)
		
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