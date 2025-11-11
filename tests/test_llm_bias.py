"""Test LLM for algorithm selection bias."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm import generate_level_config, DEFAULT_MODEL


def test_llm_bias(num_tests=10):
    """Test if LLM shows bias toward specific algorithms."""
    print("="*70)
    print("LLM BIAS TEST")
    print("="*70)
    print(f"Model: {DEFAULT_MODEL}")
    print(f"Testing {num_tests} generic prompts")
    print("="*70)
    
    # Generic prompts that shouldn't favor any algorithm
    prompts = [
        "a dungeon",
        "a level",
        "make me something",
        "a map",
        "generate a level",
        "a place to explore",
        "an adventure",
        "something fun",
        "a challenging area",
        "an interesting location",
    ][:num_tests]
    
    results = {}
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n[{i}/{num_tests}] '{prompt}'", end=" ")
        
        try:
            config, _ = generate_level_config(prompt, DEFAULT_MODEL)
            # Extract algorithm directly from config
            algo = config.algorithm
            results[algo] = results.get(algo, 0) + 1
            print(f"-> {algo}")
        except Exception as e:
            print(f"ERROR: {e}")
    
    # Analyze results
    print("\n" + "="*70)
    print("ALGORITHM DISTRIBUTION")
    print("="*70)
    
    for algo, count in sorted(results.items(), key=lambda x: x[1], reverse=True):
        percentage = 100 * count / num_tests
        bar = "#" * int(percentage / 5)
        print(f"{algo:25} {count:2}/{num_tests} {bar} {percentage:.1f}%")
    
    print("\n" + "="*70)
    
    # Evaluation
    num_algos_used = len(results)
    max_count = max(results.values()) if results else 0
    max_percent = max_count / num_tests if num_tests > 0 else 0
    
    bias_detected = False
    
    if num_algos_used == 1:
        print("[FAIL] SEVERE BIAS: Only 1 algorithm used")
        bias_detected = True
    elif num_algos_used == 2:
        print("[FAIL] STRONG BIAS: Only 2 algorithms used")
        bias_detected = True
    elif num_algos_used == 3:
        print("[WARN] MODERATE BIAS: Only 3 algorithms used")
        bias_detected = True
    elif max_percent >= 0.6:
        print(f"[WARN] One algorithm dominates: {max_count}/{num_tests} ({max_percent:.0%})")
        bias_detected = True
    else:
        print(f"[PASS] Good variety: {num_algos_used}/6 algorithms used")
        print(f"[PASS] No single algorithm dominates (max {max_percent:.0%})")
    
    print("="*70)
    
    return not bias_detected


if __name__ == "__main__":
    success = test_llm_bias()
    sys.exit(0 if success else 1)

