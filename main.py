import json
import pygame
from src.pcg_generator import generate_level  # Import the generator function
from src.renderer import Renderer, TILE_SIZE          # Import the Renderer class


def main():
    # --- 1. Load Config ---
    try:
        with open('jsons/dense`.json', 'r') as f:  # Use our prototype config
            config = json.load(f)
    except FileNotFoundError:
        print("Error: map file not found!")
        return
    except json.JSONDecodeError:
        print("Error: map file is not valid JSON!")
        return

    # --- 2. Generate Level ---
    try:
        level_grid = generate_level(config)
    except KeyError as e:
        print(f"Error: Missing key in config JSON: {e}")
        return
    except Exception as e:  # Catch other potential errors during generation
        print(f"Error during level generation: {e}")
        return

    # --- 3. Initialize Renderer ---
    map_width = config['layout']['map_width']
    map_height = config['layout']['map_height']
    screen_width = map_width * TILE_SIZE
    screen_height = map_height * TILE_SIZE

    game_renderer = Renderer(screen_width, screen_height)

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
