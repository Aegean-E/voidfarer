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
- **Consequences**: The V10 economy/inventory feature is stable, documented, and covered by 33 new tests (`test_economy.py`, `test_inventory.py`, and regressions) â€” 120 tests total, 100% green in about 2 seconds. Cargo math, chassis listings, market prices, and the advertised consumable terminal now match what the player experiences in CLI, REST, and the Web Cockpit, which also renders fully offline. Deferred to a future milestone: wiring the inert `stat_bonus` effects of the newer hardware modules and chassis perks, restoring the unreachable web mini-games, and completing the phishing panel.

### ADR-011: Windows Launcher Crash Repair: Escaped Banner Pipes, CRLF Endings, and Launcher Regression Tests
- **Date**: 2026-10-18
- **Status**: Accepted
- **Context**: Double-clicking `play.bat` on Windows appeared to do nothing: the console window flashed and closed before any menu. Reproduction showed `cmd /c play.bat` exiting with code 255 after printing only the first banner lines, with `'_' is not recognized as an internal or external command`. Root causes: (1) two unescaped `|` groups in the ASCII banner (`\|_` and `_||`) made cmd treat the rest of the echo as a piped command line, aborting the script before the menu; (2) both launchers shipped LF-only line endings, which cmd parses unreliably and editors easily reintroduce; (3) the banner's bottom line rendered `\_|\______` instead of the canonical `\_\|______` art used by the Python status banner in `cli.py`; (4) the menu hard-coded "68 Unit Tests", long stale.
- **Decision**:
  1. Escape every literal pipe in the banner (`\|` â†’ `\^|` and `||` â†’ `^|^|`) so the art renders without cmd interpreting it as a pipeline.
  2. Convert `play.bat` and `voidfarer.bat` to CRLF line endings.
  3. Align the banner's final line with the canonical art in `cli.py`.
  4. Replace the stale "68 Unit Tests" menu label with "Automated Test Suite" so it cannot drift from the real count again.
  5. Add `tests/test_batch_launchers.py`: a CRLF policy unit test for both launchers plus a Windows-only integration test that runs the real menu path (choice `0`) and requires a clean exit 0 with the menu rendered.
- **Consequences**: Double-click launch works again from Explorer, argument passthrough (`play.bat status`, `voidfarer.bat status`) still exits 0, and launcher regressions now fail the suite â€” 123 tests total, 100% green in about 2 seconds.

### ADR-012: Relics Command API Repair and Test Isolation from the Live Save
- **Date**: 2026-10-18
- **Status**: Accepted
- **Context**: The Phase 4 gate failed on `test_cli_relics` once the save contained a relic: `cmd_relics` called `calculate_passive_multipliers(relics, specializations)` although the function takes only `ship`, and then printed key names (`scanner_bounty_mult`, `laser_damage_mult`, â€¦) the returned dict never contains. Both defects had been masked because the CLI test suite ran against the player's real save in `%LOCALAPPDATA%\.voidfarer`: `TestCLI` calls `main()` with no isolation, so mutating test commands (for example `power`) persisted into live player progress, and the tests only exercised the relics path while the live save happened to have no relics.
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
  1. Restructure `index.html` (blocks moved verbatim by a balanced-tag span extraction â€” no markup retyped): `#panelRight` holds only the log panel (`#logPanel`, with `#btnToggleLog` + `#clearLogBtn` in a `log-header-actions` group); `#panelCenter` stacks the combat/anomaly alert cards, the NAV-radar sub-panel (`#panelNav`) and the reactor matrix (`#panelReactor`); the new `#panelLeft` deck carries the vertical tab rail (`#deckTabsHeader`) plus a `terminal-content-stack` with all seven tab contents; the chrono deck is the last block of `#hudTopBar`.
  2. `style.css`: `.cockpit-grid` columns become `1.5fr 1.15fr 0.9fr`; `.panel-left` turns into a two-column grid (170px rail + content) and its `.deck-tabs-header` stacks vertically; `.panel-right` pins its content to the corner with `justify-content: flex-end`; `.hud-time-deck` gains `margin-left: auto`; `.log-panel.log-collapsed` hides the stream; below 1200px the rail collapses into a wrapping row.
  3. `app.js`: cache `#logPanel`/`#btnToggleLog` and bind a click handler that toggles `log-collapsed` and swaps the HIDE/SHOW label; the collapse state is view-only and persists nothing.
  4. Add `tests/test_cockpit_layout.py`: eleven structural tests (stdlib `html.parser` element tree over the real assets) pinning deck membership, document order, the CSS rules, and the JS wiring â€” written failing-first (11/11 red before the restructure, 11/11 green after).
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

