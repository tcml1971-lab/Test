"""
inventory.py — Items and artifacts.

Items in this game are not tools of power. They are vessels of meaning.
An artifact might be a broken device, a piece of alien calligraphy,
or a stone that hums at a frequency just below hearing. Each one
may (or may not) illuminate some aspect of the protagonist's past.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Item:
    """A collectible item or artifact.

    Attributes:
        item_id:      Unique identifier.
        name:         Display name.
        description:  Atmospheric description text.
        item_type:    Category: "artifact", "tool", "personal", "unknown".
        fragment_id:  If examining this item reveals a fragment, its ID.
        examined:     Whether the player has examined this item.
    """
    item_id: str
    name: str
    description: str
    item_type: str = "artifact"
    fragment_id: str | None = None
    examined: bool = False

    @property
    def type_symbol(self) -> str:
        symbols = {
            "artifact": "\u25A0",   # ■
            "tool":     "\u2692",   # ⚒
            "personal": "\u2661",   # ♡
            "unknown":  "\u003F",   # ?
        }
        return symbols.get(self.item_type, "\u00B7")


class Inventory:
    """The player's collection of items.

    Items are stored in discovery order. The inventory is small by design —
    this is not a hoarding game. Each item should feel deliberate.
    """

    def __init__(self, max_size: int = 12):
        self._items: dict[str, Item] = {}
        self.max_size = max_size

    @property
    def items(self) -> list[Item]:
        return list(self._items.values())

    @property
    def count(self) -> int:
        return len(self._items)

    @property
    def is_full(self) -> bool:
        return self.count >= self.max_size

    def add_item(self, item: Item) -> bool:
        """Add an item to the inventory. Returns False if full."""
        if self.is_full:
            return False
        self._items[item.item_id] = item
        return True

    def get_item(self, item_id: str) -> Item | None:
        return self._items.get(item_id)

    def has_item(self, item_id: str) -> bool:
        return item_id in self._items

    def remove_item(self, item_id: str) -> Item | None:
        return self._items.pop(item_id, None)


# ─── Predefined Items ───────────────────────────────────────────────────────

SHIP_ITEMS: list[Item] = [
    Item(
        item_id="broken_compass",
        name="Broken Compass",
        description=(
            "A navigational instrument that points nowhere. Its needle "
            "spins freely, pausing occasionally — not at north, but at "
            "something it remembers. The casing is scratched with "
            "fingernail marks."
        ),
        item_type="personal",
        fragment_id="ship_log_02",
    ),
]
