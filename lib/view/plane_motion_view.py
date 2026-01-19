"""
View layer: Pygame rendering implementation with custom menu system.
Responsible for all visual representation, no business logic.
"""

import pygame
import pygame_gui
from typing import Optional, Tuple, TYPE_CHECKING
from lib.model import Component, Circle, Rectangle, Trapezoid, Connection
from lib.view.menu_system import MenuManager

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
        
        # Unified top bar height
        self.menu_height = 34
        self.canvas_top = self.menu_height
        
        # Initialize pygame display with resizable flag
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        
        # Initialize GUI manager with theme
        import os
        theme_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'theme.json')
        if os.path.exists(theme_path):
            self.gui_manager = pygame_gui.UIManager((width, height), theme_path)
        else:
            self.gui_manager = pygame_gui.UIManager((width, height))
        
        # Initialize menu manager
        self.menu_manager = MenuManager(self.gui_manager, (width, height))
        
        # Create menu bar
        self._create_menu_bar()
        
        # Colors
        self.bg_color = (30, 30, 40)
        self.menu_bg_color = (45, 45, 55)
        self.selection_color = (255, 255, 0)
        self.preview_line_color = (150, 150, 150)
        self.help_text_color = (200, 200, 200)
        
        # Font
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)

    def _create_menu_bar(self):
        """Create the menu bar with File and Edit buttons."""
        # Menu bar panel
        self.menubar = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, 0, self.width, self.menu_height),
            manager=self.gui_manager
        )
        
        # File button
        self.btn_file = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(6, 4, 80, self.menu_height - 8),
            text='File',
            manager=self.gui_manager,
            container=self.menubar,
            object_id='#file_menu_button'
        )
        
        # Edit button
        self.btn_edit = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(90, 4, 80, self.menu_height - 8),
            text='Edit',
            manager=self.gui_manager,
            container=self.menubar,
            object_id='#edit_menu_button'
        )

    def get_file_menu_items(self):
        """Get File menu structure."""
        return [
            {"type": "item", "label": "Open", "shortcut": "Ctrl+O", "action": "open"},
            {"type": "item", "label": "Save", "shortcut": "Ctrl+S", "action": "save"},
            {"type": "item", "label": "Save As", "shortcut": "Ctrl+Shift+S", "action": "save_as"},
            {"type": "separator"},
            {"type": "item", "label": "Exit", "shortcut": "Alt+F4", "action": "exit"},
        ]
    
    def get_edit_menu_items(self):
        """Get Edit menu structure."""
        return [
            {"type": "item", "label": "Insert", "submenu": [
                {"type": "item", "label": "Circle", "action": "insert_circle"},
                {"type": "item", "label": "Rectangle", "action": "insert_rectangle"},
                {"type": "item", "label": "Trapezoid", "action": "insert_trapezoid"},
            ]},
            {"type": "separator"},
            {"type": "item", "label": "Delete Selected", "shortcut": "Del", "action": "delete"},
            {"type": "item", "label": "Rotate 90°", "shortcut": "R", "action": "rotate"},
            {"type": "separator"},
            {"type": "item", "label": "Reset View", "shortcut": "Ctrl+0", "action": "reset_view"},
        ]
    
    def get_context_menu_items(self):
        """Get right-click context menu structure."""
        return [
            {"type": "item", "label": "Insert Here", "submenu": [
                {"type": "item", "label": "Circle", "action": "context_circle"},
                {"type": "item", "label": "Rectangle", "action": "context_rectangle"},
                {"type": "item", "label": "Trapezoid", "action": "context_trapezoid"},
            ]},
            {"type": "separator"},
            {"type": "item", "label": "Delete", "shortcut": "Del", "action": "delete"},
            {"type": "item", "label": "Rotate 90°", "shortcut": "R", "action": "rotate"},
        ]

    def render(self, mouse_pos: Optional[Tuple[int, int]] = None):
        """
        Render the entire scene.
        
        Args:
            mouse_pos: Current mouse position for preview rendering
        """
        # Clear screen
        self.screen.fill(self.bg_color)
        
        # Draw unified top bar background
        pygame.draw.rect(self.screen, self.menu_bg_color,
                pygame.Rect(0, 0, self.width, self.menu_height))
        
        # Draw GUI elements first (buttons and menus)
        self.gui_manager.draw_ui(self.screen)
        
        # Draw separator line after GUI so it appears on top
        pygame.draw.line(self.screen, (80, 80, 90), 
                        (0, self.menu_height), (self.width, self.menu_height), 2)
        
        # Set clip area to canvas only (below menu)
        canvas_rect = pygame.Rect(0, self.canvas_top, self.width, self.height - self.canvas_top)
        self.screen.set_clip(canvas_rect)
        
        # Draw connections
        self._render_connections()
        
        # Draw connection preview
        if mouse_pos and self.viewmodel.is_creating_connection():
            self._render_connection_preview(mouse_pos)
        
        # Draw components
        self._render_components()
        
        # Reset clip
        self.screen.set_clip(None)
        
        # Draw UI overlays (always in screen space)
        self._render_status_message()
        self._render_zoom_indicator()

    def _render_components(self):
        """Render all components."""
        for component in self.viewmodel.get_all_components():
            is_selected = self.viewmodel.is_component_selected(component)
            self._render_component(component, is_selected)

    def _render_component(self, component: Component, is_selected: bool):
        """Render a single component."""
        if isinstance(component, Circle):
            self._render_circle(component, is_selected)
        elif isinstance(component, Rectangle):
            self._render_rectangle(component, is_selected)
        elif isinstance(component, Trapezoid):
            self._render_trapezoid(component, is_selected)

    def _render_circle(self, circle: Circle, is_selected: bool):
        """Render a circle component."""
        screen_x, screen_y = self.viewmodel.world_to_screen(circle.x, circle.y)
        screen_radius = circle.radius * self.viewmodel.viewport_zoom
        
        pygame.draw.circle(
            self.screen,
            circle.color,
            (int(screen_x), int(screen_y)),
            int(screen_radius)
        )
        
        if is_selected:
            pygame.draw.circle(
                self.screen,
                self.selection_color,
                (int(screen_x), int(screen_y)),
                int(screen_radius) + 2,
                2
            )

    def _render_rectangle(self, rectangle: Rectangle, is_selected: bool):
        """Render a rectangle component."""
        vertices = rectangle.get_vertices()
        screen_points = [self.viewmodel.world_to_screen(x, y) for x, y in vertices]
        pygame.draw.polygon(self.screen, rectangle.color, screen_points)
        if is_selected:
            pygame.draw.polygon(self.screen, self.selection_color, screen_points, 2)

    def _render_trapezoid(self, trapezoid: Trapezoid, is_selected: bool):
        """Render a trapezoid component."""
        vertices = trapezoid.get_vertices()
        screen_points = [self.viewmodel.world_to_screen(x, y) for x, y in vertices]
        pygame.draw.polygon(self.screen, trapezoid.color, screen_points)
        if is_selected:
            pygame.draw.polygon(self.screen, self.selection_color, screen_points, 2)

    def _render_connections(self):
        """Render all connections."""
        for connection in self.viewmodel.get_all_connections():
            self._render_connection(connection)

    def _render_connection(self, connection: Connection):
        """Render a single connection."""
        start_pos_world, end_pos_world = connection.get_line_endpoints()
        start_pos = self.viewmodel.world_to_screen(*start_pos_world)
        end_pos = self.viewmodel.world_to_screen(*end_pos_world)
        line_width = max(1, int(connection.line_width * self.viewmodel.viewport_zoom))
        
        pygame.draw.line(self.screen, connection.color, start_pos, end_pos, line_width)
        
        circle_radius = max(2, int(4 * self.viewmodel.viewport_zoom))
        pygame.draw.circle(self.screen, connection.color, 
                          (int(start_pos[0]), int(start_pos[1])), circle_radius)
        pygame.draw.circle(self.screen, connection.color, 
                          (int(end_pos[0]), int(end_pos[1])), circle_radius)

    def _render_connection_preview(self, mouse_pos: Tuple[int, int]):
        """Render the connection preview line."""
        world_mouse_x, world_mouse_y = self.viewmodel.screen_to_world(mouse_pos[0], mouse_pos[1])
        preview = self.viewmodel.get_connection_preview_line(world_mouse_x, world_mouse_y)
        if preview:
            start_pos_world, end_pos_world = preview
            start_pos = self.viewmodel.world_to_screen(*start_pos_world)
            end_pos = self.viewmodel.world_to_screen(*end_pos_world)
            pygame.draw.line(self.screen, self.preview_line_color, start_pos, end_pos, 1)

    def _render_zoom_indicator(self):
        """Render zoom level indicator."""
        zoom_percent = int(self.viewmodel.viewport_zoom * 100)
        zoom_text = f"Zoom: {zoom_percent}%"
        text_surface = self.small_font.render(zoom_text, True, self.help_text_color)
        text_rect = text_surface.get_rect()
        text_rect.right = self.width - 10
        text_rect.top = self.canvas_top + 10
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

    def resize(self, width: int, height: int):
        """Handle window resize."""
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        self.gui_manager.set_window_resolution((width, height))
        self.menu_manager.update_window_size((width, height))
        if hasattr(self, 'menubar') and self.menubar is not None:
            self.menubar.set_dimensions((width, self.menu_height))

    def update(self, time_delta: float):
        """Update GUI manager."""
        self.gui_manager.update(time_delta)

    def process_event(self, event) -> bool:
        """Process GUI events."""
        return self.gui_manager.process_events(event)

    def set_window_title(self, title: str):
        """Set the window title."""
        pygame.display.set_caption(title)