### ADR-015: Audit-Driven Hardening: Service Guards, Relic Stats, Storage/Server Resilience, CLI Parity, and Cockpit Runtime Contracts
- **Date**: 2026-10-19
- **Status**: Accepted
- **Context**: A full-project audit found defects spanning four layers. Engine: negative repair/refuel amounts minted credits and removed hull/fuel; buying an upgrade or chassis recomputed maximum hull/shield from chassis plus modules only, discarding permanent relic maxima; random max-stat relics were inert; `scan()` and `step_orbits()` dropped `StarSystem.dominant_corp`; occupied upgrade slots left ghost modules; drone harvest bypassed cargo volume; the victory path discarded a streak decrement; a zero `next_level_xp` could hang the engine; story choices updated a separate reputation store; invalid drone systems were accepted; repeat scans paid full bounties forever. Storage: failed atomic replacements returned success, temp names could collide, and schema-invalid saves skipped backup recovery. Server: malformed JSON silently became `{}` (triggering default mutations), unguarded integer conversions reset connections, `/api/step` did not save, and `/api/reset` bypassed the engine lock and RNG reset. CLI: documented combat actions, shipyard subcommands, `corporations`, and positional repair/refuel amounts were unreachable behind argparse. Cockpit: pointer hit tests used CSS pixels against intrinsic canvas pixels, state was dereferenced before load, power sliders overwrote authoritative power, cargo showed unit counts instead of volume, scan audio read non-existent response fields, and canvas colors used invalid CSS variables.
- **Decision**:
  1. Guard repair/refuel with positive-integer validation; preserve relic/talent `max_hull`/`shield_cap` when buying or selling modules and chassis; apply newly acquired max-stat relics immediately through `_apply_relic_stat_bonuses`; cap `_award_pilot_xp` at `next_level_xp >= 1`; preserve `dominant_corp`; reject occupied-slot replacement until the old module is sold; reject drone harvest when the incoming titanium volume exceeds free hold space; map story alignments into `faction_standings`; validate drone target systems; gate repeat scans on `scan_completed`; and share `MIN_STOCK`/`MAX_STOCK` between trade and the economy tick.
  2. Harden storage with a write lock, `uuid4` temp names, an atomic backup path, a raised `OSError` after failed replacements, invalid-UTF-8 handling, and schema-invalid primary quarantine plus backup fallback.
  3. Harden the HTTP server with bounded body parsing, dict-only JSON, typed `_int_field`/`_float_field`/`_bool_field` helpers, 400 responses for malformed input, a lock-protected `SimulationEngine.reset(seed)` with a fresh RNG, persisted `/api/step`, bind-error guidance, ticker save-error reporting, and a final save plus ticker join on shutdown.
  4. Restore CLI parity: full combat action set with subsystem target, `shipyard chassis|sell`, a `corporations` alias, and positional repair/refuel amounts.
  5. Fix cockpit runtime contracts: CSS-to-canvas pointer scaling, drag/click suppression, null-state guards, dirty-aware power-slider sync, manifest volume for the cargo meter, `discovery.relic`/`near_miss` audio, literal canvas colors, selected-target refresh after polling, market-tab rendering, and story auto-scroll only when new messages arrive.
- **Consequences**: All 179 tests pass in about 2.5 seconds and `aikit check voidfarer` remains the gate. The changes close economy-corrupting inputs, silent save failures, malformed-request crashes, permanent-stat loss, and several cockpit state mismatches. Trade-offs: occupied-slot replacement is now a two-step action (sell, then buy) to avoid surprising automatic resale; drone harvest fails rather than partially collecting when the hold is full; repeat scans no longer pay bounties; and failed saves surface as 500 responses instead of silent success. Deferred with rationale: faction tier perks and archetype `rep_rewards` remain descriptive data (implementing them changes balance and needs explicit tuning); multi-stat relic descriptions still exceed the single-passive relic model; combat/anomaly cargo grants still do not enforce hold capacity; the REPL-launched server still lacks the CLI ticker; and cockpit HTML interpolation remains unescaped for tampered local saves. These are recorded as known gaps rather than silently claimed as fixed.

