import pygame
import math
import webbrowser
from collections import defaultdict
from menu import getMenu, loadMenus
from util import drawButton, renderText

pygame.init()
pygame.display.set_caption('Conway\'s Game of Life')

#Calculate size for pc, this is ignored on mobile
screen_height = pygame.display.Info().current_h
scale_factor = 0.8
window_height = int(screen_height * scale_factor)
window_width = int(window_height * 51 / 80)

screen = pygame.display.set_mode((window_width, window_height))

#constants
WIDTH, HEIGHT = screen.get_width(), screen.get_height()
TOUCHSCREEN = not (WIDTH == window_width and HEIGHT == window_height) #if the window is not the set size, it is probably on mobile
COLORS = {
	"White": (255,255,255),
	"Red": pygame.Color("red1"),
	"Yellow": pygame.Color("yellow1"),
	"Blue": pygame.Color("dodgerblue"),
	"Green": pygame.Color("green2"),
	"Orange": pygame.Color("orange1"),
	"Purple": pygame.Color("purple"),
	"Cyan": pygame.Color("cyan1")
}
SECCOLOR = (0,0,0)
FONT = pygame.font.SysFont("Arial", int(HEIGHT * 0.03), True)
SMALLFONT = pygame.font.SysFont("Arial", int(HEIGHT * 0.02), True)
UPDATEEVENT = pygame.USEREVENT + 1
UPDATESP1 = 1000 #ms
UPDATESP2 = 500 #ms
UPDATESP3 = 250 #ms
UPDATESP4 = 100 #ms
UPDATESP6 = 50 #ms
UPDATESP8 = 25 #ms

#sizes
BORDERSIZE = int(HEIGHT * 0.002)
SPACING = int(HEIGHT * 0.006)
CTRLBTNHEIGHT = int(HEIGHT * 0.07)
CTRLBTNWIDTH = (WIDTH - (BORDERSIZE * 2) - (SPACING * 2)) // 3
MINCELLSIZE = WIDTH // 300 if WIDTH // 300 < HEIGHT // 240 else HEIGHT // 240
MAXCELLSIZE = WIDTH // 3 if WIDTH // 3 < HEIGHT // 2 else HEIGHT // 2

#rects
TITLERECT = pygame.Rect(0, 0, WIDTH, int(HEIGHT * 0.05))
FIELDRECT = pygame.Rect(BORDERSIZE, TITLERECT.bottom, WIDTH - (BORDERSIZE * 2), HEIGHT-TITLERECT.height - CTRLBTNHEIGHT - SPACING - BORDERSIZE)
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
LOADINGTEXT = "Loading..."
LIFETEXT = "Welcome to Conway's Game of Life!"
HINTTEXT = "Start by drawing some cells"

