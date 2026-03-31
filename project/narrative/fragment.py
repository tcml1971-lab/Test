"""
fragment.py — Story fragments, logs, and memories.

These are the scattered pieces of narrative the player collects.
Each fragment is a self-contained piece of prose — not a quest objective,
but a piece of a mosaic that may or may not form a coherent picture.

Fragments are stored in the IdentityMatrix (core/identity.py).
This module provides the content library: the actual text of each
fragment that can be discovered in the game world.
"""

from __future__ import annotations

from core.identity import IdentityFragment


# ─── Ship Fragments ─────────────────────────────────────────────────────────
# Found aboard the player's vessel. These are the first clues.

SHIP_FRAGMENTS: list[IdentityFragment] = [
    IdentityFragment(
        fragment_id="ship_log_01",
        fragment_type="memory",
        title="Waking",
        content=(
            "You woke with the taste of static in your mouth. "
            "The ship hummed around you — not a greeting, but a continuation. "
            "As though it had been humming long before you were there to hear it.\n\n"
            "There is a dent in the wall beside your sleeping alcove. "
            "It is shaped like a fist. You do not know whose."
        ),
        certainty=0.7,
        domain="self",
        source="Ship's log",
    ),
    IdentityFragment(
        fragment_id="ship_log_02",
        fragment_type="artifact",
        title="The scratched coordinate",
        content=(
            "On the underside of the navigation console, someone has scratched "
            "a series of numbers with a sharp object. They are not coordinates "
            "to any star system in the database.\n\n"
            "Below the numbers, in smaller, more careful lettering: "
            "'DON'T FOLLOW THIS.'\n\n"
            "The handwriting looks like it might be yours."
        ),
        certainty=0.3,
        domain="origin",
        source="Ship artifact",
    ),
    IdentityFragment(
        fragment_id="ship_log_03",
        fragment_type="vision",
        title="The dream of falling upward",
        content=(
            "In the space between sleep and waking, you saw yourself — "
            "or someone wearing your body — falling upward into a sky "
            "that was not a sky but a mouth. A vast, patient opening "
            "that did not swallow but received.\n\n"
            "You woke gasping. The ship's lights had changed color, "
            "as though something had passed through them."
        ),
        certainty=0.15,
        domain="purpose",
        source="Dream",
    ),
]


# ─── Planet Fragments ────────────────────────────────────────────────────────
# Found on planetary surfaces. Tied to structures and artifacts.

def get_structure_fragment(structure_id: str) -> IdentityFragment | None:
    """Return a fragment associated with a planetary structure, if any.

    Not all structures yield fragments. Discovery should feel rare
    and meaningful, not systematic.
    """
    fragments = {
        "planet_0_struct_0": IdentityFragment(
            fragment_id="planet_0_struct_frag",
            fragment_type="artifact",
            title="The unfinished letter",
            content=(
                "Inside the structure, etched into a surface that might be "
                "stone or might be bone, you find text. It reads:\n\n"
                "'I am writing this so that when you return — and you will "
                "return, because you always do — you will know that I waited. "
                "I do not resent the waiting. I resent that you made it "
                "feel like a choice.'\n\n"
                "The letter is unsigned. The surface is warm to the touch."
            ),
            certainty=0.4,
            domain="connection",
            source="Unknown author",
        ),
    }
    return fragments.get(structure_id)


# ─── Fragment Presentation ───────────────────────────────────────────────────

def format_fragment_poetic(fragment: IdentityFragment) -> list[str]:
    """Format a fragment for poetic display in the journal.

    Returns a list of lines, with the title, type symbol,
    certainty label, and content formatted for rendering.
    """
    lines = [
        f"{fragment.type_symbol}  {fragment.title}",
        "",
        f"    {fragment.certainty_label}",
        f"    Source: {fragment.source}",
        "",
    ]

    # Wrap content into lines of ~60 characters.
    words = fragment.content.split()
    current_line = "    "
    for word in words:
        if word == "\n\n":
            lines.append(current_line)
            lines.append("")
            current_line = "    "
        elif len(current_line) + len(word) + 1 > 64:
            lines.append(current_line)
            current_line = "    " + word
        else:
            if current_line.strip():
                current_line += " " + word
            else:
                current_line += word
    if current_line.strip():
        lines.append(current_line)

    # Contradiction note.
    if fragment.contradicts:
        lines.append("")
        lines.append("    ~ This fragment contradicts another memory ~")

    return lines
