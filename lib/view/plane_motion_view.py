"""
View layer: Pygame rendering implementation with GUI menu.
Responsible for all visual representation, no business logic.
"""

import pygame
import pygame_gui
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
        
        # Menu and control bar heights
        self.menu_height = 35
        self.control_height = 40
        self.canvas_top = self.menu_height + self.control_height
        
        # Initialize pygame display with resizable flag
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        
        # Initialize GUI manager with theme
        import os
        theme_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'theme.json')
        if os.path.exists(theme_path):
            self.gui_manager = pygame_gui.UIManager((width, height), theme_path)
        else:
            self.gui_manager = pygame_gui.UIManager((width, height))
        
        # Create menu and control bars
        self._create_menu_bar()
        self._create_control_bar()
        
        # Colors
        self.bg_color = (30, 30, 40)
        self.menu_bg_color = (45, 45, 55)
        self.control_bg_color = (35, 35, 45)
        self.selection_color = (255, 255, 0)
        self.preview_line_color = (150, 150, 150)
        self.help_text_color = (200, 200, 200)
        
        # Font
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)

    def _create_menu_bar(self):
        """Create the menu bar with File and Insert menus."""
        menu_bar_height = self.menu_height
        
        # File menu button
        self.file_menu_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((5, 5), (80, menu_bar_height - 10)),
            text='File',
            manager=self.gui_manager,
            object_id='#file_menu_button'
        )
        
        # Dropdown menus (created dynamically)
        self.file_dropdown = None
        self.insert_dropdown = None
        self.file_dropdown_visible = False
        self.insert_dropdown_visible = False

    def _create_control_bar(self):
        """Create the control bar with common actions."""
        self.control_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, self.menu_height), (self.width, self.control_height)),
            manager=self.gui_manager
        )

        x = 12
        y = 6
        height = self.control_height - 12

        self.create_circle_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((x, y), (110, height)),
            text='Circle',
            manager=self.gui_manager,
            container=self.control_panel
        )
        x += 118

        self.create_rectangle_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((x, y), (120, height)),
            text='Rectangle',
            manager=self.gui_manager,
            container=self.control_panel
        )
        x += 128

        self.delete_selected_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((x, y), (90, height)),
            text='Delete',
            manager=self.gui_manager,
            container=self.control_panel
        )
        x += 98

        self.reset_view_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((x, y), (110, height)),
            text='Reset View',
            manager=self.gui_manager,
            container=self.control_panel
        )

    def render(self, mouse_pos: Optional[Tuple[int, int]] = None):
        """
        Render the entire scene.
        
        Args:
            mouse_pos: Current mouse position for preview rendering
        """
        # Clear screen
        self.screen.fill(self.bg_color)
        
        # Draw menu bar background
        pygame.draw.rect(self.screen, self.menu_bg_color,
                pygame.Rect(0, 0, self.width, self.menu_height))

        # Draw control bar background
        pygame.draw.rect(self.screen, self.control_bg_color,
                pygame.Rect(0, self.menu_height, self.width, self.control_height))
        
        # Draw GUI elements first (buttons and dropdowns)
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
        """
        Handle window resize.
        
        Args:
            width: New window width
            height: New window height
        """
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        self.gui_manager.set_window_resolution((width, height))
        if hasattr(self, 'control_panel') and self.control_panel is not None:
            self.control_panel.set_relative_position((0, self.menu_height))
            self.control_panel.set_dimensions((width, self.control_height))

    def update(self, time_delta: float):
        """
        Update GUI manager.
        
        Args:
            time_delta: Time since last update in seconds
        """
        self.gui_manager.update(time_delta)

    def process_event(self, event) -> bool:
        """
        Process GUI events.
        
        Args:
            event: Pygame event
            
        Returns:
            True if event was handled by GUI, False otherwise
        """
        return self.gui_manager.process_events(event)

    def show_file_menu(self):
        """Toggle the File dropdown menu."""
        # Close insert menu if open
        if self.insert_dropdown_visible:
            self.close_insert_dropdown()
        
        # Toggle file dropdown
        if self.file_dropdown_visible:
            self.close_file_dropdown()
        else:
            options_list = ['Open', 'Save', 'Save As', 'Exit']
            self.file_dropdown = pygame_gui.elements.UIDropDownMenu(
                options_list=options_list,
                starting_option='Open',
                relative_rect=pygame.Rect((5, self.menu_height), (150, 40)),
                manager=self.gui_manager,
                object_id='#file_dropdown'
            )
            self.file_dropdown_visible = True

    def show_insert_menu(self):
        """Toggle the Insert dropdown menu."""
        # Close file menu if open
        if self.file_dropdown_visible:
            self.close_file_dropdown()
        
        # Toggle insert dropdown
        if self.insert_dropdown_visible:
            self.close_insert_dropdown()
        else:
            templates = self.viewmodel.get_component_templates()
            if not templates:
                # Add default options to create initial templates
                options_list = ['Circle (default)', 'Rectangle (default)']
            else:
                options_list = []
                for template in templates:
                    if isinstance(template, Circle):
                        options_list.append(f"Circle (r={int(template.radius)})")
                    elif isinstance(template, Rectangle):
                        options_list.append(f"Rectangle ({int(template.width)}x{int(template.height)})")
            
            if options_list:
                self.insert_dropdown = pygame_gui.elements.UIDropDownMenu(
                    options_list=options_list,
                    starting_option=options_list[0],
                    relative_rect=pygame.Rect((90, self.menu_height), (220, 40)),
                    manager=self.gui_manager,
                    object_id='#insert_dropdown'
                )
                self.insert_dropdown_visible = True

    def close_dropdowns(self):
        """Close all dropdown menus."""
        self.close_file_dropdown()
        self.close_insert_dropdown()
    
    def close_file_dropdown(self):
        """Close file dropdown menu."""
        if self.file_dropdown:
            self.file_dropdown.kill()
            self.file_dropdown = None
            self.file_dropdown_visible = False
    
    def close_insert_dropdown(self):
        """Close insert dropdown menu."""
        if self.insert_dropdown:
            self.insert_dropdown.kill()
            self.insert_dropdown = None
            self.insert_dropdown_visible = False

    def set_window_title(self, title: str):
        """
        Set the window title.
        
        Args:
            title: New window title
        """
        pygame.display.set_caption(title)
