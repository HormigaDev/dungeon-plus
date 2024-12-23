import pygame
from sprites.entity import *
from config import calc_stats, font, SPRITES_SIZE, get_entity_size
from abc import ABC
from procedural import Procedural

BASE_XP = 10

class Entity(ABC):
    entity_type = None
    x = 0
    y = 0
    width = 0
    height = 0
    level = 1
    health = 1
    max_health = 1
    speed = 0.3
    gravity = 0.4
    weight = 60
    velocity_y = 0
    on_ground = False
    jumping = False
    moving = False
    last_attack_time = 0
    attack_cooldown_time = 0
    detect_entity_range = 0
    damage_range = 0
    damage = 0
    resistance = 0
    protected = False
    absortion = 0
    family = []
    weapon = None
    jump_strength = -10
    xp_multiplier = 0

    facing_right = True
    current_frame = 0
    last_update_time = 0
    frame_duration = 100

    def __init__(self, type=None, level=1, animate=False):
        if type is None:
            raise ValueError("No se proporcionó ningún tipo de entidad")
        self.level = level
        self.entity_type = type
        self.spritesheet = pygame.image.load(f"textures/entity/{self.entity_type}_sheet.png").convert_alpha()
        self.health, self.damage, self.resistance, self.speed, self.weight, self.damage_range, self.attack_cooldown_time, self.detect_entity_range, self.xp_multiplier, self.base_health = calc_stats(level, type)
        self.damage_range = SPRITES_SIZE * self.damage_range
        self.width, self.height = get_entity_size(type)
        self.max_health = self.health

        if animate is True:
            self.animation_frames_right = [
                self.spritesheet.subsurface(pygame.Rect(RIGHT_3[0] * S_WIDTH, RIGHT_3[1] * S_HEIGHT, S_WIDTH, S_HEIGHT)),
                self.spritesheet.subsurface(pygame.Rect(RIGHT_2[0] * S_WIDTH, RIGHT_2[1] * S_HEIGHT, S_WIDTH, S_HEIGHT)),
                self.spritesheet.subsurface(pygame.Rect(RIGHT_1[0] * S_WIDTH, RIGHT_1[1] * S_HEIGHT, S_WIDTH, S_HEIGHT))
            ]
            self.animation_frames_left = [
                self.spritesheet.subsurface(pygame.Rect(LEFT_3[0] * S_WIDTH, LEFT_3[1] * S_HEIGHT, S_WIDTH, S_HEIGHT)),
                self.spritesheet.subsurface(pygame.Rect(LEFT_2[0] * S_WIDTH, LEFT_2[1] * S_HEIGHT, S_WIDTH, S_HEIGHT)),
                self.spritesheet.subsurface(pygame.Rect(LEFT_1[0] * S_WIDTH, LEFT_1[1] * S_HEIGHT, S_WIDTH, S_HEIGHT))
            ]
        else:
            self.image = self.spritesheet

    def draw(self, surface, offset_x, offset_y):
        self.before_draw(surface, offset_x, offset_y)
        surface.blit(self.image, (self.x - offset_x, self.y - offset_y))

        if 'player' not in self.family:
            if self.health < self.max_health:
                bar_width = self.width
                bar_height = 4
                bar_x = self.x - offset_x
                bar_y = self.y - offset_y - 8
                pygame.draw.rect(surface, (169, 169, 169), (bar_x, bar_y, bar_width, bar_height))

                life_percentage = self.health / self.max_health
                life_width = bar_width * life_percentage
                pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, life_width, bar_height))

            level_text = f"Lvl {self.level}"
            level_surface = font(12).render(level_text, True, (255, 255, 255))
            level_rect = level_surface.get_rect(center=(self.x - offset_x + self.width // 2, self.y - offset_y - 16))
            surface.blit(level_surface, level_rect)
        self.after_draw(surface, offset_x, offset_y)

    def update(self):
        if pygame.time.get_ticks() - self.last_update_time > self.frame_duration:
            self.current_frame = (self.current_frame + 1) % 3
            self.last_update_time = pygame.time.get_ticks()
        if not self.moving:
            self.current_frame = 2

        if self.facing_right:
            self.image = self.animation_frames_right[self.current_frame]
        else:
            self.image = self.animation_frames_left[self.current_frame]

    def movement(self, procedural, direction='right'):
        if direction == 'left':
            self.facing_right = False
            x = int(self.x / procedural.width)
            y = int((self.y + (self.height / 2)) / procedural.height)
            if x > 0 and procedural.grid[y][x] in procedural.voids:
                self.x -= self.speed
                self.moving = True
            if (
                y > 1
                and procedural.grid[y - 1][x] in procedural.voids
                and procedural.grid[y][x] not in procedural.voids
                and self.on_ground
                and not self.jumping
            ):
                self.y -= procedural.height
        if direction == 'right':
            self.facing_right = True
            x = int((self.x + self.width) / procedural.width)
            y = int((self.y + (self.height / 2)) / procedural.height)
            if x < len(procedural.grid[y]) - 1 and procedural.grid[y][x] in procedural.voids:
                self.x += self.speed
                self.moving = True
            if (
                y > 1
                and procedural.grid[y - 1][x] in procedural.voids
                and procedural.grid[y][x] not in procedural.voids
                and self.on_ground
                and not self.jumping
            ):
                self.y -= procedural.height

    def apply_gravity(self, procedural):
        effective_gravity = self.gravity * (self.weight / 60)
        self.velocity_y += effective_gravity
        new_y = self.y + self.velocity_y

        grid_x = int((self.x + self.width // 2) // procedural.width)

        if self.velocity_y > 0:  # Descendiendo
            grid_y = int((new_y + self.height) // procedural.height)
            if grid_y < len(procedural.grid) and procedural.grid[grid_y][grid_x] not in procedural.voids:
                self.velocity_y = 0
                self.on_ground = True
                self.jumping = False
                new_y = grid_y * procedural.height - self.height
            elif grid_y >= len(procedural.grid):
                self.velocity_y = 0
                self.on_ground = True
                self.jumping = False
                new_y = (len(procedural.grid) - 1) * procedural.height - self.height
            else:
                self.on_ground = False

        elif self.velocity_y < 0:  # Ascendiendo
            grid_y = int(new_y // procedural.height)
            if grid_y >= 0 and procedural.grid[grid_y][grid_x] not in procedural.voids:
                self.velocity_y = 0
                new_y = (grid_y + 1) * procedural.height
                self.jumping = False
            elif grid_y < 0:
                self.velocity_y = 0
                new_y = 0
                self.jumping = False
        
        self.y = new_y
    
    def attack(self, entity, procedural):
        current_time = pygame.time.get_ticks()

        if current_time - self.last_attack_time < self.attack_cooldown_time:
            return

        def center(entity):
            x = entity.x + (entity.width / 2)
            y = entity.y + (entity.height / 2)
            return x, y
        
        x, y = center(self)
        xe, ye = center(entity)
        
        if abs(x - xe) <= self.damage_range and abs(y - ye) <= self.damage_range:
            hurt = round(self.damage / entity.resistance, 0)
            if hurt < 1:
                return
            if entity.protected:
                if hurt > entity.absortion:
                    entity.protected = False
                    entity.health -= round(hurt - entity.absortion, 1)
                    entity.absortion = 0
                else:
                    entity.absortion -= hurt
                    x,y = int(self.x/SPRITES_SIZE), int(self.y/SPRITES_SIZE)
                    if entity.facing_right:
                        if y > 0 and x > 0:
                            if procedural.grid[y-1][x+1] in procedural.voids:
                                self.x += SPRITES_SIZE
                                self.y -= SPRITES_SIZE
                    else:
                        if y > 0 and x < len(procedural.grid[0]):
                            if procedural.grid[y-1][x-1] in procedural.voids: 
                                self.x -= SPRITES_SIZE
                                self.y -= SPRITES_SIZE

            else:
                entity.health -= hurt
            self.last_attack_time = current_time
            entity.on_hurt(self, procedural)
    
    def on_hurt(self, entity, procedural):
        if self.resistance >= entity.damage - 1:
            return
        if 'player' not in self.family:
            x,y = int(self.x/SPRITES_SIZE), int(self.y/SPRITES_SIZE)
            self.after_hurt(procedural)
            if entity.facing_right:
                if y > 0 and x > 0:
                    if procedural.grid[y-1][x+1] in procedural.voids:
                        self.x += SPRITES_SIZE
                        self.y -= SPRITES_SIZE
            else:
                if y > 0 and x < len(procedural.grid[0]):
                    if procedural.grid[y-1][x-1] in procedural.voids:        
                        self.x -= SPRITES_SIZE
                        self.y -= SPRITES_SIZE
            current_time = pygame.time.get_ticks()
            self.last_attack_time = current_time

    def spawn(self, procedural: Procedural, player=None):
        if player is None:
            self.move(procedural)
        else:
            self.move(procedural, player)
            self.attack(player, procedural)
        self.apply_gravity(procedural)
        self.update()
        self.after_spawn()

    def on_death(self, player):
        player.xp += int(BASE_XP * (self.level ** self.xp_multiplier))

    #Abstract methods
    def before_draw(self, surface, offset_x, offset_y):
        pass
    def after_draw(self, surface, offset_x, offset_y):
        pass
    def move(self, procedural, player):
        pass
    def after_spawn(self):
        pass

    def after_hurt(self, procedural):
        pass