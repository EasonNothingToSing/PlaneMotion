"""
Save and load functionality for the PlaneMotion engine.
Handles serialization and deserialization of components and connections.
Works with MVVM pattern - interacts with Model layer only.
"""

import json
from typing import List, Tuple
from lib.model import Component, Circle, Rectangle, Connection


class SaveLoadManager:
    """
    Manages saving and loading of component states and connections.
    Pure utility class that works with Model layer data structures.
    """

    def save_to_file(self, components: List[Component], connections: List[Connection], filename: str = "scene.json"):
        """
        Save all components and connections to a JSON file.
        
        Args:
            components: List of components to save
            connections: List of connections to save
            filename: Output filename
        """
        # Create component ID mapping
        component_to_id = {id(component): idx for idx, component in enumerate(components)}
        
        # Serialize components
        components_data = []
        for component in components:
            components_data.append(component.to_dict())
        
        # Serialize connections
        connections_data = []
        for connection in connections:
            source_id = component_to_id[id(connection.source)]
            target_id = component_to_id[id(connection.target)]
            connections_data.append(connection.to_dict(source_id, target_id))
        
        # Create the full data structure
        scene_data = {
            'components': components_data,
            'connections': connections_data
        }
        
        # Write to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(scene_data, f, indent=2)
        
        print(f"Scene saved to {filename}")

    def load_from_file(self, filename: str = "scene.json") -> Tuple[List[Component], List[Connection]]:
        """
        Load components and connections from a JSON file.
        
        Args:
            filename: Input filename
            
        Returns:
            Tuple of (components list, connections list)
        """
        try:
            # Read from file
            with open(filename, 'r', encoding='utf-8') as f:
                scene_data = json.load(f)
            
            # Deserialize components
            components = []
            for comp_data in scene_data['components']:
                component = self._create_component_from_dict(comp_data)
                if component:
                    components.append(component)
            
            # Deserialize connections
            connections = []
            for conn_data in scene_data['connections']:
                source_id = conn_data['source_id']
                target_id = conn_data['target_id']
                
                if 0 <= source_id < len(components) and 0 <= target_id < len(components):
                    connection = Connection(
                        components[source_id],
                        components[target_id],
                        tuple(conn_data['color'])
                    )
                    connections.append(connection)
            
            print(f"Scene loaded from {filename}")
            return components, connections
            
        except FileNotFoundError:
            print(f"File {filename} not found. Starting with empty scene.")
            return [], []
        except Exception as e:
            print(f"Error loading scene: {e}")
            return [], []

    def _create_component_from_dict(self, data: dict) -> Component:
        """
        Create a component from dictionary data.
        
        Args:
            data: Dictionary containing component data
            
        Returns:
            Component instance or None if type is unknown
        """
        comp_type = data['type']
        
        if comp_type == 'circle':
            component = Circle(0, 0)
            component.from_dict(data)
            return component
        elif comp_type == 'rectangle':
            component = Rectangle(0, 0)
            component.from_dict(data)
            return component
        else:
            print(f"Unknown component type: {comp_type}")
            return None
