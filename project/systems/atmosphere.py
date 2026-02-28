"""
atmosphere.py — Ambient visual mood system.

This module handles atmospheric rendering: particle effects,
ambient lighting shifts, and mood-responsive visuals.
Sound hooks are provided as stubs for future integration.

The atmosphere responds to the player's identity state:
more contradictions create visual unease; higher coherence
produces warmer, more settled visuals.
"""

from __future__ import annotations

import math
import random

import pygame

from config import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT, STAR_PARALLAX_LAYERS


class Particle:
    """A single ambient particle — dust, light mote, or spore."""

    def __init__(self, x: float, y: float, vx: float, vy: float,
                 color: tuple[int, int, int], lifetime: float,
                 size: float = 2.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size

    @property
    def alpha(self) -> float:
        """Particle fades over its lifetime."""
        return max(0.0, self.lifetime / self.max_lifetime)

    @property
    def alive(self) -> bool:
        return self.lifetime > 0

    def update(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt


class AtmosphereSystem:
    """Manages ambient visual effects.

    Creates and updates particles, handles ambient lighting,
    and provides hooks for sound integration.

    Attributes:
        particles:       Active particle list.
        ambient_color:   Current ambient tint applied to the scene.
        mood:            Current mood string (affects visuals).
    """

    def __init__(self):
        self.particles: list[Particle] = []
        self.ambient_color: tuple[int, int, int] = COLORS["deep_space"]
        self.mood: str = "still"
        self._spawn_timer: float = 0.0
        self._phase: float = 0.0

    def set_mood(self, mood: str) -> None:
        """Set the atmospheric mood.

        Moods: "still", "uneasy", "warm", "alien", "contemplative".
        """
        self.mood = mood

    def update(self, dt: float, coherence: float = 0.5) -> None:
        """Update all particles and spawn new ones based on mood."""
        self._phase += dt
        self._spawn_timer += dt

        # Update existing particles.
        self.particles = [p for p in self.particles if p.alive]
        for particle in self.particles:
            particle.update(dt)

        # Spawn new particles periodically.
        spawn_interval = 0.3 if self.mood == "alien" else 0.6
        if self._spawn_timer >= spawn_interval:
            self._spawn_timer = 0.0
            self._spawn_particle(coherence)

        # Adjust ambient color based on mood.
        self._update_ambient(coherence)

    def _spawn_particle(self, coherence: float) -> None:
        """Spawn a particle appropriate to the current mood."""
        if self.mood == "still":
            # Slow-drifting dust motes.
            self.particles.append(Particle(
                x=random.uniform(0, SCREEN_WIDTH),
                y=random.uniform(0, SCREEN_HEIGHT),
                vx=random.uniform(-5, 5),
                vy=random.uniform(-8, -2),
                color=COLORS["ghost_white"],
                lifetime=random.uniform(3.0, 6.0),
                size=random.uniform(1.0, 2.0),
            ))

        elif self.mood == "uneasy":
            # Erratic, dimmer particles.
            self.particles.append(Particle(
                x=random.uniform(0, SCREEN_WIDTH),
                y=SCREEN_HEIGHT + 10,
                vx=random.uniform(-20, 20),
                vy=random.uniform(-30, -10),
                color=COLORS["bio_violet"],
                lifetime=random.uniform(1.5, 3.0),
                size=random.uniform(1.0, 3.0),
            ))

        elif self.mood == "warm":
            # Amber motes drifting upward.
            self.particles.append(Particle(
                x=random.uniform(0, SCREEN_WIDTH),
                y=SCREEN_HEIGHT + 5,
                vx=random.uniform(-3, 3),
                vy=random.uniform(-15, -5),
                color=COLORS["amber_dim"],
                lifetime=random.uniform(4.0, 8.0),
                size=random.uniform(1.5, 3.0),
            ))

        elif self.mood == "alien":
            # Bioluminescent particles with erratic movement.
            colors = [COLORS["bio_cyan"], COLORS["bio_green"], COLORS["bio_violet"]]
            self.particles.append(Particle(
                x=random.uniform(0, SCREEN_WIDTH),
                y=random.uniform(0, SCREEN_HEIGHT),
                vx=random.uniform(-15, 15),
                vy=random.uniform(-15, 15),
                color=random.choice(colors),
                lifetime=random.uniform(2.0, 5.0),
                size=random.uniform(2.0, 4.0),
            ))

        elif self.mood == "contemplative":
            # Very slow, faint particles.
            self.particles.append(Particle(
                x=random.uniform(0, SCREEN_WIDTH),
                y=random.uniform(0, SCREEN_HEIGHT),
                vx=random.uniform(-2, 2),
                vy=random.uniform(-3, 0),
                color=COLORS["pale_blue"],
                lifetime=random.uniform(5.0, 10.0),
                size=random.uniform(1.0, 2.5),
            ))

    def _update_ambient(self, coherence: float) -> None:
        """Shift ambient color based on mood and identity coherence."""
        target = COLORS["deep_space"]
        if self.mood == "warm":
            target = (20, 18, 14)
        elif self.mood == "uneasy":
            target = (14, 8, 18)
        elif self.mood == "alien":
            target = (8, 14, 20)

        # Lerp toward target.
        self.ambient_color = tuple(
            int(self.ambient_color[i] + (target[i] - self.ambient_color[i]) * 0.02)
            for i in range(3)
        )

    def draw(self, surface: pygame.Surface) -> None:
        """Render all active particles."""
        for p in self.particles:
            if not p.alive:
                continue
            alpha = int(255 * p.alpha * 0.6)
            size = max(1, int(p.size * p.alpha))

            if size <= 1:
                x, y = int(p.x), int(p.y)
                if 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT:
                    color = tuple(int(c * p.alpha) for c in p.color)
                    surface.set_at((x, y), color)
            else:
                particle_surf = pygame.Surface(
                    (size * 2, size * 2), pygame.SRCALPHA,
                )
                pygame.draw.circle(
                    particle_surf, (*p.color, alpha),
                    (size, size), size,
                )
                surface.blit(particle_surf,
                             (int(p.x) - size, int(p.y) - size))


# ─── Sound Hooks ─────────────────────────────────────────────────────────────
# Stubs for future ambient sound integration.

class AmbientSoundHook:
    """Placeholder for ambient sound generation.

    When implemented, this will drive procedural ambient audio
    based on mood, location, and identity state.
    """

    def __init__(self):
        self.current_mood: str = "still"
        self.volume: float = 0.5

    def set_mood(self, mood: str) -> None:
        self.current_mood = mood

    def update(self, dt: float) -> None:
        """Update ambient sound state. Currently a no-op."""
        pass

    def play_oneshot(self, sound_id: str) -> None:
        """Play a one-shot sound effect. Currently a no-op."""
        pass
