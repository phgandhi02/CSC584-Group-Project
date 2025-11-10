"""
Module for generating schema for PCG based on user text input. The LLM will be
prompted with the use's text and a schema for the desired JSON output. Its
task is to translate qualitative descriptions (e.g., "scary," "open,"
"treasure-filled") into a quantitative set of parameters. For example, the
input "a dark, claustrophobic dungeon" might yield the following JSON:

    {"corridor width": 0.2,
    "room density": 0.8,
    "light sources": 0.1,"enemy density": 0.6}

"""

import os
import locale
import json
from datetime import datetime
from pathlib import Path
from typing import (
    Literal,
    Any,
)  # for type-hinting. Also necessary for Pydantic model schema validation

from ollama import ChatResponse, ListResponse, chat, list as ollama_list  # type: ignore
from pydantic import BaseModel
from pydantic import Field as PydanticField

# Default model - can be overridden by environment variable
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")


class DrunkardParams(BaseModel):
    """Parameters specific to the Drunkard's Walk algorithm."""

    target_floor_percent: float = PydanticField(
        ge=0.2,
        le=0.5,
        description="Percentage of map that should be floor (0.2-0.5 for interesting caves)",
    )
    start_pos: str | tuple[int, int] = PydanticField(
        default="center",
        description="Starting position: 'center', 'random', or [x, y] coordinates",
    )
    straight_bias: float = PydanticField(
        ge=0.0,
        le=1.0,
        description="Probability of continuing in same direction (0.0 to 1.0)",
    )


class CellularParams(BaseModel):
    """Parameters specific to Cellular Automata algorithm."""

    initial_wall_probability: float = PydanticField(
        ge=0.45,
        le=0.60,
        default=0.52,
        description="Initial wall probability (0.45-0.60, higher = more walls)",
    )
    iterations: int = PydanticField(
        ge=3, le=6, default=4, description="Number of CA iterations (3-6)"
    )
    birth_limit: int = PydanticField(
        ge=3, le=5, default=4, description="Wall neighbors needed to birth floor"
    )
    death_limit: int = PydanticField(
        ge=2, le=4, default=3, description="Wall neighbors needed to kill floor"
    )


class RoomPlacementLayout(BaseModel):
    """Layout parameters for random room placement algorithm."""

    map_width: int = PydanticField(
        ge=40, le=80, description="Width of the map (40-80 for good screen fit)"
    )
    map_height: int = PydanticField(
        ge=30, le=50, description="Height of the map (30-50 for good screen fit)"
    )
    max_rooms: int = PydanticField(
        ge=8, le=25, description="Maximum number of rooms to generate"
    )
    room_size_min: int = PydanticField(ge=4, le=10, description="Minimum room size")
    room_size_max: int = PydanticField(ge=6, le=15, description="Maximum room size")
    corridor_width: int = PydanticField(
        ge=1, le=3, description="Width of corridors connecting rooms"
    )


class DrunkardWalkLayout(BaseModel):
    """Layout parameters for drunkard's walk algorithm."""

    map_width: int = PydanticField(
        ge=40, le=80, description="Width of the map (40-80 for good screen fit)"
    )
    map_height: int = PydanticField(
        ge=30, le=50, description="Height of the map (30-50 for good screen fit)"
    )
    drunkard_params: DrunkardParams


class CellularLayout(BaseModel):
    """Layout parameters for cellular automata algorithm."""

    map_width: int = PydanticField(
        ge=40, le=80, description="Width of the map (40-80 for good screen fit)"
    )
    map_height: int = PydanticField(
        ge=30, le=50, description="Height of the map (30-50 for good screen fit)"
    )
    cellular_params: CellularParams


