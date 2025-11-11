"""
Contains shape objects for creating rooms, and various functions for 
performing PCG of the map (i.e. generate_drunkards_walk(), generate_level(), etc.)
"""
import random
from typing import Any, Self

TILE_WALL = 0
TILE_FLOOR = 1

class Rect:
    """
    Rectangle is a data struct that holds 4 points to represent the corners.

    :param: x: x-position of the top left corner of rectangle
    :param: y: y-position of the top-left corner of rectangle
    :param: w: width of the rectangle
    :param: h: height of the rectangle
    """
    def __init__(self, x: int, y: int, w: int, h: int) -> None:
        self.x1: int = x
        self.y1: int = y
        self.x2: int = x + w
        self.y2: int = y + h

    def center(self) -> tuple[int, int]:
        """
        Calculates the center of the rectangle.

        Returns:
            tuple[int, int]: calculates the center position of the rectangle
        """
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)
        return (center_x, center_y)

    def intersects(self, other: Self) -> bool:
        """Returns True if rectangle is intersecting with another Rectangle

        Args:
            other (Rect): Other rectangle

        Returns:
            bool: True if self is intersecting another rectangle
        """
        margin = 1
        return (self.x1 <= other.x2 + margin and self.x2 >= other.x1 - margin and
                self.y1 <= other.y2 + margin and self.y2 >= other.y1 - margin)
    
    def width(self) -> int:
        """Get rectangle width."""
        return self.x2 - self.x1
    
    def height(self) -> int:
        """Get rectangle height."""
        return self.y2 - self.y1


class BSPNode:
    """Binary Space Partitioning tree node."""
    
    def __init__(self, x: int, y: int, w: int, h: int):
        self.rect = Rect(x, y, w, h)
        self.left: BSPNode | None = None
        self.right: BSPNode | None = None
        self.room: Rect | None = None
    
    def split(self, min_size: int = 8) -> bool:
        """Split this node into two children."""
        if self.left or self.right:
            return False  # Already split
        
        # Determine split direction based on shape
        width = self.rect.width()
        height = self.rect.height()
        
        if width > height and width / height >= 1.25:
            split_horizontally = False
        elif height > width and height / width >= 1.25:
            split_horizontally = True
        else:
            split_horizontally = random.choice([True, False])
        
        # Determine split size
        if split_horizontally:
            max_split = height - min_size
            if max_split <= min_size:
                return False
            split_pos = random.randint(min_size, max_split)
            self.left = BSPNode(self.rect.x1, self.rect.y1, width, split_pos)
            self.right = BSPNode(self.rect.x1, self.rect.y1 + split_pos, width, height - split_pos)
        else:
            max_split = width - min_size
            if max_split <= min_size:
                return False
            split_pos = random.randint(min_size, max_split)
            self.left = BSPNode(self.rect.x1, self.rect.y1, split_pos, height)
            self.right = BSPNode(self.rect.x1 + split_pos, self.rect.y1, width - split_pos, height)
        
        return True


def create_room(grid: list[list[int]], room: Rect) -> None:
    """Creates a room based on a rectangle size.

    Args:
        grid (list[list[int]]): map of the level
        room (Rect): Rectangle representing room dimensions
    """
    map_height: int = len(grid)
    map_width: int = len(grid[0])
    for y in range(max(1, room.y1), min(map_height - 1, room.y2)):  # Avoid carving edges
        for x in range(max(1, room.x1), min(map_width - 1, room.x2)):
            if 1 <= y < map_height - 1 and 1 <= x < map_width - 1:
                grid[y][x] = TILE_FLOOR


