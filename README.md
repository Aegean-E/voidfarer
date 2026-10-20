# VoidFarer

> **Autonomous Deep-Space Fleet, Procedural Galaxy & Holographic Cockpit Simulator.**

VoidFarer is a zero-dependency, local-first space flight, fleet management, and exploration simulation engine. Navigate procedural star systems, establish orbits around exotic planets, route reactor power, commission autonomous mining and escort drones, purchase modular hardware upgrades, engage in tactical combat with adaptive hostile AI, trade dynamic commodities across orbital stations, and pilot your flagship using either an ANSI terminal REPL or an HTML5 Canvas holographic cockpit Web HUD.

---

## ⚡ 30-Second Cold-Start Quick Reference

### 🎮 1-Click Instant Game Launch (Windows)
Double-click or run either batch launcher directly from Windows Explorer or Terminal:
```cmd
play.bat        # Interactive Mission Launcher (defaults to Holographic Web Cockpit & auto-opens browser)
voidfarer.bat   # CLI passthrough launcher (e.g. `voidfarer.bat status`, `voidfarer.bat repl`)
```

- **Runtime Prerequisites**: Python 3.10+ (Standard Library only; zero third-party packages required).
- **Canonical Regression Shield Gate**:
  ```bash
  python aikit.py check voidfarer
  ```

### 🛠️ AIKit Commands (run from the AIKit folder)
| Role | Command |
|---|---|
| Status, task and gates | `python aikit.py status voidfarer` |
| Phase 4: every gate | `python aikit.py check voidfarer` |
| Repair memory and map, then check | `python aikit.py fix voidfarer` |
| Resume an interrupted task | `python aikit.py resume voidfarer` |

---

## 📦 What's Inside

```text
voidfarer/
├── .aikit/                   <- project memory: record, ledger, decisions
│   ├── codebase_map.md       <- AST-generated symbol map
│   ├── decisions.md          <- monotonic ADR register
│   ├── guidelines.md         <- project-specific guidelines
│   ├── project.json          <- stack and gate configuration
│   └── task_ledger.json      <- power-loss safe task state
├── docs/                     <- comprehensive system design & research
│   ├── ATTENTION_MECHANICS_LITERATURE_REVIEW.md <- behavioral psychology review
│   └── NARRATIVE_AND_TUTORIAL_LITERATURE_REVIEW.md <- cognitive load & narrative review
├── .gitignore                <- transient state & python caches excluded
├── LICENSE                   <- GNU AGPL-3.0 license
├── pyproject.toml            <- build and package configuration
├── play.bat                  <- 1-click interactive Windows launcher (default: Web Cockpit)
├── voidfarer.bat             <- 1-click Windows CLI passthrough launcher
├── README.md                 <- living documentation
├── voidfarer/                <- core simulation package
│   ├── __init__.py           <- package metadata
│   ├── models.py             <- frozen dataclass DTOs and schema validators
│   ├── factions.py           <- sovereign factions, megacorps & standing tiers
│   ├── enemies.py            <- tactical enemy archetypes, abilities & generator
│   ├── galaxy.py             <- procedural star system & hyperlane generator
│   ├── engine.py             <- deterministic state machine & coordinator
│   ├── retention.py          <- relics, dynamic contracts & pilot mastery
│   ├── story.py              <- cadet academy & precursor cipher campaign
│   ├── upgrades.py           <- hardware upgrades catalog & drone templates
│   ├── economy.py            <- dynamic galactic economy, stockpiles & trade routes
│   ├── frontier.py           <- AI captains, depots, mercenaries & quantum messages
│   ├── inventory.py          <- item catalog, consumables & cargo manifest
│   ├── storage.py            <- crash-safe atomic persistence & shadow backup
│   ├── server.py             <- zero-dependency HTTP REST & cockpit server
│   ├── cli.py                <- ANSI terminal interface & interactive REPL
│   └── static/               <- holographic web cockpit UI
│       ├── index.html        <- semantic HUD structure & radar canvas
│       ├── style.css         <- sci-fi glassmorphism design system
│       └── app.js            <- radar math, Web Audio synth & REST link
└── tests/                    <- unit & integration test suite
    ├── __init__.py
    ├── test_models.py        <- model immutability & serialization tests
    ├── test_galaxy.py        <- procedural generator & market tests
    ├── test_economy.py       <- galactic market simulation & trade route tests
    ├── test_engine.py        <- state transitions, fleet & combat mechanics
    ├── test_engine_hardening.py <- audit regressions: service guards, relic stats & cargo invariants
    ├── test_ai_and_calendar.py <- adaptive enemy AI, expanded systems & DD.MM.YYYY calendar
    ├── test_frontier_systems.py <- AI trade, depots, messages, landing, fleets & moons
    ├── test_inventory.py     <- item catalog, manifest & consumable tests
    ├── test_factions_and_enemies.py <- faction geopolitics & tactical combat tests
    ├── test_perks_relics_rep.py <- faction service perks, multi-stat relics & reputation rewards
    ├── test_storage.py       <- power-loss safety & corruption quarantine
    ├── test_server.py        <- REST API request/response contracts
    ├── test_cli.py           <- command dispatch & argument parsing
    ├── test_story.py         <- academy onboarding & story campaign tests
    ├── test_batch_launchers.py <- Windows batch launcher menu & CRLF regression tests
    ├── test_cockpit_layout.py <- cockpit layout-rule DOM/CSS regression tests
    ├── test_equipment_bonuses.py <- module stat_bonus & chassis perk regression tests
    ├── test_time_and_ticks.py <- cosmic calendar, tick simulation & time controls
    └── test_transit_civ_events.py <- in-system transit, planetary civilization & cockpit popup events
```

