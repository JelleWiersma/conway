import pygame
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
def drawButton(screen, rect, text, font, border=0, redraw=True, primColor=(255,255,255), secColor= (0,0,0)):
	if redraw:
		pygame.draw.rect(screen, secColor, rect)
		if border == 0:
			pygame.draw.rect(screen, primColor, rect)
			render = font.render(text, True, secColor)
		else:
			pygame.draw.rect(screen, primColor, rect, border)
			render = font.render(text, True, primColor)
		text_rect = render.get_rect(center=rect.center)
		screen.blit(render, text_rect)
	return rect
