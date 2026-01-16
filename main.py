"""
Entry point for the PlaneMotion application.
"""

from engine import PlaneMotionEngine


def main():
    """Launch the PlaneMotion engine."""
    engine = PlaneMotionEngine(
        width=1280,
        height=720,
        title="PlaneMotion - 2D Component Engine"
    )
    engine.run()


if __name__ == "__main__":
    main()
