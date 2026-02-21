# CLAUDE.md

This file provides guidance for AI assistants working with this repository.

## Repository Overview

This is a **mixed-content educational and creative repository** with two distinct areas:

1. **Philosophy education materials** (`philosophie/`) — German-language Abitur exam documents for Q1 (upper secondary, NRW curriculum)
2. **Creative HTML demo** (`rainbow-chess-piece.html`) — A self-contained animated chess piece visualization

There is no software application, build system, package manager, test suite, or CI/CD pipeline.

---

## Repository Structure

```
Test/
├── CLAUDE.md                          # This file
├── .gitkeep                           # Empty placeholder
├── rainbow-chess-piece.html           # Standalone HTML/CSS/JS animation
└── philosophie/
    └── Q1/                            # Abitur Quarter 1 exam package
        ├── bewertungsraster/          # Grading rubrics (Darstellungsleistung)
        │   └── Philo_Q1_Raster_Darstellungsleistung_2026-02_v01.md
        ├── erwartungshorizonte/       # Expected answers / marking guide
        │   └── Philo_Q1_EH_Sartre_Freiheit_2026-02_v01.md
        └── klausuren/                 # Exam papers
            └── Philo_Q1_Klausur_Sartre_Freiheit_2026-02_v01.md
```

---

## File Naming Convention

Philosophy documents follow a consistent naming scheme:

```
Philo_<Level>_<Type>_<Topic>_<YYYY-MM>_<version>.md
```

| Segment | Example | Meaning |
|---------|---------|---------|
| `Philo` | `Philo` | Subject: Philosophy |
| `<Level>` | `Q1` | Qualification year (Q1 = Year 12, first half) |
| `<Type>` | `Klausur`, `EH`, `Raster` | Document type (see below) |
| `<Topic>` | `Sartre_Freiheit` | Topic slug |
| `<YYYY-MM>` | `2026-02` | Year and month of exam |
| `<version>` | `v01` | Version number |

**Document types:**
- `Klausur` — Exam paper (student-facing)
- `EH` — Erwartungshorizont (expected answer / marking guide, teacher-only)
- `Raster` — Bewertungsraster (grading rubric grid)

RTF versions of each Markdown file exist alongside them for Word compatibility (same base name, `.rtf` extension).

---

## Content Description

### Philosophy Exam Package (Q1 — Sartre, February 2026)

**Curriculum context:** NRW Abitur, Philosophie, Q1
**Topic:** Jean-Paul Sartre — Freiheit und Verantwortung (Freedom and Responsibility / Existentialism)
**Exam duration:** 90 minutes
**Exam type:** Materialgestützte Klausur (material-based exam)

#### Exam Paper (`klausuren/`)

Contains a Sartre-derived source text followed by three tasks:

| Task | Points | Operators | Focus |
|------|--------|-----------|-------|
| I | 40 | analysieren, erklären | Analyse the text's argument; explain the relationship between freedom and responsibility |
| II | 35 | erörtern, anwenden | Discuss Sartre's concept of freedom in contemporary moral contexts; apply to one concrete example |
| III | 25 | Stellung nehmen, beurteilen | Respond to a counter-position (social determinism); compare with Sartre; give a reasoned judgment |

#### Marking Guide (`erwartungshorizonte/`)

Teacher-only document. Contains:
- Expected content points per task
- Point distribution breakdowns
- Typical student errors
- Model answer excerpts
- Guidance on awarding Darstellungsleistung (presentation quality) points (0–15)

#### Grading Rubric (`bewertungsraster/`)

Four-level rubric (sehr gut → ungenügend) across four criteria:
1. **Sprache** — Precision of philosophical terminology
2. **Struktur** — Clarity of introduction, body, conclusion
3. **Argumentationsgang** — Logical coherence and treatment of counter-arguments
4. **Textbezug** — Correct, targeted, and functionally integrated evidence from the source material

### Rainbow Chess Piece (`rainbow-chess-piece.html`)

A self-contained, dependency-free HTML5 animation (German title: *Regenbogen-Schachfigur*).

**Techniques used:**
- CSS `@keyframes` animations: `spin`, `rainbow-shift`, `glow-pulse`, `ring-rotate`, `shadow-pulse`, `float-up`
- CSS `conic-gradient` for rotating color rings
- `-webkit-background-clip: text` for gradient-colored Unicode chess king glyph (♚, `&#9812;`)
- CSS 3D perspective (`rotateY`) for spin effect
- 10 floating particle `<div>` elements with staggered `animation-delay`
- No JavaScript, no external dependencies

---

## Conventions for Editing

### Philosophy documents

- **Language:** German throughout. Maintain formal academic register (*Bildungssprache*).
- **Terminology:** Use established philosophical terms precisely (e.g., *Geworfenheit*, *Entwurf*, *Faktizität*, *mauvaise foi*).
- **NRW operator vocabulary:** Tasks must use official NRW Abitur operators (analysieren, erörtern, Stellung nehmen, etc.). Do not substitute synonyms.
- **Point totals:** Task I + II + III must always sum to 100. Darstellungsleistung is awarded separately (0–15 points) and is not part of the 100.
- **Version bumping:** When creating a revised document, increment the version suffix (`v01` → `v02`) and update the date segment (`YYYY-MM`) accordingly.
- **Dual format:** Each Markdown file has an RTF counterpart. When updating content, both formats should remain in sync.
- **Confidentiality:** `EH` (Erwartungshorizont) files are teacher/examiner materials. Do not include their content in student-facing documents.

### HTML file

- The file is intentionally self-contained with no external dependencies. Keep it that way.
- All styles are in a single `<style>` block; all logic is CSS-only.
- The document `lang` attribute is `de` (German); keep titles/labels in German.

---

## Git Workflow

- **Default branch:** `main` (remote), `master` (local alias)
- **Feature branches:** Use the `claude/<description>-<id>` naming pattern (e.g., `claude/add-claude-documentation-o9lR1`)
- No automated CI/CD runs on push — changes are manually reviewed
- Commit messages should be in **English** or **German** (both are used in existing history); be descriptive

**Commit history context:**
```
a7f9b8e  Merge pull request #2: rainbow-chess-piece animation merge
5b07081  Add spinning rainbow chess piece animation
159690f  Merge pull request #1: Philosophy Q1 exam package merge
19d34c8  Erzeuge Word-kompatible RTF-Versionen fuer das Klausurpaket
d73a352  Initialize repository
```

---

## What This Repository Is Not

- Not a software application — there is no code to build, compile, or run (beyond opening the HTML file in a browser)
- Not tested with automated tests — no test framework, no test files
- Not linted — no ESLint, Prettier, or similar tooling
- Not a package — no `package.json`, `pyproject.toml`, or equivalent

When asked to "run tests", "build the project", or "install dependencies", clarify that none of these apply to this repository.
