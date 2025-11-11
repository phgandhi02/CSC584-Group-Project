"""Run all tests for the DunGen project."""
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import test modules
from tests.test_pcg_algorithms import run_all_tests as test_pcg
from tests.test_llm_bias import test_llm_bias
from tests.test_config_validation import test_parameter_ranges
from tests.test_llm_prompts import test_llm_prompts
from tests.test_mission_system import run_all_tests as test_mission_system


def run_all_tests():
    """Run all test suites."""
    print("\n")
    print("="*70)
    print(" " * 20 + "DUNGEN TEST SUITE")
    print("="*70)
    
    start_time = time.time()
    
    test_suites = [
        ("PCG Algorithms", test_pcg),
        ("LLM Targeted Prompts", test_llm_prompts),
        ("LLM Bias", lambda: test_llm_bias(num_tests=10)),
        ("Config Validation", lambda: test_parameter_ranges(num_tests=5)),
        ("Mission System", test_mission_system),
    ]
    
    results = {}
    
    for name, test_func in test_suites:
        print(f"\n{'='*70}")
        print(f"Running: {name}")
        print(f"{'='*70}")
        
        try:
            success = test_func()
            results[name] = "PASS" if success else "FAIL"
        except Exception as e:
            print(f"\n[ERROR] Test suite crashed: {e}")
            results[name] = "ERROR"
    
    # Summary
    elapsed = time.time() - start_time
    
    print("\n")
    print("="*70)
    print(" " * 25 + "TEST SUMMARY")
    print("="*70)
    
    for name, result in results.items():
        symbol = "[PASS]" if result == "PASS" else "[FAIL]"
        print(f"{symbol} {name:30} {result}")
    
    print("="*70)
    print(f"Total time: {elapsed:.1f}s")
    
    # Overall result
    all_passed = all(r == "PASS" for r in results.values())
    
    if all_passed:
        print("\n[SUCCESS] ALL TESTS PASSED")
    else:
        print("\n[FAILURE] SOME TESTS FAILED")
    
    print("="*70)
    
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
