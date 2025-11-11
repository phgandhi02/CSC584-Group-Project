"""
Camera system for handling viewport and rendering offset.

The Camera tracks a position in the world (in tile coordinates) and provides
methods to calculate which tiles are visible and how to convert world coordinates
to screen coordinates.
"""


class Camera:
    """Handles camera position, viewport calculations, and coordinate conversions."""

    def __init__(self, window_width: int, window_height: int, tile_size: int) -> None:
        """Initialize the camera.

        Args:
            window_width: Width of the game window in pixels
            window_height: Height of the game window in pixels
            tile_size: Size of each tile in pixels
        """
        self.window_width = window_width
        self.window_height = window_height
        self.tile_size = tile_size

        # Camera position in tile coordinates
        self.x: float = 0.0
        self.y: float = 0.0

        # Map dimensions
        self.map_width: int = 0
        self.map_height: int = 0

        # Calculate how many tiles fit in the viewport
        self.viewport_width_tiles = window_width // tile_size
        self.viewport_height_tiles = window_height // tile_size

    def set_map_dimensions(self, map_width: int, map_height: int) -> None:
        """Set the dimensions of the current map for bounds checking.

        Args:
            map_width: Width of the map in tiles
            map_height: Height of the map in tiles
        """
        self.map_width = map_width
        self.map_height = map_height

    def center_on(self, target_x: int, target_y: int) -> None:
        """Center the camera on a target position (e.g., player position).

        Args:
            target_x: X coordinate in tile space
            target_y: Y coordinate in tile space
        """
        # Center camera on target
        self.x = target_x
        self.y = target_y

        # Clamp camera to map bounds
        self._clamp_to_bounds()

    def _clamp_to_bounds(self) -> None:
        """Clamp camera position to ensure we don't show area outside the map."""
        # Calculate half viewport size
        half_viewport_width = self.viewport_width_tiles / 2
        half_viewport_height = self.viewport_height_tiles / 2

        # Clamp X coordinate
        if self.map_width <= self.viewport_width_tiles:
            # Center the map
            self.x = self.map_width / 2
        else:
            # Normal clamping
            self.x = max(half_viewport_width, self.x)
            self.x = min(self.map_width - half_viewport_width, self.x)

        # Clamp Y coordinate
        if self.map_height <= self.viewport_height_tiles:
            # Center the map
            self.y = self.map_height / 2
        else:
            # Normal clamping
            self.y = max(half_viewport_height, self.y)
            self.y = min(self.map_height - half_viewport_height, self.y)

    def get_visible_tile_range(self) -> tuple[int, int, int, int]:
        """Calculate which tiles are currently visible in the viewport.

        Returns:
            Tuple of (min_x, max_x, min_y, max_y) in tile coordinates
        """
        # Calculate the top-left corner of the viewport
        half_viewport_width = self.viewport_width_tiles / 2
        half_viewport_height = self.viewport_height_tiles / 2

        min_x = int(self.x - half_viewport_width)
        max_x = int(self.x + half_viewport_width) + 1
        min_y = int(self.y - half_viewport_height)
        max_y = int(self.y + half_viewport_height) + 1

        # Clamp to map bounds
        min_x = max(0, min_x)
        max_x = min(self.map_width, max_x)
        min_y = max(0, min_y)
        max_y = min(self.map_height, max_y)

        return (min_x, max_x, min_y, max_y)

    def world_to_screen(self, world_x: int, world_y: int) -> tuple[int, int]:
        """Convert world/tile coordinates to screen pixel coordinates.

        Args:
            world_x: X coordinate in tile space
            world_y: Y coordinate in tile space

        Returns:
            Tuple of (screen_x, screen_y) in pixel coordinates
        """
        # Calculate the top-left corner of the viewport in world space
        half_viewport_width = self.viewport_width_tiles / 2
        half_viewport_height = self.viewport_height_tiles / 2

        viewport_left = self.x - half_viewport_width
        viewport_top = self.y - half_viewport_height

        # Convert to screen coordinates
        screen_x = int((world_x - viewport_left) * self.tile_size)
        screen_y = int((world_y - viewport_top) * self.tile_size)

        return (screen_x, screen_y)

    def get_offset(self) -> tuple[int, int]:
        """Get the pixel offset for rendering.

        Returns:
            Tuple of (offset_x, offset_y) in pixels
        """
        half_viewport_width = self.viewport_width_tiles / 2
        half_viewport_height = self.viewport_height_tiles / 2

        offset_x = int((self.x - half_viewport_width) * self.tile_size)
        offset_y = int((self.y - half_viewport_height) * self.tile_size)

        return (offset_x, offset_y)
