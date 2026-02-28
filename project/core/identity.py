"""
identity.py — The philosophical core.

Identity is not a fixed property. It is a constellation of fragments,
each weighted by certainty, each colored by the source that delivered it.
Two players will construct different selves from the same materials.

An IdentityFragment is a single piece of evidence about who the protagonist is.
The IdentityMatrix holds all collected fragments and computes a shifting,
never-settled sense of self.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

from config import FRAGMENT_TYPES, CERTAINTY_LABELS, KNOWLEDGE_DOMAINS


@dataclass
class IdentityFragment:
    """A single shard of identity — memory, testimony, artifact, or vision.

    Attributes:
        fragment_id:  Unique identifier.
        fragment_type: One of FRAGMENT_TYPES.
        title:        Short evocative label (e.g. "A name spoken in anger").
        content:      The full poetic text of the fragment.
        certainty:    Float in [0.0, 1.0]. How much weight this fragment carries.
        domain:       Which knowledge axis this fragment illuminates.
        source:       Who or what provided this fragment (NPC name, artifact, etc.).
        contradicts:  Optional ID of another fragment this one opposes.
        timestamp:    When the fragment was discovered (game time).
        interpreted:  Whether the player has chosen to accept or reject this.
        player_note:  Optional annotation the player has written.
    """

    fragment_id: str
    fragment_type: str
    title: str
    content: str
    certainty: float
    domain: str
    source: str
    contradicts: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    interpreted: bool = False
    player_note: Optional[str] = None

    def __post_init__(self):
        if self.fragment_type not in FRAGMENT_TYPES:
            raise ValueError(
                f"Unknown fragment type '{self.fragment_type}'. "
                f"Must be one of {FRAGMENT_TYPES}."
            )
        if self.domain not in KNOWLEDGE_DOMAINS:
            raise ValueError(
                f"Unknown domain '{self.domain}'. "
                f"Must be one of {KNOWLEDGE_DOMAINS}."
            )
        self.certainty = max(0.0, min(1.0, self.certainty))

    @property
    def certainty_label(self) -> str:
        """Return a poetic description of this fragment's certainty."""
        for (low, high), label in CERTAINTY_LABELS.items():
            if low <= self.certainty < high:
                return label
        return "undeniable — or so it seems"

    @property
    def type_symbol(self) -> str:
        """Return a unicode symbol representing the fragment type."""
        symbols = {
            "memory":    "\u25CB",   # ○
            "testimony": "\u25CA",   # ◊
            "artifact":  "\u25A1",   # □
            "vision":    "\u25B3",   # △
        }
        return symbols.get(self.fragment_type, "\u00B7")


class IdentityMatrix:
    """The shifting sense of self, built from fragments.

    This is not a quest log. It is a philosophical instrument.
    The matrix tracks contradictions, computes weighted impressions
    per knowledge domain, and never offers a definitive answer.
    """

    def __init__(self):
        self._fragments: dict[str, IdentityFragment] = {}
        self._domain_weights: dict[str, float] = {d: 0.0 for d in KNOWLEDGE_DOMAINS}

    @property
    def fragments(self) -> list[IdentityFragment]:
        """All fragments, ordered by discovery time."""
        return sorted(self._fragments.values(), key=lambda f: f.timestamp)

    @property
    def fragment_count(self) -> int:
        return len(self._fragments)

    def add_fragment(self, fragment: IdentityFragment) -> None:
        """Add a new identity fragment to the matrix.

        If this fragment contradicts another, both lose certainty slightly —
        because truth is never comfortable when it has competition.
        """
        self._fragments[fragment.fragment_id] = fragment

        # Handle contradiction: erode certainty on both sides.
        if fragment.contradicts and fragment.contradicts in self._fragments:
            other = self._fragments[fragment.contradicts]
            other.certainty = max(0.0, other.certainty - 0.1)
            fragment.certainty = max(0.0, fragment.certainty - 0.05)

        self._recalculate_domains()

    def get_fragment(self, fragment_id: str) -> Optional[IdentityFragment]:
        return self._fragments.get(fragment_id)

    def fragments_by_domain(self, domain: str) -> list[IdentityFragment]:
        """Return all fragments for a given knowledge domain."""
        return [f for f in self.fragments if f.domain == domain]

    def fragments_by_type(self, fragment_type: str) -> list[IdentityFragment]:
        """Return all fragments of a given type."""
        return [f for f in self.fragments if f.fragment_type == fragment_type]

    def contradictions(self) -> list[tuple[IdentityFragment, IdentityFragment]]:
        """Return all pairs of contradicting fragments."""
        pairs = []
        seen = set()
        for frag in self._fragments.values():
            if frag.contradicts and frag.contradicts in self._fragments:
                pair_key = tuple(sorted([frag.fragment_id, frag.contradicts]))
                if pair_key not in seen:
                    seen.add(pair_key)
                    pairs.append((frag, self._fragments[frag.contradicts]))
        return pairs

    def domain_impression(self, domain: str) -> float:
        """Return the weighted impression for a knowledge domain.

        This is the average certainty of all fragments in that domain.
        It rises and falls as new, potentially contradictory evidence appears.
        It never reaches 1.0 — certainty is an asymptote, not a destination.
        """
        return self._domain_weights.get(domain, 0.0)

    def overall_coherence(self) -> float:
        """How coherent is the player's assembled identity?

        High coherence = few contradictions, high certainty.
        Low coherence = many contradictions, uncertain fragments.
        This is NOT a score. It is a mirror.
        """
        if not self._fragments:
            return 0.0

        total_certainty = sum(f.certainty for f in self._fragments.values())
        contradiction_penalty = len(self.contradictions()) * 0.15
        raw = (total_certainty / len(self._fragments)) - contradiction_penalty
        return max(0.0, min(1.0, raw))

    def _recalculate_domains(self) -> None:
        """Recalculate domain weights from all fragments."""
        for domain in KNOWLEDGE_DOMAINS:
            frags = self.fragments_by_domain(domain)
            if frags:
                self._domain_weights[domain] = (
                    sum(f.certainty for f in frags) / len(frags)
                )
            else:
                self._domain_weights[domain] = 0.0
