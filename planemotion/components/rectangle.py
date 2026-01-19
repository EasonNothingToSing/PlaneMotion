"""Rectangle component implementation."""

import math
from typing import Tuple, List
from planemotion.core.base_component import Component


class Rectangle(Component):
    """Rectangle component."""

    def __init__(self, x: float, y: float, width: float = 60, height: float = 40, 
                 color: Tuple[int, int, int] = (255, 100, 100)):
        """
        Initialize a rectangle component.
        
        Args:
            x: X-coordinate of the rectangle center
            y: Y-coordinate of the rectangle center
            width: Base width of the rectangle
            height: Base height of the rectangle
            color: RGB color tuple
        """
        super().__init__(x, y, color)
        self.base_width = width
        self.base_height = height

    @property
    def width(self) -> float:
        """Get the scaled width."""
        return self.base_width * self.scale

    @property
    def height(self) -> float:
        """Get the scaled height."""
        return self.base_height * self.scale

    def contains_point(self, x: float, y: float) -> bool:
        """Check if a point is inside the rectangle."""
        # Transform point to local space (undo rotation)
        if self.rotation_deg % 360 != 0:
            dx = x - self.x
            dy = y - self.y
            radians = -math.radians(self.rotation_deg)
            cos_a = math.cos(radians)
            sin_a = math.sin(radians)
            local_x = dx * cos_a - dy * sin_a + self.x
            local_y = dx * sin_a + dy * cos_a + self.y
            x, y = local_x, local_y
        
        half_width = self.width / 2
        half_height = self.height / 2
        return (self.x - half_width <= x <= self.x + half_width and
                self.y - half_height <= y <= self.y + half_height)

    def get_vertices(self) -> List[Tuple[float, float]]:
        """Get rectangle vertices in world coordinates (clockwise)."""
        half_w = self.width / 2
        half_h = self.height / 2
        local = [
            (-half_w, -half_h),
            (half_w, -half_h),
            (half_w, half_h),
            (-half_w, half_h)
        ]
        
        # Apply rotation and translation
        vertices = []
        for lx, ly in local:
            rx, ry = self._rotate_point(lx, ly, self.rotation_deg)
            vertices.append((self.x + rx, self.y + ry))
        
        return vertices

    def to_dict(self) -> dict:
        """Serialize rectangle to dictionary."""
        return {
            'type': 'rectangle',
            'x': self.x,
            'y': self.y,
            'base_width': self.base_width,
            'base_height': self.base_height,
            'color': self.color,
            'scale': self.scale,
            'rotation_deg': self.rotation_deg
        }

    def from_dict(self, data: dict):
        """Deserialize rectangle from dictionary."""
        self.x = data['x']
        self.y = data['y']
        self.base_width = data['base_width']
        self.base_height = data['base_height']
        self.color = tuple(data['color'])
        self.scale = data['scale']
        self.rotation_deg = data.get('rotation_deg', 0.0)