class Content(BaseModel):
    """Content parameters for enemies, treasures, and traps."""

    enemy_density: float = PydanticField(
        ge=0.0, le=1.0, description="Density of enemies (0.0 to 1.0)"
    )
    treasure_density: float = PydanticField(
        ge=0.0, le=1.0, description="Density of treasure (0.0 to 1.0)"
    )
    trap_density: float = PydanticField(
        ge=0.0, le=1.0, description="Density of traps (0.0 to 1.0)"
    )
    enemy_types: list[str] = PydanticField(
        description="Types of enemies (e.g., 'goblin', 'orc', 'bat', 'slime')"
    )
    treasure_types: list[str] = PydanticField(
        description="Types of treasure (e.g., 'gold_coin', 'chest', 'gem', 'potion_small')"
    )


class Aesthetic(BaseModel):
    """Aesthetic parameters for theme and lighting."""

    theme: str = PydanticField(
        description="Theme name (e.g., 'default_dungeon', 'cave', 'stone_fortress')"
    )
    lighting_level: float = PydanticField(
        ge=0.0, le=1.0, description="Lighting level (0.0 = dark, 1.0 = bright)"
    )


class ObjectivePlacement(BaseModel):
    """Specification for where an objective should be placed."""

    objective_type: Literal[
        "boss", "treasure", "key", "safe_room", "puzzle", "miniboss", "secret"
    ]
    placement_rule: Literal[
        "end_of_longest_path",  # Furthest from start
        "dead_end",  # In a dead-end branch
        "central_room",  # In largest/most central room
        "hidden",  # Hard to find location
        "checkpoint",  # Midway through level
        "random_room",  # Any suitable room
    ]
    count: int = PydanticField(ge=1, le=5, description="How many of this objective")
    description: str = PydanticField(description="What this objective represents")


class Mission(BaseModel):
    """Mission structure - the experience/story the LLM designs."""

    mission_type: Literal[
        "linear_progression",  # Start → challenges → boss
        "exploration",  # Discover scattered treasures
        "key_hunt",  # Find keys to unlock final area
        "survival",  # Navigate dangerous areas to safe zones
        "multi_objective",  # Multiple goals to complete
    ]
    objectives: list[ObjectivePlacement] = PydanticField(  # type: ignore
        min_items=1, max_items=6, description="Key objectives to place"
    )  # type: ignore
    difficulty_progression: Literal["flat", "increasing", "spike_at_end"] = (
        PydanticField(description="How difficulty changes through the level")
    )
    description: str = PydanticField(description="Brief mission narrative")


class RoomPlacementConfig(BaseModel):
    """Configuration for random room placement algorithm."""

    algorithm: Literal["random_room_placement"] = PydanticField(
        default="random_room_placement"
    )
    layout: RoomPlacementLayout
    content: Content
    aesthetic: Aesthetic
    mission: Mission


class DrunkardWalkConfig(BaseModel):
    """Configuration for drunkard's walk algorithm."""

    algorithm: Literal["drunkards_walk"] = PydanticField(default="drunkards_walk")
    layout: DrunkardWalkLayout
    content: Content
    aesthetic: Aesthetic
    mission: Mission


class RandomRoomConfig(BaseModel):
    """Complete configuration returned by LLM for random room placement algorithm."""

    algorithm: Literal["random_room_placement"] = PydanticField(
        default="random_room_placement"
    )
    layout: RoomPlacementLayout
    content: Content
    aesthetic: Aesthetic
    mission: Mission


class BSPConfig(BaseModel):
    """Complete configuration for BSP algorithm."""

    algorithm: Literal["bsp"] = PydanticField(default="bsp")
    layout: RoomPlacementLayout
    content: Content
    aesthetic: Aesthetic
    mission: Mission


class DrunkardConfig(BaseModel):
    """Complete configuration for Drunkard's Walk algorithm."""

    algorithm: Literal["drunkards_walk"] = PydanticField(default="drunkards_walk")
    layout: DrunkardWalkLayout
    content: Content
    aesthetic: Aesthetic
    mission: Mission


