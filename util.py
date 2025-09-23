import pygame
pygame.init()

def drawText(text, color, width, font, aa=True, bkg=None, lineSpacing=0):
    # First, split text into lines that fit the width
    lines = []
    while text:
        i = 1
        while font.size(text[:i])[0] < width and i < len(text):
            i += 1
            if text[i-1] == '\n':
                break
        if '\n' in text[:i]:
            split_at = text[:i].find('\n') + 1
            lines.append(text[:split_at].strip())
            text = text[split_at:]
        else:
            if i < len(text):
                i = text.rfind(" ", 0, i) + 1
            lines.append(text[:i].strip())
            text = text[i:]
    fontHeight = font.size("Tg")[1]
    total_height = len(lines) * (fontHeight + lineSpacing)
    if len(lines) == 1:
        width = font.size(lines[0])[0]
    surface = pygame.Surface((width, total_height), pygame.SRCALPHA)
    y = 0
    for line in lines:
        if bkg:
            image = renderText(line, font, color, bkg)
            image.set_colorkey(bkg)
        else:
            image = font.render(line, aa, color)
        surface.blit(image, (0, y))
        y += fontHeight + lineSpacing
    return surface

#draw button
def drawButton(screen, rect, text, font, border=0, primColor=(255,255,255), secColor=(0,0,0)):
    
    if border == 0:
        pygame.draw.rect(screen, primColor, rect)
        render = renderText(text, font, secColor, primColor)
    else:
        pygame.draw.rect(screen, primColor, rect, border)
        render = renderText(text, font, primColor, secColor)
    text_rect = render.get_rect(center=rect.center)
    screen.blit(render, text_rect)
    return rect

renderCache = {}
def renderText(text, font, color, secColor=(0,0,0)):
    key = (text, font, str(color), str(secColor))
    if key in renderCache:
        return renderCache[key]
    else:
        renderCache[key] = font.render(text, True, color, secColor)
        return renderCache[key]
