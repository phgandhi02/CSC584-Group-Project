"""Test LLM with carefully crafted prompts targeting specific algorithms."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm import generate_level_config, DEFAULT_MODEL


# Prompts designed to test each algorithm
TEST_PROMPTS = [
    # 1. Drunkard's Walk (DW) Test: Focus on "cramped" and "hard to navigate"
    ("Drunkard's Walk", 
     "I want something extremely cramped and full of twisting dead ends. Make it really hard to navigate.",
     ["drunkards_walk"]),

    # 2. Cellular Automata (CA) Test: Focus on "organic" and "grotto"
    ("Cellular Automata",
     "Could you generate a huge, organic grotto? I'm picturing deep subterranean spaces that look totally untouched by people.",
     ["cellular_automata"]),

    # 3. BSP Test: Focus on "structured" and "compound"
    ("BSP",
     "I need a very structured area, like a military compound with clean lines and a clear system of security rooms.",
     ["bsp"]),

    # 4. Arena Test: Focus on "big fights" and "halls"
    ("Cellular Rooms",
     "Give me something with lots of big rooms made specifically for fighting, maybe large battle halls connected by short bridges.",
     ["cellular_rooms"]),

    # 5. Hybrid: BSP + CA: Implied architectural contrast
    ("Hybrid (Citadel+Fissure)",
     "Let's do an old abandoned citadel that has cracked open to reveal a massive fissure in the earth below it.",
     ["hybrid_rooms_caves", "bsp", "cellular_automata"]),  # Accept multiple valid choices

    # 6. Hybrid: DW + BSP: Focus on a specific function (utility corridors)
    ("Hybrid (Tunnels+Barracks)",
     "I'd love a level where most of the travel is through tiny, claustrophobic maintenance tunnels that lead into small, organized barracks.",
     ["hybrid_rooms_caves", "drunkards_walk"]),

    # 7. Hybrid: CA + Arena: Descriptive blend of natural space and combat
    ("Hybrid (Vaults+Pits)",
     "Make it a series of naturally eroded vaults that periodically widen into huge, circular fighting pits.",
     ["cellular_rooms", "hybrid_rooms_caves", "cellular_automata"]),

    # 8. Generic/Default Test 1: Casual request
    ("Generic (Fun)",
     "Just give me a fun, challenging level to play through right now, please.",
     ["drunkards_walk", "hybrid_rooms_caves", "cellular_automata", "bsp", "random_room_placement", "cellular_rooms"]),  # Any is fine

    # 9. Generic/Default Test 2: Ambiguous concept (should resolve to varied)
    ("Generic (Tomb)",
     "How about a creepy old underground tomb for a change of pace?",
     ["cellular_automata", "cellular_rooms", "drunkards_walk", "bsp"]),  # Cave-like or structured

    # 10. Explicit Varied Test: Requesting structural unpredictability
    ("Explicit Variety",
     "Make the level highly unpredictable; I want to see a blend of different architectural styles as I progress.",
     ["hybrid_rooms_caves"]),  # Best for variety
]


def test_llm_prompts():
    """Test LLM with carefully crafted prompts."""
    print("="*70)
    print("LLM TARGETED PROMPT TEST")
    print("="*70)
    print(f"Model: {DEFAULT_MODEL}")
    print(f"Testing {len(TEST_PROMPTS)} carefully crafted prompts")
    print("="*70)
    
    results = {
        "correct": 0,
        "acceptable": 0,
        "wrong": 0,
        "error": 0
    }
    
    algorithm_usage = {}
    
    for i, (test_name, prompt, expected_algos) in enumerate(TEST_PROMPTS, 1):
        print(f"\n[{i}/{len(TEST_PROMPTS)}] {test_name}")
        print(f"Prompt: '{prompt}'")
        print(f"Expected: {expected_algos[0] if len(expected_algos) == 1 else f'One of {expected_algos}'}")
        
        try:
            config, log = generate_level_config(prompt, DEFAULT_MODEL)
            # Extract algorithm directly from config
            algo = config.algorithm
            algorithm_usage[algo] = algorithm_usage.get(algo, 0) + 1
            
            # Check if chosen algorithm is in expected list
            if algo == expected_algos[0]:
                result = "[PERFECT]"
                results["correct"] += 1
            elif algo in expected_algos:
                result = "[ACCEPTABLE]"
                results["acceptable"] += 1
            else:
                result = "[WRONG]"
                results["wrong"] += 1
            
            print(f"{result} LLM chose: {algo}")
            
            # Show reasoning (ASCII only to avoid encoding errors)
            if 'llm_reasoning' in log:
                reason = log['llm_reasoning']
                # Remove non-ASCII characters
                reason = reason.encode('ascii', 'ignore').decode('ascii')
                if len(reason) > 100:
                    reason = reason[:97] + "..."
                print(f"Reasoning: {reason}")
                
        except Exception as e:
            print(f"[ERROR] {e}")
            results["error"] += 1
    
    # Summary
    print("\n" + "="*70)
    print("RESULTS SUMMARY")
    print("="*70)
    
    total = len(TEST_PROMPTS)
    print(f"Perfect matches:     {results['correct']}/{total} ({100*results['correct']/total:.0f}%)")
    print(f"Acceptable choices:  {results['acceptable']}/{total} ({100*results['acceptable']/total:.0f}%)")
    print(f"Wrong choices:       {results['wrong']}/{total} ({100*results['wrong']/total:.0f}%)")
    print(f"Errors:              {results['error']}/{total}")
    
    success_rate = (results['correct'] + results['acceptable']) / total
    print(f"\nOverall success: {100*success_rate:.1f}%")
    
    print("\n" + "="*70)
    print("ALGORITHM USAGE")
    print("="*70)
    for algo, count in sorted(algorithm_usage.items(), key=lambda x: x[1], reverse=True):
        bar = "#" * (count * 2)
        print(f"{algo:25} {count}/{total} {bar}")
    
    print("\n" + "="*70)
    
    # Evaluation
    if success_rate >= 0.8:
        print("[EXCELLENT] LLM understands prompts very well (>=80%)")
        return True
    elif success_rate >= 0.6:
        print("[GOOD] LLM understands most prompts (>=60%)")
        return True
    elif success_rate >= 0.4:
        print("[ACCEPTABLE] LLM understands some prompts (>=40%)")
        return True
    else:
        print("[POOR] LLM struggles with prompts (<40%)")
        return False


if __name__ == "__main__":
    success = test_llm_prompts()
    sys.exit(0 if success else 1)

