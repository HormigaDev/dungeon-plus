import pygame, sys
from config import Game
from states.floor import game_loop
from states.menu import menu_loop

pygame.init()
running = True

if __name__ == "__main__":
    while running:
        if Game.state == 'floor':
            game_loop()
        elif Game.state == 'menu':
            menu_loop()
        else:
            runnig = False
    sys.exit()