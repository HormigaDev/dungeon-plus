import random, math
from sprites.entity import *
from entity.entity import Entity
from entity.player import Player
from procedural import Procedural
from config import SPRITES_SIZE

class Goblin(Entity):
    stop_probability = 0.002
    change_direction_probability = 0.008
    original_speed = 0
    bloods = [1004, 1005, 1006, 1007, 1008]
    def __init__(self, level=1):
        super().__init__(type='goblin', level=level, animate=True)
        self.family = ['entity', 'monster', 'goblin']
        self.image = self.animation_frames_right[0]
        self.stop_probability = 0.6
        self.change_direction_probability = 0.005
        self.original_speed = self.speed

    def move(self, procedural: Procedural, player: Player):
        distance_to_player_x = abs(self.x - player.x)
        distance_to_player_y = abs(self.y - player.y)

        if (
            distance_to_player_x <= self.detect_entity_range * procedural.width
            and distance_to_player_y <= self.detect_entity_range * procedural.height

            and (
                self.x + self.width < player.x
                or self.x > player.x + player.width
            )
        ):
            self.speed = self.original_speed
            if self.x + self.width < player.x:
                self.facing_right = True
                self.movement(procedural, direction='right')
            elif self.x > player.x + player.width:
                self.facing_right = False
                self.movement(procedural, direction='left')
            else:
                self.facing_right = True
        else:
            self.speed = math.ceil(self.speed * 0.5)
            self.moving = True
            if random.random() < self.change_direction_probability:
                self.facing_right = not self.facing_right

            if self.facing_right:
                self.movement(procedural, direction='right')
            else:
                self.movement(procedural, direction='left')
    def after_hurt(self, procedural):
        x,y = int(self.x//SPRITES_SIZE), int(self.y//SPRITES_SIZE)
        if y < len(procedural.grid):
            if procedural.grid[y+1][x] == 0:
                seed = procedural.seed
                random.seed(None)
                procedural.surfaces[f'{x}-{y}'] = random.choice(self.bloods)
                random.seed(seed)