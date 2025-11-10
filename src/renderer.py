"""
Contains Renderer object which renders the game and the map. Contains int
values for each tile for the map. Map is represented as a list[list[int]].

"""

from typing import Literal
import pygame
from pygame.font import Font

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

TILE_SIZE = 20  # Increased for better visibility


class Renderer:
    """Handles drawing the level grid using Pygame."""

    def __init__(self, screen_width: int, screen_height: int) -> None:
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.screen: pygame.Surface = pygame.display.set_mode(
            (screen_width, screen_height)
        )
        # Basic font for any text later
        self.font: Font = pygame.font.SysFont(None, 24)

    def draw_level(self, grid: list[list[int]]) -> None:
        """Draws the entire level grid onto the screen."""
        self.screen.fill(COLOR_BLACK)  # Clear screen

        map_height: int = len(grid)
        map_width: int = len(grid[0])

        for y in range(map_height):
            for x in range(map_width):
                tile: int = grid[y][x]
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)

                if tile == TILE_WALL:
                    pygame.draw.rect(self.screen, COLOR_DARK_GREY, rect)
                elif tile == TILE_FLOOR:
                    pygame.draw.rect(self.screen, COLOR_LIGHT_GREY, rect)
                # Add more tile types (enemies, treasure) later with different colors/sprites

    def draw_start_menu(self):
        """
        Draw Start Menu for Game.
        """
        self.screen.fill((0, 0, 0))
        font = pygame.font.SysFont("arial", 40)
        title = font.render("My Game", True, (255, 255, 255))
        start_button = font.render("Start", True, (255, 255, 255))
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
