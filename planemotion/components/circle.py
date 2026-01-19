"""Circle component implementation."""

import math
from typing import Tuple
from planemotion.core.base_component import Component


class Circle(Component):
    """Circle component."""

    def __init__(self, x: float, y: float, radius: float = 30, color: Tuple[int, int, int] = (100, 100, 255)):
        """
        Initialize a circle component.
        
        Args:
            x: X-coordinate of the circle center
            y: Y-coordinate of the circle center
            radius: Base radius of the circle
            color: RGB color tuple
        """
        super().__init__(x, y, color)
        self.base_radius = radius

    @property
    def radius(self) -> float:
        """Get the scaled radius."""
        return self.base_radius * self.scale

    def contains_point(self, x: float, y: float) -> bool:
        """Check if a point is inside the circle."""
        distance = math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
        return distance <= self.radius

    def get_vertices(self):
        """Get circle vertices (approximated as polygon)."""
        # Approximate circle with 32 points
        points = []
        segments = 32
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            local_x = self.radius * math.cos(angle)
            local_y = self.radius * math.sin(angle)
            rx, ry = self._rotate_point(local_x, local_y, self.rotation_deg)
            points.append((self.x + rx, self.y + ry))
        return points

    def to_dict(self) -> dict:
        """Serialize circle to dictionary."""
        return {
            'type': 'circle',
            'x': self.x,
            'y': self.y,
            'base_radius': self.base_radius,
            'color': self.color,
            'scale': self.scale,
            'rotation_deg': self.rotation_deg
        }

    def from_dict(self, data: dict):
        """Deserialize circle from dictionary."""
        self.x = data['x']
        self.y = data['y']
        self.base_radius = data['base_radius']
        self.color = tuple(data['color'])
        self.scale = data['scale']
        self.rotation_deg = data.get('rotation_deg', 0.0)
