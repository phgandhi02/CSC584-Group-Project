"""
Contains the Game object which is a singleton that manages the DunGen game.
Game.run() contains the game flow logic. Object manages game logic, rendering,
and cleanup for pygame dep.
"""

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
        # initialize game variables
        self.running = True
        self._cwd: Path = Path.cwd()
        self.game_state = "start_menu"

        map_width: int | float = self.config["layout"]["map_width"]
        map_height: int | float = self.config["layout"]["map_height"]
        screen_width: int | float = map_width * TILE_SIZE
        screen_height: int | float = map_height * TILE_SIZE


        # Initialize Pygame
        pygame.init()

        # initialize pygame variables
        self._window = pygame.display.set_mode((800, 600))
        self._clock = pygame.time.Clock()
        # --- Initialize Renderer ---
        self._game_renderer = Renderer(int(screen_width), int(screen_height))

        icon_path: Path = self._cwd / "assets" / "icon.png"
        pygame.display.set_icon(pygame.image.load(icon_path))

    def run(self):
        """Game flow loop. Main high-level logic for game.
        """
        self.setup()
        while self.running:
            self.on_event()
            self.update()
            self.render()
            self._clock.tick(60)
        self.on_cleanup()

    def setup(self):
        """Setup the game object with any post-init
        """
        # ------------------------------- Pygame setup ------------------------------- #

        # init pygame if not already
        if pygame.get_init() is False:
            pygame.init()
        # Set caption to the game window
        pygame.display.set_caption("DunGen: A User Driven PCG Game")

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

        config_file_path: Path = Path.joinpath(
            Path.cwd(), "jsons", user_selected_config
        )
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
        
        return

    def on_event(self):
        """
        Function to handle user inputs for every game update loop.
        """
        # For every event that occured in the current game update
        for event in pygame.event.get():
            # -------------------------------- Close Game -------------------------------- #
            # if window close button clicked then stop running Game.
            if event.type == pygame.QUIT:
                self.running = False
                break

            # -------------------------------- Start Menu -------------------------------- #
            elif self.game_state == "start_menu":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.game_state = "game"
                    break

            # ------------------------------- Game Started ------------------------------- #
            # elif user presses a key then handle accordingly.
            elif event.type == pygame.KEYDOWN:
                # if the user presses left escape then stop the running Game and exit.
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    break
                # if user presses space then regenerate level
                elif event.key == pygame.K_r:
                    print("Regenerating level...")
                    try:
                        self.level_grid = generate_level(self.config)
                    except Exception as e:  # pylint: disable=broad-except
                        # Keep the old grid if regeneration fails
                        print(f"Error during level regeneration: {e}")

    def update(self):
        """
        Update game characters after capturing user inputs.
        """
        pass

    def render(self):
        """
        Render game after update.
        """
        if not self.running:
            return
        if self.game_state == "start_menu":
            self._game_renderer.draw_start_menu()
        elif self.game_state == "game_over":
            # self.game_renderer.draw_game_over_screen()
            pass
        else:
            self._game_renderer.draw_level(self.level_grid)
        pygame.display.flip()  # Update the full screen

    def on_cleanup(self):
        """Quits Pygame."""
        pygame.quit()