### ADR-016: Adaptive Enemy AI, Expanded Star Systems, and In-Game Calendar Dates
- **Date**: 2026-10-19
- **Status**: Accepted
- **Context**: Hostile encounters used fixed special-ability cooldowns and did not react to the player's tactical state; star systems generated only 2-3 planets; and the chronometer exposed a fictional stardate (`3042.xx`) that was hard to read as a date. The requested additions had to preserve existing combat, economy, save, CLI, and HUD contracts.
- **Decision**:
  1. Add `ai_profile` and `enemy_intent` to `CombatEncounter` with safe defaults for old saves. Assign profiles to all five hostile archetypes (`aggressive`, `defensive`, `opportunist`, `adaptive`, `warlord`) and add `choose_enemy_intent()` in `enemies.py`. The policy reads enemy hull/shield ratios, player hull/shield ratios, tactical combo, special-ability readiness, and profile, then chooses `fire`, `brace`, `evade`, `execute`, or `ability` and emits a matching telegraph.
  2. Apply intents in `combat_action`: `brace` reduces incoming player strike damage to 55%, `evade` gives a 35% chance to make a damaging player action miss, `execute` increases counter-battery (and shield-absorb) damage by 50%, and `ability` gates the existing special abilities. The next intent is recomputed after every exchange and persisted, so combat telemetry predicts the AI's next move.
  3. Expand each system to 5-6 planets (6 in Sol and Betelgeuse, 5 elsewhere) and add desert, ice, lava, ringed-giant, and research-outpost archetypes. Guarantee at least one dockable station per system via a deterministic fallback conversion, preserving `sol_body_1` and existing body IDs.
  4. Add `TimeState.current_date` as `DD.MM.YYYY`, derived from `elapsed_days` with a 01.01.3042 epoch, and include `date` in time payloads while retaining `stardate` for compatibility. CLI status/time, server startup, and the web chronometer now show the calendar date with the tick badge.
- **Consequences**: New games get 52 planets across 10 systems with guaranteed stations, and hostile captains visibly adapt to player behavior. Existing saves remain loadable because new combat fields default and time payloads are additive; however, existing saves keep their stored 2-3-body galaxy until the player starts a new game or resets, since systems are persisted. The AI is an explainable deterministic policy rather than an ML model, so it is testable and predictable; profile and intent strings are open-ended but validated through defaults. Calendar dates use the game epoch, not the host machine's real date, so they remain stable across systems and saves.

### ADR-017: Frontier Command Expansion: Main Menu, AI Captains, Depots, Messages, Landing, Fleets/Allies, and a Branching Perks Window
- **Date**: 2026-10-19
- **Status**: Accepted
- **Context**: The cockpit had no startup/save-management surface, the radar controls lived outside the map, the Mastery page was a passive tab, and the galaxy lacked AI traffic, cargo depots, intergalactic messaging, landing, mercenaries, allies, and persistent unit statistics. The expansion had to remain save-compatible and keep the 222-test suite and existing REST/CLI contracts intact.
- **Decision**:
  1. Add persistent `AICaptain`, `Depot`, `QuantumMessage`, `Moon`, and expanded body metadata (`gravity`, `atmosphere`, `temperature_c`, `resources`, `moons`, `landable`). Extend `FleetDrone` with level/efficiency/integrity/sorties/specialty and `ShipState` with allies/landed body. All new save fields default safely.
  2. Add `frontier.py` with a deterministic five-captain roster, one depot per system, onboarding messages, a mercenary catalog, and an AI trader simulation that moves captains between systems and mutates stockpiles each tick. Player trades already mutate the same markets, so both actors drive prices.
  3. Add engine actions for AI hail/buy/sell/hire/ally, depot deposit/withdraw/direct-sale, quantum send/read, surface landing, mercenary hire/refit/dismiss, fleet-unit dismissal, and unified quest snapshots. AI allies add trade margin and combat support; mercenaries add damage, evasion, or post-victory repair.
  4. Expand procedural generation to 15 systems with 5-6 bodies each, new star spectral types (B/O/red giant/binary), savanna/tundra/toxic/barren/super-Earth/ice-giant worlds, generated moons, asteroid belts, guaranteed habitable landing sites, and a guaranteed station per system.
  5. Add a startup main-menu overlay (Continue/Save/Load/Delete/New/Settings), a closable settings window with localStorage persistence, a centered black NAV-radar with overlaid ORBITS/GALAXY and GRID/LABELS controls, a flagship transit animation, planet/system inspector fields, landing controls, Quest/AI/Depot/Messages tabs, fleet stats/refit/dismiss, mercenary contracts, and a branching Pilot Perks window with tier-2 prerequisites.
