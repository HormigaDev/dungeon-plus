import sqlite3, json, random, os
from config import calc_health

conn = sqlite3.connect("database/game.db")
cursor = conn.cursor()

try:
    init_file = 'database/init.sql'

    with open(init_file, 'r') as file:
        init_script = file.read()

    cursor.executescript(init_script)

    conn.commit()
except sqlite3.Error as e:
    print(f"Ocurrió un error: {e}")
    conn.rollback()
    conn.close()
    exit(1)

def save_grid_as_json(grid, grid_id=1):
    grid_json = json.dumps(grid)
    cursor.execute("replace into grids (id, grid_data) values (?, ?)", (grid_id, grid_json))
    conn.commit()

def load_grid_from_json(grid_id=1):
    cursor.execute("select grid_data from grids where id = ?", (grid_id,))
    result = cursor.fetchone()
    if result:
        return json.loads(result[0])
    return None

def read_saves():
    file_path = 'data/saves.json'
    default_content = { "saves_last_id": 0 }
    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open (file_path, 'w') as file:
            json.dump(default_content, file)
        return default_content
    with open (file_path, 'r') as file:
        return json.load(file)

def get_new_id():
    saves_data = read_saves()
    id = saves_data["saves_last_id"]+1
    return id

def set_last_id():
    saves_data = read_saves()
    id = saves_data["saves_last_id"]+1
    saves_data["saves_last_id"] = id
    file_path = 'data/saves.json'
    with open (file_path, 'w') as file:
        json.dump(saves_data, file)

def create_save(save_name):
    id = get_new_id()
    file_path = f"data/saves/{id}.json"
    if os.path.exists(file_path):
        raise ValueError("Ya existe un save con ese nombre")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open (file_path, 'w') as file:
        json.dump({}, file)
    template = {
        "id": id,
        "name": save_name,
        "level": 1,
        "health": 2000,
        "xp": 0,
        "dungeons": [{"name":"CAVERNA DE LOS GOBLINS", "current_floor": 1, "floors": []}],
        "current_dungeon": 1,
    }
    random.seed(None)
    for _ in range(100):
        seed = random.randint(10, 99999)
        template["dungeons"][0]["floors"].append(seed)
    
    with open (file_path, 'w') as file:
        json.dump(template, file)
    set_last_id()
    return id

def get_save_data(save_id):
    file_path = f"data/saves/{save_id}.json"
    with open (file_path, 'r') as file:
        data = json.load(file)
    level = data["level"]
    health = data["health"]
    xp = data["xp"]
    current_dungeon = data["current_dungeon"]-1
    dungeon = data["dungeons"][current_dungeon]
    current_floor = dungeon["current_floor"]-1
    seed = dungeon["floors"][current_floor]

    return level, health, seed, xp

def get_saves():
    directory = "data/saves/"
    results = []
    
    if not os.path.exists(directory):
        return results
    
    for file_name in os.listdir(directory):
        if file_name.endswith(".json"):
            file_path = os.path.join(directory, file_name)
            try:
                with open(file_path, "r") as file:
                    data = json.load(file)
                    if "id" in data and "name" in data:
                        results.append((data["id"], data["name"]))
            except (json.JSONDecodeError, FileNotFoundError):
                continue
    
    return results

def save_game(save_id, level, health, xp):
    file_path = f"data/saves/{save_id}.json"
    with open (file_path, 'r') as file:
        data = json.load(file)
    data["health"] = health
    data["level"] = level
    data["xp"] = xp

    with open (file_path, 'w') as file:
        json.dump(data, file)