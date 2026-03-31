"""
menus.py — Main menu and pause menu.

The main menu is not a splash screen. It is a threshold —
a moment of stillness before the journey begins. Minimal text,
deep space, slow stars.
"""

from __future__ import annotations

import math
import random

import pygame

from config import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT


class MainMenu:
    """The game's main menu.

    A sparse, atmospheric title screen with drifting stars
    and a slow-breathing title. Options are minimal:
    Begin, Continue (placeholder), and Quit.

    Attributes:
        selected:    Currently highlighted option index.
        options:     List of menu option labels.
        stars:       Background star positions.
    """

    def __init__(self):
        self.selected: int = 0
        self.options: list[str] = ["Begin", "Quit"]
        self._phase: float = 0.0
        self._stars = [
            (random.randint(0, SCREEN_WIDTH),
             random.randint(0, SCREEN_HEIGHT),
             random.uniform(0.2, 1.0),
             random.uniform(0.3, 1.5))
            for _ in range(200)
        ]

    def select_next(self) -> None:
        self.selected = (self.selected + 1) % len(self.options)

    def select_prev(self) -> None:
        self.selected = (self.selected - 1) % len(self.options)

    def get_selection(self) -> str:
        return self.options[self.selected]

    def draw(self, surface: pygame.Surface, dt: float,
             font_title: pygame.font.Font,
             font_body: pygame.font.Font,
             font_small: pygame.font.Font) -> None:
        """Render the main menu."""
        self._phase += dt
        w, h = surface.get_size()

        # Background.
        surface.fill(COLORS["void"])

        # Stars.
        for x, y, brightness, speed in self._stars:
            twinkle = 0.3 + 0.7 * math.sin(self._phase * speed + x * 0.01)
            c = int(200 * brightness * twinkle)
            c = max(0, min(255, c))
            if 0 <= x < w and 0 <= y < h:
                surface.set_at((x, y), (c, c, c))

        # Title — breathing alpha.
        title_alpha = 0.6 + 0.4 * math.sin(self._phase * 0.5)
        title_color = tuple(
            int(c * title_alpha) for c in COLORS["amber"]
        )
        title_surf = font_title.render("The Unnamed Vessel", True, title_color)
        surface.blit(title_surf,
                     (w // 2 - title_surf.get_width() // 2, h // 3 - 30))

        # Subtitle.
        sub_alpha = 0.3 + 0.3 * math.sin(self._phase * 0.3 + 1.0)
        sub_color = tuple(
            int(c * sub_alpha) for c in COLORS["ui_text_dim"]
        )
        sub = font_small.render(
            "A journey of identity, told in fragments", True, sub_color,
        )
        surface.blit(sub, (w // 2 - sub.get_width() // 2, h // 3 + 30))

        # Options.
        opt_y = h // 2 + 40
        for i, option in enumerate(self.options):
            is_selected = (i == self.selected)
            if is_selected:
                pulse = 0.7 + 0.3 * math.sin(self._phase * 3)
                color = tuple(int(c * pulse) for c in COLORS["amber"])
                prefix = "\u25B8 "
            else:
                color = COLORS["ui_text_dim"]
                prefix = "  "

            opt_surf = font_body.render(prefix + option, True, color)
            surface.blit(opt_surf,
                         (w // 2 - opt_surf.get_width() // 2, opt_y + i * 40))

        # Bottom text.
        bottom = font_small.render(
            "Identity is not found. It is assembled.",
            True, COLORS["ui_text_dim"],
        )
        surface.blit(bottom,
                     (w // 2 - bottom.get_width() // 2, h - 50))


class PauseOverlay:
    """A translucent pause overlay.

    Displayed when the player presses ESC during gameplay.
    Options: Resume, Journal, Quit to Menu.
    """

    def __init__(self):
        self.selected: int = 0
        self.options: list[str] = ["Resume", "Journal", "Quit to Menu"]
        self._phase: float = 0.0

    def select_next(self) -> None:
        self.selected = (self.selected + 1) % len(self.options)

    def select_prev(self) -> None:
        self.selected = (self.selected - 1) % len(self.options)

    def get_selection(self) -> str:
        return self.options[self.selected]

    def draw(self, surface: pygame.Surface, dt: float,
             font_body: pygame.font.Font,
             font_small: pygame.font.Font) -> None:
        """Render the pause overlay."""
        self._phase += dt
        w, h = surface.get_size()

        # Dark overlay.
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        # Paused label.
        label = font_body.render("— Paused —", True, COLORS["amber_dim"])
        surface.blit(label, (w // 2 - label.get_width() // 2, h // 3))

        # Options.
        for i, option in enumerate(self.options):
            is_selected = (i == self.selected)
            if is_selected:
                pulse = 0.7 + 0.3 * math.sin(self._phase * 3)
                color = tuple(int(c * pulse) for c in COLORS["amber"])
                prefix = "\u25B8 "
            else:
                color = COLORS["ui_text_dim"]
                prefix = "  "

            opt_surf = font_body.render(prefix + option, True, color)
            surface.blit(opt_surf,
                         (w // 2 - opt_surf.get_width() // 2,
                          h // 2 + i * 40))
