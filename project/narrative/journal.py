"""
journal.py — The player's journal: a poetic record of identity fragments.

This is not a quest log. It is a personal archive of ambiguity.
Fragments are displayed with their certainty, their contradictions,
and their sources — arranged not chronologically, but by domain,
inviting the player to see patterns (or impose them).
"""

from __future__ import annotations

import math

import pygame

from config import (
    COLORS, SCREEN_WIDTH, SCREEN_HEIGHT,
    FONT_SIZES, KNOWLEDGE_DOMAINS, JOURNAL_MAX_DISPLAY,
)
from core.identity import IdentityMatrix, IdentityFragment
from narrative.fragment import format_fragment_poetic


class Journal:
    """The journal UI — a contemplative interface for reviewing identity.

    Displays fragments grouped by domain, with visual indicators for
    certainty and contradiction. The player can page through fragments
    and read each one in full.

    Attributes:
        identity:        Reference to the player's IdentityMatrix.
        current_domain:  Which knowledge domain is currently selected.
        scroll_offset:   Vertical scroll position within the current view.
        selected_index:  Index of the highlighted fragment.
        viewing_detail:  Whether a fragment is expanded for full reading.
    """

    def __init__(self, identity: IdentityMatrix):
        self.identity = identity
        self.current_domain_index: int = 0
        self.scroll_offset: int = 0
        self.selected_index: int = 0
        self.viewing_detail: bool = False
        self._phase: float = 0.0

    @property
    def current_domain(self) -> str:
        return KNOWLEDGE_DOMAINS[self.current_domain_index]

    @property
    def current_fragments(self) -> list[IdentityFragment]:
        """Fragments for the currently selected domain."""
        return self.identity.fragments_by_domain(self.current_domain)

    def next_domain(self) -> None:
        self.current_domain_index = (
            (self.current_domain_index + 1) % len(KNOWLEDGE_DOMAINS)
        )
        self.selected_index = 0
        self.scroll_offset = 0
        self.viewing_detail = False

    def prev_domain(self) -> None:
        self.current_domain_index = (
            (self.current_domain_index - 1) % len(KNOWLEDGE_DOMAINS)
        )
        self.selected_index = 0
        self.scroll_offset = 0
        self.viewing_detail = False

    def select_next(self) -> None:
        frags = self.current_fragments
        if frags:
            self.selected_index = (self.selected_index + 1) % len(frags)

    def select_prev(self) -> None:
        frags = self.current_fragments
        if frags:
            self.selected_index = (self.selected_index - 1) % len(frags)

    def toggle_detail(self) -> None:
        if self.current_fragments:
            self.viewing_detail = not self.viewing_detail

    def draw(self, surface: pygame.Surface, dt: float,
             font_heading: pygame.font.Font,
             font_body: pygame.font.Font,
             font_small: pygame.font.Font) -> None:
        """Render the journal."""
        self._phase += dt
        w, h = surface.get_size()

        # Background.
        surface.fill(COLORS["ui_bg"])

        # Title.
        title = font_heading.render("Journal", True, COLORS["amber"])
        surface.blit(title, (w // 2 - title.get_width() // 2, 20))

        # Domain tabs.
        self._draw_domain_tabs(surface, font_small, w)

        # Coherence indicator.
        coherence = self.identity.overall_coherence()
        coherence_text = f"Coherence: {coherence:.0%}"
        coh_surf = font_small.render(coherence_text, True, COLORS["ui_text_dim"])
        surface.blit(coh_surf, (w - coh_surf.get_width() - 20, 25))

        # Fragment list or detail view.
        if self.viewing_detail:
            self._draw_detail(surface, font_body, font_small, w, h)
        else:
            self._draw_fragment_list(surface, font_body, font_small, w, h)

        # Navigation hint.
        if self.viewing_detail:
            hint_text = "[ ESC ] Back to list"
        else:
            hint_text = ("[ A/D ] Domain    [ W/S ] Select    "
                         "[ ENTER ] Read    [ ESC ] Close")
        hint = font_small.render(hint_text, True, COLORS["ui_text_dim"])
        surface.blit(hint, (w // 2 - hint.get_width() // 2, h - 30))

    def _draw_domain_tabs(self, surface: pygame.Surface,
                          font: pygame.font.Font, screen_w: int) -> None:
        """Draw the domain selection tabs."""
        tab_y = 60
        total_w = 0
        tabs = []

        for i, domain in enumerate(KNOWLEDGE_DOMAINS):
            is_active = (i == self.current_domain_index)
            color = COLORS["amber"] if is_active else COLORS["ui_text_dim"]
            label = domain.upper()

            # Domain weight indicator.
            weight = self.identity.domain_impression(domain)
            if weight > 0:
                label += f"  ({weight:.0%})"

            text_surf = font.render(label, True, color)
            tabs.append((text_surf, is_active))
            total_w += text_surf.get_width() + 30

        # Center the tabs.
        x = (screen_w - total_w) // 2
        for text_surf, is_active in tabs:
            surface.blit(text_surf, (x, tab_y))
            if is_active:
                # Underline.
                pygame.draw.line(
                    surface, COLORS["amber"],
                    (x, tab_y + text_surf.get_height() + 2),
                    (x + text_surf.get_width(), tab_y + text_surf.get_height() + 2),
                    2,
                )
            x += text_surf.get_width() + 30

    def _draw_fragment_list(self, surface: pygame.Surface,
                            font_body: pygame.font.Font,
                            font_small: pygame.font.Font,
                            w: int, h: int) -> None:
        """Draw the list of fragments for the current domain."""
        frags = self.current_fragments
        list_y = 100
        list_x = 60

        if not frags:
            empty_text = font_body.render(
                "No fragments discovered in this domain.",
                True, COLORS["ui_text_dim"],
            )
            surface.blit(empty_text, (w // 2 - empty_text.get_width() // 2,
                                      h // 2 - 20))
            return

        for i, frag in enumerate(frags):
            if i >= JOURNAL_MAX_DISPLAY:
                break

            is_selected = (i == self.selected_index)
            y = list_y + i * 45

            # Selection indicator.
            if is_selected:
                sel_surf = pygame.Surface((w - 120, 40), pygame.SRCALPHA)
                pulse = 0.3 + 0.2 * math.sin(self._phase * 2)
                sel_surf.fill((*COLORS["amber_dim"], int(40 * pulse)))
                surface.blit(sel_surf, (list_x, y))

            # Type symbol and title.
            prefix = frag.type_symbol + "  "
            title_color = COLORS["amber"] if is_selected else COLORS["ui_text"]
            title_surf = font_body.render(
                prefix + frag.title, True, title_color,
            )
            surface.blit(title_surf, (list_x + 10, y + 2))

            # Certainty bar.
            bar_x = list_x + 10
            bar_y = y + 26
            bar_w = 100
            bar_h = 4
            pygame.draw.rect(surface, COLORS["ui_border"],
                             (bar_x, bar_y, bar_w, bar_h))
            filled_w = int(bar_w * frag.certainty)
            bar_color = COLORS["amber"] if frag.certainty > 0.5 else COLORS["amber_dim"]
            pygame.draw.rect(surface, bar_color,
                             (bar_x, bar_y, filled_w, bar_h))

            # Certainty label.
            cert_surf = font_small.render(
                frag.certainty_label, True, COLORS["ui_text_dim"],
            )
            surface.blit(cert_surf, (bar_x + bar_w + 10, bar_y - 4))

            # Contradiction marker.
            if frag.contradicts:
                contra = font_small.render(
                    "\u2716 contradicted", True, COLORS["bio_violet"],
                )
                surface.blit(contra, (w - 180, y + 8))

    def _draw_detail(self, surface: pygame.Surface,
                     font_body: pygame.font.Font,
                     font_small: pygame.font.Font,
                     w: int, h: int) -> None:
        """Draw a single fragment in full poetic detail."""
        frags = self.current_fragments
        if not frags or self.selected_index >= len(frags):
            return

        frag = frags[self.selected_index]
        lines = format_fragment_poetic(frag)

        y = 100
        for line in lines:
            if not line.strip():
                y += 10
                continue
            # First line (title) in amber, rest in soft white.
            if line.startswith(frag.type_symbol):
                color = COLORS["amber"]
                font = font_body
            elif line.strip().startswith("~"):
                color = COLORS["bio_violet"]
                font = font_small
            elif line.strip().startswith("Source:") or "whisper" in line or "impression" in line:
                color = COLORS["ui_text_dim"]
                font = font_small
            else:
                color = COLORS["ui_text"]
                font = font_small

            line_surf = font.render(line, True, color)
            surface.blit(line_surf, (60, y))
            y += font.get_linesize() + 3
