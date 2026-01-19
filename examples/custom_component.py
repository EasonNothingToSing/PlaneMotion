"""
Example of creating and registering custom components.

This demonstrates how to extend the engine with your own component types.
"""

import math
from typing import Tuple, List
from planemotion import PlaneMotionEngine, Component
from planemotion.components import Circle, Rectangle


class Triangle(Component):
    """A custom triangle component."""
    
    def __init__(self, x: float, y: float, size: float = 50.0):
        """
        Initialize triangle.
        
        Args:
            x: X position
            y: Y position
            size: Triangle size (height)
        """
        super().__init__(x, y)
        self.size = size
        self.color = (255, 100, 50)  # Orange
    
    def contains_point(self, x: float, y: float) -> bool:
        """Check if point is inside triangle."""
        vertices = self.get_vertices()
        if len(vertices) != 3:
            return False
        
        # Use cross product method
        def sign(p1, p2, p3):
            return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
        
        d1 = sign((x, y), vertices[0], vertices[1])
        d2 = sign((x, y), vertices[1], vertices[2])
        d3 = sign((x, y), vertices[2], vertices[0])
        
        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
        
        return not (has_neg and has_pos)
    
    def get_vertices(self) -> List[Tuple[float, float]]:
        """Get triangle vertices."""
        # Equilateral triangle pointing up
        half_base = self.size * 0.5
        height = self.size * (math.sqrt(3) / 2)
        
        # Local coordinates (centered at origin)
        local_vertices = [
            (0, -height / 2),          # Top
            (-half_base, height / 2),  # Bottom left
            (half_base, height / 2)    # Bottom right
        ]
        
        # Apply rotation and translation
        rotated = []
        for lx, ly in local_vertices:
            rx, ry = self._rotate_point(lx, ly, self.rotation_deg)
            rotated.append((
                self.x + rx * self.scale,
                self.y + ry * self.scale
            ))
        
        return rotated


class Star(Component):
    """A custom star component."""
    
    def __init__(self, x: float, y: float, outer_radius: float = 50.0, inner_radius: float = 20.0, points: int = 5):
        """
        Initialize star.
        
        Args:
            x: X position
            y: Y position
            outer_radius: Outer radius of star points
            inner_radius: Inner radius between points
            points: Number of star points
        """
        super().__init__(x, y)
        self.outer_radius = outer_radius
        self.inner_radius = inner_radius
        self.points = points
        self.color = (255, 215, 0)  # Gold
    
    def contains_point(self, x: float, y: float) -> bool:
        """Check if point is inside star (rough approximation)."""
        # Simple distance check
        dx = x - self.x
        dy = y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        return dist < self.outer_radius * self.scale
    
    def get_vertices(self) -> List[Tuple[float, float]]:
        """Get star vertices."""
        vertices = []
        angle_step = 2 * math.pi / self.points
        
        for i in range(self.points):
            # Outer point
            outer_angle = i * angle_step - math.pi / 2
            outer_x = self.outer_radius * math.cos(outer_angle)
            outer_y = self.outer_radius * math.sin(outer_angle)
            rx, ry = self._rotate_point(outer_x, outer_y, self.rotation_deg)
            vertices.append((
                self.x + rx * self.scale,
                self.y + ry * self.scale
            ))
            
            # Inner point
            inner_angle = (i + 0.5) * angle_step - math.pi / 2
            inner_x = self.inner_radius * math.cos(inner_angle)
            inner_y = self.inner_radius * math.sin(inner_angle)
            rx, ry = self._rotate_point(inner_x, inner_y, self.rotation_deg)
            vertices.append((
                self.x + rx * self.scale,
                self.y + ry * self.scale
            ))
        
        return vertices


def custom_menu_provider(engine):
    """
    Provide custom menu structure.
    
    Args:
        engine: The engine instance
    
    Returns:
        Dictionary with menu definitions
    """
    return {
        'file': [
            {"type": "item", "label": "New Scene", "action": lambda: print("New scene")},
            {"type": "separator"},
            {"type": "item", "label": "Open", "action": engine.open_file_dialog},
            {"type": "item", "label": "Save", "action": lambda: engine.save_scene()},
            {"type": "separator"},
            {"type": "item", "label": "Exit", "action": lambda: setattr(engine, 'running', False)},
        ],
        'edit': [
            {
                "type": "item",
                "label": "Insert",
                "submenu": [
                    {"type": "item", "label": "Triangle", "action": lambda: engine.insert_component_at_click('triangle')},
                    {"type": "item", "label": "Star", "action": lambda: engine.insert_component_at_click('star')},
                    {"type": "separator"},
                    {"type": "item", "label": "Circle", "action": lambda: engine.insert_component_at_click('circle')},
                    {"type": "item", "label": "Rectangle", "action": lambda: engine.insert_component_at_click('rectangle')},
                ]
            },
            {"type": "separator"},
            {"type": "item", "label": "Delete", "action": engine.viewmodel.delete_selected},
        ]
    }


def ui_customizer(view):
    """
    Customize the UI.
    
    Args:
        view: The view instance to customize
    """
    # Example: Change background color
    view.background_color = (240, 248, 255)  # Alice blue


def main():
    """Run the custom component example."""
    # Create engine
    engine = PlaneMotionEngine(
        width=1400,
        height=900,
        title="PlaneMotion - Custom Components"
    )
    
    # Register custom components
    engine.register_component_type('triangle', Triangle)
    engine.register_component_type('star', Star)
    
    # Also register built-in components
    engine.register_component_type('circle', Circle)
    engine.register_component_type('rectangle', Rectangle)
    
    # Set custom menu provider
    engine.set_menu_provider(custom_menu_provider)
    
    # Set UI customizer
    engine.set_ui_customizer(ui_customizer)
    
    # Run the engine
    engine.run()


if __name__ == '__main__':
    main()
