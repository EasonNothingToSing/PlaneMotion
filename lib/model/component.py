"""
Model layer: Pure data models for components.
Contains only data structure and basic geometric calculations.
"""

import math
from abc import ABC, abstractmethod
from typing import Tuple


def _rotate_point(x: float, y: float, cx: float, cy: float, angle_deg: float) -> Tuple[float, float]:
    """Rotate a point around a center by degrees."""
    if angle_deg % 360 == 0:
        return x, y
    radians = math.radians(angle_deg)
    cos_a = math.cos(radians)
    sin_a = math.sin(radians)
    dx = x - cx
    dy = y - cy
    rx = dx * cos_a - dy * sin_a + cx
    ry = dx * sin_a + dy * cos_a + cy
    return rx, ry


class Component(ABC):
    """
    Abstract base class for all components (Model layer).
    Contains only data attributes and geometric calculations.
    No rendering or UI logic.
    """

    def __init__(self, x: float, y: float, color: Tuple[int, int, int] = (100, 100, 255)):
        """
        Initialize a component.
        
        Args:
            x: X-coordinate of the component center
            y: Y-coordinate of the component center
            color: RGB color tuple
        """
        self.x = x
        self.y = y
        self.color = color
        self.scale = 1.0
        self.rotation_deg = 0.0

    @abstractmethod
    def contains_point(self, x: float, y: float) -> bool:
        """
        Check if a point is inside the component.
        
        Args:
            x: X-coordinate to check
            y: Y-coordinate to check
            
        Returns:
            True if the point is inside the component
        """
        pass

    @abstractmethod
    def get_connection_point(self) -> Tuple[float, float]:
        """
        Get the connection point for lines.
        
        Returns:
            Tuple of (x, y) coordinates
        """
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        """
        Serialize component to dictionary.
        
        Returns:
            Dictionary representation of the component
        """
        pass

    @abstractmethod
    def from_dict(self, data: dict):
        """
        Deserialize component from dictionary.
        
        Args:
            data: Dictionary containing component data
        """
        pass

    def update_position(self, x: float, y: float):
        """
        Update component position.
        
        Args:
            x: New X-coordinate
            y: New Y-coordinate
        """
        self.x = x
        self.y = y

    def update_scale(self, delta: float):
        """
        Update component scale.
        
        Args:
            delta: Scale change amount (positive to increase, negative to decrease)
        """
        self.scale = max(0.25, min(4.0, self.scale + delta))

    def rotate(self, delta_deg: float):
        """Rotate the component by degrees (clockwise)."""
        self.rotation_deg = (self.rotation_deg + delta_deg) % 360


class Circle(Component):
    """Circle component implementation."""

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

    def get_connection_point(self) -> Tuple[float, float]:
        """Get the center point for connections."""
        return (self.x, self.y)

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


class Rectangle(Component):
    """Rectangle component implementation."""

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
        if self.rotation_deg % 360 != 0:
            x, y = _rotate_point(x, y, self.x, self.y, -self.rotation_deg)
        half_width = self.width / 2
        half_height = self.height / 2
        return (self.x - half_width <= x <= self.x + half_width and
                self.y - half_height <= y <= self.y + half_height)

    def get_vertices(self):
        """Get rectangle vertices in world coordinates (clockwise)."""
        half_w = self.width / 2
        half_h = self.height / 2
        local = [
            (self.x - half_w, self.y - half_h),
            (self.x + half_w, self.y - half_h),
            (self.x + half_w, self.y + half_h),
            (self.x - half_w, self.y + half_h)
        ]
        if self.rotation_deg % 360 == 0:
            return local
        return [_rotate_point(x, y, self.x, self.y, self.rotation_deg) for x, y in local]

    def get_connection_point(self) -> Tuple[float, float]:
        """Get the center point for connections."""
        return (self.x, self.y)

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


class Trapezoid(Component):
    """Trapezoid component implementation."""

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

    def _get_local_vertices(self):
        """Get trapezoid vertices centered at origin (clockwise)."""
        half_h = self.height / 2
        half_top = self.top_width / 2
        half_bottom = self.bottom_width / 2
        return [
            (-half_top, -half_h),
            (half_top, -half_h),
            (half_bottom, half_h),
            (-half_bottom, half_h)
        ]

    def get_vertices(self):
        """Get trapezoid vertices in world coordinates (clockwise)."""
        local = self._get_local_vertices()
        world = [(self.x + vx, self.y + vy) for vx, vy in local]
        if self.rotation_deg % 360 == 0:
            return world
        return [_rotate_point(x, y, self.x, self.y, self.rotation_deg) for x, y in world]

    def contains_point(self, x: float, y: float) -> bool:
        """Check if a point is inside the trapezoid (ray casting)."""
        if self.rotation_deg % 360 != 0:
            x, y = _rotate_point(x, y, self.x, self.y, -self.rotation_deg)
        vertices = [(self.x + vx, self.y + vy) for vx, vy in self._get_local_vertices()]
        inside = False
        j = len(vertices) - 1
        for i in range(len(vertices)):
            xi, yi = vertices[i]
            xj, yj = vertices[j]
            intersects = ((yi > y) != (yj > y)) and \
                         (x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi)
            if intersects:
                inside = not inside
            j = i
        return inside

    def get_connection_point(self) -> Tuple[float, float]:
        """Get the center point for connections."""
        return (self.x, self.y)

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
