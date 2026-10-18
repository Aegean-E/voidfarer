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

### ADR-007: Zero-Friction 1-Click Game Launchers and Embedded Browser Auto-Launch
- **Date**: 2026-10-18
- **Status**: Accepted
- **Context**: Voidfarer required players to execute terminal commands (`python -m voidfarer.cli serve` or `repl`) from command prompts, creating friction for users who expect a 1-click startup experience directly from Windows Explorer.
- **Decision**:
  1. Implement `play.bat` with automated multi-tier Python discovery (`py -3`, `python`, `python3`, and standard installation paths), an interactive ASCII mission menu defaulting to the Web Cockpit, and transparent CLI argument passthrough.
  2. Implement `voidfarer.bat` as a fast passthrough batch launcher in both project root and workspace root.
  3. Enhance `server.py` and `cli.py` with an `--open` flag that utilizes the standard `webbrowser` module via a non-blocking timer thread to automatically launch the default browser upon server readiness.
- **Consequences**: Enables instantaneous 1-click game startup on Windows without any external pip packages, preserving 100% standard library compliance and sub-second automated test execution.

### ADR-008: Cosmic Stardate, Simulation Ticks, and Universal Time Control Architecture
- **Date**: 2026-10-18
- **Status**: Accepted
- **Context**: Voidfarer's galaxy simulation previously relied partly on asynchronous wall-clock intervals or static turns, lacking an explicit universal simulation clock, orbital angular velocity updates for celestial bodies, autonomous fleet drone time-based yield accumulation, passive shield capacitance recharge, and player temporal control mechanics (pause, speed acceleration, manual discrete tick stepping).
- **Decision**:
  1. Introduce `TimeState` immutable DTO in `models.py` tracking `tick: int`, `stardate: float`, `speed: float`, `is_paused: bool`, `time_scale: str`, and `elapsed_days: float`, serialized with backward-compatible defaults in `GameState`.
  2. Implement `SimulationEngine.tick(num_ticks: int = 1)` advancing:
     - Cosmic stardate and elapsed days (1 tick = 0.25 days = 6 hours; stardate = 3042.0 + elapsed_days / 365.25).
     - Circular/Keplerian orbital positions (`current_angle = (current_angle + orbit_speed * 0.05 * num_ticks) % (2*pi)`) across all celestial bodies in the galaxy.
     - Autonomous fleet drone harvest yield cycles across star systems.
     - Passive deflector shield capacitor regeneration out of combat.
     - Combat ability cooldown decay during active tactical encounters.
  3. Implement temporal control primitives: `pause_time()`, `resume_time()`, `set_time_speed(speed: float)` (0x, 1x, 2x, 5x, 10x), and `step_time(num_ticks: int)`.
  4. Implement REST API endpoints in `server.py`: `GET /api/time`, `POST /api/time/step`, `POST /api/time/speed`, `POST /api/time/pause`, and `POST /api/time/resume`, accompanied by a background `SimulationTicker` daemon loop scaling tick sleep intervals by `1.0 / speed` when unpaused.
  5. Provide terminal CLI and REPL parity: `voidfarer time [status|pause|resume|speed <val>|step [n]]` and interactive REPL aliases (`chrono`, `tick`, `wait`).
  6. Provide Web Cockpit HUD parity: sleek cybernetic `hud-time-deck` with glowing live stardate and tick badge, interactive pause/speed/step buttons, Spacebar/1-4/T hotkeys, and synchronized canvas radar planet orbital positions.
  7. Maintain thread safety via re-entrant engine locking and sub-second test execution across 84 automated unit tests.
- **Consequences**: Gives players full god-like temporal command over cosmic simulation flow, deepens orbital and fleet autonomy dynamics, aligns canvas radar motion with physics state, and preserves zero third-party dependencies.

### ADR-009: Universal State Preservation, Temporal Speed Memory, and Hyperspace Transit Dynamics
- **Date**: 2026-10-18
- **Status**: Accepted
- **Context**: In-depth audit of recent temporal mechanics and simulation state updates revealed critical gaps and regressions:
  1. Manual `GameState(...)` instantiation across 25 engine operations (orbit, scan, trade, refuel, repair, route_power, combat, anomaly resolution, upgrades, drones, contracts, talents, story choices, tutorial controls) omitted the `time` field, silently resetting cosmic ticks and stardate back to `tick=0, stardate=3042.0` on every action.
  2. Temporal speed memory was lost when pausing: resuming the clock defaulted to 1.0x even if the commander previously set 5.0x or 10.0x.
  3. Hyperspace jumps took instantaneous zero cosmic time, failing to advance planetary orbital revolutions or fleet drone harvest cycles during long interstellar transit.
  4. Server ticker daemon loop utilized non-interruptible `time.sleep()`, causing delay during server shutdown and missing RAII socket cleanup on Windows.
  5. Rapid keyboard repeat on Spacebar/hotkeys caused uncontrolled HTTP request stampedes to the temporal control endpoints.
