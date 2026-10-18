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

### ADR-004: Cognitive Scaffolding, Situated Cadet Flight Academy, and Narrative Transportation Space Opera Campaign
- **Date**: 2026-10-18
- **Status**: Accepted
- **Context**: The game's multi-layered simulation systems (orbital flight, sensor scanning, reactor power distribution, station commerce, autonomous fleet drones, tactical corsair encounters, pilot talents) presented an intimidating cognitive barrier to entry for novice players, risking early drop-off (Sweller's Cognitive Load Theory). Furthermore, purely mechanical systems lacked emotional immersion and extrinsic-to-intrinsic meaning (Green & Brock's Narrative Transportation Theory, Loewenstein's Information Gap Theory).
- **Decision**:
  1. Implement a 6-step non-intrusive Cadet Flight Academy (`models.py`, `story.py`, `engine.py`) grounded in Vygotsky's Zone of Proximal Development (ZPD) and Gee's Situated Learning principles. The academy passively monitors natural player actions (`orbit`, `scan`, `power`, `trade`, `drone`, `jump`) rather than imposing modal tutorial prisons, granting incremental credits and XP upon completion, culminating in graduation honors and the `relic_cadet_wings` artifact.
  2. Embed "The Precursor Cipher" space opera campaign (`story.py`, `engine.py`), featuring a 3-act episodic mystery spanning Sol, Sirius, and the Vega Gateway. Each act introduces rich character dispatches across an encrypted subspace radio array (Admiral Vance of the Sol Coalition, Cipher of the Free Spacers Syndicate, and Archon Prime of the Precursor Watch) and presents high-stakes moral dilemmas altering faction standings, economy, and unique story relics.
  3. Expand the Web Cockpit HUD (`index.html`, `style.css`, `app.js`) with an always-visible Cadet Flight Academy progress ribbon and a dedicated COMMS LOG interface complete with faction reputation chips, animated speaker avatars, and Web Audio synthesized subspace transmissions.
  4. Provide full CLI and REPL parity (`voidfarer tutorial [skip|reset]` and `voidfarer story [choose <id>]`).
  5. Preserve strict architectural decoupling between data DTOs (`models.py`) and story content templates (`story.py`), maintaining zero circular dependencies, backward compatibility with legacy save states, and sub-second test execution.
- **Consequences**: Radically flattens player onboarding friction, establishes compelling narrative stakes, maximizes player attention and retention through parasocial agency and narrative transportation, and maintains 100% standard library compliance across all platforms.

### ADR-005: Deep Hardening of Narrative Engine, Web Cockpit State Resolution, and Relic Stat Integration
- **Date**: 2026-10-18
- **Status**: Accepted
- **Context**: A comprehensive post-implementation audit of the Cadet Flight Academy and Precursor Cipher narrative campaign revealed several operational gaps: (1) In Web Cockpit JS, `story_chapters` was serialized as an array, but accessed as an object dictionary by chapter ID string, causing `curChap` to evaluate to `undefined` and preventing the story tab from rendering; (2) In `engine.py`, story choices lacked target system validation, allowing players to resolve remote acts (Sirius and Vega) without traveling to their target star systems; (3) Passive stat multipliers in `retention.py` omitted support for `max_hull` and `trade_margin`, leaving story relics like `relic_cipher_key` and `relic_cadet_wings` inert; (4) The Web HUD and CLI lacked distinct victorious visual states for completed campaigns and graduation ceremonies.
- **Decision**:
  1. Update `retention.py` `calculate_passive_multipliers` to fully calculate `max_hull`, `trade_margin`, and dual-syntax `scanner_bounty`/`scan_bounty`, and wire effective maximum hull and shield expansion directly into `engine.py` when story relics are awarded.
  2. Implement strict geographical star-system validation in `SimulationEngine.make_story_choice()`, requiring the flagship to be physically present in `current_chapter.target_system_id` to resolve narrative decisions.
  3. Harden Web Cockpit `app.js` and `server.py` with dual `story_chapters` array and `story_chapters_map` dictionary lookups, safe null-checking for chapter system coordinates, graduation celebration ribbons, and retake-academy controls.
  4. Enrich CLI `cmd_story` and `cmd_status` with prominent celebratory campaign epilogue views once all acts are resolved.
  5. Expand automated regression test coverage to 58 tests across all edge cases.
- **Consequences**: Guarantees zero UI rendering failures, aligns narrative progression with spatial flight mechanics, activates all passive story relic mechanics, and provides celebratory feedback across both web and terminal interfaces.
### ADR-006: Sovereign Factions, Megacorporations, and Advanced Dual-Layer Tactical Combat Archetypes
- **Date**: 2026-10-18
- **Status**: Accepted
- **Context**: Voidfarer's procedural galaxy lacked geopolitical depth, sovereign territorial borders, corporate commerce incentives, and tactical enemy depth beyond basic pirate skirmishes. Players required persistent diplomatic standing, ideological alliances, market price tariffs/discounts, and engaging tactical combat with deflector shields, telegraphed abilities, and subsystem targeting.
- **Decision**:
  1. Implement `Faction` and `Corporation` domain models (`factions.py`) featuring 5 canonical sovereign factions (Sol Coalition, Free Spacers Syndicate, Precursor Watch, Nebula Mining Collective, Orion Ascendancy) and 4 canonical megacorporations (Omnicorp Mining, Hyperion Dynamics, Astral Logistics, CyberneX Labs).
  2. Implement dynamic Standing Tiers (-100 to +100: Hostile, Unfriendly, Neutral, Friendly, Allied) with geopolitical market purchase modifiers (-15% discount for Allied down to +25% punitive tariff for Hostile) and corporate specialty trade margin bonuses (+15% to +22% margin on specialty commodities).
  3. Introduce star system territorial affiliation and emergent naval interdictions: hyperlane transit into systems controlled by Hostile factions (standing <= -50) triggers high-probability naval patrol interceptions.
  4. Create `EnemyArchetype` procedural generation (`enemies.py`) with 5 tactical archetypes (Corsair Interceptor, Syndicate Marauder, Corporate Enforcer, Precursor Sentinel, Warlord Dreadnought), deflector shield capacitance, telegraphed special abilities (`shield_drain`, `emp_overload`, `nanite_regen`, `tachyon_lance`), and precision subsystem targeting (`target weapons`, `target shields`).
  5. Add kinetic armor-piercing Drone Strike attacks that bypass deflector shields to directly damage enemy hulls, granting deployed fleet drone assets high-value tactical combat utility.
  6. Deliver full CLI REPL and Web Cockpit parity, including interactive Factions & Corps tabs, dual Shield/Hull telemetry meters, pulsing telegraph warning banners, and victory reputation shifts.
- **Consequences**: Deepens the galaxy with emergent geopolitical consequence, trade specialization, and high-stakes tactical space battles while preserving 100% Python standard library purity, backward compatibility for legacy save files, and sub-second test execution across 68 automated unit tests.
