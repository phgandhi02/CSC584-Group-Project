# DunGen - LLM-Driven PCG Roguelike

CSC584 Building Game AI Project

A roguelike game that uses Procedural Content Generation (PCG) and LLMs to generate levels from text descriptions.

**6 PCG Algorithms:** 4 pure + 2 smart hybrids for maximum variety

**⭐ NEW: Mission-Driven Geometry** - The LLM now designs missions that directly influence level structure! Boss fights get boss arenas, treasure hunts get more branches, escape missions get checkpoints.

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run game
python main.py
```

**How to use:**
- Enter 1-6 for quick setting selection
- Or describe the **setting/atmosphere** (LLM will invent the mission!):
  - **"dark ancient dragon's lair"** → LLM invents boss fight mission + creates arena
  - **"sprawling underground cave network"** → LLM invents exploration + adds branches
  - **"crumbling dangerous ruins"** → LLM invents survival mission + adds checkpoints
  - **"mysterious forgotten catacombs"** → LLM invents treasure hunt + structures layout
  - Be descriptive about the PLACE and MOOD - the LLM designs the mission AND adjusts geometry!

**Controls:** Arrow keys, SPACE to regenerate, ESC to exit

**Logs:** All generations saved to `logs/` folder with timestamps.

## Testing

**Run all tests:**
```bash
python run_tests.py
```

**5 Test Suites** - All passing:
- ✓ **PCG Algorithms** (6/6) - All 6 algorithms generate valid levels
- ✓ **LLM Targeted Prompts** (90%) - LLM correctly interprets specific requests
- ✓ **LLM Bias** (PASS) - LLM shows variety, 4+ algorithms used, no dominance  
- ✓ **Config Validation** (5/5) - Parameters stay within valid ranges
- ✓ **Mission System** (4/4) - Missions design experiences and adjust geometry

**Individual tests:**
```bash
python tests/test_pcg_algorithms.py     # Test all 6 PCG algorithms
python tests/test_llm_prompts.py        # Test targeted prompts (90% accuracy)
python tests/test_mission_system.py     # Test mission-driven generation
python tests/test_config_validation.py  # Validate parameter ranges
python tests/test_llm_generation.py     # Compare LLM models
```

**Setup test models:**
```bash
.\setup_test_models.ps1  # Windows
./setup_test_models.sh   # Linux/Mac
```

--- 

## Setup LLM

- Using Docker:
To set up the LLM, you can use the following Docker command to run the Ollama LLM server with GPU support:
```bash
docker run --gpus=all -d -v ollama:/root/.ollama -p 11434:11434 --name LLM ollama/ollama
```
Then start the model by entering the container (make sure the container is running, otherwise start it with `docker start LLM`):
```bash
docker exec -it LLM bash
ollama run <model-name>
```
- Local Installation:
Ollama can be locally installed by downloading and installing the Ollama application from [here](https://ollama.com/download). Then, start the ollama server and run the model (it will also download the model if not on the machine already) by using the following command:
```bash
ollama run <model-name>
```

The project uses port 11434 by default to connect to the LLM server. Make sure that the port is open and accessible. This port may be occupied by other apps such as Docker containers, so ensure that there are no conflicts.

### Recommended Models

Default: **llama3.2:3b** (fast, 2-4 seconds per generation)

Alternatives: **gemma2:2b**, **qwen2.5**

⚠️ **Avoid reasoning models** (deepseek-r1, etc.) - they are 20x slower.

## Relevant Repos
- https://github.com/1allan/tower-of-bullets
- https://github.com/VictorHachard/pygame-roguelike
- https://github.com/sandromund/pygame_roguelike

## Tutorials:
- https://www.roguebasin.com/index.php/Complete_Roguelike_Tutorial,_using_python%2Blibtcod,_part_1
- https://pygame-dev.blogspot.com/
- [Cellular Automata Method for Generating Random Cave-Like Levels](https://www.roguebasin.com/index.php?title=Cellular_Automata_Method_for_Generating_Random_Cave-Like_Levels)
- [Code design basics](https://roguebasin.com/index.php/Code_design_basics)

## Relevant Articles
- https://slsdo.github.io/procedural-dungeon/
- http://pcg.wikidot.com/pcg-algorithm:dungeon-generation (many resources in here)



## References:
[/assets/icon.png](https://stablediffusionweb.com/image/43360801-pixel-art-crusader)