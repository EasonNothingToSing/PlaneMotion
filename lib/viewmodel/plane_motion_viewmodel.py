"""
ViewModel layer: Business logic and state management.
Handles user interactions, component state, and coordinates between Model and View.
"""

from typing import List, Optional, Tuple
from lib.model import Component, Circle, Rectangle, Connection


class PlaneMotionViewModel:
    """
    ViewModel for the PlaneMotion engine.
    Manages application state and business logic.
    """

    def __init__(self):
        """Initialize the ViewModel."""
        # Component and connection storage
        self.components: List[Component] = []
        self.connections: List[Connection] = []
        
        # Selection state
        self.selected_component: Optional[Component] = None
        
        # Dragging state
        self.dragging_component: Optional[Component] = None
        self.drag_offset_x = 0.0
        self.drag_offset_y = 0.0
        
        # Connection creation state
        self.connection_start: Optional[Component] = None
        
        # Notifications for View
        self.status_message: str = ""

    # Component creation methods
    def create_circle(self, x: float, y: float, radius: float = 30, 
                     color: Tuple[int, int, int] = (100, 100, 255)) -> Circle:
        """
        Create a new circle component.
        
        Args:
            x: X-coordinate
            y: Y-coordinate
            radius: Circle radius
            color: RGB color tuple
            
        Returns:
            Created Circle instance
        """
        circle = Circle(x, y, radius, color)
        self.components.append(circle)
        self.status_message = "Circle created"
        return circle

    def create_rectangle(self, x: float, y: float, width: float = 60, height: float = 40,
                        color: Tuple[int, int, int] = (255, 100, 100)) -> Rectangle:
        """
        Create a new rectangle component.
        
        Args:
            x: X-coordinate
            y: Y-coordinate
            width: Rectangle width
            height: Rectangle height
            color: RGB color tuple
            
        Returns:
            Created Rectangle instance
        """
        rectangle = Rectangle(x, y, width, height, color)
        self.components.append(rectangle)
        self.status_message = "Rectangle created"
        return rectangle

    def create_connection(self, source: Component, target: Component) -> Optional[Connection]:
        """
        Create a connection between two components.
        
        Args:
            source: Source component
            target: Target component
            
        Returns:
            Created Connection instance or None if invalid
        """
        if source == target:
            self.status_message = "Cannot connect component to itself"
            return None
        
        # Check if connection already exists
        for conn in self.connections:
            if (conn.source == source and conn.target == target) or \
               (conn.source == target and conn.target == source):
                self.status_message = "Connection already exists"
                return None
        
        connection = Connection(source, target)
        self.connections.append(connection)
        self.status_message = "Connection created"
        return connection

    # Selection methods
    def select_component_at_point(self, x: float, y: float) -> Optional[Component]:
        """
        Select a component at the given point.
        
        Args:
            x: X-coordinate
            y: Y-coordinate
            
        Returns:
            Selected component or None
        """
        # Check components in reverse order (top to bottom)
        for component in reversed(self.components):
            if component.contains_point(x, y):
                self.selected_component = component
                return component
        
        # No component found, deselect
        self.selected_component = None
        return None

    def deselect_all(self):
        """Deselect all components."""
        self.selected_component = None

    # Dragging methods
    def start_drag(self, x: float, y: float) -> bool:
        """
        Start dragging operation at the given point.
        
        Args:
            x: Mouse X-coordinate
            y: Mouse Y-coordinate
            
        Returns:
            True if drag started successfully
        """
        component = self.select_component_at_point(x, y)
        if component:
            self.dragging_component = component
            self.drag_offset_x = component.x - x
            self.drag_offset_y = component.y - y
            return True
        return False

    def update_drag(self, x: float, y: float):
        """
        Update dragging position.
        
        Args:
            x: Current mouse X-coordinate
            y: Current mouse Y-coordinate
        """
        if self.dragging_component:
            new_x = x + self.drag_offset_x
            new_y = y + self.drag_offset_y
            self.dragging_component.update_position(new_x, new_y)

    def stop_drag(self):
        """Stop dragging operation."""
        self.dragging_component = None

    # Scaling methods
    def scale_selected(self, delta: float):
        """
        Scale the selected component.
        
        Args:
            delta: Scale change amount
        """
        if self.selected_component:
            self.selected_component.update_scale(delta)

    # Connection creation methods
    def start_connection_at_point(self, x: float, y: float) -> bool:
        """
        Start or complete connection creation.
        
        Args:
            x: Mouse X-coordinate
            y: Mouse Y-coordinate
            
        Returns:
            True if operation succeeded
        """
        component = self.get_component_at_point(x, y)
        if not component:
            return False
        
        if self.connection_start is None:
            # Start new connection
            self.connection_start = component
            self.status_message = "Connection start selected"
            return True
        else:
            # Complete connection
            if self.create_connection(self.connection_start, component):
                self.connection_start = None
                return True
            self.connection_start = None
            return False

    def cancel_connection(self):
        """Cancel ongoing connection creation."""
        if self.connection_start:
            self.connection_start = None
            self.status_message = "Connection cancelled"

    def get_connection_preview_line(self, mouse_x: float, mouse_y: float) -> Optional[Tuple[Tuple[float, float], Tuple[float, float]]]:
        """
        Get the preview line for connection creation.
        
        Args:
            mouse_x: Current mouse X-coordinate
            mouse_y: Current mouse Y-coordinate
            
        Returns:
            Tuple of (start_pos, end_pos) or None
        """
        if self.connection_start:
            start_pos = self.connection_start.get_connection_point()
            end_pos = (mouse_x, mouse_y)
            return (start_pos, end_pos)
        return None

    # Deletion methods
    def delete_selected(self) -> bool:
        """
        Delete the selected component and its connections.
        
        Returns:
            True if deletion succeeded
        """
        if self.selected_component:
            self.delete_component(self.selected_component)
            self.selected_component = None
            return True
        return False

    def delete_component(self, component: Component):
        """
        Delete a component and all its connections.
        
        Args:
            component: Component to delete
        """
        # Remove all connections involving this component
        self.connections = [
            conn for conn in self.connections
            if conn.source != component and conn.target != component
        ]
        
        # Remove the component
        self.components.remove(component)
        self.status_message = "Component deleted"

    # Query methods
    def get_component_at_point(self, x: float, y: float) -> Optional[Component]:
        """
        Get component at the given point (without selection).
        
        Args:
            x: X-coordinate
            y: Y-coordinate
            
        Returns:
            Component at point or None
        """
        for component in reversed(self.components):
            if component.contains_point(x, y):
                return component
        return None

    def get_all_components(self) -> List[Component]:
        """Get all components."""
        return self.components

    def get_all_connections(self) -> List[Connection]:
        """Get all connections."""
        return self.connections

    def is_component_selected(self, component: Component) -> bool:
        """
        Check if a component is selected.
        
        Args:
            component: Component to check
            
        Returns:
            True if selected
        """
        return component == self.selected_component

    def is_dragging(self) -> bool:
        """Check if currently dragging."""
        return self.dragging_component is not None

    def is_creating_connection(self) -> bool:
        """Check if currently creating a connection."""
        return self.connection_start is not None

    # Scene management
    def clear_scene(self):
        """Clear all components and connections."""
        self.components.clear()
        self.connections.clear()
        self.selected_component = None
        self.dragging_component = None
        self.connection_start = None
        self.status_message = "Scene cleared"

    def set_components_and_connections(self, components: List[Component], connections: List[Connection]):
        """
        Set components and connections (used for loading).
        
        Args:
            components: List of components
            connections: List of connections
        """
        self.components = components
        self.connections = connections
        self.selected_component = None
        self.dragging_component = None
        self.connection_start = None

    def get_status_message(self) -> str:
        """Get the current status message."""
        return self.status_message

    def clear_status_message(self):
        """Clear the status message."""
        self.status_message = ""