class CellularAutomataConfig(BaseModel):
    """Complete configuration for Cellular Automata algorithm."""

    algorithm: Literal["cellular_automata"] = PydanticField(default="cellular_automata")
    layout: CellularLayout
    content: Content
    aesthetic: Aesthetic
    mission: Mission


class HybridRoomsCavesConfig(BaseModel):
    """Complete configuration for Hybrid Rooms+Caves algorithm."""

    algorithm: Literal["hybrid_rooms_caves"] = PydanticField(
        default="hybrid_rooms_caves"
    )
    layout: RoomPlacementLayout
    content: Content
    aesthetic: Aesthetic
    mission: Mission


class CellularRoomsConfig(BaseModel):
    """Complete configuration for Cellular Rooms algorithm."""

    algorithm: Literal["cellular_rooms"] = PydanticField(default="cellular_rooms")
    layout: CellularLayout
    content: Content
    aesthetic: Aesthetic
    mission: Mission


# Union type for all possible configs
LevelConfig = (
    RandomRoomConfig
    | BSPConfig
    | DrunkardConfig
    | CellularAutomataConfig
    | HybridRoomsCavesConfig
    | CellularRoomsConfig
)


def get_available_models() -> list[str]:
    """
    Get list of available Ollama models on the local system.

    Returns:
        list[str]: List of model names available locally
    """
    try:
        response: ListResponse = ollama_list()  # type: ignore
        # Handle both dict with 'models' key and direct list response
        if isinstance(response, dict):
            models: dict[str, Any] = response.get("models", [])
        else:
            models = response  # type: ignore

        # Extract model names - handle different response structures
        model_names: list[str] = []
        for model in models:
            # Try to get the model name from various sources
            if hasattr(model, "model"):  # Ollama Model object
                model_names.append(model.model)  # type: ignore
            elif isinstance(model, dict):
                name: str | None = model.get("name") or model.get("model")  # type: ignore
                if name:
                    model_names.append(name)  # type: ignore
            # elif isinstance(model, str):
            #     model_names.append(model)
        return model_names

    except Exception as e:
        print(f"Warning: Could not fetch model list: {e}")
        return []


def select_model_interactive() -> str:
    """
    Prompt user to select a model from available models.

    Returns:
        str: Selected model name
    """
    available_models = get_available_models()

    if not available_models:
        print(f"No models found. Using default: {DEFAULT_MODEL}")
        return DEFAULT_MODEL

    print("\nAvailable Ollama models:")
    for i, model in enumerate(available_models, 1):
        default_marker: Literal[" (default)"] | Literal[""] = (
            " (default)" if model == DEFAULT_MODEL else ""
        )
        print(f"{i}. {model}{default_marker}")

    while True:
        choice = input(
            f"\nSelect a model (1-{len(available_models)}) or \
            press Enter for default [{DEFAULT_MODEL}]: "
        ).strip()

        if not choice:
            return DEFAULT_MODEL

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(available_models):
                return available_models[idx]
            else:
                print(f"Please enter a number between 1 and {len(available_models)}")
        except ValueError:
            print("Please enter a valid number")


