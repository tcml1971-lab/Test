"""
progression.py — Progression through knowledge, not experience points.

There is no XP. There is no leveling. Progression is measured along
four axes of understanding: self, origin, purpose, and connection.
Each axis is a spectrum, not a bar to fill. Understanding deepens —
but it also shifts, contradicts, and sometimes retreats.
"""

from __future__ import annotations

from config import KNOWLEDGE_DOMAINS
from core.identity import IdentityMatrix


class KnowledgeState:
    """Tracks the player's progression along knowledge domains.

    This is not a score. It is a portrait of understanding:
    how much the player has explored each axis of identity,
    and how coherent that understanding is.

    Attributes:
        identity:   Reference to the player's IdentityMatrix.
    """

    def __init__(self, identity: IdentityMatrix):
        self.identity = identity

    def domain_depth(self, domain: str) -> float:
        """How deeply has this domain been explored?

        Returns a value in [0.0, 1.0] based on the number of fragments
        and their average certainty. Not a completion percentage —
        a depth of engagement.
        """
        frags = self.identity.fragments_by_domain(domain)
        if not frags:
            return 0.0

        count_factor = min(1.0, len(frags) / 5.0)  # Cap at 5 fragments.
        certainty_factor = sum(f.certainty for f in frags) / len(frags)
        return count_factor * 0.6 + certainty_factor * 0.4

    def overall_depth(self) -> float:
        """Average depth across all domains."""
        depths = [self.domain_depth(d) for d in KNOWLEDGE_DOMAINS]
        return sum(depths) / len(depths) if depths else 0.0

    def has_contradictions(self, domain: str) -> bool:
        """Does this domain contain contradicting fragments?"""
        frags = self.identity.fragments_by_domain(domain)
        for frag in frags:
            if frag.contradicts:
                return True
        return False

    def narrative_stage(self) -> str:
        """Return a poetic description of the player's overall progress.

        This replaces the concept of 'levels' or 'chapters' with
        a description of where the player stands in their journey.
        """
        depth = self.overall_depth()
        coherence = self.identity.overall_coherence()
        contradictions = len(self.identity.contradictions())

        if depth < 0.1:
            return "The silence before the first question"
        elif depth < 0.3:
            if contradictions == 0:
                return "The first fragments of a story not yet told"
            return "Whispers that do not agree"
        elif depth < 0.5:
            if coherence > 0.6:
                return "A pattern emerging from the noise"
            return "Many voices, no chorus"
        elif depth < 0.7:
            if contradictions > 2:
                return "The truth wears many faces"
            return "The shape of someone beginning to form"
        else:
            if coherence > 0.7:
                return "Almost whole — but 'almost' is its own country"
            return "Everything known, nothing certain"