- **Decision**:
  1. Introduce `_clone_state(**kwargs) -> GameState` in `SimulationEngine` that preserves `time` and `stats` fields unless explicitly overwritten, and refactor all 25 methods across `engine.py` to use `_clone_state(...)`.
  2. Upgrade `pause_time()`, `resume_time()`, and `set_time_speed()` to store and remember configured playback speed rate across pause/resume cycles.
  3. Advance cosmic time by 2 ticks (12 hours / 0.5 days transit) on interstellar hyperspace jumps, updating planetary orbits across all systems and persisting realistic transit duration.
  4. Refactor `_ticker_loop` to use `ticker_stop.wait(interval)` for instant thread termination, and add a `finally:` block in `run_server` ensuring `server.server_close()` is always invoked.
  5. Add hotkey repeat suppression (`if (e.repeat) return;`) and drone harvest yield telemetry logging in Web Cockpit `app.js`.
  6. Expand automated test coverage with regression tests for state preservation, speed memory, and hyperspace transit time.
- **Consequences**: Guarantees zero simulation clock resets across any player action, realistic cosmic transit time during interstellar jumps, smooth temporal control UX, instant clean server shutdown, and 100% test pass rate across all automated suites.

### ADR-010: V10 Economy & Inventory Stabilization: Combat Tick Rebuild, Volume Cargo Gate, Chassis Listing, Consumable Terminal, and Housekeeping
- **Date**: 2026-10-18
- **Status**: Accepted
- **Context**: An independent review of the in-flight V10 economy/trading/inventory work (`economy.py`, `inventory.py`, engine hooks, REST/CLI surfaces) confirmed several defects blocking the feature:
  1. `tick()` rebuilt the active combat encounter with non-existent fields (`enemy_type`, `enemy_weapons`, `threat_level`, `tactical_turn`, `combat_log`), raising `TypeError` whenever a special-ability enemy had an active `ability_cooldown`; the Web Cockpit background ticker thread died on the first such tick.
  2. The buy-side cargo gate compared raw unit counts against a volume requirement, silently overselling hold space for multi-volume commodities (titanium, xenoliths).
  3. `get_available_chassis` was called with the ship's class name instead of the chassis id, so the current hull always appeared purchasable in the REST shipyard payload and Web HUD; the zero-cost starter hull could also be re-bought for free hull/shield/fuel refreshes.
  4. `sell_upgrade` cleared the equipped slot but left the module name in `ship.upgrades`, producing ghost modules in the HUD.
  5. The item catalog defined four usable consumables, but no purchase path existed: the CLI hint pointed at a non-existent `inventory buy`, and the REST API offered `use`/`jettison` without a buy endpoint.
  6. Bare `int()` conversions in `inventory jettison`, `repair`, `refuel` (CLI/REPL) and `/api/inventory/jettison` (REST) crashed on non-numeric input.
  7. `cmd_market` displayed legacy static prices while `trade()` charged dynamic stock/event/faction-adjusted prices.
  8. The hygiene gate flagged three Google Fonts links and four silent `except Exception: pass` blocks (browser launch, server teardown, console reconfigure).
- **Decision**:
  1. Rebuild the combat encounter via `dataclasses.replace(...)` for ability-cooldown decay.
  2. Centralize hold math in `inventory.calculate_cargo_volume` and use it in `trade()` and the new `buy_item()`.
  3. Resolve the current chassis through `SimulationEngine.current_chassis_id` for `get_available_chassis` (state snapshot + REST shipyard) and reject zero-cost starter hull purchases in `buy_ship_chassis`.
  4. Remove the sold module's display name from `ship.upgrades` on sale.
  5. Add `SimulationEngine.buy_item` with CLI `inventory buy <id> [qty]` (including top-level argparse parity) and `POST /api/inventory/buy`; malformed REST quantities answer `400`.
  6. Guard CLI/REPL numeric conversions and REST quantity parsing with clean messages.
  7. Render `calculate_dynamic_market_quote` values plus the faction trade modifier in `cmd_market`, matching what `trade()` actually charges.
  8. Drop the Google Fonts links, extend the CSS font variables with local fallback stacks, and narrow the exception handlers while keeping best-effort teardown (browser launch reports a manual-visit hint instead of failing silently).