---

## 🚀 Quick Start & CLI Usage

VoidFarer requires only Python 3.10+ and standard library modules.

### 1. Flagship Telemetry Status
```bash
python -m voidfarer.cli status
```
Displays commander dossier, vital telemetry (hull, shields, fuel), reactor power distribution, installed modules, fleet drone count, current system coordinates, and proximity hazard alerts.

### 2. Galaxy Starmap & Celestial Radar
```bash
python -m voidfarer.cli chart
```
Prints the sector hyperlane network, visited system flags, security ratings, and all celestial bodies in the local star system. Each system now hosts 5-6 planets, moons, ice worlds, lava worlds, ringed giants, and research outposts, with a guaranteed dockable station.

### 3. Navigation & Spaceflight
```bash
# Enter orbit around a planet or space station
python -m voidfarer.cli orbit sol_body_1

# Initiate timed sublight or quantum in-system transit
python -m voidfarer.cli travel sol_body_2 --mode sublight
python -m voidfarer.cli travel sol_body_4 --mode quantum

# Inspect or dismiss cockpit popup events
python -m voidfarer.cli events list
python -m voidfarer.cli events dismiss evt_2_1

# Perform sensor sweep of orbiting body (earns research bounty)
python -m voidfarer.cli scan

# Hyperspace jump to an adjacent star system
python -m voidfarer.cli jump alpha_centauri
```

### 4. Hardware Upgrades & Station Arsenal
```bash
# Inspect available hardware modules and equipped status
python -m voidfarer.cli upgrades

# Purchase and equip an upgrade module
python -m voidfarer.cli upgrades buy warp_booster_mk2
python -m voidfarer.cli upgrades buy subspace_cargo_pods
```

### 5. Autonomous Fleet & Drones
```bash
# List active fleet drones and accumulated harvest yield
python -m voidfarer.cli fleet

# Commission a new drone (mining, scout, or combat_escort)
python -m voidfarer.cli fleet buy mining sol

# Redeploy a drone to another system
python -m voidfarer.cli fleet deploy drone_mining_1 alpha_centauri

# Harvest accumulated resources and credits from fleet
python -m voidfarer.cli fleet harvest
```

