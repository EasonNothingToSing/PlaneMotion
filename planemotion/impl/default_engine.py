"""
Default implementation of PlaneMotion engine.

This wraps the existing engine.py implementation.
"""

import pygame
import pygame_gui
import sys
import tkinter as tk
from tkinter import filedialog
from typing import Dict, Type, Callable, Optional
from planemotion.core.base_component import Component
from planemotion.core.viewmodel import PlaneMotionViewModel
from planemotion.core.view import PlaneMotionView
from planemotion.core.connection import Connection


class DefaultPlaneMotionEngine:
    """
    Default implementation of the PlaneMotion engine.
    
    This is the actual engine that runs. The public API wraps this.
    """
    
    def __init__(
        self,
        width: int,
        height: int,
        title: str,
        component_types: Dict[str, Type[Component]],
        menu_provider: Optional[Callable] = None,
        ui_customizer: Optional[Callable] = None
    ):
        self.width = width
        self.height = height
        self.title = title
        self.component_types = component_types
        self.menu_provider = menu_provider
        self.ui_customizer = ui_customizer
        
        # Initialize ViewModel and View
        self.viewmodel = PlaneMotionViewModel()
        self.view = PlaneMotionView(self.viewmodel, width, height)
        self.view.set_window_title(title)
        
        # Apply UI customization if provided
        if ui_customizer:
            ui_customizer(self.view)
        
        # Game loop control
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.running = True
        
        # Resize hover/cursor state
        self.resize_hit_threshold_px = 8
        self.current_cursor = pygame.SYSTEM_CURSOR_ARROW
        
        # Save/Load manager
        from planemotion.impl.save_load import SaveLoadManager
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
        """Update game state."""
        self.view.update(time_delta)
    
    def render(self):
        """Render the scene."""
        mouse_pos = pygame.mouse.get_pos()
        self.view.render(mouse_pos)
        self.view.flip()
    
    def handle_events(self):
        """Handle all pygame events."""
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
        """Handle mouse button down events."""
        screen_x, screen_y = event.pos
        
        if screen_y < self.view.canvas_top:
            return
        
        if event.button == 1:
            world_x, world_y = self.viewmodel.screen_to_world(screen_x, screen_y)
            self.viewmodel.record_last_click(world_x, world_y)
            
            if self.view.is_connection_mode():
                self.viewmodel.start_connection_at_point(world_x, world_y)
            else:
                resize_threshold_world = self.resize_hit_threshold_px / self.viewmodel.viewport_zoom
                if self.viewmodel.start_resize(world_x, world_y, resize_threshold_world):
                    return
                if not self.viewmodel.start_drag(world_x, world_y):
                    self.viewmodel.deselect_all()
        
        elif event.button == 2:
            self.viewmodel.start_pan(screen_x, screen_y)
        
        elif event.button == 3:
            world_x, world_y = self.viewmodel.screen_to_world(screen_x, screen_y)
            self.viewmodel.record_last_click(world_x, world_y)
            self.show_context_menu(event.pos)
    
    def handle_mouse_up(self, event):
        """Handle mouse button up events."""
        if event.button == 1:
            self.viewmodel.stop_resize()
            self.viewmodel.stop_drag()
        elif event.button == 2:
            self.viewmodel.stop_pan()
    
    def handle_mouse_motion(self, event):
        """Handle mouse motion events."""
        screen_x, screen_y = event.pos
        
        if self.viewmodel.is_panning:
            self.viewmodel.update_pan(screen_x, screen_y)
        elif self.viewmodel.is_resizing():
            world_x, world_y = self.viewmodel.screen_to_world(screen_x, screen_y)
            self.viewmodel.update_resize(world_x, world_y)
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
        """Handle mouse wheel events for viewport zooming."""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.viewmodel.zoom_viewport(event.y, mouse_x, mouse_y)
    
    def handle_window_resize(self, event):
        """Handle window resize event."""
        self.view.resize(event.w, event.h)
    
    def handle_key_down(self, event):
        """Handle keyboard events."""
        if event.key == pygame.K_DELETE:
            self.viewmodel.delete_selected()
        elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
            self.save_scene()
        elif event.key == pygame.K_o and pygame.key.get_mods() & pygame.KMOD_CTRL:
            self.open_file_dialog()
        elif event.key == pygame.K_0 and pygame.key.get_mods() & pygame.KMOD_CTRL:
            self.viewmodel.reset_viewport()
        elif event.key == pygame.K_ESCAPE:
            self.viewmodel.cancel_connection()
    
    def handle_gui_button(self, event):
        """Handle GUI button press events."""
        if event.ui_element == self.view.btn_file:
            r = self.view.btn_file.get_abs_rect()
            items = self._get_file_menu_with_actions()
            self.view.menu_manager.open_root_menu((r.left, r.bottom), items)
        elif event.ui_element == self.view.btn_edit:
            r = self.view.btn_edit.get_abs_rect()
            items = self._get_edit_menu_with_actions()
            self.view.menu_manager.open_root_menu((r.left, r.bottom), items)
        elif event.ui_element == self.view.btn_connect:
            self.view.toggle_connection_mode()
    
    def _get_file_menu_with_actions(self):
        """Get File menu items."""
        if self.menu_provider:
            menus = self.menu_provider(self)
            if 'file' in menus:
                return menus['file']
        
        return [
            {"type": "item", "label": "Open", "shortcut": "Ctrl+O", "action": self.open_file_dialog},
            {"type": "item", "label": "Save", "shortcut": "Ctrl+S", "action": lambda: self.save_scene()},
            {"type": "item", "label": "Save As", "shortcut": "Ctrl+Shift+S", "action": self.save_as_dialog},
            {"type": "separator"},
            {"type": "item", "label": "Exit", "shortcut": "Alt+F4", "action": lambda: setattr(self, 'running', False)},
        ]
    
    def _get_edit_menu_with_actions(self):
        """Get Edit menu items."""
        if self.menu_provider:
            menus = self.menu_provider(self)
            if 'edit' in menus:
                return menus['edit']
        
        # Default edit menu with registered component types
        insert_submenu = []
        for name in self.component_types:
            insert_submenu.append({
                "type": "item",
                "label": name.capitalize(),
                "action": lambda n=name: self.insert_component_at_click(n)
            })
        
        return [
            {"type": "item", "label": "Insert", "submenu": insert_submenu},
            {"type": "separator"},
            {"type": "item", "label": "Delete Selected", "shortcut": "Del", "action": self.viewmodel.delete_selected},
            {"type": "item", "label": "Rotate 90°", "shortcut": "R", "action": lambda: self.viewmodel.rotate_selected(90.0)},
            {"type": "separator"},
            {"type": "item", "label": "Reset View", "shortcut": "Ctrl+0", "action": self.viewmodel.reset_viewport},
        ]
    
    def insert_component_at_click(self, component_type: str):
        """Insert component at last click position."""
        if component_type not in self.component_types:
            return
        
        if self.viewmodel.has_last_click():
            x, y = self.viewmodel.get_last_click()
        else:
            center_x = self.view.width / 2
            center_y = self.view.canvas_top + (self.view.height - self.view.canvas_top) / 2
            x, y = self.viewmodel.screen_to_world(center_x, center_y)
        
        component_class = self.component_types[component_type]
        component = component_class(x, y)
        self.viewmodel.components.append(component)
    
    def show_context_menu(self, pos):
        """Show context menu at mouse position."""
        insert_submenu = []
        for name in self.component_types:
            insert_submenu.append({
                "type": "item",
                "label": name.capitalize(),
                "action": lambda n=name: self.insert_component_at_click(n)
            })
        
        items = [
            {"type": "item", "label": "Insert Here", "submenu": insert_submenu},
            {"type": "separator"},
            {"type": "item", "label": "Delete", "shortcut": "Del", "action": self.viewmodel.delete_selected},
            {"type": "item", "label": "Rotate 90°", "shortcut": "R", "action": lambda: self.viewmodel.rotate_selected(90.0)},
        ]
        self.view.menu_manager.open_root_menu(pos, items)
    
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
        """Save the current scene."""
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
        """Load a scene from file."""
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
