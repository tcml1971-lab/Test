"""
planet.py — Planets: each one a world of questions.

Every planet has a biome, an atmosphere, a color palette, and a mystery level.
All properties are derived deterministically from the planet's seed.
The planet surface is rendered as a side-scrolling explorable landscape
with procedurally placed features.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

import numpy as np
import pygame

from config import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT


# ─── Planet generation tables ────────────────────────────────────────────────

PLANET_CLASSES = [
    "Terrestrial",
    "Crystalline",
    "Oceanic",
    "Volcanic",
    "Fungal",
    "Desolate",
]

ATMOSPHERES = [
    "thin and biting",
    "thick with spores",
    "eerily still",
    "shimmering with heat",
    "luminescent haze",
    "breathable, impossibly",
]

BIOMES = [
    "Glass Deserts",
    "Singing Caverns",
    "Frozen Tidal Flats",
    "Bioluminescent Forests",
    "Obsidian Plains",
    "Coral Mesas",
]

PLANET_NAMES = [
    "Veridian-7",
    "Cygnus Hollow",
    "Amber Reach",
    "The Whispering",
    "Null Garden",
    "Pale Meridian",
    "Drift Sanctum",
    "Wraith Shore",
    "Echo Basin",
]

# Color palettes per planet class.
PLANET_PALETTES = {
    "Terrestrial": ((60, 90, 50), (40, 70, 35), (80, 110, 65)),
    "Crystalline":  ((100, 140, 200), (70, 110, 180), (130, 170, 220)),
    "Oceanic":      ((30, 80, 130), (20, 60, 110), (50, 100, 160)),
    "Volcanic":     ((160, 60, 30), (130, 40, 20), (200, 90, 40)),
    "Fungal":       ((120, 80, 160), (90, 60, 140), (150, 110, 190)),
    "Desolate":     ((80, 75, 70), (60, 55, 50), (100, 95, 90)),
}


@dataclass
class SurfaceFeature:
    """A feature on the planet surface — structure, landmark, or encounter point.

    Attributes:
        x:          Horizontal position on the surface.
        y:          Vertical position (ground level offset).
        width:      Feature width.
        height:     Feature height.
        kind:       Type of feature: "rock", "structure", "glow", "encounter".
        color:      Base color tuple.
        interactable: Whether the player can interact with this feature.
        interaction_id: Identifier for what happens on interaction.
    """
    x: int
    y: int
    width: int
    height: int
    kind: str
    color: tuple[int, int, int]
    interactable: bool = False
    interaction_id: str | None = None


@dataclass
class Planet:
    """A procedurally generated planet.

    Attributes:
        planet_id:     Unique identifier.
        seed:          Seed used to generate this planet.
        name:          Generated name.
        planet_class:  Broad category (Terrestrial, Crystalline, etc.).
        atmosphere:    Descriptive atmosphere string.
        biome:         Primary biome.
        mystery_level: 1–5, how many secrets this planet holds.
        map_x, map_y:  Position on the galaxy map.
        palette:       Three-color tuple for the planet's visual identity.
        ground_y:      Y-coordinate of the ground line.
        features:      List of surface features.
        encounter_ids: IDs of encounters available on this planet.
        visited:       Whether the player has been here.
    """
    planet_id: str
    seed: int
    name: str
    planet_class: str
    atmosphere: str
    biome: str
    mystery_level: int
    map_x: int
    map_y: int
    palette: tuple[tuple[int, int, int], ...]
    ground_y: int = 500
    features: list[SurfaceFeature] = field(default_factory=list)
    encounter_ids: list[str] = field(default_factory=list)
    visited: bool = False

    # Animation state (not serialized).
    _phase: float = 0.0

    def draw_map_node(self, surface: pygame.Surface, dt: float,
                      is_selected: bool, font: pygame.font.Font) -> None:
        """Draw this planet as a node on the galaxy map."""
        self._phase += dt * 1.2

        base_radius = 12 if not is_selected else 16
        pulse = 0.7 + 0.3 * math.sin(self._phase)

        # Glow.
        if is_selected:
            glow_r = int(base_radius * 3)
            glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
            glow_col = (*self.palette[0], int(40 * pulse))
            pygame.draw.circle(glow_surf, glow_col, (glow_r, glow_r), glow_r)
            surface.blit(glow_surf, (self.map_x - glow_r, self.map_y - glow_r))

        # Planet circle.
        color = tuple(int(c * (0.7 + 0.3 * pulse)) for c in self.palette[0])
        pygame.draw.circle(surface, color, (self.map_x, self.map_y), base_radius)

        # Inner highlight.
        highlight = tuple(min(255, c + 40) for c in self.palette[2])
        pygame.draw.circle(surface, highlight,
                           (self.map_x - 3, self.map_y - 3),
                           max(2, base_radius // 3))

        # Name label.
        label = font.render(self.name, True,
                            COLORS["amber"] if is_selected else COLORS["ui_text_dim"])
        surface.blit(label, (self.map_x - label.get_width() // 2,
                             self.map_y + base_radius + 6))

        # Visited indicator.
        if self.visited:
            marker = font.render("\u2713", True, COLORS["amber_dim"])
            surface.blit(marker, (self.map_x + base_radius + 4,
                                  self.map_y - marker.get_height() // 2))

    def draw_surface(self, surface: pygame.Surface, dt: float,
                     camera_x: float) -> None:
        """Draw the planet surface — sky, ground, features."""
        self._phase += dt * 0.5
        w, h = surface.get_size()

        # Sky gradient.
        sky_top = tuple(max(0, c - 30) for c in self.palette[1])
        sky_bottom = self.palette[1]
        for y_line in range(self.ground_y):
            t = y_line / self.ground_y
            color = tuple(
                int(sky_top[i] * (1 - t) + sky_bottom[i] * t)
                for i in range(3)
            )
            pygame.draw.line(surface, color, (0, y_line), (w, y_line))

        # Ground.
        pygame.draw.rect(surface, self.palette[2],
                         (0, self.ground_y, w, h - self.ground_y))

        # Ground line accent.
        accent = tuple(min(255, c + 20) for c in self.palette[2])
        pygame.draw.line(surface, accent, (0, self.ground_y),
                         (w, self.ground_y), 2)

        # Draw features (offset by camera).
        for feat in self.features:
            fx = feat.x - int(camera_x)
            if -feat.width < fx < w + feat.width:
                self._draw_feature(surface, feat, fx, feat.y)

    def _draw_feature(self, surface: pygame.Surface,
                      feat: SurfaceFeature, x: int, y: int) -> None:
        """Draw a single surface feature."""
        if feat.kind == "rock":
            points = [
                (x, y),
                (x + feat.width // 3, y - feat.height),
                (x + feat.width * 2 // 3, y - feat.height * 3 // 4),
                (x + feat.width, y),
            ]
            pygame.draw.polygon(surface, feat.color, points)

        elif feat.kind == "structure":
            rect = pygame.Rect(x, y - feat.height, feat.width, feat.height)
            pygame.draw.rect(surface, feat.color, rect)
            # Window glow.
            pulse = 0.5 + 0.5 * math.sin(self._phase * 2)
            win_color = (
                int(COLORS["amber"][0] * pulse),
                int(COLORS["amber"][1] * pulse),
                int(COLORS["amber"][2] * pulse * 0.5),
            )
            win_rect = pygame.Rect(
                x + feat.width // 4,
                y - feat.height * 3 // 4,
                feat.width // 2,
                feat.height // 4,
            )
            pygame.draw.rect(surface, win_color, win_rect)

        elif feat.kind == "glow":
            glow_r = max(feat.width, feat.height) // 2
            pulse = max(0.0, 0.4 + 0.6 * math.sin(self._phase * 1.5 + x * 0.01))
            glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
            glow_col = (*feat.color, int(80 * pulse))
            pygame.draw.circle(glow_surf, glow_col, (glow_r, glow_r), glow_r)
            surface.blit(glow_surf,
                         (x + feat.width // 2 - glow_r,
                          y - feat.height // 2 - glow_r))

        elif feat.kind == "encounter":
            # NPC encounter marker — a softly pulsing diamond.
            pulse = 0.5 + 0.5 * math.sin(self._phase * 2.5)
            cx = x + feat.width // 2
            cy = y - feat.height // 2
            size = int(10 + 4 * pulse)
            points = [
                (cx, cy - size),
                (cx + size, cy),
                (cx, cy + size),
                (cx - size, cy),
            ]
            color = tuple(int(c * (0.6 + 0.4 * pulse)) for c in COLORS["bio_cyan"])
            pygame.draw.polygon(surface, color, points)

    def get_nearby_feature(self, player_x: float, player_y: float,
                           camera_x: float,
                           threshold: float = 40) -> SurfaceFeature | None:
        """Return the nearest interactable feature within threshold."""
        for feat in self.features:
            if not feat.interactable:
                continue
            fx = feat.x - camera_x + feat.width / 2
            fy = feat.y - feat.height / 2
            dist = math.hypot(player_x - fx, player_y - fy)
            if dist < threshold:
                return feat
        return None


def generate_planet(planet_id: str, seed: int,
                    map_x: int, map_y: int, index: int) -> Planet:
    """Generate a complete planet from a seed.

    All properties — name, class, biome, features — are deterministic.
    The same seed always produces the same world.
    """
    rng = np.random.RandomState(seed)

    name = PLANET_NAMES[index % len(PLANET_NAMES)]
    planet_class = PLANET_CLASSES[int(rng.randint(0, len(PLANET_CLASSES)))]
    atmosphere = ATMOSPHERES[int(rng.randint(0, len(ATMOSPHERES)))]
    biome = BIOMES[int(rng.randint(0, len(BIOMES)))]
    mystery_level = int(rng.randint(1, 6))
    palette = PLANET_PALETTES[planet_class]
    ground_y = int(rng.randint(420, 520))

    # Generate surface features.
    features = []
    num_features = int(rng.randint(8, 20))
    surface_width = 3000  # Scrollable surface width.

    for i in range(num_features):
        fx = int(rng.randint(50, surface_width - 50))
        fw = int(rng.randint(20, 80))
        fh = int(rng.randint(15, 60))
        kind_roll = float(rng.uniform(0, 1))

        if kind_roll < 0.5:
            kind = "rock"
            color = tuple(
                int(c + rng.randint(-20, 20)) for c in palette[2]
            )
            color = tuple(max(0, min(255, c)) for c in color)
            features.append(SurfaceFeature(
                x=fx, y=ground_y, width=fw, height=fh,
                kind=kind, color=color,
            ))
        elif kind_roll < 0.7:
            kind = "glow"
            glow_colors = [COLORS["bio_cyan"], COLORS["bio_green"], COLORS["bio_violet"]]
            color = glow_colors[int(rng.randint(0, 3))]
            features.append(SurfaceFeature(
                x=fx, y=ground_y, width=fw, height=fh,
                kind=kind, color=color,
            ))
        elif kind_roll < 0.85:
            kind = "structure"
            color = tuple(
                int(c + rng.randint(-10, 30)) for c in palette[1]
            )
            color = tuple(max(0, min(255, c)) for c in color)
            features.append(SurfaceFeature(
                x=fx, y=ground_y, width=fw + 20, height=fh + 30,
                kind=kind, color=color,
                interactable=True,
                interaction_id=f"{planet_id}_struct_{i}",
            ))
        else:
            kind = "encounter"
            features.append(SurfaceFeature(
                x=fx, y=ground_y, width=30, height=40,
                kind=kind, color=COLORS["bio_cyan"],
                interactable=True,
                interaction_id=f"{planet_id}_encounter_{i}",
            ))

    # Ensure at least one encounter on the first planet.
    if index == 0:
        has_encounter = any(f.kind == "encounter" for f in features)
        if not has_encounter:
            features.append(SurfaceFeature(
                x=400, y=ground_y, width=30, height=40,
                kind="encounter", color=COLORS["bio_cyan"],
                interactable=True,
                interaction_id=f"{planet_id}_encounter_main",
            ))

    encounter_ids = [f.interaction_id for f in features
                     if f.kind == "encounter" and f.interaction_id]

    return Planet(
        planet_id=planet_id,
        seed=seed,
        name=name,
        planet_class=planet_class,
        atmosphere=atmosphere,
        biome=biome,
        mystery_level=mystery_level,
        map_x=map_x,
        map_y=map_y,
        palette=palette,
        ground_y=ground_y,
        features=features,
        encounter_ids=encounter_ids,
    )
