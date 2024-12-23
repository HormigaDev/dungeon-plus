import random, math, pygame
import sprites.map as sprites
import sprites.weapons_sprites as details
from config import SPRITES_SIZE

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

class Procedural():
    sprite_sheet = False
    sprite_ids = {
        0: sprites.STONE_CENTER,
        1: sprites.VOID,
        2: sprites.STONE_BORDER_TOP,
        3: sprites.STONE_BORDER_BOTTOM,
        4: sprites.STONE_BORDER_RIGHT,
        5: sprites.STONE_BORDER_LEFT,
        6: sprites.STONE_CORNER_TOP_RIGHT,
        7: sprites.STONE_CORNER_TOP_LEFT,
        8: sprites.STONE_CORNER_BOTTOM_RIGHT,
        9: sprites.STONE_CORNER_BOTTOM_LEFT,
        10: sprites.REVERSE_CORNER_TOP_RIGHT,
        11: sprites.REVERSE_CORNER_TOP_LEFT,
        12: sprites.REVERSE_CORNER_BOTTOM_RIGHT,
        13: sprites.REVERSE_CORNER_BOTTOM_LEFT,
        1000: details.CLOSED_GATE,
        1001: details.OPEN_GATE,
        1002: details.CLOSED_CHEST,
        1003: details.OPEN_CHEST,
        1004: details.GOBLIN_BLOOD_1,
        1005: details.GOBLIN_BLOOD_2,
        1006: details.GOBLIN_BLOOD_3,
        1007: details.GOBLIN_BLOOD_4,
        1008: details.GOBLIN_BLOOD_5,
    }

    voids = [1, 1001, 1002, 1003]
    solids = [1004, 1005, 1006, 1007, 1008, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
    surfaces = {}

    width = SPRITES_SIZE
    height = SPRITES_SIZE
    grid_width = 0
    grid_height = 0

    grid = []
    paths = []
    seed = 0
    first_block = (0, 0)

    def __init__(self, spritesheet, seed):
        self.sprite_sheet = spritesheet
        self.details_sheet = pygame.image.load('textures/weapons_items_and_details.png').convert_alpha()
        self.seed = seed

    def get_sprite(self, id):
        if not hasattr(self, '_sprite_cache'):
            self._sprite_cache = {}
        sp = None
        if id not in self._sprite_cache:
            sprite = self.sprite_ids[id]
            x, y = sprite
            if id < 1000:
                self._sprite_cache[id] = self.sprite_sheet.subsurface((
                    x * self.width,
                    y * self.height,
                    self.width,
                    self.height
                ))
            if id >= 1000 and id < 2000:
                self._sprite_cache[id] = self.details_sheet.subsurface((
                    x * self.width,
                    y * self.height,
                    self.width,
                    self.height
                ))
        return self._sprite_cache[id]
    
    def find_first_valid_position(self):
        x,y = self.first_block
        if x > 0:
            x = x-1
            self.grid[y][x] = 1001
            self.grid[y+1][x] = 0
            self.grid[y+1][x-1] = 0
            self.grid[y+1][x+1] = 0
        if y > 0:
            self.grid[y-1][x-1] = 0
            self.grid[y-1][x] = 0
            self.grid[y-1][x+1] = 0
        
        return x * self.width, y * self.height
    def draw_map(self, surface, offset_x, offset_y):
        if not self.grid or not len(self.grid):
            return
        start_col = int(max(0, offset_x // self.width))
        end_col = int(min(len(self.grid[0]), (offset_x + SCREEN_WIDTH) // self.width + 1))

        start_row = int(max(0, offset_y // self.height))
        end_row = int(min(len(self.grid), (offset_y + SCREEN_HEIGHT) // self.height + 1))

        for y in range(start_row, end_row):
            row = self.grid[y]
            for x in range(start_col, end_col):
                tile_id = row[x]
                if tile_id not in self.solids and tile_id != 0:
                    surface.blit(self.get_sprite(1), (x * self.width - offset_x, y * self.height - offset_y))
                surface.blit(self.get_sprite(tile_id), (x * self.width - offset_x, y * self.height - offset_y))
                layer = self.surfaces.get(f'{x}-{y}', None)
                if layer is not None:
                    surface.blit(self.get_sprite(layer), (x * self.width - offset_x, y * self.height - offset_y))

    def select_numbers(self, count=8):
        count = min(count, 8)
        return random.sample(range(101), count)
    
    def set_seed(self):
        seed = self.generate_seed(self.seed)
        self.seed = seed
        random.seed(self.seed)

    def generate_seed(self, base_number):
        return int((math.sin(base_number) * 10000) + (math.log1p(base_number) * 10000)) % 2**32

    def generate_maze(self, width, height, step_callback=None):
            maze = [[0 for _ in range(width)] for _ in range(height)]
            paths = []
            selected = False
            iterations = 1
            for _ in range(iterations):
                for i in range(height):
                    self.set_seed()
                    if random.random() < 0.8:
                        continue
                    self.set_seed()
                    index = random.randint(0, width-1)
                    paths.append((index, i))
                    if not selected:
                        self.first_block = (index, i)
                        selected = True
                    maze[i][index] = 1
                    if step_callback:
                        step_callback()
            self.set_seed()
            point_a = None
            point_b = None

            def generate_snake_path(matrix, point_a, point_b):
                x, y = point_a
                target_x, target_y = point_b

                while (x, y) != (target_x, target_y):
                    self.set_seed()
                    path_length = random.randint(3, 5)

                    for _ in range(path_length):
                        if (x, y) == (target_x, target_y):
                            break

                        dx = target_x - x
                        dy = target_y - y

                        self.set_seed()
                        if random.choice([True, False]):
                            self.set_seed()
                            direction = random.choice([(-1, 1), (1, 1), (-1, -1), (1, -1)])
                            x += direction[0]
                            y += direction[1]
                            
                            for adj_x, adj_y in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                                if 0 <= x + adj_x < len(matrix[0]) and 0 <= y + adj_y < len(matrix):
                                    matrix[y + adj_y][x + adj_x] = 1
                        else:
                            if abs(dx) > abs(dy):
                                x += 1 if dx > 0 else -1
                            else:
                                y += 1 if dy > 0 else -1

                            for adj_x, adj_y in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                                if 0 <= x + adj_x < len(matrix[0]) and 0 <= y + adj_y < len(matrix):
                                    matrix[y + adj_y][x + adj_x] = 1

                        if 0 <= x < len(matrix[0]) and 0 <= y < len(matrix):
                            matrix[y][x] = 1

            while len(paths) > 0:
                if point_a is None:
                    point_a = paths.pop()
                self.set_seed()
                index = random.randint(0, len(paths)-1)
                point_b = paths.pop(index)
                generate_snake_path(maze, point_a, point_b)
                point_a = point_b
            
            self.grid = maze
    
    def delete_invalid_sprites(self):
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                if self.grid[y][x] == 1:
                    continue
                conditions = []
                if x > 0 and self.grid[y][x-1] == 1:
                    conditions.append('left')
                if x < len(self.grid[y])-1 and self.grid[y][x+1] == 1:
                    conditions.append('right')
                if y > 0 and self.grid[y-1][x] == 1:
                    conditions.append('top')
                if y < len(self.grid)-1 and self.grid[y+1][x] == 1:
                    conditions.append('bottom')
                
                if len(conditions) > 2:
                    self.grid[y][x] = 1

                top = 'top' in conditions
                right = 'right' in conditions
                bottom = 'bottom' in conditions
                left = 'left' in conditions
                
                if len(conditions) == 2:
                    if left and right:
                        self.grid[y][x] = 1
                        continue
                    if top and bottom:
                        self.grid[y][x] = 1
                        continue

    def get_conditions(self, x, y):
        conditions = []
        if x > 0 and self.grid[y][x-1] == 1:
            conditions.append('left')
        if x < len(self.grid[y]) - 1 and self.grid[y][x+1] == 1:
            conditions.append('right')
        if y > 0 and self.grid[y-1][x] == 1:
            conditions.append('top')
        if y < len(self.grid) - 1 and self.grid[y+1][x] == 1:
            conditions.append('bottom')
        return conditions

    def scan_sprites(self):
        for y in range(len(self.grid)):
            row = self.grid[y]
            for x in range(len(row)):
                if row[x] == 1:
                    continue

                conditions = self.get_conditions(x, y)

                top, right, bottom, left = 'top' in conditions, 'right' in conditions, 'bottom' in conditions, 'left' in conditions

                if len(conditions) == 2:
                    if left and right or top and bottom:
                        self.grid[y][x] = 1
                        continue

                    if top and left:
                        self.grid[y][x] = 7
                    if top and right:
                        self.grid[y][x] = 6
                    if bottom and left:
                        self.grid[y][x] = 9
                    if bottom and right:
                        self.grid[y][x] = 8

                elif len(conditions) == 1:
                    if top:
                        self.grid[y][x] = 2
                    if bottom:
                        self.grid[y][x] = 3
                    if right:
                        self.grid[y][x] = 4
                    if left:
                        self.grid[y][x] = 5

    def place_reverse_corners(self):
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                if self.grid[y][x] != 0:
                    continue
                conditions = []
                if x > 0 and self.grid[y][x-1] not in [1,0]:
                    conditions.append('left')
                if x < len(self.grid[y])-1 and self.grid[y][x+1] not in [1 ,0]:
                    conditions.append('right')
                if y > 0 and self.grid[y-1][x] not in [1,0]:
                    conditions.append('top')
                if y < len(self.grid)-1 and self.grid[y+1][x] not in [1,0]:
                    conditions.append('bottom')

                top = 'top' in conditions
                right = 'right' in conditions
                bottom = 'bottom' in conditions
                left = 'left' in conditions

                if top and left and self.grid[y-1][x-1] == 1:
                    self.grid[y][x] = 12
                if top and right and self.grid[y-1][x+1] == 1:
                    self.grid[y][x] = 13
                if bottom and right and self.grid[y+1][x+1] == 1:
                    self.grid[y][x] = 11
                if bottom and left and self.grid[y+1][x-1] == 1:
                    self.grid[y][x] = 10

    def refine_paths(self):
        self.delete_invalid_sprites()
        self.scan_sprites()
        self.place_reverse_corners()

        self.delete_invalid_sprites()
        self.scan_sprites()
        self.place_reverse_corners()

    def place_entities(self, entityTypes, group_length=2, step_callback=None):
        entities = []
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                if self.grid[y][x] != 1:
                    continue
                self.set_seed()
                if (
                    self.grid[y][x] in self.voids
                    and y < len(self.grid)-1
                    and self.grid[y+1][x] == 2
                    and probability_in_range(self, 0, len(self.grid)-1, y)
                ):
                    length = random.randint(1, group_length)
                    level = self.get_level_by_height(y)
                    for i in range(length):
                        self.set_seed()
                        pos = random.randint(-4, 4)
                        self.set_seed()
                        Entity = random.choice(entityTypes)
                        entity = Entity(level=level)
                        entity.x = x * self.width + pos
                        entity.y = (y-i) * self.height
                        entities.append(entity)
                        if step_callback:
                            step_callback()
        return entities
    
    def get_level_by_height(self, height):
        base_level = int((height / 1000) * 100)

        base_level = min(base_level, 100)

        min_level = max(base_level - 5, 1)
        max_level = min(base_level + 5, 100)
        self.set_seed()
        level_variation = random.randint(min_level, max_level)
        return level_variation

def probability_in_range(self, min_val: int, max_val: int, value: int):
    normalized = (value - min_val) / (max_val - min_val)
    probability = 0.1 * (1 - normalized)
    seed = self.seed
    random.seed(None)
    is_probable = random.random() < probability
    random.seed(seed)
    return is_probable