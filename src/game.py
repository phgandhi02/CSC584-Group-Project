from pathlib import Path
import json
import locale
from typing import Any

import pygame

from src.pcg_generator import generate_level  # Import the generator function
from src.renderer import Renderer, TILE_SIZE

class Game:
    """
    Singleton class to manage the DunGen top-down dungeon crawler game.

    A rogue-like game that uses PCG and LLMs to automatically generate levels
    based on the input that a user gives. This object manages the behavior
    related to game logic, rendering, and user input.

    Public methods:
        run(): Manages the game loop after the Game obj is created.

    Attributes:
        _instance: Class attribute to hold the single instance of the class.
    """

    def __init__(self):
        """
        Create singleton instance of the game object. This object handles the
        interface for game logic, rendering, and user input.
        """
        pygame.init()
        self.window = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("DunGen: A User Driven PCG Game")
        self.cwd: Path = Path.cwd()
        icon_path: Path = self.cwd / "assets" / "icon.png"
        pygame.display.set_icon(pygame.image.load(icon_path))
        self.clock = pygame.time.Clock()
        self.x = 120
        self.y = 120
        self.running = True

    def run(self):
        self.on_init()
        while self.running:
            self.on_event()
            self.update()
            self.render()
            self.clock.tick(60)
        self.on_cleanup()

    def on_init(self):
        print("Hi there!, Please choose one of the maps below to get started.")
        user_selected_config: str = input(
            "Type the corresponding number to load the map params. \
            \n1.dense \
            \n2.maze \
            \n3.open \
            \n4.sample \
            \n"
        )
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

        config_file_path: Path = Path.joinpath(Path.cwd(),"jsons", user_selected_config)
        # --- 1. Load Config ---
        try:
            with open(config_file_path, "r", encoding=locale.getencoding()) as f:
                # Use our prototype config
                self.config: dict[str, Any] = json.load(f)
        except FileNotFoundError:
            print("Error: map file not found!")
            return
        except json.JSONDecodeError:
            print("Error: map file is not valid JSON!")
            return
         # --- 2. Generate Level ---
        try:
            self.level_grid: list[list[int]] = generate_level(self.config)
        except KeyError as e:
            print(f"Error: Missing key in config JSON: {e}")
            return
        except Exception as e:  # Catch other potential errors during generation
            print(f"Error during level generation: {e}")
            return
        # --- 3. Initialize Renderer ---
        map_width: int | float = self.config['layout']['map_width']
        map_height: int | float = self.config['layout']['map_height']
        screen_width: int | float = map_width * TILE_SIZE
        screen_height: int | float = map_height * TILE_SIZE

        self.game_renderer = Renderer(int(screen_width), int(screen_height))
        return 

    def on_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    break
                elif event.key == pygame.K_SPACE:
                    print("Regenerating level...")
                    try:
                        self.level_grid = generate_level(self.config)
                    except Exception as e:
                        print(f"Error during level regeneration: {e}")
                        # Keep the old grid if regeneration fails
                elif event.key == pygame.K_RIGHT:
                    self.x += 8
                elif event.key == pygame.K_LEFT:
                    self.x -= 8
                elif event.key == pygame.K_DOWN:
                    self.y += 8
                elif event.key == pygame.K_UP:
                    self.y -= 8

    def update(self):
        pass

    def render(self):
        # self.window.fill((0, 0, 0))
        # pygame.draw.rect(self.window, (0, 0, 255), (self.x, self.y, 400, 240))
        # pygame.display.update()
        # Drawing
        if not self.running:
            return
        self.game_renderer.draw_level(self.level_grid)
        pygame.display.flip()  # Update the full screen

    def on_cleanup(self):
        """ Quits Pygame. """
        pygame.quit()