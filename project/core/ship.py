"""
ship.py — The starting location. The player's only certainty.

The ship interior is sparse, lonely, aesthetically minimalist.
It contains a few interactable zones: the cockpit (galaxy map access),
a terminal (journal access), and a viewport (ambient contemplation).

The ship is rendered as a top-down room with soft amber lighting,
dark metallic walls, and a single viewport showing the stars.
"""

from __future__ import annotations

import math
import random

import pygame

from config import (
    COLORS, SCREEN_WIDTH, SCREEN_HEIGHT,
    SHIP_ROOM_WIDTH, SHIP_ROOM_HEIGHT, STAR_COUNT,
)


class InteractZone:
    """A region in the ship the player can interact with.

    Attributes:
        name:        Identifier for the zone.
        rect:        Bounding rectangle in room-local coordinates.
        label:       Text displayed when the player is nearby.
        action:      String key for the action triggered on interaction.
        glow_phase:  Animation timer for the ambient glow.
    """

    def __init__(self, name: str, rect: pygame.Rect,
                 label: str, action: str):
        self.name = name
        self.rect = rect
        self.label = label
        self.action = action
        self.glow_phase: float = random.uniform(0, math.tau)

    def world_rect(self, offset_x: int, offset_y: int) -> pygame.Rect:
        """Return this zone's rect in screen coordinates."""
        return self.rect.move(offset_x, offset_y)


class ShipInterior:
    """The ship interior scene.

    The room is centered on the screen. It contains three interactable zones
    and is drawn with a minimalist aesthetic — dark panels, amber highlights,
    a viewport into space.
    """

    def __init__(self):
        self.room_width = SHIP_ROOM_WIDTH
        self.room_height = SHIP_ROOM_HEIGHT
        self.offset_x = (SCREEN_WIDTH - self.room_width) // 2
        self.offset_y = (SCREEN_HEIGHT - self.room_height) // 2

        # Interactable zones (room-local coordinates).
        self.zones: list[InteractZone] = [
            InteractZone(
                name="cockpit",
                rect=pygame.Rect(
                    self.room_width // 2 - 60, 10, 120, 50,
                ),
                label="[ Navigation Console — E ]",
                action="galaxy_map",
            ),
            InteractZone(
                name="terminal",
                rect=pygame.Rect(
                    self.room_width - 110, self.room_height // 2 - 30, 80, 60,
                ),
                label="[ Personal Terminal — E ]",
                action="journal",
            ),
            InteractZone(
                name="viewport",
                rect=pygame.Rect(
                    15, self.room_height // 2 - 40, 70, 80,
                ),
                label="[ Viewport — E ]",
                action="viewport",
            ),
        ]

        # Background stars for the viewport.
        self._stars = [
            (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT),
             random.uniform(0.3, 1.0), random.uniform(0.5, 2.0))
            for _ in range(STAR_COUNT)
        ]
        self._star_phase: float = 0.0

    def player_bounds(self) -> tuple[float, float, float, float]:
        """Return (min_x, min_y, max_x, max_y) for player clamping."""
        margin = 20
        return (
            self.offset_x + margin,
            self.offset_y + margin,
            self.offset_x + self.room_width - margin,
            self.offset_y + self.room_height - margin,
        )

    def player_start(self) -> tuple[float, float]:
        """Return the starting position for the player in this scene."""
        return (
            self.offset_x + self.room_width // 2,
            self.offset_y + self.room_height * 0.65,
        )

    def get_nearby_zone(self, px: float, py: float,
                        threshold: float = 50) -> InteractZone | None:
        """Return the zone nearest the player if within threshold distance."""
        for zone in self.zones:
            wr = zone.world_rect(self.offset_x, self.offset_y)
            cx = wr.centerx
            cy = wr.centery
            dist = math.hypot(px - cx, py - cy)
            if dist < threshold:
                return zone
        return None

    def draw(self, surface: pygame.Surface, dt: float) -> None:
        """Render the ship interior."""
        self._star_phase += dt

        # Background: starfield.
        surface.fill(COLORS["void"])
        self._draw_stars(surface)

        # Room shell.
        room_rect = pygame.Rect(
            self.offset_x, self.offset_y,
            self.room_width, self.room_height,
        )

        # Floor.
        pygame.draw.rect(surface, COLORS["ship_floor"], room_rect)

        # Walls (layered border).
        pygame.draw.rect(surface, COLORS["ship_wall"], room_rect, 4)
        inner = room_rect.inflate(-8, -8)
        pygame.draw.rect(surface, COLORS["ship_interior"], inner, 1)

        # Draw interactable zones with pulsing glow.
        for zone in self.zones:
            zone.glow_phase += dt * 1.5
            pulse = 0.5 + 0.5 * math.sin(zone.glow_phase)
            wr = zone.world_rect(self.offset_x, self.offset_y)

            # Glow rectangle.
            glow_alpha = int(25 + 25 * pulse)
            glow_surf = pygame.Surface((wr.width, wr.height), pygame.SRCALPHA)
            glow_surf.fill((*COLORS["amber_dim"], glow_alpha))
            surface.blit(glow_surf, wr.topleft)

            # Border.
            border_color = (
                int(COLORS["amber_dim"][0] * (0.6 + 0.4 * pulse)),
                int(COLORS["amber_dim"][1] * (0.6 + 0.4 * pulse)),
                int(COLORS["amber_dim"][2] * (0.6 + 0.4 * pulse)),
            )
            pygame.draw.rect(surface, border_color, wr, 1)

        # Viewport window: a glimpse of deep space on the left wall.
        vp = self.zones[2].world_rect(self.offset_x, self.offset_y)
        pygame.draw.rect(surface, COLORS["deep_space"], vp)
        # A few bright stars inside the viewport.
        for i in range(5):
            sx = vp.left + 10 + (i * 12) % vp.width
            sy = vp.top + 10 + (i * 17 + int(self._star_phase * 3)) % vp.height
            sx = vp.left + (sx - vp.left) % vp.width
            sy = vp.top + (sy - vp.top) % vp.height
            brightness = int(150 + 105 * math.sin(self._star_phase + i))
            pygame.draw.circle(surface, (brightness, brightness, brightness),
                               (sx, sy), 1)

    def draw_zone_labels(self, surface: pygame.Surface, font: pygame.font.Font,
                         nearby_zone: InteractZone | None) -> None:
        """Draw interaction prompts for the zone the player is near."""
        if nearby_zone is None:
            return
        wr = nearby_zone.world_rect(self.offset_x, self.offset_y)
        text_surf = font.render(nearby_zone.label, True, COLORS["amber"])
        text_rect = text_surf.get_rect(centerx=wr.centerx, top=wr.bottom + 8)
        surface.blit(text_surf, text_rect)

    def _draw_stars(self, surface: pygame.Surface) -> None:
        """Draw twinkling background stars."""
        for x, y, brightness, speed in self._stars:
            twinkle = 0.5 + 0.5 * math.sin(self._star_phase * speed)
            c = int(255 * brightness * twinkle)
            c = max(0, min(255, c))
            surface.set_at((x % SCREEN_WIDTH, y % SCREEN_HEIGHT), (c, c, c))
