"""
player.py — The protagonist: unnamed, uncertain, moving through space.

The player has no fixed identity. They have a position, an inventory,
and a growing collection of identity fragments. Their "stats" are not
strength or dexterity — they are axes of self-knowledge.
"""

from __future__ import annotations

import pygame
from config import (
    PLAYER_SPEED, PLAYER_RADIUS, COLORS, SCREEN_WIDTH, SCREEN_HEIGHT,
)
from core.identity import IdentityMatrix


class Player:
    """The unnamed protagonist.

    Attributes:
        x, y:           Position in the current scene.
        speed:          Movement speed in pixels per frame.
        radius:         Visual radius for the player marker.
        identity:       The IdentityMatrix holding all discovered fragments.
        inventory:      List of collected item IDs.
        visited_planets: Set of planet IDs the player has been to.
        current_planet:  ID of the planet the player is currently on, or None.
    """

    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y
        self.speed = PLAYER_SPEED
        self.radius = PLAYER_RADIUS
        self.identity = IdentityMatrix()
        self.inventory: list[str] = []
        self.visited_planets: set[str] = set()
        self.current_planet: str | None = None
        self._glow_phase: float = 0.0

    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        """Move the player based on held keys. Diagonal movement is normalized."""
        dx, dy = 0.0, 0.0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1

        # Normalize diagonal movement.
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        self.x += dx * self.speed
        self.y += dy * self.speed

    def clamp_to_bounds(self, min_x: float, min_y: float,
                        max_x: float, max_y: float) -> None:
        """Keep the player within the given rectangular bounds."""
        self.x = max(min_x + self.radius, min(max_x - self.radius, self.x))
        self.y = max(min_y + self.radius, min(max_y - self.radius, self.y))

    def draw(self, surface: pygame.Surface, dt: float) -> None:
        """Render the player as a softly glowing point of light.

        The glow pulses gently — a heartbeat in the dark.
        """
        self._glow_phase += dt * 2.0
        import math
        pulse = 0.6 + 0.4 * math.sin(self._glow_phase)

        # Outer glow.
        glow_radius = int(self.radius * 2.5)
        glow_color = (
            int(COLORS["amber"][0] * pulse * 0.3),
            int(COLORS["amber"][1] * pulse * 0.3),
            int(COLORS["amber"][2] * pulse * 0.3),
        )
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            glow_surf, (*glow_color, int(60 * pulse)),
            (glow_radius, glow_radius), glow_radius,
        )
        surface.blit(
            glow_surf,
            (int(self.x) - glow_radius, int(self.y) - glow_radius),
        )

        # Core body.
        core_color = (
            int(COLORS["amber"][0] * (0.7 + 0.3 * pulse)),
            int(COLORS["amber"][1] * (0.7 + 0.3 * pulse)),
            int(COLORS["amber"][2] * (0.7 + 0.3 * pulse)),
        )
        pygame.draw.circle(
            surface, core_color,
            (int(self.x), int(self.y)), self.radius,
        )

        # Bright center dot.
        pygame.draw.circle(
            surface, COLORS["amber_glow"],
            (int(self.x), int(self.y)), max(2, self.radius // 3),
        )

    def collides_with(self, rect: pygame.Rect) -> bool:
        """Check if the player overlaps a rectangular region."""
        closest_x = max(rect.left, min(self.x, rect.right))
        closest_y = max(rect.top, min(self.y, rect.bottom))
        dx = self.x - closest_x
        dy = self.y - closest_y
        return (dx * dx + dy * dy) < (self.radius * self.radius)
