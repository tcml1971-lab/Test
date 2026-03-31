"""
main.py — The Unnamed Vessel: game loop and scene management.

This is the entry point. It initializes Pygame, creates the game world,
and runs the main loop — dispatching input and rendering to the
currently active scene.

Scenes:
    - main_menu:    Title screen.
    - ship:         The ship interior (starting location).
    - galaxy_map:   Planet selection and travel.
    - planet:       Planetary surface exploration.
    - dialogue:     NPC conversation.
    - journal:      Fragment review.

Run with: python main.py
"""

from __future__ import annotations

import sys

import pygame

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    COLORS, FONT_SIZES, FONT_PATH,
)
from core.player import Player
from core.ship import ShipInterior
from core.identity import IdentityFragment
from world.universe import Universe
from world.encounter import Encounter, create_first_encounter
from narrative.fragment import SHIP_FRAGMENTS, get_structure_fragment
from narrative.dialogue import DialogueRenderer
from narrative.journal import Journal
from systems.inventory import Inventory
from systems.atmosphere import AtmosphereSystem
from systems.progression import KnowledgeState
from ui.hud import HUD
from ui.menus import MainMenu, PauseOverlay


class Game:
    """The main game controller.

    Manages the game loop, scene transitions, and global state.
    Each scene is handled by a dedicated update/draw method pair.
    """

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        # Fonts.
        self.fonts = self._load_fonts()

        # Core systems.
        self.player = Player()
        self.ship = ShipInterior()
        self.universe = Universe()
        self.inventory = Inventory()
        self.atmosphere = AtmosphereSystem()
        self.hud = HUD(self.player.identity)
        self.journal = Journal(self.player.identity)
        self.dialogue_renderer = DialogueRenderer()

        # Menus.
        self.main_menu = MainMenu()
        self.pause_overlay = PauseOverlay()

        # Scene state.
        self.scene: str = "main_menu"
        self.paused: bool = False
        self.previous_scene: str = "ship"

        # Encounter state.
        self.active_encounter: Encounter | None = None
        self.encounters_created: dict[str, Encounter] = {}

        # Planet exploration state.
        self.camera_x: float = 0.0
        self.planet_prompt_text: str = ""

        # Give the player the initial waking fragment.
        self._give_initial_fragments()

        # Position player in ship.
        sx, sy = self.ship.player_start()
        self.player.x = sx
        self.player.y = sy
        self.hud.set_scene("The Ship")

    def _load_fonts(self) -> dict[str, pygame.font.Font]:
        """Load fonts at configured sizes."""
        fonts = {}
        for name, size in FONT_SIZES.items():
            if FONT_PATH:
                try:
                    fonts[name] = pygame.font.Font(FONT_PATH, size)
                except FileNotFoundError:
                    fonts[name] = pygame.font.Font(None, size)
            else:
                fonts[name] = pygame.font.Font(None, size)
        return fonts

    def _give_initial_fragments(self) -> None:
        """Grant the opening fragment — the act of waking."""
        first = SHIP_FRAGMENTS[0]
        self.player.identity.add_fragment(first)

    def run(self) -> None:
        """The main game loop."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)  # Cap delta to avoid physics glitches.

            self._handle_events()
            self._update(dt)
            self._draw(dt)

            pygame.display.flip()

        pygame.quit()
        sys.exit()

    # ─── Event Handling ──────────────────────────────────────────────────

    def _handle_events(self) -> None:
        """Process all pygame events and dispatch to scene handlers."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                # Global pause toggle (except in menus).
                if event.key == pygame.K_ESCAPE:
                    self._handle_escape()
                    continue

                # Dispatch to scene-specific handler.
                if self.paused:
                    self._handle_pause_input(event)
                elif self.scene == "main_menu":
                    self._handle_menu_input(event)
                elif self.scene == "ship":
                    self._handle_ship_input(event)
                elif self.scene == "galaxy_map":
                    self._handle_galaxy_input(event)
                elif self.scene == "planet":
                    self._handle_planet_input(event)
                elif self.scene == "dialogue":
                    self._handle_dialogue_input(event)
                elif self.scene == "journal":
                    self._handle_journal_input(event)

    def _handle_escape(self) -> None:
        """Handle ESC key — context-dependent."""
        if self.scene == "main_menu":
            self.running = False
        elif self.scene == "journal":
            if self.journal.viewing_detail:
                self.journal.viewing_detail = False
            else:
                self.scene = self.previous_scene
        elif self.scene == "dialogue":
            pass  # Can't escape dialogue.
        elif self.scene == "galaxy_map":
            self.scene = "ship"
            self.hud.set_scene("The Ship")
            self.atmosphere.set_mood("still")
        elif self.scene == "planet":
            # Return to galaxy map.
            self.scene = "galaxy_map"
            self.hud.set_scene("Galaxy Map")
            self.atmosphere.set_mood("contemplative")
        elif self.paused:
            self.paused = False
        else:
            self.paused = True

    def _handle_menu_input(self, event: pygame.event.EventType) -> None:
        if event.key in (pygame.K_w, pygame.K_UP):
            self.main_menu.select_prev()
        elif event.key in (pygame.K_s, pygame.K_DOWN):
            self.main_menu.select_next()
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            selection = self.main_menu.get_selection()
            if selection == "Begin":
                self.scene = "ship"
                self.hud.set_scene("The Ship")
                self.atmosphere.set_mood("still")
                self.hud.show_prompt(
                    "You wake. The ship hums. You do not remember.", 5.0,
                )
            elif selection == "Quit":
                self.running = False

    def _handle_pause_input(self, event: pygame.event.EventType) -> None:
        if event.key in (pygame.K_w, pygame.K_UP):
            self.pause_overlay.select_prev()
        elif event.key in (pygame.K_s, pygame.K_DOWN):
            self.pause_overlay.select_next()
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            sel = self.pause_overlay.get_selection()
            if sel == "Resume":
                self.paused = False
            elif sel == "Journal":
                self.paused = False
                self.previous_scene = self.scene
                self.scene = "journal"
            elif sel == "Quit to Menu":
                self.paused = False
                self.scene = "main_menu"

    def _handle_ship_input(self, event: pygame.event.EventType) -> None:
        if event.key in (pygame.K_e, pygame.K_RETURN):
            zone = self.ship.get_nearby_zone(self.player.x, self.player.y)
            if zone:
                if zone.action == "galaxy_map":
                    self.scene = "galaxy_map"
                    self.hud.set_scene("Galaxy Map")
                    self.atmosphere.set_mood("contemplative")
                elif zone.action == "journal":
                    self.previous_scene = "ship"
                    self.scene = "journal"
                elif zone.action == "viewport":
                    self.hud.show_prompt(
                        "Stars beyond counting. None of them yours.", 4.0,
                    )
                    # Give the vision fragment on first viewport use.
                    if not self.player.identity.get_fragment("ship_log_03"):
                        self.player.identity.add_fragment(SHIP_FRAGMENTS[2])
                        self.hud.show_prompt(
                            "A vision surfaces — unbidden, uncertain.", 4.0,
                        )
        elif event.key == pygame.K_j:
            self.previous_scene = "ship"
            self.scene = "journal"
        elif event.key == pygame.K_TAB:
            # Give the artifact fragment on TAB (examining the console).
            if not self.player.identity.get_fragment("ship_log_02"):
                self.player.identity.add_fragment(SHIP_FRAGMENTS[1])
                self.hud.show_prompt(
                    "Something scratched beneath the console...", 4.0,
                )

    def _handle_galaxy_input(self, event: pygame.event.EventType) -> None:
        if event.key in (pygame.K_a, pygame.K_LEFT):
            self.universe.select_prev()
        elif event.key in (pygame.K_d, pygame.K_RIGHT):
            self.universe.select_next()
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self._travel_to_planet(self.universe.selected_planet)

    def _handle_planet_input(self, event: pygame.event.EventType) -> None:
        if event.key in (pygame.K_e, pygame.K_RETURN):
            planet = self.universe.selected_planet
            feature = planet.get_nearby_feature(
                self.player.x, self.player.y, self.camera_x,
            )
            if feature and feature.interaction_id:
                if feature.kind == "encounter":
                    self._start_encounter(planet, feature.interaction_id)
                elif feature.kind == "structure":
                    frag = get_structure_fragment(feature.interaction_id)
                    if frag and not self.player.identity.get_fragment(frag.fragment_id):
                        self.player.identity.add_fragment(frag)
                        self.hud.show_prompt(
                            f"Fragment discovered: {frag.title}", 4.0,
                        )
                    else:
                        self.hud.show_prompt(
                            "An empty structure. Echoes of habitation.", 3.0,
                        )
        elif event.key == pygame.K_j:
            self.previous_scene = "planet"
            self.scene = "journal"

    def _handle_dialogue_input(self, event: pygame.event.EventType) -> None:
        renderer = self.dialogue_renderer

        if not renderer.text_complete:
            # Skip to end of text.
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                renderer.skip_to_end()
            return

        node = renderer.current_node
        if node is None:
            return

        if node.is_terminal:
            # End dialogue.
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._end_dialogue()
            return

        if event.key in (pygame.K_w, pygame.K_UP):
            renderer.select_prev_choice()
        elif event.key in (pygame.K_s, pygame.K_DOWN):
            renderer.select_next_choice()
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            choice = renderer.get_selected_choice()
            if choice:
                self._advance_dialogue(choice)

    def _handle_journal_input(self, event: pygame.event.EventType) -> None:
        if self.journal.viewing_detail:
            if event.key == pygame.K_ESCAPE:
                self.journal.viewing_detail = False
        else:
            if event.key in (pygame.K_a, pygame.K_LEFT):
                self.journal.prev_domain()
            elif event.key in (pygame.K_d, pygame.K_RIGHT):
                self.journal.next_domain()
            elif event.key in (pygame.K_w, pygame.K_UP):
                self.journal.select_prev()
            elif event.key in (pygame.K_s, pygame.K_DOWN):
                self.journal.select_next()
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.journal.toggle_detail()
            elif event.key == pygame.K_ESCAPE:
                self.scene = self.previous_scene

    # ─── Update ──────────────────────────────────────────────────────────

    def _update(self, dt: float) -> None:
        """Update game state for the current frame."""
        self.hud.update(dt)
        self.atmosphere.update(dt, self.player.identity.overall_coherence())

        if self.paused:
            return

        if self.scene == "ship":
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys)
            bounds = self.ship.player_bounds()
            self.player.clamp_to_bounds(*bounds)

        elif self.scene == "planet":
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys)
            # Horizontal scrolling on the planet surface.
            planet = self.universe.selected_planet
            self.player.clamp_to_bounds(
                50, planet.ground_y - 80,
                SCREEN_WIDTH - 50, planet.ground_y - 5,
            )
            # Camera follows player.
            self.camera_x += (self.player.x - SCREEN_WIDTH // 2 - self.camera_x) * 0.05
            self.camera_x = max(0, self.camera_x)

            # Check for nearby features.
            feature = planet.get_nearby_feature(
                self.player.x, self.player.y, self.camera_x,
            )
            if feature and feature.interactable:
                self.planet_prompt_text = "[ E ] Interact"
            else:
                self.planet_prompt_text = ""

        elif self.scene == "dialogue":
            self.dialogue_renderer.update(dt)

    # ─── Drawing ─────────────────────────────────────────────────────────

    def _draw(self, dt: float) -> None:
        """Render the current scene."""
        if self.scene == "main_menu":
            self.main_menu.draw(
                self.screen, dt,
                self.fonts["title"],
                self.fonts["body"],
                self.fonts["small"],
            )
            return

        if self.scene == "ship":
            self.ship.draw(self.screen, dt)
            self.player.draw(self.screen, dt)
            zone = self.ship.get_nearby_zone(self.player.x, self.player.y)
            self.ship.draw_zone_labels(
                self.screen, self.fonts["small"], zone,
            )
            self.atmosphere.draw(self.screen)
            self.hud.draw(self.screen, self.fonts["hud"], self.fonts["small"])

        elif self.scene == "galaxy_map":
            self.universe.draw_galaxy_map(
                self.screen, dt,
                self.fonts["body"],
                self.fonts["small"],
            )
            self.hud.draw(self.screen, self.fonts["hud"], self.fonts["small"])

        elif self.scene == "planet":
            planet = self.universe.selected_planet
            self.screen.fill(COLORS["void"])
            planet.draw_surface(self.screen, dt, self.camera_x)
            self.player.draw(self.screen, dt)
            self.atmosphere.draw(self.screen)

            if self.planet_prompt_text:
                prompt = self.fonts["small"].render(
                    self.planet_prompt_text, True, COLORS["amber"],
                )
                self.screen.blit(
                    prompt,
                    (SCREEN_WIDTH // 2 - prompt.get_width() // 2,
                     SCREEN_HEIGHT - 80),
                )

            self.hud.draw(self.screen, self.fonts["hud"], self.fonts["small"])

        elif self.scene == "dialogue":
            # Draw the underlying scene dimly.
            if self.previous_scene == "planet":
                planet = self.universe.selected_planet
                planet.draw_surface(self.screen, dt, self.camera_x)
            else:
                self.screen.fill(COLORS["void"])

            self.dialogue_renderer.draw(
                self.screen,
                self.fonts["body"],
                self.fonts["small"],
            )

        elif self.scene == "journal":
            self.journal.draw(
                self.screen, dt,
                self.fonts["heading"],
                self.fonts["body"],
                self.fonts["small"],
            )

        # Pause overlay (drawn on top of everything).
        if self.paused:
            self.pause_overlay.draw(
                self.screen, dt,
                self.fonts["body"],
                self.fonts["small"],
            )

    # ─── Scene Transitions ───────────────────────────────────────────────

    def _travel_to_planet(self, planet) -> None:
        """Transition from galaxy map to a planet surface."""
        self.scene = "planet"
        self.previous_scene = "planet"
        planet.visited = True
        self.player.visited_planets.add(planet.planet_id)
        self.player.current_planet = planet.planet_id

        # Position player on the ground.
        self.player.x = SCREEN_WIDTH // 2
        self.player.y = planet.ground_y - 20
        self.camera_x = 0.0

        self.hud.set_scene(planet.name)
        self.atmosphere.set_mood("alien")
        self.hud.show_prompt(f"Arrived at {planet.name}. {planet.atmosphere}.", 5.0)

    def _start_encounter(self, planet, interaction_id: str) -> None:
        """Begin an NPC encounter."""
        # Create encounter if it doesn't exist.
        if interaction_id not in self.encounters_created:
            encounter = create_first_encounter(planet.planet_id)
            self.encounters_created[interaction_id] = encounter

        encounter = self.encounters_created[interaction_id]

        if encounter.completed:
            self.hud.show_prompt(
                "The being is silent now. Its light turned inward.", 3.0,
            )
            return

        self.active_encounter = encounter
        self.previous_scene = "planet"
        self.scene = "dialogue"

        # Start the dialogue.
        start = encounter.dialogue_tree.get_node(
            encounter.dialogue_tree.start_node,
        )
        if start:
            self.dialogue_renderer.set_node(start)

    def _advance_dialogue(self, choice) -> None:
        """Move to the next dialogue node after a player choice."""
        if not self.active_encounter:
            return

        # Grant fragment if this choice yields one.
        if choice.fragment_id:
            for frag in self.active_encounter.fragments:
                if frag.fragment_id == choice.fragment_id:
                    if not self.player.identity.get_fragment(frag.fragment_id):
                        self.player.identity.add_fragment(frag)
                    break

        # Move to next node.
        next_node = self.active_encounter.dialogue_tree.get_node(
            choice.next_node,
        )
        if next_node:
            self.dialogue_renderer.set_node(next_node)

    def _end_dialogue(self) -> None:
        """End the current dialogue and return to the previous scene."""
        if self.active_encounter:
            self.active_encounter.completed = True
        self.active_encounter = None
        self.scene = self.previous_scene
        self.atmosphere.set_mood("contemplative")


def main():
    """Entry point."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
