"""
Main engine: Coordinates MVVM components and handles the game loop.
Acts as the controller in MVVM pattern.
"""

import pygame
import sys
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
        
        # Save/Load manager
        self.save_load_manager = SaveLoadManager()

    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(self.fps)
        
        pygame.quit()
        sys.exit()

    def handle_events(self):
        """Handle all pygame events and delegate to ViewModel."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
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
        
        # Left click - select and drag
        if event.button == 1:
            # Convert screen coordinates to world coordinates
            world_x, world_y = self.viewmodel.screen_to_world(screen_x, screen_y)
            if not self.viewmodel.start_drag(world_x, world_y):
                self.viewmodel.deselect_all()
        
        # Middle click - pan
        elif event.button == 2:
            self.viewmodel.start_pan(screen_x, screen_y)
        
        # Right click - create connections
        elif event.button == 3:
            # Convert screen coordinates to world coordinates
            world_x, world_y = self.viewmodel.screen_to_world(screen_x, screen_y)
            self.viewmodel.start_connection_at_point(world_x, world_y)

    def handle_mouse_up(self, event):
        """
        Handle mouse button up events.
        
        Args:
            event: Pygame mouse button up event
        """
        if event.button == 1:
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
        # Update dragging position
        elif self.viewmodel.is_dragging():
            world_x, world_y = self.viewmodel.screen_to_world(screen_x, screen_y)
            self.viewmodel.update_drag(world_x, world_y)

    def handle_mouse_wheel(self, event):
        """
        Handle mouse wheel events for viewport zooming.
        
        Args:
            event: Pygame mouse wheel event
        """
        # Zoom viewport around mouse cursor
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.viewmodel.zoom_viewport(event.y, mouse_x, mouse_y)

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

    def save_scene(self):
        """Save the current scene."""
        components = self.viewmodel.get_all_components()
        connections = self.viewmodel.get_all_connections()
        self.save_load_manager.save_to_file(components, connections)

    def load_scene(self):
        """Load a scene from file."""
        components, connections = self.save_load_manager.load_from_file()
        self.viewmodel.set_components_and_connections(components, connections)

    def update(self):
        """Update game state (called every frame)."""
        pass

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
