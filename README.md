# VoidFarer

> **Autonomous Deep-Space Fleet, Procedural Galaxy & Holographic Cockpit Simulator.**

VoidFarer is a zero-dependency, local-first space flight, fleet management, and exploration simulation engine. Navigate procedural star systems, establish orbits around exotic planets, route reactor power, commission autonomous mining and escort drones, purchase modular hardware upgrades, engage in tactical combat with hostile corsairs, trade dynamic commodities across orbital stations, and pilot your flagship using either an ANSI terminal REPL or an HTML5 Canvas holographic cockpit Web HUD.

---

## ⚡ 30-Second Cold-Start Quick Reference

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
│   ├── decisions.md          <- monotonic ADR register
│   ├── guidelines.md         <- project-specific guidelines
│   ├── project.json          <- stack and gate configuration
│   └── task_ledger.json      <- power-loss safe task state
├── .gitignore                <- transient state & python caches excluded
├── pyproject.toml            <- build and package configuration
├── README.md                 <- living documentation
├── voidfarer/                <- core simulation package
│   ├── __init__.py           <- package metadata
│   ├── models.py             <- frozen dataclass DTOs and schema validators
│   ├── galaxy.py             <- procedural star system & hyperlane generator
│   ├── engine.py             <- deterministic state machine & coordinator
│   ├── upgrades.py           <- hardware upgrades catalog & drone templates
│   ├── storage.py            <- crash-safe atomic persistence & shadow backup
│   ├── server.py             <- zero-dependency HTTP REST & cockpit server
│   ├── cli.py                <- ANSI terminal interface & interactive REPL
│   └── static/               <- holographic web cockpit UI
│       ├── index.html        <- semantic HUD structure & radar canvas
│       ├── style.css         <- sci-fi glassmorphism design system
│       └── app.js            <- radar math, Web Audio synth & REST link
└── tests/                    <- sub-second unit & integration test suite
    ├── __init__.py
    ├── test_models.py        <- model immutability & serialization tests
    ├── test_galaxy.py        <- procedural generator & market tests
    ├── test_engine.py        <- state transitions, fleet & combat mechanics
    ├── test_storage.py       <- power-loss safety & corruption quarantine
    ├── test_server.py        <- REST API request/response contracts
    └── test_cli.py           <- command dispatch & argument parsing
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
Prints the sector hyperlane network, visited system flags, security ratings, and all celestial bodies in the local star system.

### 3. Navigation & Spaceflight
```bash
# Enter orbit around a planet or space station
python -m voidfarer.cli orbit sol_body_1

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
When intercepted by hostile corsairs in low-security space:
```bash
# Tactical maneuvers
python -m voidfarer.cli combat fire     # Laser battery barrage
python -m voidfarer.cli combat absorb   # Overcharge shield capacitors
python -m voidfarer.cli combat evade    # High-G thruster burn
python -m voidfarer.cli combat flee     # Emergency hyperspace micro-jump
```

### 7. Commodity Commerce & Drydock Services
```bash
# Inspect local exchange prices
python -m voidfarer.cli market

# Purchase and sell commodities
python -m voidfarer.cli buy fuel_cells 5
python -m voidfarer.cli sell titanium 3

# Repair hull damage and refuel
python -m voidfarer.cli repair --amount 25
python -m voidfarer.cli refuel --amount 20
```

### 8. Interactive Terminal Cockpit REPL
```bash
python -m voidfarer.cli repl
```
Inside the interactive REPL, you can execute all commands (`status`, `chart`, `market`, `jump`, `fleet`, `upgrades`, `combat`, `scan`, `power`, etc.), or type **`serve`** to launch the concurrent background Web HUD!

### 9. Holographic Web Cockpit Interface
Launch the embedded zero-dependency Web Audio & Canvas cockpit:
```bash
python -m voidfarer.cli serve --port 8080
```
Open **`http://127.0.0.1:8080`** in any modern web browser to access:
- **Interactive Orbit Radar**: Real-time animated orbiting planets, solar corona flare effects, clickable orbital bodies, drag-to-pan, and wheel zoom.
- **Galaxy Sector Chart**: Hyperlane corridor network visualization and jump routing.
- **Station Arsenal Tab**: Modular hardware upgrades shop with real-time stat bonuses.
- **Fleet Command Tab**: Roster of autonomous mining/scout drones with live harvest buttons.
- **Tactical Combat Overlay**: Real-time battle HUD with enemy health bar and tactical action buttons.
- **Synthesized Web Audio**: Procedural sound effects for radar sweeps, warp jumps, laser fire, button clicks, and alarms.
- **Reactor Power Matrix**: Dynamic power allocation sliders with instant subsystem re-routing.

---

## 🛡️ Architecture & Resilience Guarantees

1. **Zero External Dependencies**: Built entirely on standard Python modules (`math`, `random`, `dataclasses`, `http.server`, `json`, `pathlib`).
2. **Power-Loss Recovery (PRINCIPLE-013)**: State saves use atomic replacement with file descriptor `fsync`, shadow `.bak` backups, and automatic quarantine of corrupt payloads.
3. **Sub-Second Test Verification**: Comprehensive 33-test suite runs in under 0.8 seconds (`python -m unittest discover`).
4. **Platform Parity**: Full native support for Windows, Linux, and macOS with automatic console encoding detection.
