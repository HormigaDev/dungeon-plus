import pygame
from config import font as game_font
from screen import WIDTH, HEIGHT

WHITE = (240, 240, 240)
SOFT_GRAY = (208, 208, 208)
BLUE_GRAY = (119, 136, 153)
DARK = (33, 33, 33)

class InputValue():
    def __init__(self):
        self.value = ''

class Button():
    def __init__(self, label, dimensions, center=False, color=WHITE, onclick=None, label_size=None):
        self._onclick = onclick
        self.label = label
        self.dimensions = dimensions
        self.color = color
        self.center = center
        self.label_size = label_size
    def click(self):
        if self._onclick is not None:
            self._onclick()
    def draw(self, surface, pos):
        x, y, width, height = self.dimensions
        if self.center:
            x = WIDTH / 2 - width / 2
            self.dimensions = (x,y,width,height)
        border = pygame.Rect(x-2,y-2, width+4, height+4)
        rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, BLUE_GRAY, border, 4)
        color = SOFT_GRAY if pos is not None and mouse_over(pos, self.dimensions) else self.color
        pygame.draw.rect(surface, color, rect)

        label_size = self.label_size if self.label_size is not None else height/2
        draw_text(self.label, surface, (x + (width/2), y + (height/2), label_size), DARK)

def mouse_over(pos, dimensions):
    x,y,width,height = dimensions
    xm,ym = pos
    if xm >= x and xm <= x + width:
        if ym >= y and ym <= y + height:
            return True
    return False

def draw_text(text, surface, dimensions, color=WHITE):
    x, y, font_size = dimensions
    font = game_font(int(font_size))
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_surface, text_rect)
    
class Input():
    def __init__(self, object, dimensions, oninput=None, center=None, font_size=None):
        self.focused = False
        self._oninput = oninput
        self.dimensions = dimensions
        self.object = object
        self.center = center
        self.font_size = font_size

    def draw(self, surface, pos):
        x,y,width,height = self.dimensions
        if self.center:
            x = WIDTH / 2 - width / 2
            self.dimensions = (x,y,width,height)
        font_size = self.font_size if self.font_size is not None else height // 2
        border = pygame.Rect(x-2,y-2,width+4, height+4)
        rect = pygame.Rect(x,y,width,height)
        pygame.draw.rect(surface, BLUE_GRAY, border, 4)
        color = WHITE if mouse_over(pos, self.dimensions) else SOFT_GRAY
        pygame.draw.rect(surface, color, rect)

        draw_text(self.object.value, surface, (x + (width//2), y + (height//2), font_size), DARK)

