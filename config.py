import json, math, pygame, os

TYPES = ['player', 'game']
SPRITES_SIZE = 32

class Game():
    save_id = 0
    player_health = 1000,
    player_level = 1
    seed = None
    state = 'menu'
    loading = False
    player_xp = 0

def read_config_json(type = 'game'):
    if not type in TYPES:
        type = 'game'
    file = f"config/{type}.json"
    with open(file, 'r') as f:
        return json.load(f)

def write_config_json(data = {}, type = 'game'):
    if not type in TYPES:
        type = 'game'
    file = f"config/{type}.json"
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

family_size = {
    "player": { "width": 24, "height": 32 },
    "monster": { "width": 24, "height": 24 }
}

def get_entity_size(family="player"):
    size = family_size.get(family, None)
    if size is None:
        size = { "width": 32, "height": 32 }
    width = size.get('width')
    height = size.get('height')
    return width, height

base_stats = {}

def load_entity_configs():
    global base_stats
    entity_dir = "data/entities"
    
    if not os.path.exists(entity_dir):
        raise FileNotFoundError(f"El directorio {entity_dir} no existe.")
    
    for filename in os.listdir(entity_dir):
        if filename.endswith(".json"):
            entity_type = filename[:-5]
            file_path = os.path.join(entity_dir, filename)
            
            with open(file_path, 'r') as f:
                entity_data = json.load(f)
                base_stats[entity_type] = entity_data
load_entity_configs()

def calc_stats(level=1, type="goblin"):
    if type not in base_stats:
        type = 'goblin'
    stats: dict = base_stats.get(type, {})

    resistance = stats.get('resistance', None)
    if resistance is None:
        raise ValueError(f"La resistencia no está definida en el tipo de entidad '{type}'")

    health = stats.get('health', None)
    if health is None:
        raise ValueError(f"Los puntos de vida no han sido definidos para la entidad '{type}'")

    damage = stats.get('damage', None)
    if damage is None:
        raise ValueError(f"El daño no ha sido definido para la entidad '{type}'")

    speed = stats.get('speed', None)
    if speed is None:
        raise ValueError(f"La velocidad no ha sido definida para la entidad '{type}'")

    weight = stats.get('weight', None)
    if weight is None:
        raise ValueError(f"El peso no ha sido definido para la entidad '{type}'")

    damage_range = stats.get('damage_range', None)
    if damage_range is None:
        raise ValueError(f"El rango de daño no ha sido definido para la entidad '{type}'")

    attack_cooldown_time = stats.get('attack_cooldown_time', None)
    if attack_cooldown_time is None:
        raise ValueError(f"El tiempo de recarga de ataque no ha sido definido para la entidad '{type}'")

    detect_entity_range = stats.get('detect_entity_range', None)
    if detect_entity_range is None:
        raise ValueError(f"No se proporcionó el rango de detección de entidades para la entidad '{type}'")
    
    xp_multiplier = stats.get('xp_multiplier', None)
    if xp_multiplier is None:
        raise ValueError(f"No se informó el multiplicador de experiencia en la entidad '{type}'")
    base_health = health
    resistance = calc_resistance(level)
    health = calc_health(health, level)
    damage = calc_damage(damage, resistance, level)

    if level % 10 == 0:
        damage += 5
        health += 100
    
    return health, damage, resistance, speed, weight, damage_range, attack_cooldown_time, detect_entity_range, xp_multiplier, base_health

def font(size: int):
    return pygame.font.Font('font.ttf', size)

def calc_damage(base_damage, resistance, level=1):
    power = 1.8
    damage = base_damage * (1 + resistance ** power)
    return math.ceil(damage)

def calc_health(base_health, level):
    grow_rate = 0.3
    health = base_health * (1 + level ** grow_rate)
    return math.ceil(health)

def calc_resistance(level):
    base_resistance = 1.0
    resistance = base_resistance * (1 + 0.1 * level) if level > 1 else 1
    return resistance

def calculate_required_xp(level=1):
    base_xp = 100
    exponent = 2.3

    return base_xp * (level ** exponent)