- **Consequences**: New games start with AI traffic, depots, messages, moons, and 80+ planets; existing saves receive the frontier roster/depots/messages via a bootstrap pass while keeping their stored systems. Compact UI controls moved onto the radar so the map remains the visual center, and the former Perks tab now opens a modal tree. Trade-offs: AI trade is a deterministic stockpile-flow model rather than price-optimizing agents; depots store units rather than volume; landing rewards are one-shot survey bonuses; and the main menu is web-only while the CLI retains its existing command surface. Residual: combat/anomaly cargo grants still bypass hold capacity, and cockpit HTML interpolation remains unescaped for tampered local saves (ADR-015).

### ADR-018: Capacity-Safe Reward Cargo and CLI Frontier Parity
- **Date**: 2026-10-19
- **Status**: Accepted
- **Context**: ADR-017 left two follow-ups: combat salvage and anomaly cargo rewards could push cargo volume above the hold capacity, and the new AI/depot/message/landing/mercenary/alliance systems were reachable only through the web cockpit.
- **Decision**:
  1. Add `_grant_cargo(cargo, commodity_id, quantity)` as the single capacity-aware grant helper. It computes free volume from `calculate_cargo_volume`, grants whole units that fit, and returns `(granted, overflow)`.
  2. Use the helper for combat salvage and anomaly cargo rewards. Combat messages now report the actual salvaged count and any jettisoned overflow; anomaly logs report overflow explicitly. Direct buys, drone harvest, deposits, and withdrawals already had capacity guards.
  3. Add CLI commands `quests`, `ai list|hail|buy|sell|hire|ally`, `messages list|send|read`, `depot status|deposit|withdraw|sell`, `land`, `mercs list|hire|dismiss|refit`, and `allies list|form`, reusing the same engine methods as the REST/cockpit paths.
- **Consequences**: The cargo-volume invariant now holds for all reward paths, with explicit overflow reporting instead of silent over-capacity storage. The new frontier systems are testable and usable from the terminal without changing REST or save contracts. Trade-off: overflow cargo is jettisoned rather than stored elsewhere; future depot auto-routing could recover it.

### ADR-019: Closing Advertised Faction Perks, Reputation Rewards, Multi-Stat Relics, Cockpit Escaping, and REPL Server Lifecycle Gaps
- **Date**: 2026-10-19
- **Status**: Accepted
- **Context**: ADR-015/017 recorded five remaining gaps: faction perks were descriptive only, enemy archetype `rep_rewards` were dead data, relics advertised secondary effects that the single-passive model could not apply, cockpit HTML interpolated server data without escaping, and the REPL-launched server had no ticker or stop lifecycle.
- **Decision**:
  1. Add `get_faction_service_perks(faction_id, standing)` and consume it in repair, refuel, trade margins, scan XP, drone yields, and jump encounter evasion. Friendly factions grant 10% trade margin and 15% repair discounts; allied factions grant 20% margin, free refuel, and naval escort evasion; Syndicate adds 15% sale margin, Precursor Watch adds 25% scan XP, and Nebula Collective adds 30% drone yield.
  2. Persist `archetype_id` on `CombatEncounter` and apply `EnemyArchetype.rep_rewards` on victory to both `faction_standings` and `corp_standings`, with the old faction fallback retained for legacy/test encounters.
  3. Add `PrecursorRelic.bonuses` as a secondary stat map, round-trip it through saves and random drops, apply it in `calculate_passive_multipliers` and `_apply_relic_stat_bonuses`, and populate secondary effects for story relics (`Cadet Wings`, `Core Matrix`, `Archon Crest`, `Sentinel Matrix`).
  4. Escape all dynamic market/arsenal/contract/story/talent/relic/faction/corporation strings before `innerHTML` and whitelist faction colors through `safeColor`.
  5. Add `BackgroundServer` and `start_background_server()` with a concurrent simulation ticker and guarded `stop()` (final save, ticker join, shutdown, close); wire REPL `serve`, `serve stop`, actual port reporting, and shutdown on exit.
