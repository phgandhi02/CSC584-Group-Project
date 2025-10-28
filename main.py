# Package Dependencies
import pygame

# File depedencies
from src.pcg_generator import generate_level  # Import the generator function
from src.renderer import Renderer, TILE_SIZE          # Import the Renderer class

# Python modules
import json
from typing import Any, LiteralString
import os


def main() -> None:
    print("Hi there!, Please choose one of the maps below to get started.")
    user_selected_config: str = input("Type the corresponding number to load the map params. \
          \n1.dense \
          \n2.maze \
          \n3.open \
          \n4.sample \
          \n")
    match user_selected_config:
        case "1":
            user_selected_config = "dense.json"
        case "2":
            user_selected_config = "maze.json"
        case "3":
            user_selected_config = "open.json"
        case "4":
            user_selected_config = "sample.json"
        case _:
            user_selected_config = "sample.json"

    config_file_path: LiteralString = os.path.join(
        "jsons", user_selected_config)
    # --- 1. Load Config ---
    try:
        with open(config_file_path, 'r') as f:  # Use our prototype config
            config: dict[str, Any] = json.load(f)
    except FileNotFoundError:
        print("Error: map file not found!")
        return
    except json.JSONDecodeError:
        print("Error: map file is not valid JSON!")
        return

    # --- 2. Generate Level ---
    try:
        level_grid: list[list[int]] = generate_level(config)
    except KeyError as e:
        print(f"Error: Missing key in config JSON: {e}")
        return
    except Exception as e:  # Catch other potential errors during generation
        print(f"Error during level generation: {e}")
        return

    # --- 3. Initialize Renderer ---
    map_width: int | float = config['layout']['map_width']
    map_height: int | float = config['layout']['map_height']
    screen_width: int | float = map_width * TILE_SIZE
    screen_height: int | float = map_height * TILE_SIZE

    game_renderer = Renderer(int(screen_width), int(screen_height))

    # --- 4. Main Game Loop ---
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Allow quitting with Esc
                    running = False
                if event.key == pygame.K_SPACE:  # Regenerate on Spacebar
                    print("Regenerating level...")
                    try:
                        level_grid = generate_level(config)
                    except Exception as e:
                        print(f"Error during level regeneration: {e}")
                        # Keep the old grid if regeneration fails

        # Drawing
        game_renderer.draw_level(level_grid)
        pygame.display.flip()  # Update the full screen

    # --- 5. Shutdown ---
    game_renderer.shutdown()


if __name__ == "__main__":
    main()
