"""
PlaneMotion - A 2D Component Relationship Engine

A flexible 2D component engine for building visual applications with
draggable, resizable, and connectable components.

Core Features:
- Component management (create, select, drag, resize, rotate)
- Connection system (visual links between components)
- Viewport control (pan, zoom)
- MVVM architecture
- Extensible component system
- Customizable UI

Example:
    >>> from planemotion import PlaneMotionEngine, Component
    >>> 
    >>> # Create custom component
    >>> class MyComponent(Component):
    ...     def contains_point(self, x, y):
    ...         return True
    >>> 
    >>> # Initialize engine
    >>> engine = PlaneMotionEngine()
    >>> engine.register_component_type('my_component', MyComponent)
    >>> engine.run()
"""

from planemotion.core.base_component import Component
from planemotion.core.connection import Connection

__version__ = "0.1.0"
__author__ = "PlaneMotion Contributors"


class PlaneMotionEngine:
    """
    Main API for PlaneMotion engine.
    
    This is the primary entry point for using the PlaneMotion engine.
    Create an instance, register component types, customize UI and menus,
    then call run() to start the application.
    
    Example:
        >>> engine = PlaneMotionEngine(width=1400, height=900, title="My App")
        >>> engine.register_component_type('circle', Circle)
        >>> engine.run()
    """
    
    def __init__(self, width: int = 1400, height: int = 900, title: str = "PlaneMotion"):
        """
        Initialize the PlaneMotion engine.
        
        Args:
            width: Window width in pixels
            height: Window height in pixels
            title: Window title
        """
        self.width = width
        self.height = height
        self.title = title
        self._component_types = {}
        self._menu_provider = None
        self._ui_customizer = None
        self._engine_instance = None
    
    def register_component_type(self, name: str, component_class):
        """
        Register a custom component type.
        
        The component will appear in the Insert menu and can be created
        programmatically.
        
        Args:
            name: Component type name (used in menus)
            component_class: Component class (must inherit from Component)
        
        Raises:
            TypeError: If component_class doesn't inherit from Component
        """
        if not issubclass(component_class, Component):
            raise TypeError(f"{component_class} must inherit from Component")
        self._component_types[name] = component_class
    
    def set_menu_provider(self, provider_func):
        """
        Set custom menu provider function.
        
        The provider function should take the engine instance as parameter
        and return a dictionary with 'file' and/or 'edit' keys containing
        menu item definitions.
        
        Args:
            provider_func: Function(engine) -> dict
        
        Example:
            >>> def my_menus(engine):
            ...     return {
            ...         'file': [
            ...             {"type": "item", "label": "New", "action": my_action},
            ...         ]
            ...     }
            >>> engine.set_menu_provider(my_menus)
        """
        self._menu_provider = provider_func
    
    def set_ui_customizer(self, customizer_func):
        """
        Set UI customizer function.
        
        The customizer function receives the view instance and can modify
        UI properties like colors, layouts, etc.
        
        Args:
            customizer_func: Function(view) -> None
        
        Example:
            >>> def customize(view):
            ...     view.background_color = (240, 248, 255)
            >>> engine.set_ui_customizer(customize)
        """
        self._ui_customizer = customizer_func
    
    def run(self):
        """
        Start the engine main loop.
        
        This method blocks until the application is closed.
        """
        from planemotion.impl.default_engine import DefaultPlaneMotionEngine
        
        self._engine_instance = DefaultPlaneMotionEngine(
            width=self.width,
            height=self.height,
            title=self.title,
            component_types=self._component_types,
            menu_provider=self._menu_provider,
            ui_customizer=self._ui_customizer
        )
        
        self._engine_instance.run()
    
    # Expose useful properties from underlying engine
    @property
    def viewmodel(self):
        """Access to the view model."""
        return self._engine_instance.viewmodel if self._engine_instance else None
    
    @property
    def view(self):
        """Access to the view."""
        return self._engine_instance.view if self._engine_instance else None
    
    def insert_component_at_click(self, component_type: str):
        """
        Insert component at last click position.
        
        Args:
            component_type: Type name registered with register_component_type
        """
        if self._engine_instance:
            self._engine_instance.insert_component_at_click(component_type)
    
    def open_file_dialog(self):
        """Open file dialog to load a scene."""
        if self._engine_instance:
            self._engine_instance.open_file_dialog()
    
    def save_scene(self, file_path: str = None):
        """
        Save scene to file.
        
        Args:
            file_path: Path to save file. If None, uses last saved path
                      or opens save dialog.
        """
        if self._engine_instance:
            self._engine_instance.save_scene(file_path)


__all__ = [
    # Core classes
    'PlaneMotionEngine',
    'Component',
    'Connection',
]

