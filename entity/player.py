import pygame
from sprites.entity import *
from entity.entity import Entity
from sprites.weapons_sprites import KATANA, S_WIDTH as anch, S_HEIGHT as alt
from database.db import conn, cursor
from config import calculate_required_xp, calc_health, calc_damage, calc_resistance

katana_rotate = False
class Player(Entity):
    attacking = False
    xp = 0
    armor = 'iron'
    face_item = 'iron'
    base_damage = 10

    def __init__(self, level, health, xp):
        super().__init__(type='player', level=level, animate=True)
        self.family = ['player', 'entity', 'human']

        spritesheet = pygame.image.load('textures/weapons_items_and_details.png').convert_alpha()
        self.katana_sprite = spritesheet.subsurface(pygame.Rect(
            anch * KATANA[0],
            alt * KATANA[1],
            anch,
            alt
        ))
        self.katana_sprite = pygame.transform.scale(self.katana_sprite, (16, 16))
        self.katana_sprite_rotate = pygame.transform.rotate(self.katana_sprite, -45)
        self.ktn = self.katana_sprite

        self.armor_sheet = pygame.image.load(f"textures/armor/{self.armor}_armor.png").convert_alpha()
        self.face_item_sheet = pygame.image.load(f"textures/armor/{self.face_item}_face_protector.png").convert_alpha()

        self.armor_frames_right = [
            self.armor_sheet.subsurface(pygame.Rect(RIGHT_3[0] * S_WIDTH, RIGHT_3[1] * S_HEIGHT, S_WIDTH, S_HEIGHT)),
            self.armor_sheet.subsurface(pygame.Rect(RIGHT_2[0] * S_WIDTH, RIGHT_2[1] * S_HEIGHT, S_WIDTH, S_HEIGHT)),
            self.armor_sheet.subsurface(pygame.Rect(RIGHT_1[0] * S_WIDTH, RIGHT_1[1] * S_HEIGHT, S_WIDTH, S_HEIGHT))
        ]
        self.armor_frames_left = [
            self.armor_sheet.subsurface(pygame.Rect(LEFT_3[0] * S_WIDTH, LEFT_3[1] * S_HEIGHT, S_WIDTH, S_HEIGHT)),
            self.armor_sheet.subsurface(pygame.Rect(LEFT_2[0] * S_WIDTH, LEFT_2[1] * S_HEIGHT, S_WIDTH, S_HEIGHT)),
            self.armor_sheet.subsurface(pygame.Rect(LEFT_1[0] * S_WIDTH, LEFT_1[1] * S_HEIGHT, S_WIDTH, S_HEIGHT))
        ]

        self.face_item_frames_right = [
            self.face_item_sheet.subsurface(pygame.Rect(RIGHT_1[0] * S_WIDTH, RIGHT_1[1] * S_HEIGHT, S_WIDTH, S_HEIGHT)),
            self.face_item_sheet.subsurface(pygame.Rect(RIGHT_1[0] * S_WIDTH, RIGHT_1[1] * S_HEIGHT, S_WIDTH, S_HEIGHT)),
            self.face_item_sheet.subsurface(pygame.Rect(RIGHT_1[0] * S_WIDTH, RIGHT_1[1] * S_HEIGHT, S_WIDTH, S_HEIGHT))
        ]
        self.face_item_frames_left = [
            self.face_item_sheet.subsurface(pygame.Rect(LEFT_1[0] * S_WIDTH, LEFT_1[1] * S_HEIGHT, S_WIDTH, S_HEIGHT)),
            self.face_item_sheet.subsurface(pygame.Rect(LEFT_1[0] * S_WIDTH, LEFT_1[1] * S_HEIGHT, S_WIDTH, S_HEIGHT)),
            self.face_item_sheet.subsurface(pygame.Rect(LEFT_1[0] * S_WIDTH, LEFT_1[1] * S_HEIGHT, S_WIDTH, S_HEIGHT))
        ]

        self.required_xp = calculate_required_xp(self.level)
        self.health = health
        self.xp = xp

    def move(self, procedural, player=None):
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()

        self.moving = False

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.movement(procedural, direction='left')

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.movement(procedural, direction='right')
        
        if mouse[2]:
            if self.absortion > 0:
                self.protected = True
    
    def before_draw(self, surface, offset_x, offset_y):
        global katana_rotate
        if self.attacking:
            if not katana_rotate:
                self.katana_sprite = self.katana_sprite_rotate
        else:
            katana_rotate = False
            self.katana_sprite = self.ktn

        x = self.x + (self.width / 2)
        y = self.y + (self.height / 2)
        
        if self.facing_right:
            surface.blit(self.katana_sprite, (x - offset_x + 6, y - offset_y - 2))
        else:
            surface.blit(pygame.transform.flip(self.katana_sprite, True, False), (x - offset_x - 16, y - offset_y - 3))

    def after_draw(self, surface, offset_x, offset_y):
        frames = self.armor_frames_left if not self.facing_right else self.armor_frames_right
        frames_face = self.face_item_frames_left if not self.facing_right else self.face_item_frames_right
        surface.blit(frames[self.current_frame], (self.x - offset_x, self.y - offset_y))
        surface.blit(frames_face[self.current_frame], (self.x - offset_x, self.y - offset_y))

    def after_spawn(self):
        if self.xp >= self.required_xp:
            xp_remaining = int(self.xp - self.required_xp)
            self.level += 1
            self.required_xp = calculate_required_xp(self.level)
            self.xp = xp_remaining
            self.resistance = calc_resistance(self.level)
            self.health = calc_health(self.base_health, self.level)
            self.max_health = self.health
            self.damage = calc_damage(self.damage, self.resistance, self.level)