### 6. Tactical Combat Maneuvers
When intercepted by hostile corsairs, syndicate marauders, or faction enforcers in low-security space:
```bash
# Tactical maneuvers
python -m voidfarer.cli combat fire             # Laser battery barrage (depletes deflector shields, overflows to hull)
python -m voidfarer.cli combat drone            # Kinetic drone torpedo strike (armor-piercing; bypasses deflector shields)
python -m voidfarer.cli combat target weapons   # Precision strike to disable enemy offensive arrays
python -m voidfarer.cli combat target shields   # Precision strike to destabilize shield harmonic generators
python -m voidfarer.cli combat absorb           # Overcharge deflector shield capacitors
python -m voidfarer.cli combat evade            # High-G thruster burn to dodge telegraphed attacks
python -m voidfarer.cli combat flee             # Emergency hyperspace micro-jump
```

Hostile captains use adaptive AI profiles (`aggressive`, `defensive`, `opportunist`, `adaptive`, `warlord`). They read your hull, shields, and tactical combo to brace, evade, execute wounded targets, drain shields, EMP weapon systems, tachyon-lance hull, or regenerate nanites. The combat telemetry line shows the next predicted maneuver.

### 7. Dynamic Sector Bounties & Contracts (Zeigarnik Loop)
```bash
# View active contracts, progress bars, and rewards
python -m voidfarer.cli contracts

# Claim completed contract reward and draw replacement assignment
python -m voidfarer.cli contracts claim contract_explore_alpha_centauri
```

### 8. Pilot Mastery & Specializations (Self-Determination)
```bash
# Display Pilot rank, XP progress, and available talent perks
python -m voidfarer.cli mastery

# Unlock specialization perk using earned Talent Points
python -m voidfarer.cli mastery unlock void_cartographer
python -m voidfarer.cli mastery unlock dreadnought_tactics
```

### 9. Ancient Precursor Relics Vault (Variable-Ratio)
```bash
# Inspect recovered alien artifacts and active passive fleet modifiers
python -m voidfarer.cli relics
```

### 10. Expedition Jump Streaks (Loss Aversion)
```bash
# Check current jump streak and cumulative multiplier (+15% up to x2.50)
python -m voidfarer.cli streak
```

### 11. Commodity Commerce & Drydock Services
```bash
# Inspect local exchange prices
python -m voidfarer.cli market

# Purchase and sell commodities
python -m voidfarer.cli buy fuel_cells 5
python -m voidfarer.cli sell titanium 3

# Repair hull damage and refuel
python -m voidfarer.cli repair --amount 25
python -m voidfarer.cli refuel --amount 20

# Inspect the living galactic economy: stockpiles, market shocks, and best trade routes
python -m voidfarer.cli economy

# Inspect the cargo manifest, buy station consumables, and use them in space
python -m voidfarer.cli inventory
python -m voidfarer.cli inventory buy nanite_repair_paste 2
python -m voidfarer.cli inventory use nanite_repair_paste
```

### 12. Cadet Flight Academy (Situated Scaffolding)
```bash
# Check current tutorial milestone and curriculum progress
python -m voidfarer.cli tutorial

# Skip tutorial prompts or reset onboarding curriculum
python -m voidfarer.cli tutorial skip
python -m voidfarer.cli tutorial reset
```

### 13. The Precursor Cipher Narrative Campaign (Space Opera)
```bash
# Display active chapter synopsis, transmissions log, and moral choices
python -m voidfarer.cli story

# Resolve an episodic narrative dilemma
python -m voidfarer.cli story choose choice_vance_telemetry
```

### 14. Geopolitical Factions & Megacorporations
```bash
# View all sovereign galactic factions, ideologies, territorial HQs, and standing
python -m voidfarer.cli factions

# View galactic megacorporations, commercial specialties, and trade perks
python -m voidfarer.cli corporations
```