- **Consequences**: Advertised perks and relic descriptions now match simulation behavior, reputation rewards are data-driven, tampered save/API strings cannot inject markup, and the REPL-hosted cockpit advances time and saves like the standalone server. Trade-offs: faction perks are simple tier thresholds rather than per-faction bespoke rules; `void_eye` retains its existing special-case scan bonus instead of double-counting a bonuses map; naval escort is modeled as encounter evasion rather than a visible escort unit. These are intentional simplifications with regression coverage.

### ADR-020: In-System Sublight/Quantum Transit, Planetary Civilization Metadata, and Dismissible Cockpit Popup Events
- **Date**: 2026-10-19
- **Status**: Accepted
- **Context**: Players and automated clients needed tick-based in-system transit (`sublight` and `quantum` modes) alongside immediate orbital capture (`orbit`), planetary civilization telemetry (`faction`, `population`, `government`) on inhabited bodies, and structured dismissible cockpit popup alerts (`GameEvent`) for arrivals and simulation events without breaking legacy save compatibility or the existing 238 unit tests.
- **Decision**:
  1. Add frozen `TravelState` and `GameEvent` DTOs in `voidfarer/models.py`, extend `CelestialBody` with `faction`, `population`, and `government`, add `travel: TravelState | None = None` to `ShipState`, and serialize `events: tuple[GameEvent, ...] = ()` in `GameState.to_dict()` / `from_dict()`.
  2. Populate deterministic civilization metadata (`faction`, `population`, `government`) on inhabited planets and stations in `GalaxyGenerator._generate_bodies` without consuming RNG calls, and backfill legacy saves in `SimulationEngine._bootstrap_frontier`.
  3. Add `start_travel(body_id, mode="sublight")`, `emit_event(kind, title, message)`, and `dismiss_event(event_id)` in `SimulationEngine`, advance and complete active `TravelState` on `tick()`, and include `undismissed_events` in `get_status_snapshot()` while preserving immediate `orbit(body_id)`.
  4. Expose `/api/travel` and `/api/events/dismiss` in `voidfarer/server.py`, add CLI `travel` and `events` subcommands in `voidfarer/cli.py`, and render planetary civilization fields, sublight/quantum transit buttons, and escaped popup event cards in `voidfarer/static/index.html` and `voidfarer/static/app.js`.
- **Consequences**: In-system navigation supports both instant orbital capture (`orbit`) and timed sublight/quantum transit (`start_travel`), inhabited worlds expose rich civilization telemetry, and cockpit alerts can be inspected and dismissed from both the web HUD and CLI with full save round-trip compatibility.

