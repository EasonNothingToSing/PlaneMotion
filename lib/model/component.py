"""
Model layer: Pure data models for components.
Contains only data structure and basic geometric calculations.
"""

import math
from abc import ABC, abstractmethod
from typing import Tuple


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
        self.scale = max(0.5, min(3.0, self.scale + delta))


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
            'scale': self.scale
        }

    def from_dict(self, data: dict):
        """Deserialize circle from dictionary."""
        self.x = data['x']
        self.y = data['y']
        self.base_radius = data['base_radius']
        self.color = tuple(data['color'])
        self.scale = data['scale']


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
        half_width = self.width / 2
        half_height = self.height / 2
        return (self.x - half_width <= x <= self.x + half_width and
                self.y - half_height <= y <= self.y + half_height)

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
            'scale': self.scale
        }

    def from_dict(self, data: dict):
        """Deserialize rectangle from dictionary."""
        self.x = data['x']
        self.y = data['y']
        self.base_width = data['base_width']
        self.base_height = data['base_height']
        self.color = tuple(data['color'])
        self.scale = data['scale']
