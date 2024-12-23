import pygame, sys
from screen import screen, WIDTH, HEIGHT
from gui import draw_text, mouse_over, Button, Input, InputValue
from PIL import Image, ImageFilter
from config import Game
from database.db import create_save, get_save_data, get_saves
from utils.colors import *

title = (WIDTH // 2, 48, 48)

background = Image.open('textures/background_2.webp')
background = background.resize((WIDTH, HEIGHT))
background = background.filter(ImageFilter.GaussianBlur(3))
background = pygame.image.fromstring(background.tobytes(), background.size, background.mode)

def menu_loop():
    class Menu():
        tab = 'main'
        running = True
    pygame.mouse.set_visible(True)
    
    def start_click():
        Menu.tab = 'start'
    start = Button("Iniciar Partida", (0, 250, 200, 32), center=True, onclick=start_click)
    def load_click():
        Menu.tab = 'load'
    load = Button("Cargar Partida", (0, 300, 200, 32), center=True, onclick=load_click)
    configurations = Button("Configuraciones", (0, 350, 200, 32), center=True)
    about = Button("Sobre el juego", (0, 400, 200, 32), center=True)

    def toback_click():
        Menu.tab = 'main'
    toback = Button("<", (24, 24, 32, 32), label_size=20, onclick=toback_click)
    save_name = InputValue()
    save = Input(save_name, (0, 250, 500, 32), center=True, font_size=18)
    def start_game_click():
        id = create_save(save_name.value)
        level, health, seed,xp = get_save_data(id)
        Game.player_level = level
        Game.player_health = health
        Game.seed = seed
        Game.player_xp = xp
        Game.save_id = id
        Game.state = 'floor'
        Menu.running = False
    start_game = Button("Empezar!", (0, 310, 200, 32), center=True, onclick=start_game_click)
    clock = pygame.time.Clock()

    visible_start = 0
    visible_end = 4
    selected_save = 0
    saves = get_saves()
    save_count = len(saves)

    while Menu.running:
        pos = pygame.mouse.get_pos()
        screen.blit(background, (0,0))
        draw_text("Bienvenido a Dungeon +plus", screen, title)

        if Menu.tab == 'main':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    Menu.running = False
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        pos = pygame.mouse.get_pos()
                        if mouse_over(pos, start.dimensions):
                            start.click()
                        if mouse_over(pos, load.dimensions):
                            load.click()
                        if mouse_over(pos, configurations.dimensions):
                            configurations.click()
                        if mouse_over(pos, about.dimensions):
                            about.click()

            # Dibujar botones
            start.draw(screen, pos)
            load.draw(screen, pos)
            configurations.draw(screen, pos)
            about.draw(screen, pos)
        
        elif Menu.tab == 'start':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    Menu.running = False
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    save.focused = False
                    if event.button == 1:
                        pos = pygame.mouse.get_pos()
                        if mouse_over(pos, toback.dimensions):
                            toback.click()
                        if mouse_over(pos, save.dimensions):
                            save.focused = True
                        if mouse_over(pos, start_game.dimensions):
                            start_game.click()
                if event.type == pygame.KEYDOWN:
                    if save.focused:
                        if event.unicode.isprintable():
                            if len(save.object.value) <= 25:
                                save.object.value += event.unicode

                        elif event.key == pygame.K_BACKSPACE:
                            save.object.value = save.object.value[:-1]
            
            toback.draw(screen, pos)
            save.draw(screen, pos)
            draw_text("Nombre de la partida", screen, (save.dimensions[0] + (save.dimensions[2]//2), 220, 24))
            start_game.draw(screen, pos)

        elif Menu.tab == 'load':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    Menu.running = False
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        pos = pygame.mouse.get_pos()
                        if mouse_over(pos, toback.dimensions):
                            toback.click()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        if selected_save > 0:
                            selected_save -= 1
                            if selected_save < visible_start and visible_start > 0:
                                visible_start -= 1
                                visible_end -= 1

                    elif event.key == pygame.K_DOWN:
                        if selected_save < save_count - 1:
                            selected_save += 1
                            if selected_save >= visible_end and visible_end < save_count:
                                visible_start += 1
                                visible_end += 1

                    elif event.key == pygame.K_RETURN:
                        current_save = saves[selected_save]
                        id,name = current_save
                        print(id)
                        level, health, seed, xp = get_save_data(id)
                        Game.player_level = level
                        Game.player_health = health
                        Game.seed = seed
                        Game.player_xp = xp
                        Game.save_id = id
                        Game.state = 'floor'
                        Menu.running = False

                    elif event.key == pygame.K_BACKSPACE:
                        Menu.tab = 'main'

            # Dibujar los saves visibles
            toback.draw(screen, pos)
            y_pos = 250
            for i in range(visible_start, visible_end):
                if len(saves) <= i:
                    break
                if len(saves) > 0:
                    color = BLUE if i == selected_save else WHITE
                    id, name = saves[i]
                    draw_text(f"{id} - {name}", screen, (WIDTH // 2, y_pos, 24), color=color)
                    y_pos += 40
                    

        pygame.display.flip()
        clock.tick(60)