"""
Base Component class for PlaneMotion engine.

All custom components must inherit from this class.
"""

from abc import ABC, abstractmethod
from typing import Tuple, List, Dict, Any
import math


class Component(ABC):
    """
    Abstract base class for all components in the PlaneMotion engine.
    
    Custom components must implement:
    - contains_point(x, y): Point collision detection
    - get_vertices(): Return polygon vertices for rendering
    
    Attributes:
        x (float): Center X position in world coordinates
        y (float): Center Y position in world coordinates
        color (tuple): RGB color tuple (0-255)
        scale (float): Uniform scale factor (default 1.0)
        rotation_deg (float): Rotation in degrees (default 0.0)
    """
    
    def __init__(self, x: float, y: float, color: Tuple[int, int, int] = (100, 150, 200)):
        """
        Initialize a component.
        
        Args:
            x: Center X position
            y: Center Y position
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
        Check if a point is inside this component.
        
        Args:
            x: World X coordinate
            y: World Y coordinate
            
        Returns:
            True if point is inside component
        """
        pass
    
    @abstractmethod
    def get_vertices(self) -> List[Tuple[float, float]]:
        """
        Get component vertices for rendering.
        
        Returns:
            List of (x, y) tuples representing vertices
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize component to dictionary.
        
        Returns:
            Dictionary representation of component
        """
        return {
            'type': self.__class__.__name__,
            'x': self.x,
            'y': self.y,
            'color': self.color,
            'scale': self.scale,
            'rotation_deg': self.rotation_deg,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Component':
        """
        Deserialize component from dictionary.
        
        Args:
            data: Dictionary representation
            
        Returns:
            Component instance
        """
        component = cls(
            x=data['x'],
            y=data['y'],
            color=tuple(data['color'])
        )
        component.scale = data.get('scale', 1.0)
        component.rotation_deg = data.get('rotation_deg', 0.0)
        return component
    
    def _rotate_point(self, px: float, py: float, cx: float, cy: float, angle_deg: float) -> Tuple[float, float]:
        """
        Rotate a point around a center.
        
        Args:
            px, py: Point to rotate
            cx, cy: Center of rotation
            angle_deg: Rotation angle in degrees
            
        Returns:
            Rotated (x, y) coordinates
        """
        if angle_deg == 0:
            return px, py
        
        angle_rad = math.radians(angle_deg)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        dx = px - cx
        dy = py - cy
        
        rotated_x = cx + (dx * cos_a - dy * sin_a)
        rotated_y = cy + (dx * sin_a + dy * cos_a)
        
        return rotated_x, rotated_y
