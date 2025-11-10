"""Player entity for the roguelike game."""

from pathlib import Path
import pygame


class Player:
    """Represents the player character in the game."""

    TILE_FLOOR = 1  # Must match the constant in pcg_generator.py

    def __init__(self, x: int, y: int, tile_size: int = 10) -> None:
        """
        Initialize the player at the given grid position.

        Args:
            x: Grid x-coordinate
            y: Grid y-coordinate
            tile_size: Size of each tile in pixels (default 10)
        """
        self.x = x
        self.y = y
        self.tile_size = tile_size

        # Load and scale the player sprite
        assets_path = Path(__file__).parent.parent / "assets"
        sprite_path = assets_path / "guy.png"
        self.sprite = pygame.image.load(str(sprite_path))
        self.sprite = pygame.transform.scale(self.sprite, (tile_size, tile_size))

    def move(self, dx: int, dy: int, level_grid: list[list[int]]) -> bool:
        """
        Attempt to move the player by the given delta.

        Args:
            dx: Change in x-coordinate (-1, 0, or 1)
            dy: Change in y-coordinate (-1, 0, or 1)
            level_grid: 2D grid of the level (grid[y][x])

        Returns:
            True if the move was successful, False if blocked
        """
        new_x = self.x + dx
        new_y = self.y + dy

        # Check bounds
        if new_y < 0 or new_y >= len(level_grid):
            return False
        if new_x < 0 or new_x >= len(level_grid[0]):
            return False

        # Check for wall collision
        if level_grid[new_y][new_x] != self.TILE_FLOOR:
            return False

        # Move is valid
        self.x = new_x
        self.y = new_y
        return True

    def get_position(self) -> tuple[int, int]:
        """
        Get the player's current grid position.

        Returns:
            Tuple of (x, y) grid coordinates
        """
        return (self.x, self.y)

    def get_pixel_position(self) -> tuple[int, int]:
        """
        Get the player's position in pixel coordinates.

        Returns:
            Tuple of (x, y) pixel coordinates
        """
        return (self.x * self.tile_size, self.y * self.tile_size)
