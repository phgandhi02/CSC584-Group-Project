"""
Contains Renderer object which renders the game and the map. Contains int
values for each tile for the map. Map is represented as a list[list[int]].

"""
from pathlib import Path
from typing import Literal
import pygame
from pygame.font import Font
from src.camera import Camera

TILE_WALL = 0
TILE_FLOOR = 1

COLOR_BLACK: tuple[Literal[0], Literal[0], Literal[0]] = (0, 0, 0)
COLOR_DARK_GREY: tuple[Literal[50], Literal[50], Literal[50]] = (
    50,
    50,
    50,
)  # Wall color
COLOR_LIGHT_GREY: tuple[Literal[150], Literal[150], Literal[150]] = (
    150,
    150,
    150,
)  # Floor color

# Tile size for visibility
TILE_SIZE = 40

# Fixed window dimensions
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600


class Renderer:
    """Handles drawing the level grid using Pygame."""

    def __init__(self, screen_width: int, screen_height: int) -> None:
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.screen_margin_width  = 20
        self.screen: pygame.Surface = pygame.display.set_mode(
            (screen_width, screen_height)
        )
        # Basic font for any text later
        self.font: Font = pygame.font.SysFont(None, 24)
        self._cwd: Path = Path.cwd()
        self._assets_path = Path.cwd() / "assets"

        pygame.display.set_icon(pygame.image.load(self._assets_path / "icon.png"))
        self._bkgd_im = pygame.image.load(self._assets_path / "startmenu.png")

        # Load and cache player sprite
        self._player_sprite = pygame.image.load(self._assets_path / "guy.png")
        self._player_sprite = pygame.transform.scale(
            self._player_sprite, (TILE_SIZE, TILE_SIZE)
        )

        # Initialize camera
        self.camera: Camera = Camera(screen_width, screen_height, TILE_SIZE)

    def draw_level(
        self, grid: list[list[int]], player_pos: tuple[int, int] | None = None
    ) -> None:
        """Draws the visible portion of the level grid and player onto the screen.

        Args:
            grid: 2D list representing the level layout
            player_pos: Optional tuple of (x, y) grid coordinates for player position
        """
        self.screen.fill(COLOR_BLACK)  # Clear screen

        map_height: int = len(grid)
        map_width: int = len(grid[0])

        # Update camera with map dimensions
        self.camera.set_map_dimensions(map_width, map_height)

        # Get visible tile range from camera
        min_x, max_x, min_y, max_y = self.camera.get_visible_tile_range()

        # Draw only visible level tiles
        for y in range(min_y, max_y):
            for x in range(min_x, max_x):
                tile: int = grid[y][x]

                # Convert world coordinates to screen coordinates
                screen_x, screen_y = self.camera.world_to_screen(x, y)
                rect = pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)

                if tile == TILE_WALL:
                    pygame.draw.rect(self.screen, COLOR_DARK_GREY, rect)
                elif tile == TILE_FLOOR:
                    pygame.draw.rect(self.screen, COLOR_LIGHT_GREY, rect)
                # Add more tile types (enemies, treasure) later with different colors/sprites

        # Draw player sprite on top of the level
        if player_pos is not None:
            player_x, player_y = player_pos
            # Convert player world position to screen position
            screen_x, screen_y = self.camera.world_to_screen(player_x, player_y)
            self.screen.blit(self._player_sprite, (screen_x, screen_y))

    def draw_start_menu(self):
        """
        Draw Start Menu for Game.
        """
        self.screen.fill((0, 0, 0))
        self.screen.blit(self._bkgd_im, (20,0))
        font = pygame.font.SysFont("arial", 40)
        title = font.render("DunGen", True, (255, 255, 255))
        start_button = font.render("Press Space to Start", True, (255, 255, 255))
        self.screen.blit(
            title,
            (
                self.screen_width / 2 - title.get_width() / 2,
                self.screen_height / 2 - title.get_height() / 2,
            ),
        )
        self.screen.blit(
            start_button,
            (
                self.screen_width / 2 - start_button.get_width() / 2,
                self.screen_height / 2 + start_button.get_height() / 2,
            ),
        )

    def draw_selection_menu(self):
        """
        Draw Selection Menu for Game.
        TODO: Not being called by the game object because
        it is immediately goes to the game state.
        """
        self.screen.fill((0, 0, 0))
        margin_offset = self.screen_margin_width
        rect = pygame.Rect(margin_offset,margin_offset,
                           self.screen_width - margin_offset, self.screen_height - margin_offset)
        pygame.draw.rect(self.screen,(105,105,105), rect)
        font = pygame.font.SysFont("arial", 40)
        title = font.render("Select a default level description or " \
            "write your own in the terminal.", True, (255, 255, 255))
        self.screen.blit(
            title,
            (
                self.screen_width / 2 - title.get_width() / 2,
                self.screen_height / 2 - title.get_height() / 2,
            ),
        )
