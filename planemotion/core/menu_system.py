"""
Custom menu system for PlaneMotion.
Implements dropdown menus, submenus, and context menus using pygame_gui.
"""

import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UIButton, UILabel, UIImage
from typing import List, Dict, Optional, Tuple, Callable


class MenuPanel:
    """
    A single menu panel containing menu items.
    """
    ITEM_H = 28
    DESC_H = 18
    SEP_H = 8
    PAD = 6
    ICON_W = 22
    RIGHT_W = 90

    def __init__(self, manager: pygame_gui.UIManager, items: List[Dict], topleft: Tuple[int, int], layer: int = 50):
        """
        Initialize a menu panel.
        
        Args:
            manager: pygame_gui UIManager
            items: List of menu item dictionaries
            topleft: Screen position (x, y)
            layer: Z-layer for rendering
        """
        self.manager = manager
        self.items = items
        self.layer = layer
        self.rows = []  # Each row: dict(button=..., item=..., rect=..., enabled=...)
        self.panel = None
        self._build(topleft)

    def kill(self):
        """Clean up the panel and all its elements."""
        if self.panel:
            self.panel.kill()
        self.panel = None
        self.rows.clear()

    def _calc_size(self) -> Tuple[int, int]:
        """Calculate panel size based on items."""
        width = 280
        height = self.PAD * 2
        for it in self.items:
            if it.get("type", "item") == "separator":
                height += self.SEP_H
            else:
                height += self.ITEM_H
                if it.get("description"):
                    height += self.DESC_H
        return width, height

    def _build(self, topleft: Tuple[int, int]):
        """Build the menu panel UI."""
        w, h = self._calc_size()
        self.panel = UIPanel(
            relative_rect=pygame.Rect(topleft[0], topleft[1], w, h),
            manager=self.manager,
            object_id='#menu_panel'
        )

        y = self.PAD
        for it in self.items:
            if it.get("type", "item") == "separator":
                # Separator line
                sep = UILabel(
                    relative_rect=pygame.Rect(self.PAD, y + self.SEP_H//2, w - self.PAD*2, 1),
                    text="",
                    manager=self.manager,
                    container=self.panel
                )
                y += self.SEP_H
                continue

            enabled = it.get("enabled", True)
            row_h = self.ITEM_H + (self.DESC_H if it.get("description") else 0)
            row_rect = pygame.Rect(0, y, w, row_h)

            # Icon (if provided)
            if it.get("icon_surf") is not None:
                UIImage(
                    relative_rect=pygame.Rect(self.PAD, y + 6, 16, 16),
                    image_surface=it["icon_surf"],
                    manager=self.manager,
                    container=self.panel
                )

            # Main label
            label_text = it.get("label", "")
            UILabel(
                relative_rect=pygame.Rect(self.PAD + self.ICON_W, y + 4, w - self.PAD*2 - self.ICON_W - self.RIGHT_W, 20),
                text=label_text,
                manager=self.manager,
                container=self.panel
            )

            # Right side: shortcut / submenu arrow
            right_text = it.get("shortcut", "")
            if it.get("submenu") is not None:
                right_text = (right_text + "    " if right_text else "") + "▶"

            if right_text:
                UILabel(
                    relative_rect=pygame.Rect(w - self.PAD - self.RIGHT_W, y + 4, self.RIGHT_W, 20),
                    text=right_text,
                    manager=self.manager,
                    container=self.panel
                )

            # Description (subtitle in gray)
            if it.get("description"):
                UILabel(
                    relative_rect=pygame.Rect(self.PAD + self.ICON_W, y + 20, w - self.PAD*2 - self.ICON_W, 16),
                    text=f"<font color=#AAAAAA>{it['description']}</font>",
                    manager=self.manager,
                    container=self.panel
                )

            # Transparent button covering the entire row for click handling
            btn = UIButton(
                relative_rect=pygame.Rect(0, y, w, row_h),
                text="",
                manager=self.manager,
                container=self.panel,
                object_id='#menu_item_button'
            )
            if not enabled:
                btn.disable()

            self.rows.append({"button": btn, "item": it, "rect": row_rect, "enabled": enabled})
            y += row_h

    def screen_rect_of_row_button(self, row: Dict) -> pygame.Rect:
        """Get screen-space rectangle of a row button."""
        panel_abs = self.panel.get_abs_rect()
        btn_rel = row["button"].get_relative_rect()
        return pygame.Rect(panel_abs.x + btn_rel.x, panel_abs.y + btn_rel.y, btn_rel.w, btn_rel.h)

    def get_hover_row(self, mouse_pos: Tuple[int, int]) -> Optional[Dict]:
        """Get the row under the mouse cursor."""
        if not self.panel:
            return None
        panel_abs = self.panel.get_abs_rect()
        if not panel_abs.collidepoint(mouse_pos):
            return None
        for row in self.rows:
            r = self.screen_rect_of_row_button(row)
            if r.collidepoint(mouse_pos):
                return row
        return None


class MenuManager:
    """
    Manages menu stack and backdrop for dropdown/context menus.
    """

    def __init__(self, ui_manager: pygame_gui.UIManager, window_size: Tuple[int, int]):
        """
        Initialize the menu manager.
        
        Args:
            ui_manager: pygame_gui UIManager
            window_size: (width, height) of the window
        """
        self.ui_manager = ui_manager
        self.window_size = window_size
        self.mask_button = None
        self.stack = []  # [MenuPanel, MenuPanel, ...]
        self._hover_row_per_level = {}  # level -> row

    def is_open(self) -> bool:
        """Check if any menu is open."""
        return len(self.stack) > 0

    def close_all(self):
        """Close all open menus."""
        for p in self.stack:
            p.kill()
        self.stack.clear()
        self._hover_row_per_level.clear()
        if self.mask_button:
            self.mask_button.kill()
            self.mask_button = None

    def _ensure_mask(self):
        """Create a fullscreen backdrop button to catch clicks outside menus."""
        if self.mask_button is None:
            self.mask_button = UIButton(
                relative_rect=pygame.Rect(0, 0, self.window_size[0], self.window_size[1]),
                text="",
                manager=self.ui_manager
            )

    def open_root_menu(self, pos: Tuple[int, int], items: List[Dict]):
        """
        Open a root menu at the specified position.
        
        Args:
            pos: (x, y) screen position
            items: List of menu item dictionaries
        """
        self.close_all()
        self._ensure_mask()

        # Prevent menu from going off-screen
        x, y = pos
        panel = MenuPanel(self.ui_manager, items, (x, y), layer=60)
        abs_rect = panel.panel.get_abs_rect()
        dx = max(0, abs_rect.right - self.window_size[0])
        dy = max(0, abs_rect.bottom - self.window_size[1])
        if dx or dy:
            panel.kill()
            panel = MenuPanel(self.ui_manager, items, (x - dx, y - dy), layer=60)

        self.stack = [panel]

    def open_submenu_for_row(self, level: int, row: Dict):
        """
        Open or close submenu for a menu item row.
        
        Args:
            level: Parent menu level index
            row: Menu row dictionary
        """
        item = row["item"]
        submenu = item.get("submenu")
        if not submenu:
            # No submenu: close deeper levels
            while len(self.stack) > level + 1:
                self.stack.pop().kill()
            return

        # Position submenu to the right of parent row
        parent_panel = self.stack[level]
        row_rect = parent_panel.screen_rect_of_row_button(row)
        x = row_rect.right
        y = row_rect.top

        # Close deeper levels before opening new one
        while len(self.stack) > level + 1:
            self.stack.pop().kill()

        new_panel = MenuPanel(self.ui_manager, submenu, (x, y), layer=60 + level + 1)

        # If submenu goes off-screen right, show it on the left
        abs_rect = new_panel.panel.get_abs_rect()
        if abs_rect.right > self.window_size[0]:
            new_panel.kill()
            new_panel = MenuPanel(self.ui_manager, submenu, (row_rect.left - 280, y), layer=60 + level + 1)
            abs_rect = new_panel.panel.get_abs_rect()

        # If submenu goes off-screen bottom, move it up
        if abs_rect.bottom > self.window_size[1]:
            dy = abs_rect.bottom - self.window_size[1]
            new_panel.kill()
            new_panel = MenuPanel(self.ui_manager, submenu, (new_panel.panel.get_abs_rect().x, y - dy), layer=60 + level + 1)

        self.stack.append(new_panel)

    def update_window_size(self, new_size: Tuple[int, int]):
        """Update window size for menu positioning."""
        self.window_size = new_size
        if self.mask_button:
            self.mask_button.kill()
            self.mask_button = None
            if self.is_open():
                self._ensure_mask()

    def handle_event(self, event) -> bool:
        """
        Handle pygame events for menu interaction.
        
        Args:
            event: pygame event
            
        Returns:
            True if event was handled by menu system
        """
        # ESC closes menu
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.is_open():
                self.close_all()
                return True

        # Mask button click closes menu
        if event.type == pygame_gui.UI_BUTTON_PRESSED and self.mask_button is not None:
            if event.ui_element == self.mask_button:
                self.close_all()
                return True

        # Menu item button click
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            for level, panel in enumerate(self.stack):
                for row in panel.rows:
                    if event.ui_element == row["button"]:
                        it = row["item"]
                        if it.get("submenu"):
                            self.open_submenu_for_row(level, row)
                        else:
                            act = it.get("action")
                            if callable(act):
                                act()
                            self.close_all()
                        return True

        # Mouse motion: hover to expand submenus
        if event.type == pygame.MOUSEMOTION and self.is_open():
            pos = event.pos
            for level, panel in enumerate(self.stack):
                row = panel.get_hover_row(pos)
                if row is not None:
                    if row["item"].get("submenu"):
                        prev = self._hover_row_per_level.get(level)
                        if prev is not row:
                            self._hover_row_per_level[level] = row
                            self.open_submenu_for_row(level, row)
                    else:
                        self._hover_row_per_level[level] = row
                        while len(self.stack) > level + 1:
                            self.stack.pop().kill()
                    return True

        return False