- **Consequences**: The V10 economy/inventory feature is stable, documented, and covered by 33 new tests (`test_economy.py`, `test_inventory.py`, and regressions) — 120 tests total, 100% green in about 2 seconds. Cargo math, chassis listings, market prices, and the advertised consumable terminal now match what the player experiences in CLI, REST, and the Web Cockpit, which also renders fully offline. Deferred to a future milestone: wiring the inert `stat_bonus` effects of the newer hardware modules and chassis perks, restoring the unreachable web mini-games, and completing the phishing panel.

### ADR-011: Windows Launcher Crash Repair: Escaped Banner Pipes, CRLF Endings, and Launcher Regression Tests
- **Date**: 2026-10-18
- **Status**: Accepted
- **Context**: Double-clicking `play.bat` on Windows appeared to do nothing: the console window flashed and closed before any menu. Reproduction showed `cmd /c play.bat` exiting with code 255 after printing only the first banner lines, with `'_' is not recognized as an internal or external command`. Root causes: (1) two unescaped `|` groups in the ASCII banner (`\|_` and `_||`) made cmd treat the rest of the echo as a piped command line, aborting the script before the menu; (2) both launchers shipped LF-only line endings, which cmd parses unreliably and editors easily reintroduce; (3) the banner's bottom line rendered `\_|\______` instead of the canonical `\_\|______` art used by the Python status banner in `cli.py`; (4) the menu hard-coded "68 Unit Tests", long stale.
- **Decision**:
  1. Escape every literal pipe in the banner (`\|` → `\^|` and `||` → `^|^|`) so the art renders without cmd interpreting it as a pipeline.
  2. Convert `play.bat` and `voidfarer.bat` to CRLF line endings.
  3. Align the banner's final line with the canonical art in `cli.py`.
  4. Replace the stale "68 Unit Tests" menu label with "Automated Test Suite" so it cannot drift from the real count again.
  5. Add `tests/test_batch_launchers.py`: a CRLF policy unit test for both launchers plus a Windows-only integration test that runs the real menu path (choice `0`) and requires a clean exit 0 with the menu rendered.
- **Consequences**: Double-click launch works again from Explorer, argument passthrough (`play.bat status`, `voidfarer.bat status`) still exits 0, and launcher regressions now fail the suite — 123 tests total, 100% green in about 2 seconds.

### ADR-012: Relics Command API Repair and Test Isolation from the Live Save
- **Date**: 2026-10-18
- **Status**: Accepted
- **Context**: The Phase 4 gate failed on `test_cli_relics` once the save contained a relic: `cmd_relics` called `calculate_passive_multipliers(relics, specializations)` although the function takes only `ship`, and then printed key names (`scanner_bounty_mult`, `laser_damage_mult`, …) the returned dict never contains. Both defects had been masked because the CLI test suite ran against the player's real save in `%LOCALAPPDATA%\.voidfarer`: `TestCLI` calls `main()` with no isolation, so mutating test commands (for example `power`) persisted into live player progress, and the tests only exercised the relics path while the live save happened to have no relics.
- **Decision**:
  1. Call `calculate_passive_multipliers(engine.state.ship)` in `cmd_relics` and map the canonical keys: `scan_bounty`, `trade_margin`, `laser_dmg` and `drone_yield` as delta percentages, `shield_cap` and `max_hull` as absolute bonuses, and `fuel_efficiency` as savings.
  2. Isolate every test that reaches `main()`/`_get_engine` from the live save: `tests/test_cli.py` gains an `_IsolatedCliTestCase` base that patches `LOCALAPPDATA`, `HOME`, and `USERPROFILE` into a per-test temp directory, and `tests/test_story.py::test_cli_main_entrypoint` wraps its `main()` calls the same way.
  3. Add `TestCLIRelicsWithRecoveredRelics`, which seeds a save containing all six story relics and asserts the vault and modifier block render with exit 0.
- **Consequences**: The relics command works for any save, the automated suite can no longer read or write the player's live save (`%LOCALAPPDATA%\.voidfarer` verified untouched by hashing it before and after full-suite runs), and total coverage is 124 tests, 100% green in about 2 seconds.

