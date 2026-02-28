"""
universe.py — Procedural universe generation (seed-based).

The universe is a collection of planets arranged in 2D space,
generated deterministically from a seed. Each planet has unique
properties derived from the seed, ensuring the same seed always
produces the same universe.

The galaxy map is the player's interface to this universe — a
sparse, beautiful rendering of reachable worlds against the void.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

import numpy as np
import pygame

from config import (
    COLORS, SCREEN_WIDTH, SCREEN_HEIGHT, NUM_PLANETS,
    UNIVERSE_SEED, GALAXY_MAP_MARGIN,
)
from world.planet import Planet, generate_planet


@dataclass
class StarField:
    """Background stars for the galaxy map, generated from seed."""

    stars: list[tuple[int, int, float, float]] = field(default_factory=list)

    @classmethod
    def generate(cls, seed: int, count: int = 300) -> StarField:
        rng = np.random.RandomState(seed + 999)
        stars = []
        for _ in range(count):
            x = int(rng.uniform(0, SCREEN_WIDTH))
            y = int(rng.uniform(0, SCREEN_HEIGHT))
            brightness = float(rng.uniform(0.2, 1.0))
            speed = float(rng.uniform(0.3, 2.0))
            stars.append((x, y, brightness, speed))
        return cls(stars=stars)


class Universe:
    """The procedural universe.

    Contains a list of planets with positions on the galaxy map.
    Planets are generated from the universe seed — each gets a
    sub-seed that determines all its properties.

    Attributes:
        seed:     The master seed for this universe.
        planets:  List of Planet objects.
        starfield: Background stars for the galaxy map.
    """

    def __init__(self, seed: int = UNIVERSE_SEED):
        self.seed = seed
        self.planets: list[Planet] = []
        self.starfield = StarField.generate(seed)
        self._selected_index: int = 0
        self._generate()

    def _generate(self) -> None:
        """Generate planets deterministically from the seed."""
        rng = np.random.RandomState(self.seed)

        # Place planets in a rough circle around the center, with variation.
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        radius = min(SCREEN_WIDTH, SCREEN_HEIGHT) // 2 - GALAXY_MAP_MARGIN

        for i in range(NUM_PLANETS):
            angle = (2 * math.pi * i / NUM_PLANETS) + float(rng.uniform(-0.3, 0.3))
            dist = radius * float(rng.uniform(0.4, 0.85))
            map_x = int(center_x + math.cos(angle) * dist)
            map_y = int(center_y + math.sin(angle) * dist)

            planet_seed = int(rng.randint(0, 2**31))
            planet = generate_planet(
                planet_id=f"planet_{i}",
                seed=planet_seed,
                map_x=map_x,
                map_y=map_y,
                index=i,
            )
            self.planets.append(planet)

    @property
    def selected_planet(self) -> Planet:
        return self.planets[self._selected_index]

    def select_next(self) -> None:
        self._selected_index = (self._selected_index + 1) % len(self.planets)

    def select_prev(self) -> None:
        self._selected_index = (self._selected_index - 1) % len(self.planets)

    def draw_galaxy_map(self, surface: pygame.Surface, dt: float,
                        font_body: pygame.font.Font,
                        font_small: pygame.font.Font) -> None:
        """Render the galaxy map — planets as glowing nodes in the void."""
        surface.fill(COLORS["void"])

        # Draw starfield.
        phase = pygame.time.get_ticks() / 1000.0
        for x, y, brightness, speed in self.starfield.stars:
            twinkle = 0.4 + 0.6 * math.sin(phase * speed)
            c = int(200 * brightness * twinkle)
            c = max(0, min(255, c))
            surface.set_at((x, y), (c, c, c))

        # Draw connection lines (faint, implied routes).
        for i in range(len(self.planets)):
            for j in range(i + 1, len(self.planets)):
                p1 = self.planets[i]
                p2 = self.planets[j]
                line_color = (*COLORS["ui_border"][:3], 40)
                line_surf = pygame.Surface(
                    (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA,
                )
                pygame.draw.line(
                    line_surf, line_color,
                    (p1.map_x, p1.map_y), (p2.map_x, p2.map_y), 1,
                )
                surface.blit(line_surf, (0, 0))

        # Draw ship position (center, small).
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        pygame.draw.circle(surface, COLORS["amber_dim"], (cx, cy), 4)

        # Draw each planet.
        for i, planet in enumerate(self.planets):
            is_selected = (i == self._selected_index)
            planet.draw_map_node(surface, dt, is_selected, font_small)

        # Draw selected planet info panel.
        selected = self.selected_planet
        self._draw_planet_info(surface, selected, font_body, font_small)

        # Navigation hint.
        hint = font_small.render(
            "[ A/D ] Select Planet    [ ENTER ] Travel    [ ESC ] Return to Ship",
            True, COLORS["ui_text_dim"],
        )
        surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2,
                            SCREEN_HEIGHT - 35))

    def _draw_planet_info(self, surface: pygame.Surface, planet: Planet,
                          font_body: pygame.font.Font,
                          font_small: pygame.font.Font) -> None:
        """Draw an info panel for the selected planet."""
        panel_w, panel_h = 320, 160
        panel_x = SCREEN_WIDTH - panel_w - 30
        panel_y = 30

        # Panel background.
        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel_surf.fill((10, 14, 26, 200))
        pygame.draw.rect(panel_surf, COLORS["ui_border"],
                         (0, 0, panel_w, panel_h), 1)
        surface.blit(panel_surf, (panel_x, panel_y))

        # Planet name.
        name_surf = font_body.render(planet.name, True, COLORS["amber"])
        surface.blit(name_surf, (panel_x + 15, panel_y + 12))

        # Details.
        details = [
            f"Class: {planet.planet_class}",
            f"Atmosphere: {planet.atmosphere}",
            f"Biome: {planet.biome}",
            f"Mystery Level: {'*' * planet.mystery_level}",
        ]
        for j, line in enumerate(details):
            line_surf = font_small.render(line, True, COLORS["ui_text"])
            surface.blit(line_surf, (panel_x + 15, panel_y + 48 + j * 24))
