"""
Main engine: Coordinates MVVM components and handles the game loop.
Acts as the controller in MVVM pattern.
"""

import pygame
import pygame_gui
import sys
import tkinter as tk
from tkinter import filedialog
from lib.viewmodel import PlaneMotionViewModel
from lib.view import PlaneMotionView
from lib.utils import SaveLoadManager


class PlaneMotionEngine:
    """
    Main engine class that coordinates ViewModel and View.
    Handles the game loop and user input delegation.
    """

    def __init__(self, width: int = 1280, height: int = 720, title: str = "PlaneMotion Engine"):
        """
        Initialize the PlaneMotion engine.
        
        Args:
            width: Window width in pixels
            height: Window height in pixels
            title: Window title
        """
        pygame.init()
        
        # Initialize MVVM components
        self.viewmodel = PlaneMotionViewModel()
        self.view = PlaneMotionView(self.viewmodel, width, height)
        self.view.set_window_title(title)
        
        # Game loop control
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.running = True

        # Resize hover/cursor state
        self.resize_hit_threshold_px = 8
        self.current_cursor = pygame.SYSTEM_CURSOR_ARROW
        
        # Save/Load manager
        self.save_load_manager = SaveLoadManager()

    def run(self):
        """Main game loop."""
        while self.running:
            time_delta = self.clock.tick(self.fps) / 1000.0
            self.handle_events()
            self.update(time_delta)
            self.render()
        
        pygame.quit()
        sys.exit()

    def update(self, time_delta: float):
        """
        Update game state.
        
        Args:
            time_delta: Time since last update in seconds
        """
        self.view.update(time_delta)

    def render(self):
        """Render the scene."""
        mouse_pos = pygame.mouse.get_pos()
        self.view.render(mouse_pos)
        self.view.flip()

    def handle_events(self):
        """Handle all pygame events and delegate to ViewModel."""
        for event in pygame.event.get():
            # Menu manager handles its events first
            if self.view.menu_manager.handle_event(event):
                continue
            
            # Let GUI handle events next
            if self.view.process_event(event):
                continue
            
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.VIDEORESIZE:
                self.handle_window_resize(event)
            
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                self.handle_gui_button(event)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_down(event)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                self.handle_mouse_up(event)
            
            elif event.type == pygame.MOUSEMOTION:
                self.handle_mouse_motion(event)
            
            elif event.type == pygame.MOUSEWHEEL:
                self.handle_mouse_wheel(event)
            
            elif event.type == pygame.KEYDOWN:
                self.handle_key_down(event)

    def handle_mouse_down(self, event):
        """
        Handle mouse button down events.
        
        Args:
            event: Pygame mouse button down event
        """
        screen_x, screen_y = event.pos
        
        # Ignore clicks on menu bar
        if screen_y < self.view.canvas_top:
            return
        
        # Left click
        if event.button == 1:
            # Convert screen coordinates to world coordinates
            world_x, world_y = self.viewmodel.screen_to_world(screen_x, screen_y)
            self.viewmodel.record_last_click(world_x, world_y)
            
            # Connection mode: create connections with left click
            if self.view.is_connection_mode():
                self.viewmodel.start_connection_at_point(world_x, world_y)
            else:
                # Normal mode: select and drag
                resize_threshold_world = self.resize_hit_threshold_px / self.viewmodel.viewport_zoom
                if self.viewmodel.start_resize(world_x, world_y, resize_threshold_world):
                    return
                if not self.viewmodel.start_drag(world_x, world_y):
                    self.viewmodel.deselect_all()
        
        # Middle click - pan
        elif event.button == 2:
            self.viewmodel.start_pan(screen_x, screen_y)
        
        # Right click - context menu
        elif event.button == 3:
            # Convert screen coordinates to world coordinates
            world_x, world_y = self.viewmodel.screen_to_world(screen_x, screen_y)
            self.viewmodel.record_last_click(world_x, world_y)
            # Show context menu
            self.show_context_menu(event.pos)

    def handle_mouse_up(self, event):
        """
        Handle mouse button up events.
        
        Args:
            event: Pygame mouse button up event
        """
        if event.button == 1:
            self.viewmodel.stop_resize()
            self.viewmodel.stop_drag()
        elif event.button == 2:
            self.viewmodel.stop_pan()

    def handle_mouse_motion(self, event):
        """
        Handle mouse motion events.
        
        Args:
            event: Pygame mouse motion event
        """
        screen_x, screen_y = event.pos
        
        # Update panning
        if self.viewmodel.is_panning:
            self.viewmodel.update_pan(screen_x, screen_y)
        # Update resizing
        elif self.viewmodel.is_resizing():
            world_x, world_y = self.viewmodel.screen_to_world(screen_x, screen_y)
            self.viewmodel.update_resize(world_x, world_y)
        # Update dragging position
        elif self.viewmodel.is_dragging():
            world_x, world_y = self.viewmodel.screen_to_world(screen_x, screen_y)
            self.viewmodel.update_drag(world_x, world_y)

        self._update_hover_cursor(screen_x, screen_y)

    def _update_hover_cursor(self, screen_x: float, screen_y: float):
        """Update mouse cursor based on hover state."""
        if self.viewmodel.is_resizing():
            target_cursor = pygame.SYSTEM_CURSOR_SIZENWSE
        elif self.viewmodel.is_dragging():
            target_cursor = pygame.SYSTEM_CURSOR_HAND
        else:
            world_x, world_y = self.viewmodel.screen_to_world(screen_x, screen_y)
            resize_threshold_world = self.resize_hit_threshold_px / self.viewmodel.viewport_zoom
            if self.viewmodel.get_resize_component_at_point(world_x, world_y, resize_threshold_world):
                target_cursor = pygame.SYSTEM_CURSOR_SIZENWSE
            else:
                target_cursor = pygame.SYSTEM_CURSOR_ARROW

        if target_cursor != self.current_cursor:
            pygame.mouse.set_cursor(target_cursor)
            self.current_cursor = target_cursor

    def handle_mouse_wheel(self, event):
        """
        Handle mouse wheel events for viewport zooming.
        
        Args:
            event: Pygame mouse wheel event
        """
        # Zoom viewport around mouse cursor
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.viewmodel.zoom_viewport(event.y, mouse_x, mouse_y)

    def handle_window_resize(self, event):
        """
        Handle window resize event.
        
        Args:
            event: Pygame VIDEORESIZE event
        """
        self.view.resize(event.w, event.h)

    def handle_key_down(self, event):
        """
        Handle keyboard events.
        
        Args:
            event: Pygame key down event
        """
        # C - Create circle at mouse position
        if event.key == pygame.K_c:
            screen_x, screen_y = pygame.mouse.get_pos()
            world_x, world_y = self.viewmodel.screen_to_world(screen_x, screen_y)
            self.viewmodel.create_circle(world_x, world_y)
        
        # R - Create rectangle at mouse position
        elif event.key == pygame.K_r:
            screen_x, screen_y = pygame.mouse.get_pos()
            world_x, world_y = self.viewmodel.screen_to_world(screen_x, screen_y)
            self.viewmodel.create_rectangle(world_x, world_y)
        
        # Delete - Delete selected component
        elif event.key == pygame.K_DELETE:
            self.viewmodel.delete_selected()
        
        # Ctrl+S - Save scene
        elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
            self.save_scene()
        
        # Ctrl+L - Load scene
        elif event.key == pygame.K_l and pygame.key.get_mods() & pygame.KMOD_CTRL:
            self.load_scene()
        
        # Ctrl+0 - Reset viewport
        elif event.key == pygame.K_0 and pygame.key.get_mods() & pygame.KMOD_CTRL:
            self.viewmodel.reset_viewport()
        
        # ESC - Cancel connection creation
        elif event.key == pygame.K_ESCAPE:
            self.viewmodel.cancel_connection()

    def handle_gui_button(self, event):
        """
        Handle GUI button press events.
        
        Args:
            event: pygame_gui button pressed event
        """
        if event.ui_element == self.view.btn_file:
            # Show File menu
            r = self.view.btn_file.get_abs_rect()
            items = self._get_file_menu_with_actions()
            self.view.menu_manager.open_root_menu((r.left, r.bottom), items)
        elif event.ui_element == self.view.btn_edit:
            # Show Edit menu
            r = self.view.btn_edit.get_abs_rect()
            items = self._get_edit_menu_with_actions()
            self.view.menu_manager.open_root_menu((r.left, r.bottom), items)
        elif event.ui_element == self.view.btn_connect:
            # Toggle connection mode
            self.view.toggle_connection_mode()
    
    def _get_file_menu_with_actions(self):
        """Get File menu items with actual action functions."""
        return [
            {"type": "item", "label": "Open", "shortcut": "Ctrl+O", "action": self.open_file_dialog},
            {"type": "item", "label": "Save", "shortcut": "Ctrl+S", "action": lambda: self.save_scene()},
            {"type": "item", "label": "Save As", "shortcut": "Ctrl+Shift+S", "action": self.save_as_dialog},
            {"type": "separator"},
            {"type": "item", "label": "Exit", "shortcut": "Alt+F4", "action": lambda: setattr(self, 'running', False)},
        ]
    
    def _get_edit_menu_with_actions(self):
        """Get Edit menu items with actual action functions."""
        return [
            {"type": "item", "label": "Insert", "submenu": [
                {"type": "item", "label": "Circle", "action": lambda: self.insert_at_click(self.viewmodel.create_circle)},
                {"type": "item", "label": "Rectangle", "action": lambda: self.insert_at_click(self.viewmodel.create_rectangle)},
                {"type": "item", "label": "Trapezoid", "action": lambda: self.insert_at_click(self.viewmodel.create_trapezoid)},
            ]},
            {"type": "separator"},
            {"type": "item", "label": "Delete Selected", "shortcut": "Del", "action": self.viewmodel.delete_selected},
            {"type": "item", "label": "Rotate 90°", "shortcut": "R", "action": lambda: self.viewmodel.rotate_selected(90.0)},
            {"type": "separator"},
            {"type": "item", "label": "Reset View", "shortcut": "Ctrl+0", "action": self.viewmodel.reset_viewport},
        ]
    
    def insert_at_click(self, create_func):
        """Insert component at last click position or screen center."""
        if self.viewmodel.has_last_click():
            x, y = self.viewmodel.get_last_click()
        else:
            # Use screen center
            center_x = self.view.width / 2
            center_y = self.view.canvas_top + (self.view.height - self.view.canvas_top) / 2
            x, y = self.viewmodel.screen_to_world(center_x, center_y)
        create_func(x, y)
    
    def show_context_menu(self, pos):
        """Show context menu at mouse position."""
        items = [
            {"type": "item", "label": "Insert Here", "submenu": [
                {"type": "item", "label": "Circle", "action": lambda: self.insert_at_click(self.viewmodel.create_circle)},
                {"type": "item", "label": "Rectangle", "action": lambda: self.insert_at_click(self.viewmodel.create_rectangle)},
                {"type": "item", "label": "Trapezoid", "action": lambda: self.insert_at_click(self.viewmodel.create_trapezoid)},
            ]},
            {"type": "separator"},
            {"type": "item", "label": "Delete", "shortcut": "Del", "action": self.viewmodel.delete_selected},
            {"type": "item", "label": "Rotate 90°", "shortcut": "R", "action": lambda: self.viewmodel.rotate_selected(90.0)},
        ]
        self.view.menu_manager.open_root_menu(pos, items)

    def _get_insertion_point(self):
        """
        Get insertion point based on last click or canvas center.
        
        Returns:
            Tuple of (world_x, world_y)
        """
        if self.viewmodel.has_last_click():
            return self.viewmodel.get_last_click()
        
        center_screen_x = self.view.width / 2
        center_screen_y = self.view.canvas_top + (self.view.height - self.view.canvas_top) / 2
        return self.viewmodel.screen_to_world(center_screen_x, center_screen_y)

    def open_file_dialog(self):
        """Open file dialog to load a scene."""
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        file_path = filedialog.askopenfilename(
            title="Open Scene",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            self.load_scene(file_path)
        
        root.destroy()

    def save_as_dialog(self):
        """Open save as dialog."""
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        file_path = filedialog.asksaveasfilename(
            title="Save Scene As",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            self.save_scene(file_path)
        
        root.destroy()

    def save_scene(self, file_path: str = None):
        """
        Save the current scene.
        
        Args:
            file_path: Optional file path to save to
        """
        if file_path is None:
            file_path = self.viewmodel.get_file_path()
        
        if file_path is None:
            self.save_as_dialog()
            return
        
        try:
            components = self.viewmodel.get_all_components()
            connections = self.viewmodel.get_all_connections()
            self.save_load_manager.save_to_file(components, connections, file_path)
            self.viewmodel.set_file_path(file_path)
            self.viewmodel.status_message = f"Saved to {file_path}"
        except Exception as e:
            self.viewmodel.status_message = f"Failed to save: {str(e)}"

    def load_scene(self, file_path: str = None):
        """
        Load a scene from file.
        
        Args:
            file_path: Optional file path to load from
        """
        if file_path is None:
            self.open_file_dialog()
            return
        
        try:
            components, connections = self.save_load_manager.load_from_file(file_path)
            self.viewmodel.set_components_and_connections(components, connections)
            self.viewmodel.set_file_path(file_path)
            self.viewmodel.status_message = f"Loaded from {file_path}"
        except Exception as e:
            self.viewmodel.status_message = f"Failed to load: {str(e)}"

    def update(self, time_delta: float):
        """
        Update game state (called every frame).
        
        Args:
            time_delta: Time since last update in seconds
        """
        self.view.update(time_delta)

    def render(self):
        """Render the scene using View."""
        mouse_pos = pygame.mouse.get_pos()
        self.view.render(mouse_pos)
        self.view.flip()


def main():
    """Entry point for the PlaneMotion engine."""
    engine = PlaneMotionEngine()
    engine.run()


if __name__ == "__main__":
    main()
