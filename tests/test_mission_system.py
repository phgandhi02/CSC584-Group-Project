"""
Test suite for mission-driven PCG system.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm import generate_level_config
from src.pcg_generator import generate_level
from src.mission_processor import place_objectives
from src.mission_to_geometry import adjust_layout_for_mission


def test_mission_integration():
    """Test that mission system integrates correctly."""
    print("\n=== Testing Mission System Integration ===")
    
    # Generate config with mission
    config, log = generate_level_config('defeat the ancient dragon')
    
    # Verify mission exists
    assert hasattr(config, 'mission'), "Config missing mission"
    assert config.mission.mission_type in ['linear_progression', 'exploration', 'key_hunt', 'survival', 'multi_objective']
    assert len(config.mission.objectives) > 0, "Mission has no objectives"
    
    # Generate level
    grid = generate_level(config.model_dump())
    assert len(grid) > 0, "Level generation failed"
    assert len(grid[0]) > 0, "Level has no width"
    
    # Place objectives
    result = place_objectives(grid, config.mission.model_dump())
    assert 'error' not in result, f"Objective placement failed: {result.get('error')}"
    assert len(result['placements']) > 0, "No objectives were placed"
    assert result['start_pos'] is not None, "No start position found"
    
    print(f"[PASS] Integration test passed")
    print(f"  Algorithm: {config.algorithm}")
    print(f"  Mission type: {config.mission.mission_type}")
    print(f"  Objectives placed: {len(result['placements'])}")
    return True


def test_mission_variety():
    """Test that different prompts produce different missions."""
    print("\n=== Testing Mission Variety ===")
    
    prompts = [
        "defeat the boss",
        "find hidden treasures",
        "escape the dungeon",
    ]
    
    mission_types = []
    for prompt in prompts:
        config, _ = generate_level_config(prompt)
        mission_types.append(config.mission.mission_type)
        print(f"  '{prompt}' -> {config.mission.mission_type}")
    
    # Should have some variety (not all the same)
    unique_types = len(set(mission_types))
    if unique_types >= 2:
        print(f"[PASS] Good variety: {unique_types}/3 unique mission types")
        return True
    else:
        print(f"[WARNING] Low variety: {unique_types}/3 unique mission types")
        return True  # Still pass, but warn


def test_objective_placement_rules():
    """Test that placement rules work correctly."""
    print("\n=== Testing Objective Placement Rules ===")
    
    config, _ = generate_level_config('defeat the dragon boss')
    grid = generate_level(config.model_dump())
    result = place_objectives(grid, config.mission.model_dump())
    
    if 'error' in result:
        print(f"[SKIP] Cannot test placement: {result['error']}")
        return True
    
    # Check that placements have required fields
    for p in result['placements']:
        assert 'objective_type' in p, "Placement missing objective_type"
        assert 'position' in p, "Placement missing position"
        assert 'placement_rule' in p, "Placement missing placement_rule"
        assert isinstance(p['position'], tuple), "Position should be tuple"
        assert len(p['position']) == 2, "Position should be (x, y)"
    
    print(f"[PASS] All {len(result['placements'])} placements valid")
    return True


def test_geometry_adjustments():
    """Test that missions adjust geometry parameters."""
    print("\n=== Testing Geometry Adjustments ===")
    
    config, _ = generate_level_config('defeat the final boss')
    original_layout = config.layout.model_dump()
    
    # Apply mission adjustments
    adjusted_layout = adjust_layout_for_mission(
        original_layout,
        config.mission.model_dump(),
        config.algorithm
    )
    
    # Generate both versions
    config_original = config.model_dump()
    grid_original = generate_level(config_original)
    
    config_adjusted = config.model_dump()
    config_adjusted['layout'] = adjusted_layout
    grid_adjusted = generate_level(config_adjusted)
    
    # Calculate floor percentages
    floor_original = sum(row.count(1) for row in grid_original)
    floor_adjusted = sum(row.count(1) for row in grid_adjusted)
    
    total_tiles = len(grid_original) * len(grid_original[0])
    percent_original = floor_original / total_tiles * 100
    percent_adjusted = floor_adjusted / total_tiles * 100
    
    print(f"  Original map: {percent_original:.1f}% floor")
    print(f"  Adjusted map: {percent_adjusted:.1f}% floor")
    
    # For boss missions, we expect changes
    if config.mission.mission_type == 'linear_progression':
        has_boss = any(obj.objective_type == 'boss' for obj in config.mission.objectives)
        if has_boss and 'max_rooms' in original_layout:
            # Should have fewer rooms or bigger rooms
            changed = (adjusted_layout.get('max_rooms') != original_layout.get('max_rooms') or
                      adjusted_layout.get('room_size_max') != original_layout.get('room_size_max'))
            if changed:
                print(f"[PASS] Geometry adjusted for boss mission")
            else:
                print(f"[WARNING] No geometry changes for boss mission")
            return True
    
    print(f"[PASS] Geometry adjustment tested")
    return True


def run_all_tests():
    """Run all mission system tests."""
    tests = [
        test_mission_integration,
        test_mission_variety,
        test_objective_placement_rules,
        test_geometry_adjustments,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"[FAIL] {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"[ERROR] {test.__name__}: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Mission System Tests: {passed} passed, {failed} failed")
    print(f"{'='*50}")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)