def generate_level_config(
    user_prompt: str,
    model: str = DEFAULT_MODEL,
    prefer_algorithm: str | None = None,
    save_log: bool = False,
) -> tuple[LevelConfig, dict[str, str | Any]]:
    """
    Generate a level configuration using the LLM.

    Args:
        user_prompt: User description of desired level
        model: Ollama model to use
        prefer_algorithm: Prefer specific algorithm
        save_log: Whether to save the full response log

    Returns:
        tuple: (config, log_data) where log_data contains prompt, response, thinking, etc.
    """

    # Step 1: LLM chooses the best algorithm
    class AlgorithmReasoning(BaseModel):
        """LLM's reasoning for algorithm choice."""

        chosen_algorithm: Literal[
            "random_room_placement",
            "bsp",
            "drunkards_walk",
            "cellular_automata",
            "hybrid_rooms_caves",
            "cellular_rooms",
        ]
        reason: str = PydanticField(
            description="Why this algorithm fits the user's request"
        )

    algo_prompt = f"""You are a roguelike level designer. Analyze this
        request and choose the BEST algorithm.

USER REQUEST: "{user_prompt}"

AVAILABLE ALGORITHMS (all equally good - choose based on specific keywords):
1. random_room_placement: Rectangular rooms + corridors. Best for: "dungeon", "temple", "structured"
2. bsp: Hierarchical organized rooms. Best for: "fortress", "military", "castle", "organized"
3. drunkards_walk: Winding narrow tunnels. Best for: "maze", "cramped", "twisting". NOT for: "boss", "lair", "arena"
4. cellular_automata: Organic flowing caves. Best for: "cave", "natural", "grotto", "underground"
5. hybrid_rooms_caves: Rooms + tunnels mix. Best for: "variety", "mixed", "citadel"
6. cellular_rooms: Large battle halls. Best for: "arena", "pit", "chamber", "fighting"

IMPORTANT RULES:
1. Match EXACT keywords to algorithms (e.g., "maze"→drunkards_walk, "cave"→cellular_automata, "fortress"→bsp)
2. For "boss", "lair", "dragon": Choose random_room_placement OR cellular_rooms (NOT drunkards_walk - too narrow!)
3. For generic prompts with NO specific keywords: Pick randomly among random_room_placement, bsp, cellular_automata, cellular_rooms
4. Don't over-use hybrid_rooms_caves - it's not always the best choice!

Choose ONE algorithm and explain why in 1-2 sentences."""

    if prefer_algorithm:
        algo_prompt += "\nThe user prefers to use ${prefer_algorithm} as the algorithm."

    algo_response = chat(
        model=model,
        messages=[{"role": "user", "content": algo_prompt}],
        format=AlgorithmReasoning.model_json_schema(),
    )

    if not algo_response.message.content:
        raise ValueError("LLM returned empty algorithm reasoning")

    reasoning = AlgorithmReasoning.model_validate_json(algo_response.message.content)
    chosen_algo = reasoning.chosen_algorithm

    # Step 2: Generate parameters AND mission design for chosen algorithm
    param_prompt = f"""You are a roguelike level designer. The user described a SETTING/ATMOSPHERE.
Your job: INVENT a fitting mission for that setting, then generate parameters.

USER'S SETTING DESCRIPTION: "{user_prompt}"
CHOSEN ALGORITHM: {chosen_algo}

STEP 1 - INVENT A MISSION THAT FITS THE SETTING:

Based on the atmosphere/description, what mission makes sense?
- "dragon's lair" → linear_progression with boss fight
- "sprawling caves" → exploration to find treasures
- "crumbling ruins" → survival/escape mission
- "guarded vault" → key_hunt to unlock treasure
- "arena chambers" → multi_objective combat challenges
- "mysterious catacombs" → exploration to discover secrets

Mission Types:
- linear_progression: Clear path to climactic boss encounter
- exploration: Discover scattered rewards/secrets
- key_hunt: Find keys to unlock final area
- survival: Navigate dangers to reach safe zones
- multi_objective: Multiple different goals

STEP 2 - DESIGN OBJECTIVES (1-6) FOR YOUR MISSION:

Objective types: boss, treasure, key, safe_room, puzzle, miniboss, secret

Placement rules:
- end_of_longest_path: Furthest from start (perfect for final boss)
- dead_end: In branch paths (perfect for treasure/secrets)
- central_room: In largest room (perfect for miniboss/puzzle)
- hidden: Hard to find (perfect for secrets)
- checkpoint: Midway through (perfect for safe rooms)
- random_room: Any suitable location

Examples:
- Dragon's lair → linear_progression: [boss at end, treasure in dead_ends, puzzle in central]
- Sprawling caves → exploration: [5 treasures in hidden/dead_end locations]
- Crumbling ruins → survival: [3 safe_rooms at checkpoints, 1 key for exit]
- Guarded vault → key_hunt: [2 keys in dead_ends, treasure at end]

STEP 3 - SET PARAMETERS:

Map Size: width=50-60, height=35-45
Densities: enemy=0.05-0.15, treasure=0.03-0.10, trap=0.01-0.05
Lighting: 0.0=dark, 0.5=dim, 1.0=bright (match atmosphere!)
Room algorithms: max_rooms=10-20, room_size_min=4-8, room_size_max=8-15
Drunkard's walk: target_floor_percent=0.22-0.35, straight_bias=0.6-0.8
Cellular: initial_wall_probability=0.45-0.55, iterations=3-5

IMPORTANT: 
- INVENT a mission that fits the setting's mood/atmosphere
- Be creative with objectives and their placement
- Match lighting and parameters to the setting's feel

Return ONLY valid JSON matching the schema for {chosen_algo}."""

    # Select the appropriate config schema
    schema_map: dict[str, Any] = {
        "random_room_placement": RandomRoomConfig,
        "bsp": BSPConfig,
        "drunkards_walk": DrunkardConfig,
        "cellular_automata": CellularAutomataConfig,
        "hybrid_rooms_caves": HybridRoomsCavesConfig,
        "cellular_rooms": CellularRoomsConfig,
    }

    config_schema: LevelConfig = schema_map[chosen_algo]

    param_response: ChatResponse = chat(
        model=model,
        messages=[{"role": "user", "content": param_prompt}],
        format=config_schema.model_json_schema(),
    )

    if not param_response.message.content:
        raise ValueError("LLM returned empty parameters")

    config: LevelConfig = config_schema.model_validate_json(
        param_response.message.content
    )

    # Build log data
    log_data: dict[str, Any] = {
        "user_prompt": user_prompt,
        "model": model,
        "algorithm": chosen_algo,
        "reasoning": reasoning.reason,
        "algo_prompt": algo_prompt,
        "param_prompt": param_prompt,
        "response_content": param_response.message.content,
        "config": config.model_dump(),  # type: ignore
    }

    # Save log if requested
    if save_log:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / f"llm_generation_{timestamp}.json"
        with open(log_file, "w", encoding=locale.getencoding()) as file:
            json.dump(log_data, file, indent=2)

        print(f"Saved log to {log_file}")

    return config, log_data


