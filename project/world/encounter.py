"""
encounter.py — NPC and creature encounters.

Every encounter is a philosophical event. NPCs don't give quests —
they give perspectives. They claim to know who you are, but their
accounts are unsettling, contradictory, and never quite complete.

The first encounter is with a being who "recognizes" the player.
Their testimony is vivid but ambiguous — it could be true,
it could be projection, it could be a lie.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from core.identity import IdentityFragment
from narrative.dialogue import DialogueTree, DialogueNode, DialogueChoice


@dataclass
class Encounter:
    """A meeting with another being.

    Attributes:
        encounter_id:  Unique identifier.
        npc_name:      The name (or designation) of the being.
        description:   Brief atmospheric description of the being.
        dialogue_tree: The conversation structure.
        fragments:     Identity fragments this encounter can yield.
        completed:     Whether this encounter has been resolved.
    """
    encounter_id: str
    npc_name: str
    description: str
    dialogue_tree: DialogueTree
    fragments: list[IdentityFragment] = field(default_factory=list)
    completed: bool = False


def create_first_encounter(planet_id: str) -> Encounter:
    """Create the first NPC encounter — the being who 'recognizes' you.

    This encounter is the philosophical hook of the game. The NPC's
    account is detailed enough to feel true, but wrong enough to
    feel unsettling. The player must choose what to believe.
    """
    # The identity fragments this encounter can yield.
    fragment_remembered = IdentityFragment(
        fragment_id=f"{planet_id}_frag_remembered",
        fragment_type="testimony",
        title="A name spoken in recognition",
        content=(
            "The being called you 'Seren.' It spoke the name as though "
            "tasting something bittersweet. 'You came here before,' it said. "
            "'You were different then. Or perhaps I was.' Its eyes — if they "
            "were eyes — held a grief that felt older than the planet itself."
        ),
        certainty=0.45,
        domain="self",
        source="The Resonant",
    )

    fragment_warned = IdentityFragment(
        fragment_id=f"{planet_id}_frag_warned",
        fragment_type="testimony",
        title="A warning dressed as memory",
        content=(
            "'The last time you stood here,' the being murmured, 'you asked "
            "me to forget you. You said it was kinder.' It paused, light "
            "shifting across its form. 'I tried. I could not. Some things "
            "refuse to be unmade.'"
        ),
        certainty=0.35,
        domain="origin",
        source="The Resonant",
    )

    fragment_rejected = IdentityFragment(
        fragment_id=f"{planet_id}_frag_rejected",
        fragment_type="testimony",
        title="The dissonance of being unnamed",
        content=(
            "You told the being you don't remember. It seemed relieved — "
            "or perhaps disappointed. 'Then you are free,' it said, 'and "
            "I am the only one who carries the weight of what you were.' "
            "You cannot tell if this is a gift or a burden."
        ),
        certainty=0.5,
        domain="self",
        source="The Resonant",
        contradicts=f"{planet_id}_frag_remembered",
    )

    # Build the dialogue tree.
    # Entry node: the NPC speaks first.
    entry = DialogueNode(
        node_id="entry",
        speaker="The Resonant",
        text=(
            "...\n\n"
            "It takes a long time for the being to speak. Light moves across "
            "its surface like thought made visible.\n\n"
            "\"You.\"\n\n"
            "The word is not a greeting. It is not a question. "
            "It is the sound of something long-buried breaking the surface."
        ),
        choices=[
            DialogueChoice(
                text="\"Do you know me?\"",
                next_node="know_me",
            ),
            DialogueChoice(
                text="Say nothing. Wait.",
                next_node="silence",
            ),
            DialogueChoice(
                text="\"I don't know who I am.\"",
                next_node="dont_know",
            ),
        ],
    )

    know_me = DialogueNode(
        node_id="know_me",
        speaker="The Resonant",
        text=(
            "\"Know you?\" A ripple passes through its form — not laughter, "
            "but something adjacent to it. Something sadder.\n\n"
            "\"I knew someone who wore your shape. Someone who stood "
            "where you are standing and asked a different question. "
            "Whether you are the same... that depends on what you "
            "believe a self is.\""
        ),
        choices=[
            DialogueChoice(
                text="\"What was my name?\"",
                next_node="the_name",
            ),
            DialogueChoice(
                text="\"What did I do here?\"",
                next_node="what_happened",
            ),
        ],
    )

    silence = DialogueNode(
        node_id="silence",
        speaker="The Resonant",
        text=(
            "The silence stretches. The being watches you, or perhaps "
            "watches something behind you that only it can see.\n\n"
            "\"You always were patient,\" it says finally. "
            "\"Or perhaps you are simply empty. I have never been able "
            "to tell the difference.\""
        ),
        choices=[
            DialogueChoice(
                text="\"Tell me what you see when you look at me.\"",
                next_node="what_happened",
            ),
            DialogueChoice(
                text="Turn away.",
                next_node="reject",
            ),
        ],
    )

    dont_know = DialogueNode(
        node_id="dont_know",
        speaker="The Resonant",
        text=(
            "A long pause. The light within it dims, then brightens — "
            "like a breath held and released.\n\n"
            "\"Then we are alike in that,\" it says. \"I have never known "
            "what I am either. I only know what I remember. And I remember "
            "you. Seren.\"\n\n"
            "The name hangs in the air between you like something fragile."
        ),
        choices=[
            DialogueChoice(
                text="\"That name means nothing to me.\"",
                next_node="reject",
            ),
            DialogueChoice(
                text="\"Seren...\" Let the name settle.",
                next_node="the_name",
            ),
        ],
    )

    the_name = DialogueNode(
        node_id="the_name",
        speaker="The Resonant",
        text=(
            "\"Seren.\" It speaks the name like a stone placed carefully "
            "on a cairn. \"You came to this world carrying questions "
            "the way others carry weapons. You wanted to understand "
            "something — not about this place. About yourself.\"\n\n"
            "\"I do not know if you found it. You left before I could ask.\""
        ),
        choices=[
            DialogueChoice(
                text="\"I accept this. I was Seren.\"",
                next_node="accept",
                fragment_id=f"{planet_id}_frag_remembered",
            ),
            DialogueChoice(
                text="\"How can I trust your memory?\"",
                next_node="trust",
            ),
        ],
    )

    what_happened = DialogueNode(
        node_id="what_happened",
        speaker="The Resonant",
        text=(
            "\"You asked me to forget you.\" Its voice — if voice is the "
            "right word — carries a weight that bends the air.\n\n"
            "\"You said it was kinder. That some things should not be "
            "remembered because memory gives them power, and power gives "
            "them teeth.\"\n\n"
            "\"I tried to forget. I could not.\""
        ),
        choices=[
            DialogueChoice(
                text="\"I'm sorry.\"",
                next_node="accept_warning",
                fragment_id=f"{planet_id}_frag_warned",
            ),
            DialogueChoice(
                text="\"That doesn't sound like me.\"",
                next_node="reject",
            ),
        ],
    )

    trust = DialogueNode(
        node_id="trust",
        speaker="The Resonant",
        text=(
            "\"You cannot.\" It says this without bitterness. As a fact. "
            "As gravity.\n\n"
            "\"I am the only witness, and every witness is also a storyteller. "
            "I tell you what I remember, but memory is not truth. "
            "It is what truth leaves behind when it passes through a mind.\"\n\n"
            "\"Believe me or don't. Either way, you were here. Either way, "
            "you will leave. That is the only certainty I can offer.\""
        ),
        choices=[
            DialogueChoice(
                text="\"Then I'll carry your version of me. For now.\"",
                next_node="accept",
                fragment_id=f"{planet_id}_frag_remembered",
            ),
            DialogueChoice(
                text="\"I'd rather build my own story.\"",
                next_node="reject",
            ),
        ],
    )

    accept = DialogueNode(
        node_id="accept",
        speaker="The Resonant",
        text=(
            "Something shifts in the being — not relief, not joy, "
            "but a settling. Like sediment finding the riverbed.\n\n"
            "\"Then Seren walks again,\" it says. \"Or walks still. "
            "I was never sure you ever stopped.\"\n\n"
            "It turns away — not in dismissal, but in completion. "
            "There is nothing more it can give you. The rest is yours."
        ),
        choices=[],
    )

    accept_warning = DialogueNode(
        node_id="accept_warning",
        speaker="The Resonant",
        text=(
            "\"Do not apologize for what you do not remember doing. "
            "That is someone else's debt.\"\n\n"
            "The being dims. Not dying — retreating. Returning to "
            "whatever interior world it inhabits when no one is watching.\n\n"
            "\"Go carefully, traveler. The universe remembers even when you don't.\""
        ),
        choices=[],
    )

    reject = DialogueNode(
        node_id="reject",
        speaker="The Resonant",
        text=(
            "\"Then you are unnamed,\" it says. There is no judgment in "
            "the words — only a vast, patient sadness.\n\n"
            "\"Perhaps that is better. To be unnamed is to be unfinished, "
            "and the unfinished are the only ones who can still become.\"\n\n"
            "The being turns its attention inward, its light folding "
            "like a closing book. You are alone again — but differently."
        ),
        choices=[],
    )

    nodes = {
        "entry": entry,
        "know_me": know_me,
        "silence": silence,
        "dont_know": dont_know,
        "the_name": the_name,
        "what_happened": what_happened,
        "trust": trust,
        "accept": accept,
        "accept_warning": accept_warning,
        "reject": reject,
    }

    dialogue_tree = DialogueTree(
        tree_id=f"{planet_id}_first_encounter",
        nodes=nodes,
        start_node="entry",
    )

    return Encounter(
        encounter_id=f"{planet_id}_first_encounter",
        npc_name="The Resonant",
        description=(
            "A being of shifting light and geometry, standing motionless "
            "on the surface as though it has been waiting. Not for you "
            "specifically — but for whoever you turn out to be."
        ),
        dialogue_tree=dialogue_tree,
        fragments=[fragment_remembered, fragment_warned, fragment_rejected],
    )
