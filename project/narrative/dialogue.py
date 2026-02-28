"""
dialogue.py — NPC dialogue system with contradiction logic.

Dialogue is not a menu. It is a conversation that shapes identity.
Each choice the player makes potentially adds, modifies, or contradicts
an identity fragment. NPCs remember (or claim to remember) the protagonist
differently, and the system tracks these contradictions.

The dialogue is rendered as a typewriter-effect text with choices
displayed as poetic options, not numbered lists.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import pygame

from config import COLORS, FONT_SIZES, SCREEN_WIDTH, SCREEN_HEIGHT, DIALOGUE_SPEED


@dataclass
class DialogueChoice:
    """A single choice the player can make in dialogue.

    Attributes:
        text:        The displayed text of the choice.
        next_node:   ID of the dialogue node this leads to.
        fragment_id: Optional — ID of a fragment this choice reveals.
        condition:   Optional — a callable that determines if this choice is available.
    """
    text: str
    next_node: str
    fragment_id: str | None = None
    condition: str | None = None  # Reserved for future use.


@dataclass
class DialogueNode:
    """A single node in a dialogue tree.

    Attributes:
        node_id:   Unique identifier within the tree.
        speaker:   Name of the being speaking (or empty for narration).
        text:      The full text of this node.
        choices:   List of choices available after this text is displayed.
    """
    node_id: str
    speaker: str
    text: str
    choices: list[DialogueChoice] = field(default_factory=list)

    @property
    def is_terminal(self) -> bool:
        """Is this node a conversation endpoint?"""
        return len(self.choices) == 0


@dataclass
class DialogueTree:
    """A complete dialogue conversation.

    Attributes:
        tree_id:     Unique identifier.
        nodes:       Dict of node_id -> DialogueNode.
        start_node:  ID of the first node.
    """
    tree_id: str
    nodes: dict[str, DialogueNode]
    start_node: str

    def get_node(self, node_id: str) -> DialogueNode | None:
        return self.nodes.get(node_id)


class DialogueRenderer:
    """Renders dialogue with typewriter effect and choice selection.

    The renderer manages the visual presentation of conversation:
    typewriter text reveal, choice highlighting, speaker display,
    and the atmospheric framing around the dialogue.
    """

    def __init__(self):
        self.current_node: DialogueNode | None = None
        self.revealed_chars: int = 0
        self.reveal_timer: float = 0.0
        self.selected_choice: int = 0
        self.text_complete: bool = False
        self.speaker_name: str = ""
        self._fade_alpha: float = 0.0

    def set_node(self, node: DialogueNode) -> None:
        """Begin displaying a new dialogue node."""
        self.current_node = node
        self.revealed_chars = 0
        self.reveal_timer = 0.0
        self.selected_choice = 0
        self.text_complete = False
        self.speaker_name = node.speaker

    def update(self, dt: float) -> None:
        """Advance the typewriter effect."""
        if self.current_node is None:
            return

        if self._fade_alpha < 1.0:
            self._fade_alpha = min(1.0, self._fade_alpha + dt * 3.0)

        if not self.text_complete:
            self.reveal_timer += dt * 1000  # Convert to milliseconds.
            chars_to_reveal = int(self.reveal_timer / DIALOGUE_SPEED)
            if chars_to_reveal > self.revealed_chars:
                self.revealed_chars = chars_to_reveal

            if self.revealed_chars >= len(self.current_node.text):
                self.text_complete = True
                self.revealed_chars = len(self.current_node.text)

    def skip_to_end(self) -> None:
        """Instantly reveal all text."""
        if self.current_node:
            self.revealed_chars = len(self.current_node.text)
            self.text_complete = True

    def select_next_choice(self) -> None:
        if self.current_node and self.current_node.choices:
            self.selected_choice = (
                (self.selected_choice + 1) % len(self.current_node.choices)
            )

    def select_prev_choice(self) -> None:
        if self.current_node and self.current_node.choices:
            self.selected_choice = (
                (self.selected_choice - 1) % len(self.current_node.choices)
            )

    def get_selected_choice(self) -> DialogueChoice | None:
        """Return the currently highlighted choice, or None."""
        if (self.current_node and self.text_complete
                and self.current_node.choices):
            return self.current_node.choices[self.selected_choice]
        return None

    def draw(self, surface: pygame.Surface, font_body: pygame.font.Font,
             font_small: pygame.font.Font) -> None:
        """Render the dialogue scene."""
        if self.current_node is None:
            return

        w, h = surface.get_size()

        # Dark overlay.
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(200 * self._fade_alpha)))
        surface.blit(overlay, (0, 0))

        # Dialogue panel.
        panel_w = min(700, w - 80)
        panel_h = min(500, h - 80)
        panel_x = (w - panel_w) // 2
        panel_y = (h - panel_h) // 2

        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((10, 14, 26, int(240 * self._fade_alpha)))
        pygame.draw.rect(panel, COLORS["ui_border"], (0, 0, panel_w, panel_h), 1)
        surface.blit(panel, (panel_x, panel_y))

        # Speaker name.
        if self.speaker_name:
            speaker_surf = font_body.render(
                self.speaker_name, True, COLORS["amber"],
            )
            surface.blit(speaker_surf, (panel_x + 20, panel_y + 15))

        # Revealed text.
        text = self.current_node.text[:self.revealed_chars]
        self._draw_wrapped_text(
            surface, text, font_small,
            panel_x + 20, panel_y + 50,
            panel_w - 40, COLORS["ui_text"],
        )

        # Choices (shown only when text is complete).
        if self.text_complete and self.current_node.choices:
            choice_y = panel_y + panel_h - 30 - len(self.current_node.choices) * 30
            for i, choice in enumerate(self.current_node.choices):
                is_selected = (i == self.selected_choice)
                prefix = "\u25B8 " if is_selected else "  "
                color = COLORS["amber"] if is_selected else COLORS["ui_text_dim"]
                choice_surf = font_small.render(
                    prefix + choice.text, True, color,
                )
                surface.blit(choice_surf, (panel_x + 30, choice_y + i * 30))

        # Terminal node: show exit prompt.
        if self.text_complete and self.current_node.is_terminal:
            hint = font_small.render(
                "[ ENTER to continue ]", True, COLORS["ui_text_dim"],
            )
            surface.blit(hint, (panel_x + panel_w // 2 - hint.get_width() // 2,
                                panel_y + panel_h - 30))

    def _draw_wrapped_text(self, surface: pygame.Surface, text: str,
                           font: pygame.font.Font, x: int, y: int,
                           max_width: int, color: tuple) -> None:
        """Draw text with word wrapping and paragraph support."""
        paragraphs = text.split("\n\n")
        line_y = y

        for para_idx, paragraph in enumerate(paragraphs):
            if para_idx > 0:
                line_y += 12  # Paragraph spacing.

            lines = paragraph.split("\n")
            for line in lines:
                words = line.split(" ")
                current_line = ""
                for word in words:
                    test = current_line + (" " if current_line else "") + word
                    test_w = font.size(test)[0]
                    if test_w > max_width and current_line:
                        line_surf = font.render(current_line, True, color)
                        surface.blit(line_surf, (x, line_y))
                        line_y += font.get_linesize() + 2
                        current_line = word
                    else:
                        current_line = test

                if current_line:
                    line_surf = font.render(current_line, True, color)
                    surface.blit(line_surf, (x, line_y))
                    line_y += font.get_linesize() + 2
