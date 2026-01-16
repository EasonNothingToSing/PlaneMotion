"""
View layer: Pygame rendering implementation.
Responsible for all visual representation, no business logic.
"""

import pygame
from typing import Optional, Tuple, TYPE_CHECKING
from lib.model import Component, Circle, Rectangle, Connection

if TYPE_CHECKING:
    from lib.viewmodel import PlaneMotionViewModel


class PlaneMotionView:
    """
    View layer for PlaneMotion engine.
    Handles all pygame rendering based on ViewModel state.
    """

    def __init__(self, viewmodel: 'PlaneMotionViewModel', width: int = 1280, height: int = 720):
        """
        Initialize the View.
        
        Args:
            viewmodel: ViewModel instance to observe
            width: Window width
            height: Window height
        """
        self.viewmodel = viewmodel
        self.width = width
        self.height = height
        
        # Initialize pygame display
        self.screen = pygame.display.set_mode((width, height))
        
        # Colors
        self.bg_color = (30, 30, 40)
        self.selection_color = (255, 255, 0)
        self.preview_line_color = (150, 150, 150)
        self.help_text_color = (200, 200, 200)
        
        # Font
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)

    def render(self, mouse_pos: Optional[Tuple[int, int]] = None):
        """
        Render the entire scene.
        
        Args:
            mouse_pos: Current mouse position for preview rendering
        """
        # Clear screen
        self.screen.fill(self.bg_color)
        
        # Draw connections
        self._render_connections()
        
        # Draw connection preview
        if mouse_pos and self.viewmodel.is_creating_connection():
            self._render_connection_preview(mouse_pos)
        
        # Draw components
        self._render_components()
        
        # Draw UI overlays
        self._render_help_text()
        self._render_status_message()

    def _render_components(self):
        """Render all components."""
        for component in self.viewmodel.get_all_components():
            is_selected = self.viewmodel.is_component_selected(component)
            self._render_component(component, is_selected)

    def _render_component(self, component: Component, is_selected: bool):
        """
        Render a single component.
        
        Args:
            component: Component to render
            is_selected: Whether the component is selected
        """
        if isinstance(component, Circle):
            self._render_circle(component, is_selected)
        elif isinstance(component, Rectangle):
            self._render_rectangle(component, is_selected)

    def _render_circle(self, circle: Circle, is_selected: bool):
        """
        Render a circle component.
        
        Args:
            circle: Circle to render
            is_selected: Whether the circle is selected
        """
        # Draw the circle
        pygame.draw.circle(
            self.screen,
            circle.color,
            (int(circle.x), int(circle.y)),
            int(circle.radius)
        )
        
        # Draw selection outline if selected
        if is_selected:
            pygame.draw.circle(
                self.screen,
                self.selection_color,
                (int(circle.x), int(circle.y)),
                int(circle.radius) + 2,
                2
            )

    def _render_rectangle(self, rectangle: Rectangle, is_selected: bool):
        """
        Render a rectangle component.
        
        Args:
            rectangle: Rectangle to render
            is_selected: Whether the rectangle is selected
        """
        # Calculate top-left corner
        left = int(rectangle.x - rectangle.width / 2)
        top = int(rectangle.y - rectangle.height / 2)
        
        # Draw the rectangle
        rect = pygame.Rect(left, top, int(rectangle.width), int(rectangle.height))
        pygame.draw.rect(self.screen, rectangle.color, rect)
        
        # Draw selection outline if selected
        if is_selected:
            pygame.draw.rect(self.screen, self.selection_color, rect, 2)

    def _render_connections(self):
        """Render all connections."""
        for connection in self.viewmodel.get_all_connections():
            self._render_connection(connection)

    def _render_connection(self, connection: Connection):
        """
        Render a single connection.
        
        Args:
            connection: Connection to render
        """
        start_pos, end_pos = connection.get_line_endpoints()
        
        # Draw the main line
        pygame.draw.line(
            self.screen,
            connection.color,
            start_pos,
            end_pos,
            connection.line_width
        )
        
        # Draw small circles at connection points
        pygame.draw.circle(
            self.screen,
            connection.color,
            (int(start_pos[0]), int(start_pos[1])),
            4
        )
        pygame.draw.circle(
            self.screen,
            connection.color,
            (int(end_pos[0]), int(end_pos[1])),
            4
        )

    def _render_connection_preview(self, mouse_pos: Tuple[int, int]):
        """
        Render the connection preview line.
        
        Args:
            mouse_pos: Current mouse position
        """
        preview = self.viewmodel.get_connection_preview_line(mouse_pos[0], mouse_pos[1])
        if preview:
            start_pos, end_pos = preview
            pygame.draw.line(
                self.screen,
                self.preview_line_color,
                start_pos,
                end_pos,
                1
            )

    def _render_help_text(self):
        """Render help information on screen."""
        help_lines = [
            "C: Create Circle | R: Create Rectangle",
            "Left Click: Select/Drag | Right Click: Connect",
            "Mouse Wheel: Scale | Delete: Remove",
            "Ctrl+S: Save | Ctrl+L: Load"
        ]
        
        y_offset = 10
        for line in help_lines:
            text_surface = self.font.render(line, True, self.help_text_color)
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 25

    def _render_status_message(self):
        """Render status message at the bottom of the screen."""
        status = self.viewmodel.get_status_message()
        if status:
            text_surface = self.small_font.render(status, True, (255, 255, 255))
            text_rect = text_surface.get_rect()
            text_rect.centerx = self.width // 2
            text_rect.bottom = self.height - 10
            self.screen.blit(text_surface, text_rect)

    def flip(self):
        """Update the display."""
        pygame.display.flip()

    def set_window_title(self, title: str):
        """
        Set the window title.
        
        Args:
            title: New window title
        """
        pygame.display.set_caption(title)
