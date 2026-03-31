"""
config.py — Constants, settings, and aesthetic parameters for the game.

This file is the single source of truth for all tunable values.
Nothing here should contain logic — only data that shapes the world.
"""

# ─── Window ──────────────────────────────────────────────────────────────────

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "The Unnamed Vessel"

# ─── Color Palette ───────────────────────────────────────────────────────────
# Deep space blues, amber warmth, bioluminescent accents.

COLORS = {
    # Backgrounds
    "void":              (4,   6,  15),
    "deep_space":        (8,  12,  28),
    "ship_interior":     (14, 18,  32),
    "ship_floor":        (22, 26,  42),
    "ship_wall":         (18, 22,  38),

    # Accent & UI
    "amber":             (218, 165, 50),
    "amber_dim":         (140, 105, 30),
    "amber_glow":        (255, 200, 80),
    "soft_white":        (200, 195, 185),
    "pale_blue":         (130, 160, 200),
    "ghost_white":       (170, 175, 180),

    # Bioluminescence
    "bio_cyan":          (40,  200, 210),
    "bio_green":         (50,  210, 120),
    "bio_violet":        (140, 80,  220),

    # Planet palette bases (hue-shifted per planet)
    "planet_warm":       (180, 90,  45),
    "planet_cold":       (45,  80,  160),
    "planet_toxic":      (90,  180, 60),

    # Narrative
    "memory_tint":       (180, 160, 130),
    "testimony_tint":    (130, 150, 180),
    "artifact_tint":     (180, 130, 160),
    "vision_tint":       (160, 180, 130),

    # UI
    "ui_bg":             (10,  14,  26),
    "ui_border":         (50,  55,  70),
    "ui_highlight":      (218, 165, 50),
    "ui_text":           (190, 185, 175),
    "ui_text_dim":       (100, 100, 110),
    "ui_text_bright":    (240, 235, 220),

    # Functional
    "black":             (0,   0,   0),
    "white":             (255, 255, 255),
    "transparent_black": (0,   0,   0,  180),
}

# ─── Typography ──────────────────────────────────────────────────────────────

FONT_SIZES = {
    "title":     48,
    "heading":   32,
    "body":      20,
    "small":     16,
    "tiny":      13,
    "journal":   18,
    "dialogue":  20,
    "hud":       16,
}

# We use Pygame's default font (freesansbold) as a fallback.
# Replace with a custom .ttf for the melancholic aesthetic.
FONT_PATH = None  # Set to e.g. "assets/fonts/SpaceMono-Regular.ttf"

# ─── Ship ────────────────────────────────────────────────────────────────────

SHIP_ROOM_WIDTH = 800
SHIP_ROOM_HEIGHT = 500
PLAYER_SPEED = 3
PLAYER_RADIUS = 12

# ─── Galaxy ──────────────────────────────────────────────────────────────────

UNIVERSE_SEED = 42
NUM_PLANETS = 3
GALAXY_MAP_MARGIN = 100

# ─── Identity ────────────────────────────────────────────────────────────────

FRAGMENT_TYPES = ("memory", "testimony", "artifact", "vision")

# Certainty thresholds for display
CERTAINTY_LABELS = {
    (0.0, 0.2): "barely a whisper",
    (0.2, 0.4): "a faint impression",
    (0.4, 0.6): "uncertain but present",
    (0.6, 0.8): "vivid, almost real",
    (0.8, 1.0): "undeniable — or so it seems",
}

# ─── Narrative ───────────────────────────────────────────────────────────────

DIALOGUE_SPEED = 30  # milliseconds per character for typewriter effect
JOURNAL_MAX_DISPLAY = 12  # fragments shown per journal page

# ─── Atmosphere ──────────────────────────────────────────────────────────────

STAR_COUNT = 200
STAR_PARALLAX_LAYERS = 3
NEBULA_ALPHA = 40

# ─── Scenes ──────────────────────────────────────────────────────────────────

SCENES = {
    "ship":       "ship_interior",
    "galaxy_map": "galaxy_map",
    "planet":     "planet_surface",
    "dialogue":   "dialogue",
    "journal":    "journal",
    "main_menu":  "main_menu",
}

# ─── Progression ─────────────────────────────────────────────────────────────

# Knowledge domains — not XP, but axes of understanding.
KNOWLEDGE_DOMAINS = (
    "self",        # Who you are
    "origin",      # Where you came from
    "purpose",     # Why you are here
    "connection",  # Your relationship to others
)
