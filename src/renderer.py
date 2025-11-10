"""
Contains Renderer object which renders the game and the map. Contains int
values for each tile for the map. Map is represented as a list[list[int]].

"""
from pathlib import Path
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

TILE_SIZE = 10  # Increased for better visibility


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
