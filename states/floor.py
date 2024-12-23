import pygame, sys, threading, time
from screen import screen, WIDTH as SCREEN_WIDTH, HEIGHT as SCREEN_HEIGHT
from config import font as game_font, SPRITES_SIZE, Game
from procedural import Procedural
from entity.goblin import Goblin
from entity.player import Player
from gui import draw_text, Button, mouse_over
from utils.colors import *
from database.db import save_game

FLOOR_SIZE = 1000
SPRITE_SHEET_PATH = "textures/terrain.png"
MAP_WIDTH = SPRITES_SIZE * FLOOR_SIZE
MAP_HEIGHT = SPRITES_SIZE * FLOOR_SIZE
CAMERA_SPEED = 4

def load_sheet(path):
    return pygame.image.load(path).convert_alpha()
camera_x, camera_y = 0,0
def game_loop():
    global camera_x, camera_y
    Game.loading = True
    running = True
    clock = pygame.time.Clock()
    last_update_time = time.time()
    spritesheet = load_sheet(SPRITE_SHEET_PATH)
    print(Game.seed)
    procedural = Procedural(spritesheet, Game.seed)
    player = Player(level=Game.player_level, health=Game.player_health, xp=Game.player_xp)
    entities = []

    leave = Button("<", (SCREEN_WIDTH - 44, SCREEN_HEIGHT - 44, 32, 32), label_size=20)

    def generate_world(procedural, entities, player):
        procedural.generate_maze(FLOOR_SIZE, FLOOR_SIZE, step_callback=pygame.event.pump)
        procedural.refine_paths()
        entities.extend(procedural.place_entities([Goblin], step_callback=pygame.event.pump))
        player.x, player.y = procedural.find_first_valid_position()
        Game.loading = False
    thread = threading.Thread(target=generate_world, args=(procedural, entities, player))
    thread.start()
    loading_number = 1
    while Game.loading:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Game.state = 'end'
                running = False
                sys.exit()
        screen.fill(DARK)
        text = "CARGANDO" + ("." if loading_number == 1 else ".." if loading_number <= 2 else "...")
        draw_text(text, screen, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2, 56))
        current_time = time.time()
        if current_time - last_update_time >= 0.5:
            last_update_time = current_time
            loading_number += 1
            if loading_number >= 4:
                loading_number = 1
        pygame.display.flip()
        clock.tick(60)

    def draw_visible_area(surface, offset_x, offset_y):
        procedural.draw_map(surface, offset_x, offset_y)

    def update_camera():
        global camera_x, camera_y
        buffer_x = SCREEN_WIDTH // 4
        buffer_y = SCREEN_HEIGHT // 4

        if player.x < camera_x + buffer_x:
            camera_x = max(0, player.x - buffer_x)
        if player.x > camera_x + SCREEN_WIDTH - buffer_x:
            camera_x = min(MAP_WIDTH - SCREEN_WIDTH, player.x - (SCREEN_WIDTH - buffer_x))
        if player.y < camera_y + buffer_y:
            camera_y = max(0, player.y - buffer_y)
        if player.y > camera_y + SCREEN_HEIGHT - buffer_y:
            camera_y = min(MAP_HEIGHT - SCREEN_HEIGHT, player.y - (SCREEN_HEIGHT - buffer_y))

    def handle_entities():
        for i in range(len(entities) - 1, -1, -1):
            entity = entities[i]
            if entity.health <= 0:
                entity.on_death(player)
                del entities[i]
                continue
            if (entity.x >= camera_x-(SPRITES_SIZE*10) and entity.y >= camera_y-(SPRITES_SIZE*10)
                and entity.x <= camera_x + SCREEN_WIDTH + (SPRITES_SIZE*10)
                and entity.y <= camera_y + SCREEN_HEIGHT) + (SPRITES_SIZE*10):
                entity.spawn(procedural, player)

    def draw_health_bar():
        pygame.draw.rect(screen, GRAY, (12, 12, 300, 12))
        pygame.draw.rect(screen, GREEN, (12, 12, (player.health / player.max_health) * 300, 12))
        font = pygame.font.SysFont('Arial', 10)
        if player.health < 0:
            player.health = 0
        text_surface = font.render(f"{int(player.health)} / {player.max_health}", True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.center = (162, 18)
        screen.blit(text_surface, text_rect)

        pygame.draw.rect(screen, GRAY, (12, 32, 300, 4))
        pygame.draw.rect(screen, BLUE, (12, 32, (player.xp / player.required_xp) * 300, 4))

        text_surface = font.render(f"{int(player.xp)} / {int(player.required_xp)}", True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.center = (162, 42)
        screen.blit(text_surface, text_rect)

        text_surface = font.render(f"Lvl {player.level}", True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.center = (332, 18)
        screen.blit(text_surface, text_rect)

        text_surface = font.render(f"X: {int(player.x / SPRITES_SIZE)}   Y: {int(player.y / SPRITES_SIZE)}", True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.center = (SCREEN_WIDTH - 100, 18)
        screen.blit(text_surface, text_rect)

    def draw_text_centered(text, font, color, surface):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()

        text_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        surface.blit(text_surface, text_rect)

    def get_closest_entity(player, entities):
        closest_entity = None
        closest_distance = 32

        for entity in entities:
            distance = ((player.x - entity.x) ** 2 + (player.y - entity.y) ** 2) ** 0.5
            if distance <= closest_distance:
                closest_distance = distance
                closest_entity = entity

        return closest_entity

    font = game_font(74)
    pause = False
    game_over = False
    pygame.mouse.set_visible(False)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Game.state = 'end'
                running = False
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause = not pause
                    pygame.mouse.set_visible(pause)
                if event.key == pygame.K_w and not pause:
                    if player.on_ground or not player.jumping:
                        player.jumping = True
                        player.on_ground = False
                        player.velocity_y = player.jump_strength
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if not pause:
                        player.attacking = True
                        closest_entity = get_closest_entity(player, entities)
                        if closest_entity:
                            player.attack(closest_entity, procedural)
                    pos = pygame.mouse.get_pos()
                    if pause and mouse_over(pos, leave.dimensions):
                        save_game(Game.save_id, player.level, player.health, player.xp)
                        Game.state = 'menu'
                        running = False
                        camera_x, camera_y = 0,0
                        break
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    player.attacking = False
        
        if not pause:
            pygame.mouse.set_pos((SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        
        if pause:
            if not game_over:
                draw_text("PAUSE", screen, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2, 56))
            pygame.mouse.set_visible(True)
            pos = pygame.mouse.get_pos()
            leave.draw(screen, pos)
            pygame.display.flip()
            continue

        player.spawn(procedural)
        handle_entities()

        update_camera()

        screen.fill(BLACK)
        draw_visible_area(screen, camera_x, camera_y)
        player.draw(screen, camera_x, camera_y)

        for entity in entities:
            if (entity.x >= camera_x and entity.y >= camera_y
                and entity.x <= camera_x + SCREEN_WIDTH
                and entity.y <= camera_y + SCREEN_HEIGHT):
                entity.draw(screen, camera_x, camera_y)

        draw_health_bar()
        if player.health <= 0:
            draw_text_centered("GAME OVER", font, RED, screen)
            pause = True
            game_over = True

        pygame.display.flip()
        clock.tick(60)
