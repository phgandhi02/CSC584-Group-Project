"""
Comprehensive test suite for LLM level generation.
Tests multiple prompts and measures generation time.
"""
import json
import time
from pathlib import Path
from typing import Any

from src.llm import generate_level_config, DEFAULT_MODEL, get_available_models


class TestResult:
    """Stores results of a single test."""
    def __init__(self, prompt: str, success: bool, config: dict[str, Any] | None, 
                 time_taken: float, error: str | None = None):
        self.prompt = prompt
        self.success = success
        self.config = config
        self.time_taken = time_taken
        self.error = error


def test_prompt(prompt: str, model: str) -> TestResult:
    """
    Test a single prompt and measure generation time.
    
    Args:
        prompt: User description of desired level
        model: Ollama model to use
    
    Returns:
        TestResult with timing and success information
    """
    print(f"\n{'='*70}")
    print(f"Testing: '{prompt}'")
    print(f"{'='*70}")
    
    start_time = time.time()
    
    try:
        level_config, log_data = generate_level_config(prompt, model=model)
        end_time = time.time()
        time_taken = end_time - start_time
        
        config_dict = level_config.model_dump()
        
        print(f"[SUCCESS] Generated in {time_taken:.2f} seconds")
        print(f"Algorithm: {config_dict['algorithm']}")
        print(f"Map Size: {config_dict['layout']['map_width']}x{config_dict['layout']['map_height']}")
        print(f"Theme: {config_dict['aesthetic']['theme']}")
        print(f"Lighting: {config_dict['aesthetic']['lighting_level']}")
        
        # Validate structure
        if config_dict['algorithm'] == 'drunkards_walk':
            if 'drunkard_params' not in config_dict['layout']:
                print("[WARNING] Missing drunkard_params for drunkards_walk algorithm!")
        elif config_dict['algorithm'] == 'random_room_placement':
            required = ['max_rooms', 'room_size_min', 'room_size_max', 'corridor_width']
            missing = [k for k in required if k not in config_dict['layout']]
            if missing:
                print(f"[WARNING] Missing parameters for room placement: {missing}")
        
        print("\nFull Configuration:")
        print(json.dumps(config_dict, indent=2))
        
        return TestResult(prompt, True, config_dict, time_taken)
        
    except Exception as e:
        end_time = time.time()
        time_taken = end_time - start_time
        
        print(f"[FAILED] Error after {time_taken:.2f} seconds: {e}")
        import traceback
        traceback.print_exc()
        
        return TestResult(prompt, False, None, time_taken, str(e))


def save_generated_config(config: dict[str, Any], filename: str) -> None:
    """Save a generated configuration to jsons folder."""
    jsons_dir = Path("jsons")
    jsons_dir.mkdir(exist_ok=True)
    
    filepath = jsons_dir / f"{filename}.json"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    print(f"[SAVED] Configuration saved to {filepath}")


