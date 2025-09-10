import pygame
from collections import defaultdict
pygame.init()

# downloaded from https://www.pygame.org/wiki/TextWrap
# draw some text into an area of a surface
# automatically wraps words
# returns any text that didn't get blitted
def drawText(surface, text, color, rect, font, aa=False, bkg=None):
    rect = pygame.Rect(rect)
    y = rect.top
    lineSpacing = -2

    # get the height of the font
    fontHeight = font.size("Tg")[1]

    while text:
        i = 1

        # determine if the row of text will be outside our area
        if y + fontHeight > rect.bottom:
            break

        # determine maximum width of line
        while font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1

        # if we've wrapped the text, then adjust the wrap to the last word      
        if i < len(text): 
            i = text.rfind(" ", 0, i) + 1

        # render the line and blit it to the surface
        if bkg:
            image = font.render(text[:i], 1, color, bkg)
            image.set_colorkey(bkg)
        else:
            image = font.render(text[:i], aa, color)

        surface.blit(image, (rect.left, y))
        y += fontHeight + lineSpacing

        # remove the text we just blitted
        text = text[i:]

    return text

#draw button
def drawButton(screen, rect, text, font, active=False, redraw=True, primColor=(255,255,255), secColor= (0,0,0)):
	if redraw:
		pygame.draw.rect(screen, secColor, rect)
		if active:
			pygame.draw.rect(screen, primColor, rect)
			render = font.render(text, True, secColor)
		else:
			pygame.draw.rect(screen, primColor, rect, 5)
			render = font.render(text, True, primColor)
		pos = (
			rect.centerx - render.get_width() / 2,
			rect.centery - render.get_height() / 2
		)
		screen.blit(render, pos)
	return rect

_fade_cache = {}

def fadeColor(color, alpha):
    # Normalize key: works for both pygame.Color and RGB tuples
    if isinstance(color, pygame.Color):
        key = (color.r, color.g, color.b, alpha)
    elif isinstance(color, tuple):
        key = (*color, alpha)
    else:
        raise TypeError("Color must be a tuple or pygame.Color")

    # Return from cache if available
    if key in _fade_cache:
        return _fade_cache[key]

    # Only create once, no repeat copy
    faded = pygame.Color(*key[:3])
    faded.a = key[3]
    _fade_cache[key] = faded
    return faded
	
def updateCells(grid):
	resGrid = set()
	neighbourCounts = defaultdict(int)
	#for every alive cell, add one alive cell to the count of all the neighbours
	for cell in grid:
		for dx in [-1, 0, 1]:
			for dy in [-1,0,1]:
				if not (dx == 0 and dy == 0):
					currentNb = (cell[0] + dx, cell[1] + dy)
					neighbourCounts[currentNb] += 1
	
	#Take every relevant cell and check if they live
	for cell, count in neighbourCounts.items():
		if count == 3 or (count == 2 and cell in grid):
			resGrid.add(cell)
	return resGrid