TTEXTTOP = TITLERECT.height // 2 - FONT.get_height() // 2
TITLEPOS = (2*SPACING, TTEXTTOP)
LIFETEXTPOS = (FIELDRECT.width//2 - FONT.size(LIFETEXT)[0]//2, FIELDRECT.height//2.5 - FONT.get_height()//2)
HINTTEXTPOS = (FIELDRECT.width//2 - SMALLFONT.size(HINTTEXT)[0]//2, LIFETEXTPOS[1] + FONT.get_height() + SPACING)



#buttons
def drawPauseButton():
	global paused
	if paused:
		drawButton(screen, PBUTTONRECT, PLAYTEXT, FONT, 0, primColor)
	else:
		drawButton(screen, PBUTTONRECT, PAUSETEXT, FONT, BORDERSIZE, primColor)
		
def drawSpeedButton():
	global speedText
	drawButton(screen, SBUTTONRECT, speedText, FONT, BORDERSIZE, primColor)
		
def drawDragButton():
	global draw
	if draw:
		drawButton(screen, DBUTTONRECT, DRAWTEXT, FONT, 0, primColor)
	else:
		drawButton(screen, DBUTTONRECT, DRAGTEXT, FONT, BORDERSIZE, primColor)

#title
def drawTitle():
	tRender = renderText(f"Turns: {turns}", FONT, primColor)
	lRender = renderText(f"{firstX},{firstY}", FONT, primColor)
	locPos = (MBUTTONRECT.left-2*SPACING-lRender.get_width(), TTEXTTOP)
		
	screen.blit(tRender, TITLEPOS)
	screen.blit(lRender, locPos)
	
	if ingame:
		drawButton(screen, MBUTTONRECT, MENUTEXT, FONT, BORDERSIZE, primColor)
	else:
		drawButton(screen, MBUTTONRECT, CLOSETEXT, FONT, 0, primColor)
	

#field
def drawField():
	field.fill(SECCOLOR)
	pygame.draw.rect(field, primColor, field.get_rect(), BORDERSIZE)

	if currentGrid == set():
		lRender = renderText(LIFETEXT, FONT, primColor)
		hRender = renderText(HINTTEXT, SMALLFONT, primColor)
		field.blit(lRender, LIFETEXTPOS)
		field.blit(hRender, HINTTEXTPOS)
	
	#draw cells
	for (x, y) in currentGrid:
		if firstX - 2 <= x < firstX + columns + 2 and firstY - 2 <= y < firstY + rows + 2:
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
	lastGrid = currentGrid
	currentGrid = set(newAlive)

#update grid size and offset
def updateGrid(dX, dY, dDist, zoomcenter=None):
	global firstX, firstY, offsX, offsY, cellSize, rows, columns, use_touch
	
	#add offset to total
	offsX += dX
	offsY += dY

	zoomFactor = 1 + (dDist / 300)
	proposedSize = int(cellSize * zoomFactor)
	if dDist != 0 and cellSize == proposedSize:
		proposedSize += 1 if dDist > 0 else -1
	newCellSize = max(MINCELLSIZE, min(MAXCELLSIZE, proposedSize))

	
	
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

	rows = FIELDRECT.height // cellSize
	columns = FIELDRECT.width // cellSize
	
#cycle through colors
def cycleColor():
	global color, primColor
	color = color + 1 if color < 7 else 0
	settings["color"] = list(COLORS)[color]
	primColor = COLORS[settings["color"]]

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
			settings["cleared"] = False
			settings["resetPos"] = False
			settings["load"] = False
		#clear
		elif menuBtnRects[0].collidepoint((x,y)):
			settings["cleared"] = True
			reset(True, False, False)
		#reset pos
		elif menuBtnRects[1].collidepoint((x,y)):
			settings["pos"] = True
			reset(False, True, False)
		#color
		elif menuBtnRects[2].collidepoint((x,y)):
			cycleColor()
		#animations
		elif menuBtnRects[3].collidepoint((x,y)):
			pass
		#mode
		elif menuBtnRects[4].collidepoint((x,y)):
			pass
		#still
		elif menuBtnRects[5].collidepoint((x,y)):
			settings["still"] = not settings["still"]
		#load
		elif menuBtnRects[6].collidepoint((x,y)):
			settings["load"] = True
			loadFirst()
		#github
		elif menuBtnRects[7].collidepoint((x,y)):
			webbrowser.open("https://github.com/JelleWiersma/conway", 2, True)
		#pydroid
		elif menuBtnRects[8].collidepoint((x,y)):
			webbrowser.open("https://play.google.com/store/apps/details?id=ru.iiec.pydroid3", 2, True)

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
primColor = COLORS["White"]
loading = renderText(LOADINGTEXT, FONT, primColor)
screen.blit(loading, (WIDTH//2 - loading.get_width()//2, HEIGHT//2 - loading.get_height()//2))
pygame.display.flip()
running = ingame = paused = draw = True
still = mouseActive = update = False
ptouch = stouch = dtouch = mtouch = None
turns = color = offsX = offsY = firstX = firstY = 0
cellSize = max(10, FIELDRECT.width // 80, FIELDRECT.height // 60)
speed = UPDATESP1
fingers = {}
oldFingers = {}
field = pygame.Surface((FIELDRECT.width, FIELDRECT.height))
field.set_clip(field.get_rect())
clock = pygame.time.Clock()
rows, columns = FIELDRECT.height // cellSize, FIELDRECT.width // cellSize
currentGrid = set()
firstGrid = set()
lastGrid = set()
pygame.time.set_timer(UPDATEEVENT, UPDATESP1)
settings = {"cleared": False, "resetPos": False, "speed": 1, "pos": False, "color": "White", "anims": False, "mode": 1, "still": False, "load": False}
speedText = SP1TEXT
menuBtnRects = loadMenus(WIDTH, HEIGHT, TITLERECT.bottom, settings, COLORS)
	
#game loop
while running:
	update = False
	for event in pygame.event.get():
		
		#Process events
		if event.type == pygame.QUIT:
			running = False

		if event.type == UPDATEEVENT:
			update = True
			continue
		
		if TOUCHSCREEN:
			#touch input
			if event.type == pygame.FINGERDOWN:

				x = event.x * WIDTH 
				y = event.y * HEIGHT
				if ingame:
					handleFDGame(x,y, event.finger_id)
				else:
					handleFDMenu(x,y, event.finger_id)
				continue
					
			if event.type == pygame.FINGERMOTION:
				x = event.x * WIDTH
				y = event.y * HEIGHT
				dx = event.dx*WIDTH
				dy = event.dy*HEIGHT
				
				if ingame:
					handleFMGame(x,y,dx,dy, event.finger_id)
				continue
						
			if event.type == pygame.FINGERUP:
				handleFU(event.finger_id)
				continue
		else:
			#mouse input
			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1: #left click
					mx, my = event.pos
					if ingame:
						handleFDGame(mx,my, "mouse")
					else:
						handleFDMenu(mx,my, "mouse")
					mouseActive = True
				elif event.button in (4,5): #scroll
					if FIELDRECT.collidepoint(event.pos) and ingame:
						dy = WIDTH // 20 if event.button == 4 else 1 - WIDTH // 20
						updateGrid(0,0,dy,event.pos)
						
			if event.type == pygame.MOUSEMOTION:
				mx, my = event.pos
				if mouseActive:
					if ingame:
						handleFMGame(mx,my,event.rel[0], event.rel[1], "mouse")
						
			if event.type == pygame.MOUSEBUTTONUP:
				if event.button == 1: #left click
					handleFU("mouse")
					mouseActive = False
		
	if ingame:

		#draw fingers
		if draw:
			for finger, pos in fingers.items():
				if FIELDRECT.collidepoint(pos):
					fx, fy = pos[0], pos[1]
					cx = int((fx - FIELDRECT.left - offsX) // cellSize + firstX)
					cy = int((fy - FIELDRECT.top - offsY) // cellSize + firstY)
					currentGrid.add((cx,cy))
		
		#update cells
		if (not paused) & update:
			if settings["still"] and still:
				paused = True
				settings["still"] = False
				continue
			
			if turns == 0:
				firstGrid = currentGrid
			turns += 1
			updateCells()
	
	#draw stuff
	screen.fill(SECCOLOR)
	drawTitle()

	if ingame:
		drawPauseButton()
		drawSpeedButton()
		drawDragButton()
		drawField()

	else:
		menu = getMenu(WIDTH, HEIGHT, TITLERECT.bottom, settings, primColor)
		screen.blit(menu, (0,TITLERECT.bottom))
		
	pygame.display.flip()
	clock.tick(144)