### 15. Cosmic Calendar & Temporal Clock Controls
```bash
# Check the in-game calendar date, stardate, and active simulation tick
python -m voidfarer.cli time status

# Pause or resume the cosmic simulation clock
python -m voidfarer.cli time pause
python -m voidfarer.cli time resume

# Adjust simulation speed multiplier (1x normal, 2x fast, 5x sub-warp, 10x hyper-warp)
python -m voidfarer.cli time speed 5

# Advance cosmic simulation by a discrete number of ticks (+1, +4, +10)
python -m voidfarer.cli time step 4
```

### 16. Interactive Terminal Cockpit REPL
```bash
python -m voidfarer.cli repl
```
Inside the interactive REPL, you can execute all commands (`status`, `chart`, `time`, `factions`, `corporations`, `contracts`, `mastery`, `relics`, `streak`, `market`, `economy`, `inventory`, `shipyard`, `jump`, `fleet`, `upgrades`, `combat`, `scan`, `power`, `tutorial`, `story`, etc.), or type **`serve`** to launch the concurrent background Web HUD!

Frontier commands are also available directly:
```bash
python -m voidfarer.cli quests
python -m voidfarer.cli ai list
python -m voidfarer.cli ai hail captain_vega
python -m voidfarer.cli messages list
python -m voidfarer.cli messages send "Captain Vega" "Trade lane" "Meeting at Sol."
python -m voidfarer.cli depot status
python -m voidfarer.cli depot deposit titanium 2
python -m voidfarer.cli depot sell titanium 1
python -m voidfarer.cli land sol_body_2
python -m voidfarer.cli mercs list
python -m voidfarer.cli mercs hire merc_ironclad
python -m voidfarer.cli allies list
python -m voidfarer.cli allies form captain_sable
python -m voidfarer.cli saves list
python -m voidfarer.cli saves save slot_1
python -m voidfarer.cli saves load slot_1
```

