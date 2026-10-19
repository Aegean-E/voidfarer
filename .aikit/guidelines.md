# Project Guidelines

Rules for this project only, written by people or AI agents. They add to AIKit's principles and
rank below them: a guideline never overrides a principle (PRINCIPLE-000 R6, PRINCIPLE-001 R4).
Add one with `python aikit.py guideline <name> "<rule>" --source <user|ADR-NNN|person>`, or by
hand as one line below in the form `- **G-NNN** (source): rule`; IDs are never reused.

## Rules
- **G-001** (user): Cockpit layout rule 1: the TELEMETRY / Tactical Flight Log panel is anchored at the lower-right corner and carries a HIDE/SHOW button.
- **G-002** (user): Cockpit layout rule 2: the Chrono tick and time settings deck is pinned to the upper-right corner, at the far right of the top status bar.
- **G-003** (user): Cockpit layout rule 3: the Commerce/Arsenal/Fleet terminal runs vertically (up to down) on the left side: a vertical tab rail with the active tab's content beside it.
- **G-004** (user): Cockpit layout rule 4: the NAV-Radar orbital map is the full-viewport background layer, with all HUD decks and panels rendered on top of it.
- **G-005** (user): Cockpit layout rule 5: HUD overlays must remain sleek and unbulky over the background radar: NAV-RADAR orbital title is a transparent on-map label, the left terminal rail expands content to the right on demand (collapsible drawer), and the lower-right tactical flight log sits directly on the map without a containing box.
- **G-006** (user): Cockpit layout rule 6: the reactor power routing panel is expandable with a HIDE/SHOW button like the flight log, the top-bar actions line sits to the left of the vitals row, and all vital stat cards share equal dimensions.
- **G-007** (user): Cockpit layout & navigation rule 7: Enter orbit and sublight transit adhere to the exact same 2D polar Euclidean distance calculation, and top-bar vital stat cards match the height of the chrono date box on a single non-wrapping line.
