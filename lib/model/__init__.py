"""
Model layer package.
Contains pure data models for components and connections.
"""

from .component import Component, Circle, Rectangle
from .connection import Connection

__all__ = ['Component', 'Circle', 'Rectangle', 'Connection']
