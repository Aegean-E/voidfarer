# Decisions

Why this project is built the way it is, oldest first. One entry per decision that changes a
contract, a dependency, a data format or the architecture; IDs are consecutive and never reused.


### ADR-001: Architecture, Storage Schema, and Zero-Dependency Simulation Engine for VoidFarer
- **Date**: 2026-10-18
- **Status**: Accepted
- **Context**: Autonomous deep-space exploration and fleet simulations require deterministic procedural generation, fast state transitions, crash-safe persistence, and multi-interface usability (both CLI and Web HUD) without third-party runtime package dependencies.
- **Decision**:
  1. Build core engine using Python 3.10+ standard library exclusively (`math`, `random`, `dataclasses`, `http.server`, `json`, `pathlib`).
  2. Implement frozen immutable DTO models (`models.py`) with explicit schema validation.
  3. Ensure power-loss safe atomic disk persistence with shadow backup (`.bak`), quarantine on corruption, and fsync flushing (`storage.py`).
  4. Provide dual interfaces: an ANSI-colored CLI terminal REPL (`cli.py`) and a zero-dependency local HTTP REST daemon with an HTML5 Canvas holographic cockpit Web HUD (`server.py`, `static/`).
- **Consequences**: Zero external pip dependencies required; instant cold-start startup; sub-second test execution; full multi-platform compatibility across Windows, Linux, and macOS.

### ADR-002: Autonomous Fleet Assets, Modular Arsenal Upgrades, and Hostile Tactical Intercepts
- **Date**: 2026-10-18
- **Status**: Accepted
- **Context**: The simulation engine lacked long-term player progression, modular equipment slots, autonomous fleet scaling, and interactive combat encounters during low-security star system transit.
- **Decision**:
  1. Introduce `FleetDrone` models allowing players to commission, deploy, and harvest yield from autonomous mining, recon, and escort drones across star systems.
  2. Implement `ShipUpgrade` modular hardware slots (engines, shields, sensors, weapons, cargo) with concrete mathematical stat bonuses to fuel efficiency, shield capacitance, scan bounties, and hold capacity.
  3. Add `CombatEncounter` mechanics with tactical choices (laser strike, shield absorption, evasive burn, emergency jump) governed by power routing.
  4. Enhance REPL with multi-threaded `serve` daemon launch, command aliases, and tolerant input handling.
- **Consequences**: Fulfills the deep-space fleet simulator vision with layered meta-progression, rich tactical gameplay, and seamless concurrent web and terminal operation without introducing any external dependencies.

### ADR-003: Behavioral Attention Mechanics, Variable-Ratio Reinforcement, Zeigarnik Task Loops, and Loss Aversion
- **Date**: 2026-10-18
- **Status**: Accepted
- **Context**: Following an academic literature review on addiction and attentional psychology (Reward Prediction Error, operant conditioning schedules, near-miss effects, Zeigarnik cognitive tension, loss aversion, and self-determination theory), the core simulation needed retention loops that create genuine engagement and agency without deceptive dark patterns.
- **Decision**:
  1. Integrate Variable-Ratio Precursor Relic drops with Near-Miss sensor detection: Scans roll for ancient artifacts across 4 rarity tiers. Near-miss rolls generate distinct acoustic resonance and a persistent scanner boost for the subsequent sweep (Schultz 1997, Clark et al. 2009).
  2. Implement an active Sector Bounties board leveraging the Zeigarnik Effect (1927) and Goal-Gradient hypothesis: Fulfilling an active task immediately draws a new assignment, ensuring an incomplete progress bar remains active in the player's cognitive queue.
  3. Introduce Expedition Jump Streaks leveraging Prospect Theory Loss Aversion (Kahneman & Tversky 1979): Each safe hyperlane jump grants a cumulative +15% multiplier (up to x2.50) to rewards, but fleeing from hostile combat resets the streak to 1, raising physiological arousal and decision weight.
  4. Implement Pilot Mastery and Specialization Trees grounded in Self-Determination Theory (Ryan & Deci 2000): Career XP unlocks talent perk trees (`void_cartographer`, `dreadnought_tactics`, `swarm_commander`, `quantum_smuggler`) satisfying player competence and autonomy.
  5. Add Tactical Combat Combo Counters and Critical Overcharge to induce Flow State (Csikszentmihalyi 1990) with procedural Web Audio synthesis for kinesthetic juice (Swink 2008).
- **Consequences**: Player engagement is deeply reinforced through cognitive resonance, tangible meta-progression, and responsive sensory feedback while maintaining 100% standard library compliance and test execution in <1.0s.



