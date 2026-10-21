# Project Guidelines

Rules for this project only, written by people or AI agents. They add to AIKit's principles and
rank below them: a guideline never overrides a principle (PRINCIPLE-000 R6, PRINCIPLE-001 R4).
Add one with `python aikit.py guideline <name> "<rule>" --source <user|ADR-NNN|person>`, or by
hand as one line below in the form `- **G-NNN** (source): rule`; IDs are never reused.

## Rules
- **G-001** (user): Cockpit layout rule 1: the TELEMETRY / Tactical Flight Log panel is anchored on the right of the bottom command strip (G-013) and carries a HIDE/SHOW button.
- **G-002** (user): Cockpit layout rule 2: the Chrono tick and time settings deck is pinned to the upper-right corner, at the far right of the top status bar.
- **G-003** (user): Cockpit layout rule 3: the Commerce/Arsenal/Fleet terminal runs vertically (up to down) on the left side: a vertical tab rail with the active tab's content beside it.
- **G-004** (user): Cockpit layout rule 4: the NAV-Radar orbital map is the full-viewport background layer, with all HUD decks and panels rendered on top of it.
- **G-005** (user): Cockpit layout rule 5: HUD overlays must remain sleek and unbulky over the background radar: NAV-RADAR orbital title is a transparent on-map label, the left terminal rail expands content to the right on demand (collapsible drawer), and the bottom command strip stays compact between the left terminal and the right corner.
- **G-006** (user): Cockpit layout rule 6: the reactor power routing panel is expandable with a HIDE/SHOW button like the flight log, the top-bar actions line sits to the left of the vitals row, and all vital stat cards share equal dimensions.
- **G-007** (user): Cockpit layout & navigation rule 7: Enter orbit and sublight transit adhere to the exact same 2D polar Euclidean distance calculation, and top-bar vital stat cards match the height of the chrono date box on a single non-wrapping line.
- **G-008** (user): Cockpit layout rule 8: the SHIP MODS section lives in the left vertical terminal as a first-class tab and follows the same drawer behavior as COMMERCE, ARSENAL, and FLEET.
- **G-009** (user): Cockpit layout rule 9: vital stat cards are compact 44px equal-height boxes, and orbital rings fade to the black void at the sensor-range edge.
- **G-010** (user): Setting rule 10: the campaign starts on 01.01.3042 in the Quantum Age (31st Century); messaging must remain branch-resolvable and every branch outcome persistent.
- **G-011** (user): Cockpit UI must adapt to the viewport: ultrawide, desktop, tablet, phone, short-height, reduced-motion, safe-area, DPR-correct radar, and touch pan/pinch; density and HUD scale are user-selectable with an automatic resolution-aware default.
- **G-012** (user): New exploration mechanics must stay deterministic per save seed, stdlib-only, exposed through CLI/REST/cockpit parity, and every permanent change must be serialized with a backward-compatible default.
- **G-013** (user): Cockpit layout rule 13: the bottom command strip spans from the left panel to the right corner in three equal columns: reactor distribution left, skills middle, and a right column with a separate radar settings panel above the tactical flight log; radar zoom controls stack vertically as circular +, center, and − icon buttons; every panel has an icon and a hotkey, reactor channels use Q/W/E/R, skills use SHIFT+1..6, and panel toggles use P/K/L; the flight log keeps a compact height; the PLAYER tab must not duplicate the skills summary; the cockpit uses themed SVG cursors, and this layout is documented in the guide.
