"""Trapezoid component implementation."""

import math
from typing import Tuple, List
from planemotion.core.base_component import Component


class Trapezoid(Component):
    """Trapezoid component."""

    def __init__(self, x: float, y: float, top_width: float = 50, bottom_width: float = 90,
                 height: float = 50, color: Tuple[int, int, int] = (120, 200, 140)):
        """
        Initialize a trapezoid component.
        
        Args:
            x: X-coordinate of the trapezoid center
            y: Y-coordinate of the trapezoid center
            top_width: Base top width
            bottom_width: Base bottom width
            height: Base height
            color: RGB color tuple
        """
        super().__init__(x, y, color)
        self.base_top_width = top_width
        self.base_bottom_width = bottom_width
        self.base_height = height

    @property
    def top_width(self) -> float:
        """Get the scaled top width."""
        return self.base_top_width * self.scale

    @property
    def bottom_width(self) -> float:
        """Get the scaled bottom width."""
        return self.base_bottom_width * self.scale

    @property
    def height(self) -> float:
        """Get the scaled height."""
        return self.base_height * self.scale

    def _get_local_vertices(self) -> List[Tuple[float, float]]:
        """Get trapezoid vertices centered at origin (clockwise)."""
        half_h = self.height / 2
        half_top = self.top_width / 2
        half_bottom = self.bottom_width / 2
        return [
            (-half_top, -half_h),      # Top left
            (half_top, -half_h),       # Top right
            (half_bottom, half_h),     # Bottom right
            (-half_bottom, half_h)     # Bottom left
        ]

    def get_vertices(self) -> List[Tuple[float, float]]:
        """Get trapezoid vertices in world coordinates (clockwise)."""
        local = self._get_local_vertices()
        
        # Apply rotation and translation
        vertices = []
        for lx, ly in local:
            rx, ry = self._rotate_point(lx, ly, self.rotation_deg)
            vertices.append((self.x + rx, self.y + ry))
        
        return vertices

    def contains_point(self, x: float, y: float) -> bool:
        """Check if a point is inside the trapezoid (ray casting)."""
        # Transform to local space if rotated
        if self.rotation_deg % 360 != 0:
            dx = x - self.x
            dy = y - self.y
            radians = -math.radians(self.rotation_deg)
            cos_a = math.cos(radians)
            sin_a = math.sin(radians)
            local_x = dx * cos_a - dy * sin_a
            local_y = dx * sin_a + dy * cos_a
        else:
            local_x = x - self.x
            local_y = y - self.y
        
        # Ray casting algorithm
        vertices = self._get_local_vertices()
        inside = False
        j = len(vertices) - 1
        for i in range(len(vertices)):
            xi, yi = vertices[i]
            xj, yj = vertices[j]
            intersects = ((yi > local_y) != (yj > local_y)) and \
                         (local_x < (xj - xi) * (local_y - yi) / (yj - yi + 1e-9) + xi)
            if intersects:
                inside = not inside
            j = i
        return inside

    def to_dict(self) -> dict:
        """Serialize trapezoid to dictionary."""
        return {
            'type': 'trapezoid',
            'x': self.x,
            'y': self.y,
            'base_top_width': self.base_top_width,
            'base_bottom_width': self.base_bottom_width,
            'base_height': self.base_height,
            'color': self.color,
            'scale': self.scale,
            'rotation_deg': self.rotation_deg
        }

    def from_dict(self, data: dict):
        """Deserialize trapezoid from dictionary."""
        self.x = data['x']
        self.y = data['y']
        self.base_top_width = data['base_top_width']
        self.base_bottom_width = data['base_bottom_width']
        self.base_height = data['base_height']
        self.color = tuple(data['color'])
        self.scale = data['scale']
        self.rotation_deg = data.get('rotation_deg', 0.0)
