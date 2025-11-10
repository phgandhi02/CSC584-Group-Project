"""Test configuration validation and parameter ranges."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm import generate_level_config, DEFAULT_MODEL


def test_parameter_ranges(num_tests=5):
    """Test that LLM generates parameters within valid ranges."""
    print("="*70)
    print("PARAMETER VALIDATION TEST")
    print("="*70)
    print(f"Model: {DEFAULT_MODEL}")
    print("="*70)
    
    prompts = [
        "a dark dungeon",
        "a bright fortress",
        "a tight maze",
        "an open cavern",
        "a balanced level",
    ][:num_tests]
    
    passed = 0
    failed = 0
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n[{i}/{num_tests}] Testing: '{prompt}'")
        
        try:
            config, _ = generate_level_config(prompt, DEFAULT_MODEL)
            config_dict = config.model_dump()
            
            # Check layout parameters
            layout = config_dict['layout']
            assert 40 <= layout['map_width'] <= 80, f"map_width {layout['map_width']} out of range"
            assert 30 <= layout['map_height'] <= 50, f"map_height {layout['map_height']} out of range"
            
            # Check content parameters
            content = config_dict['content']
            assert 0.0 <= content['enemy_density'] <= 1.0, f"enemy_density {content['enemy_density']} out of range"
            assert 0.0 <= content['treasure_density'] <= 1.0, f"treasure_density {content['treasure_density']} out of range"
            assert 0.0 <= content['trap_density'] <= 1.0, f"trap_density {content['trap_density']} out of range"
            
            # Check aesthetic parameters
            aesthetic = config_dict['aesthetic']
            assert 0.0 <= aesthetic['lighting_level'] <= 1.0, f"lighting_level {aesthetic['lighting_level']} out of range"
            
            # Check lists
            assert len(content['enemy_types']) > 0, "No enemy types specified"
            assert len(content['treasure_types']) > 0, "No treasure types specified"
            
            print(f"  [PASS] All parameters in valid ranges")
            print(f"    enemy_density: {content['enemy_density']:.2f}")
            print(f"    lighting: {aesthetic['lighting_level']:.2f}")
            passed += 1
            
        except AssertionError as e:
            print(f"  [FAIL] VALIDATION FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"  [ERROR] {e}")
            failed += 1
    
    print("\n" + "="*70)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*70)
    
    return failed == 0


if __name__ == "__main__":
    success = test_parameter_ranges()
    sys.exit(0 if success else 1)

