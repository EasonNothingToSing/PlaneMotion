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
        
        # Draw UI overlays (always in screen space)
        self._render_help_text()
        self._render_status_message()
        self._render_zoom_indicator()

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
        # Transform world coordinates to screen coordinates
        screen_x, screen_y = self.viewmodel.world_to_screen(circle.x, circle.y)
        screen_radius = circle.radius * self.viewmodel.viewport_zoom
        
        # Draw the circle
        pygame.draw.circle(
            self.screen,
            circle.color,
            (int(screen_x), int(screen_y)),
            int(screen_radius)
        )
        
        # Draw selection outline if selected
        if is_selected:
            pygame.draw.circle(
                self.screen,
                self.selection_color,
                (int(screen_x), int(screen_y)),
                int(screen_radius) + 2,
                2
            )

    def _render_rectangle(self, rectangle: Rectangle, is_selected: bool):
        """
        Render a rectangle component.
        
        Args:
            rectangle: Rectangle to render
            is_selected: Whether the rectangle is selected
        """
        # Transform world coordinates to screen coordinates
        screen_x, screen_y = self.viewmodel.world_to_screen(rectangle.x, rectangle.y)
        screen_width = rectangle.width * self.viewmodel.viewport_zoom
        screen_height = rectangle.height * self.viewmodel.viewport_zoom
        
        # Calculate top-left corner
        left = int(screen_x - screen_width / 2)
        top = int(screen_y - screen_height / 2)
        
        # Draw the rectangle
        rect = pygame.Rect(left, top, int(screen_width), int(screen_height))
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
        start_pos_world, end_pos_world = connection.get_line_endpoints()
        
        # Transform to screen coordinates
        start_pos = self.viewmodel.world_to_screen(*start_pos_world)
        end_pos = self.viewmodel.world_to_screen(*end_pos_world)
        
        # Scale line width with zoom
        line_width = max(1, int(connection.line_width * self.viewmodel.viewport_zoom))
        
        # Draw the main line
        pygame.draw.line(
            self.screen,
            connection.color,
            start_pos,
            end_pos,
            line_width
        )
        
        # Draw small circles at connection points
        circle_radius = max(2, int(4 * self.viewmodel.viewport_zoom))
        pygame.draw.circle(
            self.screen,
            connection.color,
            (int(start_pos[0]), int(start_pos[1])),
            circle_radius
        )
        pygame.draw.circle(
            self.screen,
            connection.color,
            (int(end_pos[0]), int(end_pos[1])),
            circle_radius
        )

    def _render_connection_preview(self, mouse_pos: Tuple[int, int]):
        """
        Render the connection preview line.
        
        Args:
            mouse_pos: Current mouse position (in screen space)
        """
        # Convert mouse position to world space
        world_mouse_x, world_mouse_y = self.viewmodel.screen_to_world(mouse_pos[0], mouse_pos[1])
        
        preview = self.viewmodel.get_connection_preview_line(world_mouse_x, world_mouse_y)
        if preview:
            start_pos_world, end_pos_world = preview
            # Transform to screen coordinates
            start_pos = self.viewmodel.world_to_screen(*start_pos_world)
            end_pos = self.viewmodel.world_to_screen(*end_pos_world)
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
            "Mouse Wheel: Zoom | Middle Click: Pan",
            "Ctrl+S: Save | Ctrl+L: Load | Ctrl+0: Reset View"
        ]
        
        y_offset = 10
        for line in help_lines:
            text_surface = self.font.render(line, True, self.help_text_color)
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 25

    def _render_zoom_indicator(self):
        """Render zoom level indicator."""
        zoom_percent = int(self.viewmodel.viewport_zoom * 100)
        zoom_text = f"Zoom: {zoom_percent}%"
        text_surface = self.small_font.render(zoom_text, True, self.help_text_color)
        text_rect = text_surface.get_rect()
        text_rect.right = self.width - 10
        text_rect.top = 10
        self.screen.blit(text_surface, text_rect)

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
