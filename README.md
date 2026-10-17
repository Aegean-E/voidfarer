# VoidFarer

> **Autonomous Deep-Space Fleet, Procedural Galaxy & Holographic Cockpit Simulator.**

VoidFarer is a zero-dependency, local-first space flight and exploration simulation engine. Navigate procedural star systems, establish orbits around exotic planets, route reactor power, trade dynamic commodities across orbital stations, investigate dangerous spatial anomalies, and pilot your flagship using either an ANSI terminal REPL or an HTML5 Canvas holographic cockpit Web HUD.

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
    ├── test_engine.py        <- state transitions & anomaly mechanics
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
Displays commander dossier, vital telemetry (hull, shields, fuel), reactor power distribution, current system coordinates, and proximity hazard alerts.

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

### 4. Reactor Power Routing
Distribute 100% of your ship's reactor power across subsystems:
```bash
# power <engines> <shields> <sensors> <weapons>
python -m voidfarer.cli power 35 25 25 15
```

### 5. Commodity Commerce & Drydock Services
```bash
# Inspect local exchange prices
python -m voidfarer.cli market

# Purchase trade goods
python -m voidfarer.cli buy fuel_cells 5

# Sell cargo for credits
python -m voidfarer.cli sell titanium 3

# Repair hull damage and refuel
python -m voidfarer.cli repair --amount 25
python -m voidfarer.cli refuel --amount 20
```

### 6. Interactive Terminal Cockpit REPL
```bash
python -m voidfarer.cli repl
```

### 7. Holographic Web Cockpit Interface
Launch the embedded zero-dependency Web Audio & Canvas cockpit:
```bash
python -m voidfarer.cli serve --port 8080
```
Open **`http://127.0.0.1:8080`** in any modern web browser to access:
- **Interactive Orbit Radar**: Real-time animated orbiting planets, solar corona flare effects, clickable orbital bodies, and trajectory locking.
- **Galaxy Sector Chart**: Hyperlane corridor network visualization and jump routing.
- **Synthesized Web Audio**: Procedural sound effects for radar sweeps, warp jumps, button clicks, and alarms.
- **Reactor Power Matrix**: Dynamic power allocation sliders with instant subsystem re-routing.
- **Commodity Exchange**: Live trading terminal with buy/sell actions and cargo capacity meters.
- **Anomaly Encounters**: Tactical hazard modals with power checks and multi-branch outcomes.

---

## 🛡️ Architecture & Resilience Guarantees

1. **Zero External Dependencies**: Built entirely on standard Python modules (`math`, `random`, `dataclasses`, `http.server`, `json`, `pathlib`).
2. **Power-Loss Recovery (PRINCIPLE-013)**: State saves use atomic replacement with file descriptor `fsync`, shadow `.bak` backups, and automatic quarantine of corrupt payloads.
3. **Sub-Second Test Verification**: Comprehensive 25-test suite runs in under 0.7 seconds (`python -m unittest discover`).
4. **Platform Parity**: Full native support for Windows, Linux, and macOS with automatic console encoding detection.