# Test code - only runs when this file is executed directly
if __name__ == "__main__":
    print("=== LLM Level Generator Test ===")

    # Select model
    selected_model = select_model_interactive()
    print(f"\nUsing model: {selected_model}")

    # Get user prompt
    print("\n" + "=" * 50)
    print("Example prompts:")
    print("  - 'a dark, claustrophobic dungeon with many enemies'")
    print("  - 'a bright, open fortress with treasure rooms'")
    print("  - 'a scary cave system with winding passages'")
    print("=" * 50)

    user_input = input(
        "\nDescribe the level you want (or press Enter for default): "
    ).strip()
    if not user_input:
        user_input = "a balanced dungeon level with moderate difficulty"

    print(f"\nPrompt: {user_input}")
    print("\nGenerating level configuration...")

    try:
        level_config, log_data = generate_level_config(user_input, model=selected_model)

        print("\n" + "=" * 50)
        print("Generated Level Configuration:")
        print("=" * 50)

        # Convert to dict for pretty printing
        config_dict = level_config.model_dump()
        print(json.dumps(config_dict, indent=2))

        # Offer to save
        save = input("\n\nSave this configuration? (y/n): ").strip().lower()
        if save == "y":
            filename = input("Enter filename (without .json): ").strip()
            if filename:
                filepath = f"jsons/{filename}.json"
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(config_dict, f, indent=2)
                print(f"[SUCCESS] Saved to {filepath}")

    except Exception as e:
        print(f"\n[ERROR] Error generating level: {e}")
        import traceback

        traceback.print_exc()
