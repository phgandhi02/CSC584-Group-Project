"""Tests for PCG algorithms to ensure they generate valid levels."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pcg_generator import generate_level, TILE_FLOOR, TILE_WALL


def make_single_region_config(algo: str, width: int, height: int, params: dict = None) -> dict:
    """Helper to create a config for testing individual algorithms."""
    base_config = {
        "algorithm": algo,
        "content": {
            "enemy_density": 0.1,
            "treasure_density": 0.05,
            "trap_density": 0.02,
            "enemy_types": ["goblin"],
            "treasure_types": ["gold_coin"]
        },
        "aesthetic": {
            "theme": "default",
            "lighting_level": 0.5
        }
    }
    
    # Add appropriate layout based on algorithm
    if algo in ["random_room_placement", "bsp", "hybrid_rooms_caves"]:
        base_config["layout"] = {
            "map_width": width,
            "map_height": height,
            "max_rooms": 15,
            "room_size_min": 4,
            "room_size_max": 10,
            "corridor_width": 1
        }
    elif algo == "drunkards_walk":
        base_config["layout"] = {
            "map_width": width,
            "map_height": height,
            "drunkard_params": {
                "target_floor_percent": 0.25,
                "straight_bias": 0.7,
                "start_pos": "center"
            }
        }
    elif algo in ["cellular_automata", "cellular_rooms"]:
        base_config["layout"] = {
            "map_width": width,
            "map_height": height,
            "cellular_params": {
                "initial_wall_probability": 0.55,
                "iterations": 4
            }
        }
    
    return base_config


def count_tiles(grid, tile_type):
    """Count occurrences of a tile type in the grid."""
    return sum(row.count(tile_type) for row in grid)


def test_random_room_placement():
    """Test random room placement algorithm."""
    config = make_single_region_config("random_room_placement", 50, 40, {
        "max_rooms": 10,
        "room_size_min": 5,
        "room_size_max": 10,
        "corridor_width": 1
    })
    
    grid = generate_level(config)
    
    assert len(grid) == 40, f"Height should be 40, got {len(grid)}"
    assert len(grid[0]) == 50, f"Width should be 50, got {len(grid[0])}"
    
    floor_count = count_tiles(grid, TILE_FLOOR)
    total_tiles = 50 * 40
    floor_percent = floor_count / total_tiles
    
    assert floor_percent > 0.1, f"Too few floor tiles: {floor_percent:.1%}"
    assert floor_percent < 0.7, f"Too many floor tiles: {floor_percent:.1%}"
    
    print(f"[PASS] random_room_placement: {floor_count}/{total_tiles} floor tiles ({floor_percent:.1%})")


def test_bsp():
    """Test BSP algorithm."""
    config = make_single_region_config("bsp", 60, 40, {
        "max_rooms": 15,
        "room_size_min": 6,
        "room_size_max": 12,
        "corridor_width": 2
    })
    
    grid = generate_level(config)
    
    assert len(grid) == 40
    assert len(grid[0]) == 60
    
    floor_count = count_tiles(grid, TILE_FLOOR)
    total_tiles = 60 * 40
    floor_percent = floor_count / total_tiles
    
    assert floor_percent > 0.15, f"Too few floor tiles: {floor_percent:.1%}"
    assert floor_percent < 0.6, f"Too many floor tiles: {floor_percent:.1%}"
    
    print(f"[PASS] bsp: {floor_count}/{total_tiles} floor tiles ({floor_percent:.1%})")


def test_drunkards_walk():
    """Test drunkard's walk algorithm."""
    config = make_single_region_config("drunkards_walk", 50, 40)
    
    grid = generate_level(config)
    
    assert len(grid) == 40
    assert len(grid[0]) == 50
    
    floor_count = count_tiles(grid, TILE_FLOOR)
    total_tiles = 50 * 40
    floor_percent = floor_count / total_tiles
    
    # Should be close to target (0.25)
    assert 0.15 < floor_percent < 0.35, f"Floor percent {floor_percent:.1%} not near target 25%"
    
    print(f"[PASS] drunkards_walk: {floor_count}/{total_tiles} floor tiles ({floor_percent:.1%})")


def test_cellular_automata():
    """Test cellular automata algorithm."""
    config = make_single_region_config("cellular_automata", 60, 40)
    
    grid = generate_level(config)
    
    assert len(grid) == 40
    assert len(grid[0]) == 60
    
    floor_count = count_tiles(grid, TILE_FLOOR)
    total_tiles = 60 * 40
    floor_percent = floor_count / total_tiles
    
    assert floor_percent > 0.3, f"Too few floor tiles: {floor_percent:.1%}"
    assert floor_percent < 0.7, f"Too many floor tiles: {floor_percent:.1%}"
    
    print(f"[PASS] cellular_automata: {floor_count}/{total_tiles} floor tiles ({floor_percent:.1%})")


def test_hybrid_rooms_caves():
    """Test hybrid algorithm."""
    config = make_single_region_config("hybrid_rooms_caves", 55, 40)
    
    grid = generate_level(config)
    
    assert len(grid) == 40
    assert len(grid[0]) == 55
    
    floor_count = count_tiles(grid, TILE_FLOOR)
    total_tiles = 55 * 40
    floor_percent = floor_count / total_tiles
    
    assert floor_percent > 0.2, f"Too few floor tiles: {floor_percent:.1%}"
    assert floor_percent < 0.6, f"Too many floor tiles: {floor_percent:.1%}"
    
    print(f"[PASS] hybrid_rooms_caves: {floor_count}/{total_tiles} floor tiles ({floor_percent:.1%})")


def test_cellular_rooms():
    """Test cellular rooms algorithm."""
    config = make_single_region_config("cellular_rooms", 60, 40)
    
    grid = generate_level(config)
    
    assert len(grid) == 40
    assert len(grid[0]) == 60
    
    floor_count = count_tiles(grid, TILE_FLOOR)
    total_tiles = 60 * 40
    floor_percent = floor_count / total_tiles
    
    assert floor_percent > 0.25, f"Too few floor tiles: {floor_percent:.1%}"
    assert floor_percent < 0.65, f"Too many floor tiles: {floor_percent:.1%}"
    
    print(f"[PASS] cellular_rooms: {floor_count}/{total_tiles} floor tiles ({floor_percent:.1%})")


def run_all_tests():
    """Run all PCG algorithm tests."""
    print("="*70)
    print("PCG ALGORITHM TESTS")
    print("="*70)
    
    tests = [
        ("Random Room Placement", test_random_room_placement),
        ("BSP", test_bsp),
        ("Drunkard's Walk", test_drunkards_walk),
        ("Cellular Automata", test_cellular_automata),
        ("Hybrid Rooms + Caves", test_hybrid_rooms_caves),
        ("Cellular Rooms", test_cellular_rooms),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {name}: {e}")
            failed += 1
        except Exception as e:
            print(f"[ERROR] {name}: {e}")
            failed += 1
    
    print("\n" + "="*70)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