def run_test_suite(model: str = DEFAULT_MODEL, save_outputs: bool = False) -> None:
    """
    Run complete test suite with various prompts.
    
    Args:
        model: Ollama model to use
        save_outputs: Whether to save generated configs to jsons folder
    """
    print("="*70)
    print("LLM LEVEL GENERATION TEST SUITE")
    print("="*70)
    print(f"Model: {model}")
    print(f"Save outputs: {save_outputs}")
    print("="*70)
    
    # Define test prompts
    test_prompts = [
        "a dark, claustrophobic dungeon with many enemies and few treasures",
        "a bright, open fortress with large rooms and lots of treasure",
        "a winding organic cave system with twisting passages",
        "a scary crypt with undead enemies and low lighting",
        "a balanced dungeon level with moderate difficulty",
        "a maze-like structure perfect for getting lost in",
    ]
    
    results: list[TestResult] = []
    total_start = time.time()
    
    # Run all tests
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n\n### TEST {i}/{len(test_prompts)} ###")
        result = test_prompt(prompt, model)
        results.append(result)
        
        # Optionally save successful generations
        if save_outputs and result.success and result.config:
            filename = f"llm_generated_{i}_{result.config['algorithm'][:8]}"
            save_generated_config(result.config, filename)
        
        # Small delay between tests to avoid overwhelming the LLM
        if i < len(test_prompts):
            time.sleep(0.5)
    
    total_end = time.time()
    total_time = total_end - total_start
    
    # Print summary
    print("\n\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]
    
    print(f"Total tests: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    print(f"Success rate: {len(successful)/len(results)*100:.1f}%")
    print(f"\nTotal time: {total_time:.2f} seconds")
    print(f"Average time per test: {total_time/len(results):.2f} seconds")
    
    if successful:
        avg_success_time = sum(r.time_taken for r in successful) / len(successful)
        print(f"Average time (successful): {avg_success_time:.2f} seconds")
        
        # Algorithm distribution
        algorithms = {}
        for r in successful:
            if r.config:
                algo = r.config['algorithm']
                algorithms[algo] = algorithms.get(algo, 0) + 1
        
        print(f"\nAlgorithm distribution:")
        for algo, count in algorithms.items():
            print(f"  {algo}: {count} ({count/len(successful)*100:.1f}%)")
    
    if failed:
        print(f"\n[FAILED TESTS]")
        for r in failed:
            print(f"  - {r.prompt[:50]}... ({r.error})")
    
    print("="*70)


def compare_models(models: list[str], save_outputs: bool = False) -> None:
    """
    Run test suite across multiple models and compare results.
    
    Args:
        models: List of model names to compare
        save_outputs: Whether to save generated configs
    """
    print("="*70)
    print("MULTI-MODEL COMPARISON TEST")
    print("="*70)
    print(f"Testing {len(models)} models:")
    for i, model in enumerate(models, 1):
        print(f"  {i}. {model}")
    print("="*70)
    
    all_results: dict[str, list[TestResult]] = {}
    model_timings: dict[str, dict[str, float]] = {}
    
    for model_idx, model in enumerate(models, 1):
        print(f"\n\n{'#'*70}")
        print(f"# MODEL {model_idx}/{len(models)}: {model}")
        print(f"{'#'*70}\n")
        
        # Define test prompts (same for all models)
        test_prompts = [
            "a dark, claustrophobic dungeon with many enemies and few treasures",
            "a bright, open fortress with large rooms and lots of treasure",
            "a winding organic cave system with twisting passages",
        ]
        
        results: list[TestResult] = []
        total_start = time.time()
        
        # Run tests for this model
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n### TEST {i}/{len(test_prompts)} ###")
            result = test_prompt(prompt, model)
            results.append(result)
            
            # Optionally save successful generations
            if save_outputs and result.success and result.config:
                # Create safe filename from model name and test number
                safe_model_name = model.replace(':', '_').replace('.', '_')
                filename = f"llm_generated_{safe_model_name}_test{i}_{result.config['algorithm'][:8]}"
                save_generated_config(result.config, filename)
            
            # Small delay between tests
            if i < len(test_prompts):
                time.sleep(0.5)
        
        total_end = time.time()
        total_time = total_end - total_start
        
        # Store results
        all_results[model] = results
        successful = [r for r in results if r.success]
        
        model_timings[model] = {
            'total_time': total_time,
            'avg_time': total_time / len(results),
            'success_rate': len(successful) / len(results) * 100,
            'avg_success_time': sum(r.time_taken for r in successful) / len(successful) if successful else 0
        }
    
    # Print comparison summary
    print("\n\n" + "="*70)
    print("COMPARISON SUMMARY")
    print("="*70)
    
    print("\n{:<20} {:>12} {:>12} {:>12} {:>12}".format(
        "Model", "Total Time", "Avg Time", "Success Rate", "Avg (Success)"
    ))
    print("-"*70)
    
    for model in models:
        timings = model_timings[model]
        print("{:<20} {:>11.2f}s {:>11.2f}s {:>11.1f}% {:>11.2f}s".format(
            model[:20],
            timings['total_time'],
            timings['avg_time'],
            timings['success_rate'],
            timings['avg_success_time']
        ))
    
    # Find fastest
    fastest_model = min(model_timings.items(), key=lambda x: x[1]['avg_success_time'])
    print("\n" + "="*70)
    print(f"FASTEST MODEL: {fastest_model[0]}")
    print(f"Average generation time: {fastest_model[1]['avg_success_time']:.2f}s")
    
    # Calculate speedup
    print("\nSPEEDUP COMPARISON (vs slowest):")
    print("-"*70)
    slowest_time = max(t['avg_success_time'] for t in model_timings.values())
    
    for model in models:
        timing = model_timings[model]['avg_success_time']
        if timing > 0:
            speedup = slowest_time / timing
            print(f"{model:<20} {speedup:>6.2f}x faster")
    
    print("="*70)


def main():
    """Main test entry point."""
    import sys
    
    print("="*70)
    print("LLM Level Generation Test Suite")
    print("="*70)
    
    # Check for comparison mode
    if "--compare" in sys.argv:
        print("\n[COMPARISON MODE]")
        print("This will test multiple models and compare their performance.")
        
        # Check if including slow models
        include_slow = "--include-slow" in sys.argv
        
        if include_slow:
            # Include reasoning model (slow but accurate)
            compare_models_list = [
                "deepseek-r1:8b",
                "gemma2:2b",
                "llama3.2:3b"
            ]
            print("\n[INCLUDING SLOW MODELS]")
            print("Note: deepseek-r1:8b is a reasoning model and will be much slower (~50s per test)")
        else:
            # Default: only fast models
            compare_models_list = [
                "gemma2:2b",
                "llama3.2:3b"
            ]
            print("\nTip: Add --include-slow to also test deepseek-r1:8b (reasoning model)")
        
        print("\nModels to test:")
        for i, model in enumerate(compare_models_list, 1):
            print(f"  {i}. {model}")
        
        print("\nNote: Models will be used if available. Install missing models with:")
        print("  ollama pull <model-name>")
        
        try:
            choice = input("\nSave generated configs? (y/n, default=n): ").strip().lower()
            save_outputs = (choice == "y")
        except EOFError:
            save_outputs = False
            print("Running in non-interactive mode, not saving outputs")
        
        compare_models(compare_models_list, save_outputs)
        return
    
    # Single model mode
    available_models = get_available_models()
    if available_models:
        print("\nAvailable models:")
        for i, model in enumerate(available_models, 1):
            default_marker = " (default)" if model == DEFAULT_MODEL else ""
            print(f"  {i}. {model}{default_marker}")
    
    # Select model
    if len(sys.argv) > 1 and sys.argv[1] != "--compare":
        model = sys.argv[1]
        print(f"\nUsing model from argument: {model}")
    else:
        model = DEFAULT_MODEL
        print(f"\nUsing default model: {model}")
    
    # Ask about saving
    print("\nOptions:")
    print("  1. Run tests only")
    print("  2. Run tests and save generated configs to jsons/")
    
    try:
        choice = input("\nSelect option (1 or 2, default=1): ").strip()
        save_outputs = (choice == "2")
    except EOFError:
        save_outputs = False
        print("Running in non-interactive mode, not saving outputs")
    
    # Run the test suite
    run_test_suite(model=model, save_outputs=save_outputs)


if __name__ == "__main__":
    main()

