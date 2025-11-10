from typing import Literal
import pygame
from pygame.font import Font

TILE_WALL = 0
TILE_FLOOR = 1

COLOR_BLACK: tuple[Literal[0], Literal[0], Literal[0]] = (0, 0, 0)
COLOR_DARK_GREY: tuple[Literal[50], Literal[50], Literal[50]] = (50, 50, 50)
COLOR_LIGHT_GREY: tuple[Literal[150], Literal[150], Literal[150]] = (150, 150, 150)

TILE_SIZE = 20  # Increased for better visibility


class Renderer:
    """ Handles drawing the level grid using Pygame. """

    def __init__(self, screen_width: int, screen_height: int) -> None:
        """ Initializes Pygame and sets up the screen. """
        pygame.init()
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.screen: pygame.Surface = pygame.display.set_mode(
            (screen_width, screen_height))
        pygame.display.set_caption("LLM PCG Dungeon")
        # Basic font for any text later
        self.font: Font = pygame.font.SysFont(None, 24)

    def draw_level(self, grid: list[list[int]]) -> None:
        """ Draws the entire level grid onto the screen. """
        self.screen.fill(COLOR_BLACK)  # Clear screen

        map_height: int = len(grid)
        map_width: int = len(grid[0])

        for y in range(map_height):
            for x in range(map_width):
                tile: int = grid[y][x]
                rect = pygame.Rect(x * TILE_SIZE, y *
                                   TILE_SIZE, TILE_SIZE, TILE_SIZE)

                if tile == TILE_WALL:
                    pygame.draw.rect(self.screen, COLOR_DARK_GREY, rect)
                elif tile == TILE_FLOOR:
                    pygame.draw.rect(self.screen, COLOR_LIGHT_GREY, rect)
                # Add more tile types (enemies, treasure) later with different colors/sprites

    def shutdown(self) -> None:
        """ Quits Pygame. """
        pygame.quit()
