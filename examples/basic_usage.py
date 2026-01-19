"""
Basic usage example of the PlaneMotion engine.

This demonstrates how to use the engine with built-in components.
"""

from planemotion import PlaneMotionEngine
from planemotion.components import Circle, Rectangle, Trapezoid


def main():
    """Run the basic example."""
    # Create engine instance
    engine = PlaneMotionEngine(
        width=1400,
        height=900,
        title="PlaneMotion - Basic Example"
    )
    
    # Register built-in components
    engine.register_component_type('circle', Circle)
    engine.register_component_type('rectangle', Rectangle)
    engine.register_component_type('trapezoid', Trapezoid)
    
    # Start the engine
    engine.run()


if __name__ == '__main__':
    main()