### ADR-021: ESC Menu Hotkey, Multi-Slot Atomic Saves, and Full-Viewport Background NAV-Radar Orbital Map (G-004)
- **Date**: 2026-10-19
- **Status**: Accepted
- **Context**: The user requested three enhancements: (1) pressing `ESC` opens/closes the Main Menu (or dismisses open modal windows first), (2) multiple save slots so players can create, list, load, and delete independent saves from the Main Menu, REST API, and CLI without losing default-slot compatibility, and (3) making the NAV-Radar orbital map the full-viewport background layer of the game with all HUD decks and panels rendered on top of it (`G-004`).
- **Decision**:
  1. Extend `StorageManager` (`voidfarer/storage.py`) with `resolve_slot(slot)`, `get_save_path(slot)`, `list_saves()`, and optional `slot: str | None = None` parameters on `save()`, `load()`, and `clear()` / `delete_save()`. Slot `"default"` (or `None`/`""`) maps to `self.save_file` (`voidfarer_save.json`) for 100% backward compatibility; named slots (`^[A-Za-z0-9_-]{1,40}$`) map to `voidfarer_save_<slot>.json` with the same atomic temp+fsync+replace and `.bak` shadow backup recovery.
  2. Add `GET /api/saves` and extend `POST /api/save`, `POST /api/load`, and `POST /api/delete-save` in `voidfarer/server.py` to accept an optional `slot` field, returning the resolved slot and updated save metadata list. Add `voidfarer saves [list|save|load|delete] [slot]` in `voidfarer/cli.py`.
  3. Wire `Escape` in `voidfarer/static/app.js` to close `#settingsOverlay` or `#perksOverlay` if open, or toggle `#mainMenuOverlay` (`toggleMainMenu()`), and add a multi-save slot manager (`#saveSlotInput`, `#saveSlotsList`, quick slot buttons, per-slot load/save/delete) inside `#mainMenuOverlay`.
  4. Enforce layout guideline `G-004` in `voidfarer/static/style.css` and `voidfarer/static/app.js` while keeping `#panelNav` above `#panelReactor` inside `#panelCenter` in the DOM: style `.canvas-radar-container` as `position: fixed; inset: 0; width: 100vw; height: 100vh; z-index: 0;`, clear `backdrop-filter` on `#panelCenter`/`#panelNav` so `position: fixed` anchors to the viewport, set `pointer-events: none` on transparent layout containers and `pointer-events: auto` on interactive HUD panels (`z-index >= 2`) and the radar canvas, and dynamically resize `#radarCanvas` to viewport dimensions.
- **Consequences**: Players can toggle the Main Menu or close dialogs with `ESC`, manage multiple independent save slots with rich metadata across web and CLI, and interact directly with the full-screen background orbital/galaxy radar behind all HUD panels while all existing layout and storage regression tests continue to pass.

### ADR-022: Scientifically Accurate Planetary Physics, 2D Euclidean Sublight Transit Distance/Ticks, and Persistent Tick-Synchronized Radar Transit Animation
- **Date**: 2026-10-19
- **Status**: Accepted
- **Context**: The user reported two simulation and HUD accuracy issues: (1) clicking transit in the cockpit ended the flagship transit animation prematurely after 1.3 seconds while `ship.travel` was still in progress across multiple ticks, and sublight transit only used `abs(r2 - r1)` instead of true 2D orbital distance; (2) planetary `atmosphere`, `gravity`, `temperature_c`, and `habitability` were assigned from independent random ranges rather than physically consistent stellar flux, bulk density, radius, atmospheric greenhouse/composition, and Earth Similarity habitability equations.
- **Decision**:
  1. Add `compute_scientific_planet_properties()` and `compute_habitability_index()` in `voidfarer/galaxy.py` and extend `CelestialBody` (`voidfarer/models.py`) with `habitability: float = 0.0` (0.0 to 100.0%). Derive planetary `radius_km`, bulk density, and surface `gravity` ($g = (R/R_\oplus)(\rho/\rho_\oplus)$) by planetary class, compute surface `temperature_c` from stellar spectral luminosity ($L/L_\odot$), orbital radius ($T_{\text{eq}} \propto L^{1/4}/\sqrt{r}$), Bond albedo, and atmospheric greenhouse forcing, assign realistic chemical composition and pressure strings for `atmosphere`, and compute `habitability` from surface solidity, breathable/pressurized atmosphere, temperature, gravity, and orbital hazards while preserving the exact RNG call count in `GalaxyGenerator._generate_bodies`. Backfill legacy saves deterministically in `SimulationEngine._bootstrap_frontier`.
  2. Update `SimulationEngine.start_travel()` (`voidfarer/engine.py`) to compute true 2D Euclidean orbital distance $d_{\text{AU}} = \sqrt{(r_2\cos\theta_2 - r_1\cos\theta_1)^2 + (r_2\sin\theta_2 - r_1\sin\theta_1)^2}$ between origin and destination bodies, scale sublight `duration_ticks` proportionally to $d_{\text{AU}}$ and reactor engine power allocation (`speed_au_per_tick`), and automatically unpause `TimeState` when initiating transit so ticks advance across the transit window.
  3. Update `voidfarer/static/app.js` and `voidfarer/static/index.html` to display `#targetHabitability` and true 2D Euclidean distance in the Target Inspector, hide the static orbiting `VF-FLAGSHIP` marker while `ship.travel` is active, and synchronize `drawTravelAnimation()` continuously with `state.ship.travel` (`started_tick` to `arrival_tick` plus smooth intra-tick interpolation and trajectory vector line) so the transit animation never terminates until orbital capture completes on `arrival_tick`.