### ADR-013: Cockpit Layout Rules: Lower-Right Telemetry Log with Hide Button, Top-Right Chrono Deck, Left Vertical Terminal Rail
- **Date**: 2026-10-18
- **Status**: Accepted
- **Context**: The user stated three cockpit layout rules, now recorded as project guidelines G-001..G-003: (1) the TELEMETRY / Tactical Flight Log belongs in the lower-right corner and must carry a hide button; (2) the Chrono tick and time settings deck belongs in the right upper corner; (3) the Commerce/Arsenal/Fleet terminal runs vertically (up to down) on the left side with the active tab's content beside it. The old cockpit held the log in the center deck, the chrono deck mid-bar, and the terminal as a horizontal tab strip in the right deck. Clarification answers: the chrono deck stays inside the top status bar but is pinned to its far right edge; the lower-right deck holds only the telemetry log; the radar moves above the reactor in the center column, with the context alerts on top.
- **Decision**:
  1. Restructure `index.html` (blocks moved verbatim by a balanced-tag span extraction — no markup retyped): `#panelRight` holds only the log panel (`#logPanel`, with `#btnToggleLog` + `#clearLogBtn` in a `log-header-actions` group); `#panelCenter` stacks the combat/anomaly alert cards, the NAV-radar sub-panel (`#panelNav`) and the reactor matrix (`#panelReactor`); the new `#panelLeft` deck carries the vertical tab rail (`#deckTabsHeader`) plus a `terminal-content-stack` with all seven tab contents; the chrono deck is the last block of `#hudTopBar`.
  2. `style.css`: `.cockpit-grid` columns become `1.5fr 1.15fr 0.9fr`; `.panel-left` turns into a two-column grid (170px rail + content) and its `.deck-tabs-header` stacks vertically; `.panel-right` pins its content to the corner with `justify-content: flex-end`; `.hud-time-deck` gains `margin-left: auto`; `.log-panel.log-collapsed` hides the stream; below 1200px the rail collapses into a wrapping row.
  3. `app.js`: cache `#logPanel`/`#btnToggleLog` and bind a click handler that toggles `log-collapsed` and swaps the HIDE/SHOW label; the collapse state is view-only and persists nothing.
  4. Add `tests/test_cockpit_layout.py`: eleven structural tests (stdlib `html.parser` element tree over the real assets) pinning deck membership, document order, the CSS rules, and the JS wiring — written failing-first (11/11 red before the restructure, 11/11 green after).
- **Consequences**: The terminal rail now runs down the left side, the center column shows alerts above the radar and the reactor, the chrono controls sit in the top-right corner, and the telemetry log is anchored at the lower-right corner where it can be collapsed to reclaim space. Known limitation (unchanged): the radar click mapping assumes 1:1 canvas scaling; growing the radar container was deliberately avoided to keep pointer behaviour identical. Total coverage 135 tests, 100% green in about 2 seconds.


### ADR-014: Effective Hardware Module Bonuses, Chassis Perks, and a Portable Launcher Test
- **Date**: 2026-10-18
- **Status**: Accepted
- **Context**: ADR-010 deferred wiring the inert `stat_bonus` entries of the newer hardware modules and the chassis perks. An audit confirmed the gaps: only `warp_booster_mk2` and `deep_core_scanner` had hard-coded effects; fuel savings on MK-I/MK-III, evasion, shield regeneration, scan multipliers, relic-find, combat damage, and ECM were advertised in the arsenal but never read; and the Orion, Solaris, Chronos, and Archon chassis perks existed only as display strings. Separately, the full suite was red on this Windows host because `NoDefaultCurrentDirectoryInExePath=1` makes `cmd /c play.bat` fail to resolve the script from the project directory, even though double-click and `.\play.bat` work.
- **Decision**:
  1. Extend `ShipChassis` with a `stat_bonus` mapping and populate it from the advertised perks: Orion `+15%` trade margin, Solaris `+20` combat damage, Chronos `x1.5` scan yield, Archon `+35` combat damage; the starter Vanguard stays neutral.
  2. Add `calculate_equipment_bonuses(ship)` in `upgrades.py` as the single aggregation point. Fuel savings multiply as `(1 - value)`, scan yields multiply, and combat damage, evasion, shield regeneration, relic-find, ECM, trade margin, and passive repair sum; fuel is floored at `0.10x` and evasion/ECM at `0.90`.
  3. Consume the aggregate in the engine: jump fuel burn (replacing the `warp_booster_mk2` hard-code), hostile and low-security encounter rolls (`pirate_evasion`), scan bounties and relic chance (replacing the `deep_core_scanner` hard-code), sale margins, laser damage (replacing the `pulse_cannon_array` hard-code), evasive-burn and counter-battery dodge chance, and tick shield regeneration plus repair-bay healing.
  4. Expose `equipment_bonuses` in the status snapshot for HUD/telemetry consumers without changing the save schema or catalog ids.
  5. Add `tests/test_equipment_bonuses.py` (11 tests, failing-first) covering the aggregation rules and each engine surface, and make the Windows launcher integration test invoke the absolute `play.bat` path so hardened hosts with `NoDefaultCurrentDirectoryInExePath=1` can still run it.
- **Consequences**: Every advertised hardware effect and chassis perk now changes gameplay through one test-pinned calculation path; purchases no longer promise inert stats. Coverage is 146 tests, 100% green in about 2 seconds, with the launcher regression test portable across hardened Windows configurations. No save migration was needed because chassis identity continues to resolve from the stored ship class and bonuses are derived at read time.