### 17. Holographic Web Cockpit Interface
Launch the embedded zero-dependency Web Audio & Canvas cockpit:
```bash
python -m voidfarer.cli serve --port 8080
```
Open **`http://127.0.0.1:8080`** in any modern web browser to access:
- **Single-Line Top Status Bar & Cosmic Chronometer (`G-007`)**: Unwrapped single-line HUD topbar featuring equal-height 52px vital cards (Hull, Shields, Fuel, Credits, Fleet) and the Cosmic Chronometer time deck (date `DD.MM.YYYY`, tick badge, 1-click Pause/Resume, 1x-10x speed, step advance).
- **Main Menu (`ESC`) & Multi-Slot Save Management**: Toggle the Main Menu or close active modal windows anytime with `ESC`, and create, inspect, load, or delete multiple named save slots (`default`, `slot_1`..`slot_3`, or custom slot names) alongside Settings.
- **Sleek Decluttered Background Radar HUD (`G-004`, `G-005`)**: Full-screen black-background orbital/galaxy canvas (`100vw x 100vh`) serving as the unobstructed live backdrop with a floating semi-transparent watermark title, an on-demand right-expanding collapsible terminal drawer on the left (`COMMERCE`, `ARSENAL`, `FLEET`, etc.), and a boxless Tactical Flight Log rendered directly over space in the lower-right corner.
- **Quest, AI, Depot & Quantum Message Panels**: Unified mission control, AI captain diplomacy/trade/hire/ally actions, per-system cargo depots with direct selling, and an intergalactic quantum inbox/composer.
- **Pilot Perks Window**: The former Mastery page is now an open/close in-game window with four branching perk trees (Exploration, Combat, Fleet, Trade) and tier-2 prerequisites.
- **Planet & System Inspector & Dynamic Population (`G-007`)**: Scientifically accurate surface gravity ($g = (R/R_\oplus)(\rho/\rho_\oplus)$), chemical atmosphere (`atm`), equilibrium temperature, Earth Similarity habitability index (`%`), 2D Euclidean orbital distance parity across orbit capture and transit (`AU`), moons, resources, faction, government, and dynamic demographic population growth with colony tiers (`Outpost` to `Mega-Ecumenopolis`).
- **Tick-Synchronized Transit & Surface Landing**: Initiate sublight or quantum transit with 2D Euclidean distance and engine-scaled tick durations while the flagship animates continuously across the radar until orbital capture, or land on habitable worlds for survey rewards.
- **Mercenary & Fleet Command**: Per-unit level, efficiency, integrity, sorties, refit/dismiss controls, and hireable mercenary specialists (assault, evasion, repair).
- **Expanded Procedural Galaxy**: 15 star systems, 5-6 planets each, additional star types (B/O/red giant/binary), savanna/tundra/toxic/barren/super-Earth/ice-giant worlds, moons, and asteroid belts.
- **Dynamic AI Economy**: Autonomous trader captains move between systems and buy/sell commodities each tick, changing stockpiles and prices alongside the player's trades.
- **Concrete Faction Perks & Reputation Rewards**: Friendly repair discounts, allied free refuel and naval escort evasion, Syndicate sale margins, Precursor scan XP, and Nebula drone yields are applied in the simulation; enemy archetypes now use their catalog `rep_rewards` for faction and corporate standings.
- **Multi-Stat Relics & Hardened Cockpit Rendering**: Relics support secondary bonus maps (hull + shields, fuel + lasers, laser + research) and all dynamic cockpit text/colors are escaped or whitelisted before interpolation.
- **REPL Web Server Lifecycle**: `serve` starts a concurrent HTTP server plus simulation ticker, reports the actual bound port, and `serve stop` or REPL exit shuts it down with a final save.
- **Cadet Flight Academy Ribbon**: Persistent top-of-HUD progressive instruction banner with milestone progress, step hints, rewards, and one-click dismiss.
- **COMMS LOG Subspace Radio Tab**: Subspace transmissions stream with animated character avatars (Admiral Vance, Cipher, Archon Prime), faction alignment chips, and interactive moral choice cards.
- **Factions & Megacorporations Tab**: Live diplomatic standings (-100 to +100), territorial headquarters, tariff discounts, and corporate specialty trade margins.
- **Interactive Orbit Radar**: Real-time animated orbiting planets, solar corona flare effects, clickable orbital bodies, drag-to-pan, and wheel zoom, synchronized with simulated tick angular progression.
- **Galaxy Sector Chart**: Hyperlane corridor network visualization and jump routing.
- **Contracts & Bounties Tab**: Active operational task cards with live progress bars, Zeigarnik task renewal, and reward claim buttons.
- **Expedition Streak Multiplier**: Real-time loss aversion flame badge scaling all trade and scan yields.
- **Station Arsenal Tab**: Modular hardware upgrades shop with real-time stat bonuses.
- **Fleet Command Tab**: Roster of autonomous mining/scout drones with live harvest buttons.
- **Tactical Combat Overlay**: Battle HUD with dual-layer deflector shield and hull meters, telegraphed enemy action warning banners, armor-piercing kinetic drone strikes, and subsystem targeting.
- **Synthesized Web Audio**: Procedural sound effects for radar sweeps, warp jumps, laser fire, level-up arpeggios, bounty chimes, radio dispatches, and alarms.
- **Reactor Power Matrix (`G-006`)**: Dynamic power allocation sliders with instant subsystem re-routing and an expandable HIDE/SHOW toggle.

---

## 🛡️ Architecture & Resilience Guarantees

1. **Zero External Dependencies**: Built entirely on standard Python modules (`math`, `random`, `dataclasses`, `http.server`, `json`, `pathlib`).
2. **Power-Loss Recovery (PRINCIPLE-013)**: State saves use atomic replacement with file descriptor `fsync`, shadow `.bak` backups, and automatic quarantine of corrupt payloads.
3. **Fast Test Verification**: Comprehensive 259-test suite runs in about 4 seconds (`python -m unittest discover`).
4. **Platform Parity**: Full native support for Windows, Linux, and macOS with automatic console encoding detection.
5. **Effective Hardware & Chassis Bonuses**: Every advertised module effect (fuel savings, scan yields, combat damage, evasion, shield regeneration, ECM) and every chassis perk (trade margin, scan yield, combat damage) is aggregated and applied in the simulation.

