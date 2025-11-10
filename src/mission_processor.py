"""
Mission processor - places objectives in generated levels according to mission design.
"""
from typing import Any
import random


TILE_WALL = 0
TILE_FLOOR = 1


def find_rooms(grid: list[list[int]]) -> list[dict[str, Any]]:
    """
    Find distinct rooms in the level using flood fill.
    Returns list of rooms with their properties.
    """
    height = len(grid)
    width = len(grid[0])
    visited = [[False] * width for _ in range(height)]
    rooms = []
    
    def flood_fill(start_x: int, start_y: int) -> list[tuple[int, int]]:
        """Flood fill to find connected floor tiles."""
        tiles = []
        stack = [(start_x, start_y)]
        
        while stack:
            x, y = stack.pop()
            if x < 0 or x >= width or y < 0 or y >= height:
                continue
            if visited[y][x] or grid[y][x] == TILE_WALL:
                continue
            
            visited[y][x] = True
            tiles.append((x, y))
            
            # Add neighbors
            stack.extend([(x+1, y), (x-1, y), (x, y+1), (x, y-1)])
        
        return tiles
    
    # Find all rooms
    for y in range(height):
        for x in range(width):
            if grid[y][x] == TILE_FLOOR and not visited[y][x]:
                tiles = flood_fill(x, y)
                if len(tiles) >= 4:  # Minimum room size
                    # Calculate room center
                    avg_x = sum(t[0] for t in tiles) / len(tiles)
                    avg_y = sum(t[1] for t in tiles) / len(tiles)
                    
                    rooms.append({
                        'tiles': tiles,
                        'size': len(tiles),
                        'center': (int(avg_x), int(avg_y)),
                        'min_x': min(t[0] for t in tiles),
                        'max_x': max(t[0] for t in tiles),
                        'min_y': min(t[1] for t in tiles),
                        'max_y': max(t[1] for t in tiles),
                    })
    
    return rooms


def calculate_distances_from_start(grid: list[list[int]], start_pos: tuple[int, int]) -> dict[tuple[int, int], int]:
    """
    Calculate distances from start position to all reachable floor tiles using BFS.
    Returns dict mapping (x,y) -> distance.
    """
    height = len(grid)
    width = len(grid[0])
    distances = {}
    queue = [(start_pos, 0)]
    visited = set()
    
    while queue:
        (x, y), dist = queue.pop(0)
        
        if (x, y) in visited:
            continue
        if x < 0 or x >= width or y < 0 or y >= height:
            continue
        if grid[y][x] == TILE_WALL:
            continue
        
        visited.add((x, y))
        distances[(x, y)] = dist
        
        # Add neighbors
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            queue.append(((x+dx, y+dy), dist+1))
    
    return distances


def find_dead_ends(grid: list[list[int]]) -> list[tuple[int, int]]:
    """Find dead-end locations (floor tiles with only one floor neighbor)."""
    height = len(grid)
    width = len(grid[0])
    dead_ends = []
    
    for y in range(1, height-1):
        for x in range(1, width-1):
            if grid[y][x] == TILE_FLOOR:
                # Count floor neighbors
                neighbors = 0
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    if grid[y+dy][x+dx] == TILE_FLOOR:
                        neighbors += 1
                
                if neighbors == 1:  # Dead end
                    dead_ends.append((x, y))
    
    return dead_ends


def place_objectives(grid: list[list[int]], mission: dict[str, Any]) -> dict[str, Any]:
    """
    Place objectives in the level according to mission design.
    Returns dict with objective placements and metadata.
    """
    height = len(grid)
    width = len(grid[0])
    
    # Find start position (first floor tile from top-left)
    start_pos = None
    for y in range(height):
        for x in range(width):
            if grid[y][x] == TILE_FLOOR:
                start_pos = (x, y)
                break
        if start_pos:
            break
    
    if not start_pos:
        return {"error": "No floor tiles found", "placements": []}
    
    # Analyze level structure
    rooms = find_rooms(grid)
    distances = calculate_distances_from_start(grid, start_pos)
    dead_ends = find_dead_ends(grid)
    
    if not rooms:
        return {"error": "No rooms found", "placements": []}
    
    # Sort rooms by size for easy access
    rooms_by_size = sorted(rooms, key=lambda r: r['size'], reverse=True)
    
    # Find furthest points
    furthest_tiles = sorted(distances.items(), key=lambda item: item[1], reverse=True)
    
    placements = []
    used_positions = set()
    
    # Process each objective
    for obj in mission.get('objectives', []):
        obj_type = obj['objective_type']
        placement_rule = obj['placement_rule']
        count = obj['count']
        description = obj['description']
        
        for i in range(count):
            position = None
            
            if placement_rule == "end_of_longest_path":
                # Place at furthest reachable point
                for (x, y), dist in furthest_tiles:
                    if (x, y) not in used_positions:
                        position = (x, y)
                        used_positions.add(position)
                        break
            
            elif placement_rule == "dead_end":
                # Place in dead ends
                available_dead_ends = [de for de in dead_ends if de not in used_positions]
                if available_dead_ends:
                    position = random.choice(available_dead_ends)
                    used_positions.add(position)
            
            elif placement_rule == "central_room":
                # Place in largest room
                for room in rooms_by_size:
                    candidates = [t for t in room['tiles'] if t not in used_positions]
                    if candidates:
                        position = random.choice(candidates)
                        used_positions.add(position)
                        break
            
            elif placement_rule == "hidden":
                # Place in corners or hard-to-see locations
                corners = []
                for room in rooms:
                    # Find corner tiles (2+ wall neighbors)
                    for x, y in room['tiles']:
                        if (x, y) in used_positions:
                            continue
                        wall_neighbors = 0
                        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                            if grid[y+dy][x+dx] == TILE_WALL:
                                wall_neighbors += 1
                        if wall_neighbors >= 2:
                            corners.append((x, y))
                
                if corners:
                    position = random.choice(corners)
                    used_positions.add(position)
            
            elif placement_rule == "checkpoint":
                # Place at medium distance
                mid_distance = max(distances.values()) // 2 if distances else 0
                candidates = [(pos, dist) for pos, dist in distances.items() 
                             if abs(dist - mid_distance) < 5 and pos not in used_positions]
                if candidates:
                    position = random.choice(candidates)[0]
                    used_positions.add(position)
            
            elif placement_rule == "random_room":
                # Random room placement
                available_rooms = [r for r in rooms if any(t not in used_positions for t in r['tiles'])]
                if available_rooms:
                    room = random.choice(available_rooms)
                    candidates = [t for t in room['tiles'] if t not in used_positions]
                    if candidates:
                        position = random.choice(candidates)
                        used_positions.add(position)
            
            # Record placement
            if position:
                placements.append({
                    'objective_type': obj_type,
                    'position': position,
                    'placement_rule': placement_rule,
                    'description': description
                })
    
    return {
        'placements': placements,
        'start_pos': start_pos,
        'mission_type': mission.get('mission_type', 'unknown'),
        'mission_description': mission.get('description', ''),
        'num_rooms': len(rooms),
        'max_distance': max(distances.values()) if distances else 0,
        'dead_end_count': len(dead_ends)
    }


