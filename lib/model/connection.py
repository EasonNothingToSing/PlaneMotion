"""
Model layer: Connection data model.
Represents a connection between two components (data only).
"""

from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .component import Component


class Connection:
    """
    Represents a connection between two components (Model layer).
    Contains only data, no rendering logic.
    """

    def __init__(self, source: 'Component', target: 'Component', color: Tuple[int, int, int] = (200, 200, 200)):
        """
        Initialize a connection between two components.
        
        Args:
            source: Source component
            target: Target component
            color: RGB color tuple for the connection line
        """
        self.source = source
        self.target = target
        self.color = color
        self.line_width = 2

    def get_line_endpoints(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """
        Get the start and end points of the connection line.
        
        Returns:
            Tuple of (start_pos, end_pos) where each is (x, y)
        """
        start_pos = self.source.get_connection_point()
        end_pos = self.target.get_connection_point()
        return start_pos, end_pos

    def contains_point(self, x: float, y: float, threshold: float = 5.0) -> bool:
        """
        Check if a point is near the connection line.
        
        Args:
            x: X-coordinate to check
            y: Y-coordinate to check
            threshold: Distance threshold for selection
            
        Returns:
            True if the point is near the line
        """
        start_pos, end_pos = self.get_line_endpoints()
        x1, y1 = start_pos
        x2, y2 = end_pos
        
        # Vector from start to end
        dx = x2 - x1
        dy = y2 - y1
        
        # Length squared of the line segment
        length_squared = dx * dx + dy * dy
        
        if length_squared == 0:
            # Start and end are the same point
            distance = ((x - x1) ** 2 + (y - y1) ** 2) ** 0.5
        else:
            # Calculate parameter t that parametrizes the projection
            t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / length_squared))
            
            # Find the projection point
            proj_x = x1 + t * dx
            proj_y = y1 + t * dy
            
            # Calculate distance from point to projection
            distance = ((x - proj_x) ** 2 + (y - proj_y) ** 2) ** 0.5
        
        return distance <= threshold

    def to_dict(self, source_id: int, target_id: int) -> dict:
        """
        Serialize connection to dictionary.
        
        Args:
            source_id: ID of the source component
            target_id: ID of the target component
            
        Returns:
            Dictionary representation of the connection
        """
        return {
            'source_id': source_id,
            'target_id': target_id,
            'color': self.color
        }
