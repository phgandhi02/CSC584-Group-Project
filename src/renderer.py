import pygame

TILE_WALL = 0
TILE_FLOOR = 1

COLOR_BLACK = (0, 0, 0)
COLOR_DARK_GREY = (50, 50, 50)  # Wall color
COLOR_LIGHT_GREY = (150, 150, 150) # Floor color

TILE_SIZE = 10 # Pixels per tile

class Renderer:
    """ Handles drawing the level grid using Pygame. """

    def __init__(self, screen_width: int, screen_height: int):
        """ Initializes Pygame and sets up the screen. """
        pygame.init()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("LLM PCG Dungeon")
        self.font = pygame.font.SysFont(None, 24) # Basic font for any text later

    def draw_level(self, grid: list[list[int]]):
        """ Draws the entire level grid onto the screen. """
        self.screen.fill(COLOR_BLACK) # Clear screen

        map_height = len(grid)
        map_width = len(grid[0])

        for y in range(map_height):
            for x in range(map_width):
                tile = grid[y][x]
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)

                if tile == TILE_WALL:
                    pygame.draw.rect(self.screen, COLOR_DARK_GREY, rect)
                elif tile == TILE_FLOOR:
                    pygame.draw.rect(self.screen, COLOR_LIGHT_GREY, rect)
                # Add more tile types (enemies, treasure) later with different colors/sprites


    def shutdown(self):
        """ Quits Pygame. """
        pygame.quit()