def create_h_tunnel(grid: list[list[int]], x1: int, x2: int, y: int, width: int = 1) -> None:
    """Creates a horizontal tunnel

    Args:
        grid (list[list[int]]): map of the level
        x1 (int): _description_
        x2 (int): _description_
        y (int): Length of the tunnel/corridor
        width (int, optional): Width of the tunnel/corridor. Defaults to 1.
    """
    # get the size of the map
    map_height: int = len(grid)
    map_width: int = len(grid[0])
    for x in range(min(x1, x2), max(x1, x2) + 1):
        for i in range(width):
            tunnel_y: int = y + i - (width // 2)
            # Stay away from map edges slightly for tunnels
            if 1 <= tunnel_y < map_height - 1 and 1 <= x < map_width - 1:
                grid[tunnel_y][x] = TILE_FLOOR


def create_v_tunnel(grid: list[list[int]], y1: int, y2: int, x: int, width: int = 1) -> None:
    """Creates a vertical tunnel.

    Args:
        grid (list[list[int]]): map of the level
        x1 (int): _description_
        x2 (int): _description_
        y (int): Length of the tunnel/corridor
        width (int, optional): Width of the tunnel/corridor. Defaults to 1.
    """
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
def smooth_cave(grid: list[list[int]], iterations: int = 1) -> list[list[int]]:
    """Smooth cave walls using cellular automata rules."""
    height = len(grid)
    width = len(grid[0])
    
    for _ in range(iterations):
        new_grid = [row[:] for row in grid]  # Copy grid
        
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                # Count wall neighbors
                wall_count = 0
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        if grid[y + dy][x + dx] == TILE_WALL:
                            wall_count += 1
                
                # If mostly surrounded by walls, become wall; if mostly floor, become floor
                if wall_count >= 5:
                    new_grid[y][x] = TILE_WALL
                elif wall_count <= 3:
                    new_grid[y][x] = TILE_FLOOR
        
        grid = new_grid
    
    return grid


def generate_cellular_automata(config: dict[str, Any]) -> list[list[int]]:
    """Generates natural cave systems using Cellular Automata."""
    layout_conf: dict[str, Any] = config['layout']
    ca_conf = layout_conf.get('cellular_params', {})
    
    width: int = layout_conf['map_width']
    height: int = layout_conf['map_height']
    
    # Get parameters with defaults
    wall_probability = ca_conf.get('initial_wall_probability', 0.45)
    iterations = ca_conf.get('iterations', 5)
    birth_limit = ca_conf.get('birth_limit', 4)  # Become floor if <= this many wall neighbors
    death_limit = ca_conf.get('death_limit', 3)  # Become wall if >= this many wall neighbors
    
    # Initialize with random noise
    grid: list[list[int]] = []
    for y in range(height):
        row = []
        for x in range(width):
            # Keep edges as walls
            if x == 0 or y == 0 or x == width - 1 or y == height - 1:
                row.append(TILE_WALL)
            else:
                # Random initialization
                if random.random() < wall_probability:
                    row.append(TILE_WALL)
                else:
                    row.append(TILE_FLOOR)
        grid.append(row)
    
    # Apply cellular automata rules
    for iteration in range(iterations):
        new_grid = [row[:] for row in grid]
        
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                # Count wall neighbors (8-direction)
                wall_count = 0
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        if grid[y + dy][x + dx] == TILE_WALL:
                            wall_count += 1
                
                # Apply cellular automata rules (4-5 rule)
                if grid[y][x] == TILE_FLOOR:
                    # Floor cell - dies (becomes wall) if too many wall neighbors
                    if wall_count >= 5:
                        new_grid[y][x] = TILE_WALL
                else:
                    # Wall cell - becomes floor if few wall neighbors
                    if wall_count <= 4:
                        new_grid[y][x] = TILE_FLOOR
        
        grid = new_grid
    
    # Remove isolated areas to ensure connectivity
    grid = remove_isolated_areas(grid)
    
    return grid


def add_pillars_to_large_areas(grid: list[list[int]]) -> list[list[int]]:
    """Add pillars to large open areas for more interesting topology."""
    height = len(grid)
    width = len(grid[0])
    
    # Find large open areas (5x5 floor regions)
    for y in range(3, height - 3, 4):
        for x in range(3, width - 3, 4):
            # Check if we're in a large floor region
            floor_count = 0
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    if grid[y + dy][x + dx] == TILE_FLOOR:
                        floor_count += 1
            
            # If very open, add a pillar with 40% chance
            if floor_count >= 20 and random.random() < 0.4:
                # Create 2x2 pillar
                for dy in range(2):
                    for dx in range(2):
                        if 1 <= y + dy < height - 1 and 1 <= x + dx < width - 1:
                            grid[y + dy][x + dx] = TILE_WALL
    
    return grid


def generate_drunkards_walk(config: dict[str, Any]) -> list[list[int]]:
    """Generates interesting cave structures using multiple drunkards."""
    layout_conf: dict[str, Any] = config['layout']
    drunkard_conf = layout_conf['drunkard_params']

    width: int = layout_conf['map_width']
    height: int = layout_conf['map_height']
    grid: list[list[int]] = [
        [TILE_WALL for _ in range(width)] for _ in range(height)]

    total_tiles: int = width * height
    target_floor_tiles = int(total_tiles * drunkard_conf['target_floor_percent'])

    # Determine start position
    if drunkard_conf['start_pos'] == "center":
        start_x: int = width // 2
        start_y: int = height // 2
    elif drunkard_conf['start_pos'] == "random":
        start_x = random.randint(width // 4, 3 * width // 4)
        start_y = random.randint(height // 4, 3 * height // 4)
    else:
        start_x, start_y = drunkard_conf['start_pos']
        start_x = max(1, min(width - 2, start_x))
        start_y = max(1, min(height - 2, start_y))

    directions: list[tuple[int, int]] = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    straight_bias: float = drunkard_conf['straight_bias']
    
    # Adjust number of drunkards based on target floor percentage
    # Low floor % (< 0.30) = tight maze with fewer drunkards
    # High floor % (>= 0.30) = open caves with more drunkards
    target_percent = drunkard_conf['target_floor_percent']
    if target_percent < 0.30:
        num_drunkards = 1 + random.randint(0, 1)  # 1-2 drunkards for tight mazes
    else:
        num_drunkards = 3 + random.randint(0, 2)  # 3-5 drunkards for open caves
    
    tiles_per_drunkard = target_floor_tiles // num_drunkards
    
    for drunkard_num in range(num_drunkards):
        # Each drunkard starts from the main area or random nearby
        if drunkard_num == 0:
            current_x, current_y = start_x, start_y
        else:
            # Start from an existing floor tile
            floor_tiles = [(x, y) for y in range(height) for x in range(width) if grid[y][x] == TILE_FLOOR]
            if floor_tiles:
                current_x, current_y = random.choice(floor_tiles)
            else:
                current_x, current_y = start_x, start_y
        
        last_direction: int = random.randint(0, 3)
        drunkard_tiles = 0
        
        while drunkard_tiles < tiles_per_drunkard:
            # Carve with single tiles (no 2x2, keeps passages narrow)
            if grid[current_y][current_x] == TILE_WALL:
                grid[current_y][current_x] = TILE_FLOOR
                drunkard_tiles += 1
            
            if drunkard_tiles >= tiles_per_drunkard:
                break
            
            # Direction selection
            if random.random() < straight_bias:
                chosen_direction = last_direction
            else:
                chosen_direction = random.randint(0, 3)
            
            # Move
            dx, dy = directions[chosen_direction]
            next_x = current_x + dx
            next_y = current_y + dy
            
            if 1 <= next_x < width - 1 and 1 <= next_y < height - 1:
                current_x = next_x
                current_y = next_y
                last_direction = chosen_direction
            else:
                # Hit wall, turn randomly
                last_direction = random.randint(0, 3)

    # Only smooth and add pillars for higher floor percentages
    # Tight mazes (< 30% floor) stay raw for that maze feel
    if target_percent >= 0.30:
        # Light smoothing for caves
        grid = smooth_cave(grid, iterations=1)
        # Add pillars to any large open areas
        grid = add_pillars_to_large_areas(grid)
    
    # Always remove isolated areas
    grid = remove_isolated_areas(grid)

    return grid


def generate_bsp(config: dict[str, Any]) -> list[list[int]]:
    """Generates a dungeon using Binary Space Partitioning."""
    layout_conf: dict[str, Any] = config['layout']
    width: int = layout_conf['map_width']
    height: int = layout_conf['map_height']
    
    grid: list[list[int]] = [[TILE_WALL for _ in range(width)] for _ in range(height)]
    
    # Create root node spanning entire map
    root = BSPNode(1, 1, width - 2, height - 2)
    
    # Recursively split the space
    nodes_to_split = [root]
    all_nodes = [root]
    
    max_depth = 4  # Control subdivision depth
    for depth in range(max_depth):
        next_nodes = []
        for node in nodes_to_split:
            if node.split(min_size=8):
                if node.left:
                    next_nodes.append(node.left)
                    all_nodes.append(node.left)
                if node.right:
                    next_nodes.append(node.right)
                    all_nodes.append(node.right)
        nodes_to_split = next_nodes
        if not nodes_to_split:
            break
    
    # Create rooms in leaf nodes
    leaf_nodes = [node for node in all_nodes if not node.left and not node.right]
    
    for node in leaf_nodes:
        # Create a room within this partition (with some margin)
        rect = node.rect
        room_w = random.randint(rect.width() // 2, max(rect.width() - 2, rect.width() // 2 + 1))
        room_h = random.randint(rect.height() // 2, max(rect.height() - 2, rect.height() // 2 + 1))
        
        room_x = rect.x1 + random.randint(1, max(1, rect.width() - room_w - 1))
        room_y = rect.y1 + random.randint(1, max(1, rect.height() - room_h - 1))
        
        node.room = Rect(room_x, room_y, room_w, room_h)
        create_room(grid, node.room)
    
    # Connect sibling rooms
    def connect_siblings(node: BSPNode) -> None:
        """Recursively connect sibling nodes."""
        if node.left and node.right:
            connect_siblings(node.left)
            connect_siblings(node.right)
            
            # Get rooms from left and right subtrees
            left_room = get_room_from_subtree(node.left)
            right_room = get_room_from_subtree(node.right)
            
            if left_room and right_room:
                lx, ly = left_room.center()
                rx, ry = right_room.center()
                
                corridor_width = layout_conf.get('corridor_width', 1)
                
                # Create L-shaped corridor
                if random.choice([True, False]):
                    create_h_tunnel(grid, lx, rx, ly, corridor_width)
                    create_v_tunnel(grid, ly, ry, rx, corridor_width)
                else:
                    create_v_tunnel(grid, ly, ry, lx, corridor_width)
                    create_h_tunnel(grid, lx, rx, ry, corridor_width)
    
    def get_room_from_subtree(node: BSPNode) -> Rect | None:
        """Get a room from this node or its children."""
        if node.room:
            return node.room
        if node.left:
            room = get_room_from_subtree(node.left)
            if room:
                return room
        if node.right:
            return get_room_from_subtree(node.right)
        return None
    
    connect_siblings(root)
    
    return grid


# --- MODIFIED: Main Dispatcher Function ---
def generate_hybrid_rooms_caves(config: dict[str, Any]) -> list[list[int]]:
    """
    Hybrid: Structured rooms connected by organic winding passages.
    Combines BSP room placement with drunkard's walk corridors.
    """
    layout_conf: dict[str, Any] = config['layout']
    width: int = layout_conf['map_width']
    height: int = layout_conf['map_height']
    
    grid: list[list[int]] = [[TILE_WALL for _ in range(width)] for _ in range(height)]
    
    # 1. Generate rooms using BSP (but smaller to leave space for organic corridors)
    root = BSPNode(1, 1, width - 2, height - 2)
    nodes_to_split = [root]
    all_nodes = [root]
    
    for depth in range(3):  # Less depth for fewer, larger partitions
        next_nodes = []
        for node in nodes_to_split:
            if node.split(min_size=10):
                if node.left:
                    next_nodes.append(node.left)
                    all_nodes.append(node.left)
                if node.right:
                    next_nodes.append(node.right)
                    all_nodes.append(node.right)
        nodes_to_split = next_nodes
    
    # Create rooms
    leaf_nodes = [node for node in all_nodes if not node.left and not node.right]
    rooms = []
    
    for node in leaf_nodes:
        rect = node.rect
        # Larger rooms for better floor coverage
        room_w = random.randint(rect.width() // 2, (rect.width() * 3) // 4)
        room_h = random.randint(rect.height() // 2, (rect.height() * 3) // 4)
        room_x = rect.x1 + (rect.width() - room_w) // 2
        room_y = rect.y1 + (rect.height() - room_h) // 2
        
        room = Rect(room_x, room_y, room_w, room_h)
        create_room(grid, room)
        rooms.append(room)
    
    # 2. Connect rooms with organic drunkard's walk corridors
    for i in range(len(rooms) - 1):
        start_x, start_y = rooms[i].center()
        end_x, end_y = rooms[i + 1].center()
        
        # Drunkard walks from room i to room i+1
        current_x, current_y = start_x, start_y
        target_reached = False
        max_steps = width * height  # Prevent infinite loops
        steps = 0
        
        while not target_reached and steps < max_steps:
            grid[current_y][current_x] = TILE_FLOOR
            
            # Check if reached target
            if abs(current_x - end_x) <= 2 and abs(current_y - end_y) <= 2:
                target_reached = True
                break
            
            # Bias movement toward target
            dx = 1 if current_x < end_x else (-1 if current_x > end_x else 0)
            dy = 1 if current_y < end_y else (-1 if current_y > end_y else 0)
            
            # 70% move toward target, 30% random wander
            if random.random() < 0.7 and (dx != 0 or dy != 0):
                if dx != 0 and dy != 0:
                    # Choose x or y movement
                    if random.choice([True, False]):
                        next_x, next_y = current_x + dx, current_y
                    else:
                        next_x, next_y = current_x, current_y + dy
                elif dx != 0:
                    next_x, next_y = current_x + dx, current_y
                else:
                    next_x, next_y = current_x, current_y + dy
            else:
                # Random wander
                direction = random.choice([(0, -1), (1, 0), (0, 1), (-1, 0)])
                next_x, next_y = current_x + direction[0], current_y + direction[1]
            
            # Bounds check
            if 1 <= next_x < width - 1 and 1 <= next_y < height - 1:
                current_x, current_y = next_x, next_y
            
            steps += 1
    
    return grid


def generate_cellular_rooms(config: dict[str, Any]) -> list[list[int]]:
    """
    Hybrid: Cellular automata with hand-placed room seeds.
    Creates natural-looking caves with distinct chamber areas.
    """
    layout_conf: dict[str, Any] = config['layout']
    width: int = layout_conf['map_width']
    height: int = layout_conf['map_height']
    
    # Initialize with noise
    grid: list[list[int]] = []
    for y in range(height):
        row = []
        for x in range(width):
            if x == 0 or y == 0 or x == width - 1 or y == height - 1:
                row.append(TILE_WALL)
            else:
                row.append(TILE_WALL if random.random() < 0.58 else TILE_FLOOR)
        grid.append(row)
    
    # Seed some guaranteed open areas (rooms)
    num_seeds = random.randint(4, 7)
    for _ in range(num_seeds):
        seed_x = random.randint(width // 4, 3 * width // 4)
        seed_y = random.randint(height // 4, 3 * height // 4)
        seed_size = random.randint(3, 5)
        
        # Create small guaranteed floor area
        for dy in range(seed_size):
            for dx in range(seed_size):
                sx, sy = seed_x + dx, seed_y + dy
                if 1 <= sx < width - 1 and 1 <= sy < height - 1:
                    grid[sy][sx] = TILE_FLOOR
    
    # Apply cellular automata
    for _ in range(5):
        new_grid = [row[:] for row in grid]
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                wall_count = sum([
                    grid[y+dy][x+dx] == TILE_WALL
                    for dy in [-1, 0, 1] for dx in [-1, 0, 1]
                    if not (dx == 0 and dy == 0)
                ])
                
                if grid[y][x] == TILE_FLOOR:
                    if wall_count >= 5:
                        new_grid[y][x] = TILE_WALL
                else:
                    if wall_count <= 4:
                        new_grid[y][x] = TILE_FLOOR
        grid = new_grid
    
    grid = remove_isolated_areas(grid)
    return grid


def generate_level(config: dict[Any, Any]) -> list[list[int]]:
    """ 
    Generates a level grid based on the algorithm specified in the config.
    Acts as a dispatcher to different generation functions.
    """
    algorithm: str = config.get('algorithm', 'random_room_placement')

    if algorithm == 'random_room_placement':
        return generate_random_rooms(config)
    elif algorithm == 'drunkards_walk':
        return generate_drunkards_walk(config)
    elif algorithm == 'bsp':
        return generate_bsp(config)
    elif algorithm == 'cellular_automata':
        return generate_cellular_automata(config)
    elif algorithm == 'hybrid_rooms_caves':
        return generate_hybrid_rooms_caves(config)
    elif algorithm == 'cellular_rooms':
        return generate_cellular_rooms(config)
    else:
        print(
            f"Warning: Unknown algorithm '{algorithm}'. Using default random_room_placement.")
        return generate_random_rooms(config)


# --- RENAMED: Original Room Placement Function ---
def distance(room1: Rect, room2: Rect) -> float:
    """Calculate distance between two room centers."""
    c1_x, c1_y = room1.center()
    c2_x, c2_y = room2.center()
    return ((c1_x - c2_x) ** 2 + (c1_y - c2_y) ** 2) ** 0.5


def find_nearest_unconnected_room(room: Rect, rooms: list[Rect], connected: set[int], current_idx: int) -> int | None:
    """Find the nearest room that isn't connected yet."""
    nearest_dist = float('inf')
    nearest_idx = None
    
    for i, other_room in enumerate(rooms):
        if i != current_idx and i not in connected:
            dist = distance(room, other_room)
            if dist < nearest_dist:
                nearest_dist = dist
                nearest_idx = i
    
    return nearest_idx


def remove_isolated_areas(grid: list[list[int]]) -> list[list[int]]:
    """Remove small isolated floor regions using flood fill."""
    height = len(grid)
    width = len(grid[0])
    visited = [[False for _ in range(width)] for _ in range(height)]
    
    def flood_fill(start_x: int, start_y: int) -> int:
        """Flood fill and return area size."""
        stack = [(start_x, start_y)]
        area_tiles = []
        
        while stack:
            x, y = stack.pop()
            if visited[y][x] or grid[y][x] == TILE_WALL:
                continue
            
            visited[y][x] = True
            area_tiles.append((x, y))
            
            # Check 4 directions
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height and not visited[ny][nx]:
                    stack.append((nx, ny))
        
        return len(area_tiles), area_tiles
    
    # Find all connected regions
    regions = []
    for y in range(height):
        for x in range(width):
            if grid[y][x] == TILE_FLOOR and not visited[y][x]:
                size, tiles = flood_fill(x, y)
                regions.append((size, tiles))
    
    # Keep only the largest region, fill others with walls
    if regions:
        regions.sort(reverse=True, key=lambda r: r[0])
        largest_region = set(regions[0][1])
        
        for y in range(height):
            for x in range(width):
                if grid[y][x] == TILE_FLOOR and (x, y) not in largest_region:
                    grid[y][x] = TILE_WALL
    
    return grid


def generate_random_rooms(config: dict[Any, Any]) -> list[list[int]]:
    """Generates a dungeon level grid using random room placement with improved connectivity."""
    layout_conf: dict[str, Any] = config['layout']
    width: int = layout_conf['map_width']
    height: int = layout_conf['map_height']
    grid: list[list[int]] = [
        [TILE_WALL for _ in range(width)] for _ in range(height)]
    rooms: list[Rect] = []
    num_rooms = 0
    max_rooms: int = layout_conf['max_rooms']
    room_min_size: int = layout_conf['room_size_min']
    room_max_size: int = layout_conf['room_size_max']

    # Generate rooms with better attempts
    for _ in range(max_rooms * 3):
        if num_rooms >= max_rooms:
            break
        w: int = random.randint(room_min_size, room_max_size)
        h: int = random.randint(room_min_size, room_max_size)
        x: int = random.randint(1, width - w - 2)
        y: int = random.randint(1, height - h - 2)
        new_room = Rect(x, y, w, h)
        
        # Check if overlaps with existing rooms
        failed = False
        for other_room in rooms:
            if new_room.intersects(other_room):
                failed = True
                break
        
        if not failed:
            create_room(grid, new_room)
            rooms.append(new_room)
            num_rooms += 1

    if not rooms:
        return grid

    # Improved connectivity: connect each room to nearest unconnected room
    corridor_width: int = layout_conf['corridor_width']
    connected: set[int] = {0}  # First room is connected
    
    for i in range(1, len(rooms)):
        # Find nearest connected room
        nearest_dist = float('inf')
        nearest_idx = 0
        
        for j in connected:
            dist = distance(rooms[i], rooms[j])
            if dist < nearest_dist:
                nearest_dist = dist
                nearest_idx = j
        
        # Connect to nearest connected room
        (prev_x, prev_y) = rooms[nearest_idx].center()
        (new_x, new_y) = rooms[i].center()
        
        if random.randint(0, 1) == 1:
            create_h_tunnel(grid, prev_x, new_x, prev_y, corridor_width)
            create_v_tunnel(grid, prev_y, new_y, new_x, corridor_width)
        else:
            create_v_tunnel(grid, prev_y, new_y, prev_x, corridor_width)
            create_h_tunnel(grid, prev_x, new_x, new_y, corridor_width)
        
        connected.add(i)
    
    # Add some extra connections for loops (more interesting gameplay)
    extra_connections = min(3, len(rooms) // 4)
    for _ in range(extra_connections):
        if len(rooms) < 2:
            break
        room1_idx = random.randint(0, len(rooms) - 1)
        room2_idx = random.randint(0, len(rooms) - 1)
        
        if room1_idx != room2_idx:
            (x1, y1) = rooms[room1_idx].center()
            (x2, y2) = rooms[room2_idx].center()
            create_h_tunnel(grid, x1, x2, y1, corridor_width)
            create_v_tunnel(grid, y1, y2, x2, corridor_width)
    
    # Clean up isolated areas
    grid = remove_isolated_areas(grid)
    
    return grid
