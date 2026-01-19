"""
PlaneMotion Engine - Main API entry point.

This module provides the main engine class that coordinates all components.
"""

import pygame
import sys
from typing import Type, Dict, Callable, Optional, Tuple, List, Any
from planemotion.core.base_component import Component
from planemotion.core.connection import Connection


class PlaneMotionEngine:
    """
    Main PlaneMotion engine class.
    
    This is the primary interface for using the PlaneMotion engine.
    
    Example:
        >>> engine = PlaneMotionEngine(width=1280, height=720)
        >>> engine.register_component_type('circle', Circle)
        >>> engine.set_menu_provider(my_custom_menu_function)
        >>> engine.run()
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
        
        self.width = width
        self.height = height
        self.title = title
        
        # Component registry
        self._component_types: Dict[str, Type[Component]] = {}
        
        # Menu provider (optional)
        self._menu_provider: Optional[Callable] = None
        
        # UI customization callbacks
        self._ui_customizer: Optional[Callable] = None
        
        # Will be initialized in run()
        self._engine_instance = None
    
    def register_component_type(self, name: str, component_class: Type[Component]):
        """
        Register a custom component type.
        
        Args:
            name: Unique name for this component type
            component_class: Component class (must inherit from Component)
            
        Example:
            >>> class CustomComponent(Component):
            ...     def contains_point(self, x, y):
            ...         return True
            ...     def get_vertices(self):
            ...         return [(self.x, self.y)]
            >>> 
            >>> engine.register_component_type('custom', CustomComponent)
        """
        if not issubclass(component_class, Component):
            raise TypeError(f"{component_class} must inherit from Component")
        
        self._component_types[name] = component_class
    
    def set_menu_provider(self, menu_provider: Callable):
        """
        Set custom menu provider function.
        
        Args:
            menu_provider: Function that returns menu structure
            
        Example:
            >>> def my_menus(engine_instance):
            ...     return {
            ...         'file': [...],
            ...         'edit': [...]
            ...     }
            >>> 
            >>> engine.set_menu_provider(my_menus)
        """
        self._menu_provider = menu_provider
    
    def set_ui_customizer(self, customizer: Callable):
        """
        Set UI customization callback.
        
        Args:
            customizer: Function(view) that customizes the UI
            
        Example:
            >>> def customize_ui(view):
            ...     # Add custom buttons, panels, etc.
            ...     view.my_button = UIButton(...)
            >>> 
            >>> engine.set_ui_customizer(customize_ui)
        """
        self._ui_customizer = customizer
    
    def run(self):
        """
        Start the engine main loop.
        
        This method blocks until the application is closed.
        """
        # Import here to avoid circular dependency
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
    
    def create_component(self, component_type: str, x: float, y: float, **kwargs) -> Component:
        """
        Create a component instance.
        
        Args:
            component_type: Registered component type name
            x: X position
            y: Y position
            **kwargs: Additional component-specific parameters
            
        Returns:
            Component instance
        """
        if component_type not in self._component_types:
            raise ValueError(f"Unknown component type: {component_type}")
        
        return self._component_types[component_type](x, y, **kwargs)
    
    def get_registered_types(self) -> List[str]:
        """
        Get list of registered component types.
        
        Returns:
            List of component type names
        """
        return list(self._component_types.keys())
