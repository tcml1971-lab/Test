"""
hud.py — Heads-up display: minimal, unobtrusive, atmospheric.

The HUD is not a dashboard. It is a quiet presence at the edges
of the screen: a scene label, a fragment counter, a hint of
the player's coherence. It fades when not needed.
"""

from __future__ import annotations

import math

import pygame

from config import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT
from core.identity import IdentityMatrix
from systems.progression import KnowledgeState


class HUD:
    """The in-game heads-up display.

    Shows minimal information: current location, fragment count,
    narrative stage, and interaction prompts. Designed to be
    atmospheric rather than informational.

    Attributes:
        identity:      Reference to the player's IdentityMatrix.
        knowledge:     Reference to the KnowledgeState.
        scene_label:   Current scene name for display.
        prompt_text:   Temporary interaction prompt.
        prompt_timer:  Time remaining for the prompt display.
    """

    def __init__(self, identity: IdentityMatrix):
        self.identity = identity
        self.knowledge = KnowledgeState(identity)
        self.scene_label: str = ""
        self.prompt_text: str = ""
        self.prompt_timer: float = 0.0
        self._phase: float = 0.0
        self._fade_in: float = 0.0

    def set_scene(self, label: str) -> None:
        """Set the current scene label."""
        self.scene_label = label
        self._fade_in = 0.0

    def show_prompt(self, text: str, duration: float = 3.0) -> None:
        """Display a temporary prompt message."""
        self.prompt_text = text
        self.prompt_timer = duration

    def update(self, dt: float) -> None:
        """Update animation timers."""
        self._phase += dt
        self._fade_in = min(1.0, self._fade_in + dt * 2.0)

        if self.prompt_timer > 0:
            self.prompt_timer -= dt
            if self.prompt_timer <= 0:
                self.prompt_text = ""
                self.prompt_timer = 0.0

    def draw(self, surface: pygame.Surface,
             font_hud: pygame.font.Font,
             font_small: pygame.font.Font) -> None:
        """Render the HUD overlay."""
        w, h = surface.get_size()
        alpha = self._fade_in

        # Scene label (top-left, fades in).
        if self.scene_label:
            label_color = tuple(
                int(c * alpha) for c in COLORS["ui_text_dim"]
            )
            label = font_hud.render(self.scene_label, True, label_color)
            surface.blit(label, (15, 10))

        # Fragment counter (top-right).
        count = self.identity.fragment_count
        if count > 0:
            counter_text = f"{count} fragment{'s' if count != 1 else ''}"
            counter_color = COLORS["amber_dim"]
            counter = font_small.render(counter_text, True, counter_color)
            surface.blit(counter, (w - counter.get_width() - 15, 10))

        # Narrative stage (top-right, below counter).
        stage = self.knowledge.narrative_stage()
        stage_surf = font_small.render(stage, True, COLORS["ui_text_dim"])
        surface.blit(stage_surf, (w - stage_surf.get_width() - 15, 28))

        # Coherence indicator (subtle bar, top-right).
        if count > 0:
            coherence = self.identity.overall_coherence()
            bar_w = 80
            bar_h = 2
            bar_x = w - bar_w - 15
            bar_y = 48
            pygame.draw.rect(surface, COLORS["ui_border"],
                             (bar_x, bar_y, bar_w, bar_h))
            filled = int(bar_w * coherence)
            pygame.draw.rect(surface, COLORS["amber_dim"],
                             (bar_x, bar_y, filled, bar_h))

        # Interaction prompt (bottom-center, temporary).
        if self.prompt_text:
            fade = min(1.0, self.prompt_timer / 0.5) if self.prompt_timer < 0.5 else 1.0
            prompt_color = tuple(
                int(c * fade) for c in COLORS["amber"]
            )
            prompt = font_hud.render(self.prompt_text, True, prompt_color)
            surface.blit(prompt, (w // 2 - prompt.get_width() // 2, h - 60))
