"""
Contains the Game object which is a singleton that manages the DunGen game.
Game.run() contains the game flow logic. Object manages game logic, rendering,
and cleanup for pygame dep.
"""

# System Package Deps
from typing import Any

# External Package Deps
import pygame

# Repo Module Reps
from src.user_input import (
    verify_config_mission,
    get_user_input,
    place_mission_objectives,
)
from src.pcg_generator import generate_level
from src.renderer import Renderer, TILE_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT
from src.player import Player


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
        self.game_state = "start_menu"
        self.config: dict[str, Any] = {}
        self.level_grid: list[list[int]] = [[]]
        self.player: Player | None = None
        # self._game_renderer: Renderer

        # Initialize Pygame
        pygame.init()

        # Initialize Pygame Variables for Class Instance
        self._clock = pygame.time.Clock()

    def run(self) -> None:
        """Game flow loop. Main high-level logic for game."""
        self.setup()
        while self.running:
            self.on_event()
            if self.game_state == "start_menu":
                pass
            elif self.game_state == "selection_menu":
                self.selection_menu()
            else:
                self.update()

            self.render()
            self._clock.tick(60)
        self.on_cleanup()

    def setup(self):
        """Setup the game object with any post-init"""
        # ------------------------------- Pygame setup ------------------------------- #

        # init pygame if not already
        if pygame.get_init() is False:
            pygame.init()
        # Set caption to the game window
        pygame.display.set_caption("DunGen: A User Driven PCG Game")
        self._game_renderer = Renderer(600, 400)

        return

    def on_event(self) -> None:
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
                    self.game_state = "selection_menu"
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
                # Handle player movement with arrow keys (one move per key press)
                elif self.player is not None and self.game_state == "game":
                    if event.key == pygame.K_UP:
                        self.player.move(0, -1, self.level_grid)
                    elif event.key == pygame.K_DOWN:
                        self.player.move(0, 1, self.level_grid)
                    elif event.key == pygame.K_LEFT:
                        self.player.move(-1, 0, self.level_grid)
                    elif event.key == pygame.K_RIGHT:
                        self.player.move(1, 0, self.level_grid)

    def selection_menu(self) -> None:
        """
        Game behavior during the selection menu screen.
        """
        self.config = get_user_input()

        try:
            if "mission" in self.config:
                self.config = verify_config_mission(self.config)

            self.level_grid = generate_level(self.config)
            self.config = place_mission_objectives(self.config, self.level_grid)

            # Initialize player at the LLM-provided start position
            start_x, start_y = self.config['start_position']
            self.player = Player(start_x, start_y, TILE_SIZE)
        except KeyError as e:
            print(f"Error: Missing key in config JSON: {e}")
            return None
        except Exception as e:  # Catch other potential errors during generation
            print(f"Error during level generation: {e}")
            return None

        self.game_state = "game"
        self._game_renderer = Renderer(WINDOW_WIDTH, WINDOW_HEIGHT)

    def update(self) -> None:
        """
        Update game characters after capturing user inputs.
        Movement is now handled in on_event() for event-based input.
        """
        pass

    def render(self) -> None:
        """
        Render game after update.
        TODO: selection menu doesn't render because the selection_menu() function
        is called and then it immediately switches to the "game" game_state.
        """
        if not self.running:
            return
        if self.game_state == "start_menu":
            self._game_renderer.draw_start_menu()
        elif self.game_state == "selection_menu":
            self._game_renderer.draw_selection_menu()
        elif self.game_state == "game_over":
            # self.game_renderer.draw_game_over_screen()
            pass
        else:
            player_pos = self.player.get_position() if self.player else None
            # Update camera to follow player
            if player_pos is not None:
                self._game_renderer.camera.center_on(player_pos[0], player_pos[1])
            self._game_renderer.draw_level(self.level_grid, player_pos)
        pygame.display.flip()  # Update the full screen

    def on_cleanup(self) -> None:
        """Quits Pygame."""
        pygame.quit()