- **Consequences**: Planetary telemetry (`gravity`, `atmosphere`, `temperature_c`, `radius_km`, `habitability`) is astrophysically self-consistent across all 15 star systems and legacy saves, sublight transit duration reflects real 2D orbital geometry and engine power, and the flagship transit animation glides continuously across the background radar for the full tick duration of the voyage.

### ADR-023: Decluttered Sleek Map HUD: Transparent On-Map Radar Title, Collapsible Right-Expanding Left Terminal Drawer, and Boxless Lower-Right Tactical Flight Log (G-005)
- **Date**: 2026-10-19
- **Status**: Accepted
- **Context**: While the NAV-Radar orbital map was successfully converted into the background layer under ADR-021, bulky UI boxes still occluded critical radar space. Specifically: (1) `#radarTitle` and its containing header sat in an opaque panel box directly over the center radar; (2) the left terminal deck (`#panelLeft`) stayed permanently open with market/arsenal tables taking up wide horizontal space; (3) the lower-right Tactical Flight Log (`#panelRight` / `#logPanel`) sat inside double background-box frames (`deck-panel` and `sub-panel`) with blur filters and borders; and (4) center target/power cards occupied excessive vertical area when idle.
- **Decision**:
  1. Make the NAV-radar header (`.nav-panel > .panel-header`) boxless and transparent (`background: transparent`, `border: none`, `backdrop-filter: none`, `pointer-events: none`, `opacity: 0.45`), floating subtly as a sleek watermark title directly over the radar below the top controls without blocking clicks.
  2. Implement a collapsible right-expanding terminal drawer on the left (`#panelLeft`): by default (and whenever toggled closed), `#panelLeft` takes the `.drawer-collapsed` state, hiding `.terminal-content-stack` (`display: none`) and rendering only the slim vertical button rail (`COMMERCE`, `ARSENAL`, `FLEET`, etc.). Clicking any tab button expands `.terminal-content-stack` to the right beside the rail; clicking the active tab button again toggles the drawer closed.
  3. Strip background boxes, borders, and backdrop filters from `.panel-right`, `#logPanel`, and `.flight-log-stream` (`background: transparent`, `border: none`, `box-shadow: none`), rendering the Tactical Flight Log and its HIDE/CLEAR controls directly on top of the orbital map with crisp readable text-shadows.
  4. Keep `.nav-target-card` and `.reactor-panel` compact and anchored at the bottom of the viewport so the orbital center and star trajectories remain completely unobstructed.
  5. Add unit and structural regression tests in `tests/test_cockpit_layout.py` ensuring G-001 through G-005 invariants remain permanently green.
- **Consequences**: The orbital background radar is completely clear and visually dominant. Terminal content only expands when commanded and tucks neatly away into a slim left rail, the radar title floats as an unobtrusive semi-transparent watermark, and flight telemetry streams directly over space without boxed borders.

