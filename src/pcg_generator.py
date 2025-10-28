import random
from typing import Any

TILE_WALL = 0
TILE_FLOOR = 1


class Rect:
    def __init__(self, x: int, y: int, w: int, h: int) -> None:
        self.x1: int = x
        self.y1: int = y
        self.x2: int = x + w
        self.y2: int = y + h

    def center(self) -> tuple[int, int]:
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)
        return (center_x, center_y)

    def intersects(self, other: Any) -> bool:
        margin = 1
        return (self.x1 <= other.x2 + margin and self.x2 >= other.x1 - margin and
                self.y1 <= other.y2 + margin and self.y2 >= other.y1 - margin)


def create_room(grid: list[list[int]], room: Rect) -> None:
    map_height: int = len(grid)
    map_width: int = len(grid[0])
    for y in range(max(1, room.y1), min(map_height - 1, room.y2)):  # Avoid carving edges
        for x in range(max(1, room.x1), min(map_width - 1, room.x2)):
            if 1 <= y < map_height - 1 and 1 <= x < map_width - 1:
                grid[y][x] = TILE_FLOOR


def create_h_tunnel(grid: list[list[int]], x1: int, x2: int, y: int, width: int = 1) -> None:
    map_height: int = len(grid)
    map_width: int = len(grid[0])
    for x in range(min(x1, x2), max(x1, x2) + 1):
        for i in range(width):
            tunnel_y: int = y + i - (width // 2)
            # Stay away from map edges slightly for tunnels
            if 1 <= tunnel_y < map_height - 1 and 1 <= x < map_width - 1:
                grid[tunnel_y][x] = TILE_FLOOR


def create_v_tunnel(grid: list[list[int]], y1: int, y2: int, x: int, width: int = 1) -> None:
    # ... (Keep implementation as before) ...
    map_height: int = len(grid)
    map_width: int = len(grid[0])
    for y in range(min(y1, y2), max(y1, y2) + 1):
        for i in range(width):
            tunnel_x: int = x + i - (width // 2)
            # Stay away from map edges slightly for tunnels
            if 1 <= y < map_height - 1 and 1 <= tunnel_x < map_width - 1:
                grid[y][tunnel_x] = TILE_FLOOR


# --- NEW: Drunkard's Walk Implementation ---
def generate_drunkards_walk(config: dict[str, Any]) -> list[list[int]]:
    """ Generates a cave/maze grid using the Drunkard's Walk algorithm. """
    layout_conf: dict[str, Any] = config['layout']
    drunkard_conf = layout_conf['drunkard_params']

    width: int = layout_conf['map_width']
    height: int = layout_conf['map_height']
    grid: list[list[int]] = [
        [TILE_WALL for _ in range(width)] for _ in range(height)]

    # Calculate target steps based on percentage
    total_tiles: int = width * height
    target_floor_tiles = int(
        total_tiles * drunkard_conf['target_floor_percent'])

    # Determine start position
    if drunkard_conf['start_pos'] == "center":
        current_x: int = width // 2
        current_y: int = height // 2
    elif drunkard_conf['start_pos'] == "random":
        current_x = random.randint(1, width - 2)
        current_y = random.randint(1, height - 2)
    else:  # Assume specific coordinates if provided (add error checking later)
        current_x, current_y = drunkard_conf['start_pos']
        current_x = max(1, min(width - 2, current_x))  # Clamp to valid bounds
        current_y = max(1, min(height - 2, current_y))

    floor_tiles_created = 0

    # Store previous direction for bias (0:N, 1:E, 2:S, 3:W)
    last_direction: int = random.randint(0, 3)
    directions: list[tuple[int, int]] = [
        (0, -1), (1, 0), (0, 1), (-1, 0)]  # N, E, S, W coordinate changes

    while floor_tiles_created < target_floor_tiles:
        # Carve current position if it's a wall
        if grid[current_y][current_x] == TILE_WALL:
            grid[current_y][current_x] = TILE_FLOOR
            floor_tiles_created += 1

        # Determine next direction
        straight_bias: float = drunkard_conf['straight_bias']
        if random.random() < straight_bias:
            # Try to continue straight
            chosen_direction = last_direction
        else:
            # Choose a new random direction (could be same as last)
            chosen_direction = random.randint(0, 3)

        # Get potential new coordinates
        dx, dy = directions[chosen_direction]
        next_x: int = current_x + dx
        next_y: int = current_y + dy

        # Boundary Check: Stay within 1 tile of the edge
        if 1 <= next_x < width - 1 and 1 <= next_y < height - 1:
            current_x = next_x
            current_y = next_y
            last_direction = chosen_direction
        else:
            # Hit boundary (or near boundary), choose a completely new random direction next time
            last_direction = random.randint(0, 3)
            # Optional: Could try turning instead of picking totally random,
            # or could stop if stuck too long. For now, just pick new direction.

    return grid


# --- MODIFIED: Main Dispatcher Function ---
def generate_level(config: dict[Any, Any]) -> list[list[int]]:
    """ 
    Generates a level grid based on the algorithm specified in the config.
    Acts as a dispatcher to different generation functions.
    """
    algorithm: str = config.get(
        'algorithm', 'random_room_placement')  # Default if key missing

    if algorithm == 'random_room_placement':
        # Call the original function (renamed)
        return generate_random_rooms(config)
    elif algorithm == 'drunkards_walk':
        return generate_drunkards_walk(config)
    # --- Add calls to other algorithms like BSP Tree or Cellular Automata here ---
    # elif algorithm == 'bsp_tree':
    #    return generate_bsp(config)
    else:
        print(
            f"Warning: Unknown algorithm '{algorithm}'. Using default random_room_placement.")
        return generate_random_rooms(config)


# --- RENAMED: Original Room Placement Function ---
def generate_random_rooms(config: dict[Any, Any]) -> list[list[int]]:
    """ Generates a dungeon level grid using random room placement. """
    # --- (Implementation is exactly the same as the previous generate_level) ---
    layout_conf: dict[str, Any] = config['layout']
    width: int = layout_conf['map_width']
    height: int = layout_conf['map_height']
    grid: list[list[int]] = [
        [TILE_WALL for _ in range(width)] for _ in range(height)]
    rooms: list[Rect] = []
    num_rooms = 0
    # ... (Rest of the room placement and corridor connection logic) ...
    max_rooms: int = layout_conf['max_rooms']
    room_min_size: int = layout_conf['room_size_min']
    room_max_size: int = layout_conf['room_size_max']

    for _ in range(max_rooms * 2):
        if num_rooms >= max_rooms:
            break
        w: int = random.randint(room_min_size, room_max_size)
        h: int = random.randint(room_min_size, room_max_size)
        x: int = random.randint(1, width - w - 2)  # Keep rooms away from edge
        y: int = random.randint(1, height - h - 2)
        new_room = Rect(x, y, w, h)
        failed = False
        for other_room in rooms:
            if new_room.intersects(other_room):
                failed = True
                break
        if not failed:
            create_room(grid, new_room)
            (new_x, new_y) = new_room.center()
            rooms.append(new_room)
            num_rooms += 1

    corridor_width: int = layout_conf['corridor_width']
    for i in range(1, len(rooms)):
        (prev_x, prev_y) = rooms[i-1].center()
        (new_x, new_y) = rooms[i].center()
        if random.randint(0, 1) == 1:
            create_h_tunnel(grid, prev_x, new_x, prev_y, corridor_width)
            create_v_tunnel(grid, prev_y, new_y, new_x, corridor_width)
        else:
            create_v_tunnel(grid, prev_y, new_y, prev_x, corridor_width)
            create_h_tunnel(grid, prev_x, new_x, new_y, corridor_width)

    return grid