### ADR-024: Expandable Reactor Power Routing Panel, Top-Bar Action/Vitals Reordering, and Equal-Sized Vital Telemetry Cards (G-006)
- **Date**: 2026-10-19
- **Status**: Accepted
- **Context**: The user requested three specific cockpit HUD improvements: (1) making the reactor power distribution panel expandable/collapsible with a HIDE/SHOW toggle button identical to the Tactical Flight Log, allowing the player to collapse power routing controls to reclaim bottom-center radar space; (2) swapping the position of the vital telemetry row (`.vitals-row`) with the quick action and sound controls (`.hud-top-actions`) so controls follow Brand -> Actions -> Vitals -> Chrono Clock; and (3) standardizing all vital telemetry stat cards (`vitalHullCard`, `vitalShieldCard`, `vitalFuelCard`, `vitalCreditsCard`, `vitalStreakCard`, `vitalMasteryCard`) to identical width and height dimensions for visual symmetry.
- **Decision**:
  1. Add `#btnToggleReactor` to `#panelReactor > .panel-header`, wire it in `voidfarer/static/app.js` to toggle the `.reactor-collapsed` class on `#panelReactor`, and hide `.power-matrix` and `.power-action-row` when `.reactor-collapsed` is active (`display: none`).
  2. In `voidfarer/static/index.html`, swap the DOM order of `.hud-top-actions` and `.vitals-row` within `#hudTopBar` while ensuring `#hudTimeDeck` remains the pinned right-most child.
  3. In `voidfarer/static/style.css`, standardize `.vital-card` with equal flex distribution (`flex: 1 1 0`), identical height (`height: 52px; box-sizing: border-box;`), identical min-width (`128px`), and vertical flex alignment (`display: flex; flex-direction: column; justify-content: space-between;`), so all 6 stat cards have the exact same rectangular dimensions across both full and compact viewports.
  4. Add structural regression tests in `tests/test_cockpit_layout.py` (`TestExpandableReactorAndVitalsAlignment`) verifying the reactor toggle wiring, `.reactor-collapsed` CSS rule, topbar child ordering, and equal-dimension CSS rules.
- **Consequences**: The player can collapse the reactor matrix at will to maximize radar visibility, the top bar follows a cleaner workflow hierarchy, and all vital status cards are symmetrically aligned with matching widths and heights.

### ADR-025: Shared 2D Polar Distance Calculation for Orbit and Transit, Single-Line Top-Bar Vitals/Chrono Symmetry (G-007), and Dynamic Demographic Population Mechanics
- **Date**: 2026-10-19
- **Status**: Accepted
- **Context**: The user requested three complementary enhancements: (1) ensuring "ENTER ORBIT" and "SUBLIGHT TRANSIT" adhere strictly to the exact same 2D polar Euclidean distance calculation $d_{\text{AU}} = \sqrt{(r_2\cos\theta_2 - r_1\cos\theta_1)^2 + (r_2\sin\theta_2 - r_1\sin\theta_1)^2}$ across the simulation engine, flight log, and Target Card; (2) guaranteeing that all top-bar vital stat cards (`vitalHullCard`, `vitalShieldCard`, etc.) and the Chrono date box (`hudTimeDeck`) have the exact same height (`52px; box-sizing: border-box;`) and remain strictly on the same non-wrapping line (`flex-wrap: nowrap;`); and (3) implementing dynamic planetary population mechanics, including tick-based demographic growth scaling with habitability, demographic colony tiers (`Outpost`, `Colony`, `Settlement`, `Metropolis`, `Mega-Ecumenopolis`), and population-scaled market consumption.
- **Decision**:
  1. Add `compute_body_distance_au(target_body, origin_body=None)` in `voidfarer/engine.py` and consume it in both `orbit(body_id)` and `start_travel(body_id, mode)`. Update `orbit` flight logging and returned messages to report the true 2D Euclidean distance, and update `updateTargetCard()` in `voidfarer/static/app.js` so both the "ENTER ORBIT" and "SUBLIGHT TRANSIT" buttons display and use identical distance calculations.
  2. In `voidfarer/static/style.css`, enforce `flex-wrap: nowrap; overflow-x: auto;` on `.hud-topbar` and `.vitals-row`, and set `height: 52px; box-sizing: border-box;` on `.hud-time-deck` matching `.vital-card`, ensuring all stat cards and the chrono deck sit on a unified single line with matching vertical dimension.
  3. Add `step_population_dynamics(body, num_ticks)` in `voidfarer/galaxy.py` and `get_colony_tier(population)`. On simulation `tick()`, advance inhabited body populations based on habitability ($g \approx 0.00025 \times (\text{habitability}/100)$) or life-support station steady migration, and integrate population-tier reporting into the planet inspector and CLI status.
  4. Write failing-first tests in `tests/test_cockpit_layout.py` and `tests/test_galaxy.py` to pin the distance parity, single-line CSS, and population demographic simulation.
- **Consequences**: Navigation distances are astrophysically uniform across immediate orbital capture and timed transit, the cockpit top bar displays a clean, symmetrical, single-line layout matching the chrono clock, and star systems feature living planetary populations that evolve dynamically over time.




