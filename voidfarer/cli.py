"""Command-line interface and interactive terminal REPL for VoidFarer."""

from __future__ import annotations

import argparse
import os
import sys
import threading
from pathlib import Path
from typing import Sequence

# Enable UTF-8 streams on Windows consoles
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (ValueError, OSError):  # hygiene: allow non-reconfigurable stdio streams in test harnesses
        pass

from voidfarer.engine import SimulationEngine
from voidfarer.factions import (
    CANONICAL_CORPORATIONS,
    CANONICAL_FACTIONS,
    calculate_faction_market_modifier,
    get_faction_id_from_name,
    get_faction_standing_tier,
)
from voidfarer.galaxy import COMMODITY_MAP
from voidfarer.frontier import MERCENARY_CATALOG
from voidfarer.retention import (
    PILOT_TALENTS,
    calculate_passive_multipliers,
)
from voidfarer.server import BackgroundServer, run_server, start_background_server
from voidfarer.storage import StorageManager
from voidfarer.economy import (
    calculate_dynamic_market_quote,
    get_galactic_trade_routes,
)
from voidfarer.inventory import (
    ITEM_CATALOG,
    get_inventory_manifest,
    get_item_info,
)
from voidfarer.upgrades import (
    CATALOG_CHASSIS,
    CATALOG_DRONE_TEMPLATES,
    CATALOG_UPGRADES,
    CHASSIS_MAP,
    UPGRADE_MAP,
    get_available_chassis,
    get_sell_value,
)

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
WHITE = "\033[97m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

BANNER = f"""{CYAN}{BOLD}
__      __ _____  _____  _____   ______        _____   ______  _____  
\\ \\    / // ___ \\|_   _||  __ \\ |  ____/\\     |  __ \\ |  ____||  __ \\ 
 \\ \\  / /| |   | | | |  | |  | || |__ /  \\    | |__) || |__   | |__) |
  \\ \\/ / | |   | | | |  | |  | ||  __/ /\\ \\   |  _  / |  __|  |  _  / 
   \\  /  | |___| |_| |_ | |__| || | / ____ \\  | | \\ \\ | |____ | | \\ \\ 
    \\/    \\_____/|_____||_____/ |_|/_/    \\_\\ |_|  \\_\\|______||_|  \\_\\
{RESET}
{DIM}Autonomous Deep-Space Fleet & Procedural Galaxy Simulator v0.2.0{RESET}
"""


def _get_engine(storage_dir: Path | None = None) -> tuple[SimulationEngine, StorageManager]:
    """Initialize or restore simulation engine from disk."""
    if storage_dir is None:
        home = Path(os.environ.get("LOCALAPPDATA", Path.home()))
        storage = StorageManager(home / ".voidfarer")
    elif storage_dir.suffix.lower() == ".json":
        storage = StorageManager(storage_dir.parent)
        storage.save_file = storage_dir
    else:
        storage = StorageManager(storage_dir)
    saved_state = storage.load()
    engine = SimulationEngine(state=saved_state)
    return engine, storage


def _bar(current: int, maximum: int, length: int = 20, color: str = GREEN) -> str:
    """Generate ANSI filled progress bar."""
    ratio = max(0.0, min(1.0, current / maximum if maximum > 0 else 0.0))
    filled = int(ratio * length)
    empty = length - filled
    return f"{color}{'█' * filled}{DIM}{'░' * empty}{RESET} {current}/{maximum}"


def cmd_status(engine: SimulationEngine) -> int:
    """Display current flagship telemetry, fleet roster, and star system status."""
    ship = engine.state.ship
    cur_sys = engine.current_system
    body = engine.orbiting_body

    print(BANNER)
    print(f"{BOLD}╔════ COMMANDER DOSSIER ══════════════════════════════════════════════╗{RESET}")
    print(f"║ Commander: {CYAN}{ship.commander_name:<16}{RESET} Callsign: {YELLOW}{ship.callsign:<16}{RESET} Class: {ship.ship_class:<12} ║")
    t = engine.state.time
    print(f"║ Date:      {YELLOW}{t.current_date:<10}{RESET}  (Tick #{t.tick:<5})   Temporal Clock: {GREEN if not t.is_paused else RED}{t.time_scale:<10}{RESET}       ║")
    print(f"║ Credits:   {YELLOW}{ship.credits:>8} cr{RESET}       Cargo:    {sum(ship.cargo.values()):>2}/{ship.cargo_capacity:<2} units                     ║")
    print(f"╠════ VITAL TELEMETRY ════════════════════════════════════════════════╣{RESET}")
    streak_mult = 1.0 + min(1.5, (ship.streak - 1) * 0.15)
    print(f"║ Streak:    {RED}🔥 {ship.streak} jumps (x{streak_mult:.2f}){RESET}   Mastery:  {YELLOW}★ Lvl {ship.mastery.level} [{ship.mastery.xp}/{ship.mastery.next_level_xp} XP]{RESET}           ║")
    print(f"║ Hull:      {_bar(ship.hull, ship.max_hull, 24, RED if ship.hull < 30 else GREEN)}                      ║")
    print(f"║ Shields:   {_bar(ship.shield, ship.max_shield, 24, BLUE)}                      ║")
    print(f"║ Fuel:      {_bar(ship.fuel, ship.max_fuel, 24, YELLOW)}                      ║")
    print(f"╠════ REACTOR POWER ROUTING ══════════════════════════════════════════╣{RESET}")
    p = ship.power
    print(f"║ Engines: {CYAN}{p.engines:>3}%{RESET}   Shields: {BLUE}{p.shields:>3}%{RESET}   Sensors: {MAGENTA}{p.sensors:>3}%{RESET}   Weapons: {RED}{p.weapons:>3}%{RESET}  (Total: {p.engines+p.shields+p.sensors+p.weapons:>3}%)║")

    # Hardware upgrades summary
    upg_str = ", ".join(ship.upgrades) if ship.upgrades else "Standard Baseline"
    print(f"╠════ INSTALLED HARDWARE MODULES ═════════════════════════════════════╣{RESET}")
    print(f"║ {CYAN}{upg_str:<67}{RESET} ║")

    # Active contracts summary
    ready_cnt = sum(1 for c in ship.active_contracts if c.completed)
    contract_note = f"{len(ship.active_contracts)} active assignments ({ready_cnt} ready to claim!)" if ready_cnt > 0 else f"{len(ship.active_contracts)} active bounty contracts"
    print(f"╠════ SECTOR CONTRACTS & BOUNTIES ════════════════════════════════════╣{RESET}")
    print(f"║ {YELLOW}{contract_note:<67}{RESET} ║")

    # Fleet summary
    num_drones = len(ship.fleet_drones)
    drone_summary = f"{num_drones} active drones / escorts deployed" if num_drones > 0 else "No active drones"
    print(f"╠════ AUTONOMOUS FLEET ASSETS ════════════════════════════════════════╣{RESET}")
    print(f"║ {GREEN}{drone_summary:<67}{RESET} ║")

    # Cadet Academy & Story progression
    tut = ship.tutorial
    if tut.is_active:
        step = tut.current_step
        tut_msg = f"Milestone {tut.current_step_index + 1}/{len(tut.steps)}: {step.title} -> {step.hint}"
        print(f"╠════ CADET FLIGHT ACADEMY ═══════════════════════════════════════════╣{RESET}")
        print(f"║ {YELLOW}{tut_msg[:67]:<67}{RESET} ║")
    elif tut.completed:
        tut_msg = "🎓 Graduated: Cadet Honor Wings equipped (+1,500 cr, +400 XP)"
        print(f"╠════ CADET FLIGHT ACADEMY ═══════════════════════════════════════════╣{RESET}")
        print(f"║ {GREEN}{tut_msg[:67]:<67}{RESET} ║")

    story = ship.story
    if story.completed:
        chap_msg = "⭐ Campaign Concluded: The Precursor Cipher [ALL ACTS RESOLVED]"
    else:
        chap = story.current_chapter
        chap_status = "COMPLETED" if chap.completed else f"TARGET: {chap.target_system_id}"
        chap_msg = f"Act {story.active_act}: {chap.title} [{chap_status}]"
    print(f"╠════ THE PRECURSOR CIPHER (STORY) ════════════════════════════════════╣{RESET}")
    print(f"║ {MAGENTA}{chap_msg[:67]:<67}{RESET} ║")

    print(f"╠════ NAVIGATION COORDINATES ═════════════════════════════════════════╣{RESET}")
    print(f"║ System:    {CYAN}{cur_sys.name:<22}{RESET} Faction:  {cur_sys.faction:<22} ║")
    corp_str = f"Corp HQ:   {cur_sys.dominant_corp.replace('_', ' ').title():<22}" if cur_sys.dominant_corp else f"Corridors: {', '.join(cur_sys.connections)[:22]:<22}"
    print(f"║ Security:  {GREEN if cur_sys.security > 0.5 else RED}{cur_sys.security * 100:>5.1f}% [{('HIGH' if cur_sys.security > 0.7 else ('MED' if cur_sys.security > 0.3 else 'ANARCHY'))}]{RESET}       {corp_str} ║")
    orb_name = f"{body.name} [{body.body_type}]" if body else "Deep Space Transit"
    print(f"║ Orbit:     {orb_name:<57} ║")
    print(f"╚═════════════════════════════════════════════════════════════════════╝{RESET}")

    if engine.state.active_combat:
        c = engine.state.active_combat
        faction_badge = f" [{c.faction_id}]" if c.faction_id else ""
        print(f"\n{RED}{BOLD}⚔️  COMBAT INTERCEPT: {c.enemy_name.upper()} [{c.enemy_class.upper()}]{faction_badge}{RESET}")
        if c.enemy_max_shield > 0:
            print(f"   Enemy Shield: {_bar(c.enemy_shield, c.enemy_max_shield, 20, CYAN)}")
        print(f"   Enemy Hull:   {_bar(c.enemy_hull, c.enemy_max_hull, 20, RED)}")
        if c.telegraphed_action:
            print(f"   Telemetry:    {YELLOW}⚠ {c.telegraphed_action}{RESET}")
        print(f"   Hostile AI:   {CYAN}{c.ai_profile.upper()}{RESET} intent={c.enemy_intent.upper()}")
        if ship.tactical_combo > 0:
            crit_alert = f" {YELLOW}{BOLD}(CRITICAL OVERCHARGE READY!){RESET}" if ship.tactical_combo >= 2 else ""
            print(f"   Tactical Combo: {YELLOW}{BOLD}⚡ x{ship.tactical_combo}{crit_alert}{RESET}")
        print(f"   Tactical Options: {BOLD}combat fire{RESET} | {BOLD}combat drone{RESET} | {BOLD}combat target{RESET} | {BOLD}combat absorb{RESET} | {BOLD}combat evade{RESET} | {BOLD}combat flee{RESET}")

    elif engine.state.active_anomaly:
        anom = engine.state.active_anomaly
        print(f"\n{RED}{BOLD}⚠️  PROXIMITY ALERT: {anom.title}{RESET}")
        print(f"{DIM}{anom.description}{RESET}")
        print(f"{YELLOW}Resolution Choices:{RESET}")
        for ch in anom.choices:
            req = f"[{ch.required_power.upper()} >= {ch.min_power_threshold}%]" if ch.required_power != "none" else "[No Check]"
            print(f"  • {BOLD}{ch.choice_id}{RESET}: {ch.text} {DIM}{req}{RESET}")

    return 0


def cmd_time(engine: SimulationEngine, storage: StorageManager, argv: list[str]) -> int:
    """Manage simulation cosmic time, ticks, and speed controls."""
    if not argv or argv[0].lower() in ("status", "info"):
        t = engine.state.time
        print(f"\n{BOLD}{CYAN}╔════ COSMIC CHRONOMETRY & TEMPORAL MATRIX ════════════════════════════╗{RESET}")
        print(f"║ Date:           {YELLOW}{t.current_date}{RESET}               Epoch Tick:     {CYAN}#{t.tick}{RESET}")
        state_str = "RUNNING" if not t.is_paused else "PAUSED"
        color = GREEN if not t.is_paused else RED
        print(f"║ Temporal Speed: {color}{t.time_scale:<18}{RESET} Temporal State: {color}{state_str:<10}{RESET}")
        print(f"║ Stardate:       {t.stardate:.2f}               Elapsed Time:   {t.elapsed_days:.2f} standard days")
        print(f"╠════ TEMPORAL COMMANDS ═══════════════════════════════════════════════╣{RESET}")
        print(f"║  • {CYAN}time pause{RESET}                 Freeze temporal progression (0x)")
        print(f"║  • {CYAN}time resume{RESET}                Resume normal temporal flow (1.0x)")
        print(f"║  • {CYAN}time speed <x>{RESET}             Set speed multiplier (0.0 to 10.0x)")
        print(f"║  • {CYAN}time step [n]{RESET}              Advance simulation by n ticks immediately")
        print(f"╚══════════════════════════════════════════════════════════════════════╝{RESET}\n")
        return 0

    sub = argv[0].lower()
    if sub == "pause":
        ok, msg = engine.pause_time()
        print((GREEN if ok else RED) + msg + RESET)
        storage.save(engine.state)
        return 0

    elif sub in ("resume", "play"):
        ok, msg = engine.resume_time()
        print((GREEN if ok else RED) + msg + RESET)
        storage.save(engine.state)
        return 0

    elif sub == "speed":
        if len(argv) < 2:
            print(f"{RED}Usage:{RESET} time speed <0|1|2|5|10>")
            return 1
        try:
            sp = float(argv[1])
        except ValueError:
            print(f"{RED}Invalid speed factor '{argv[1]}'. Must be a numeric value.{RESET}")
            return 1
        ok, msg = engine.set_time_speed(sp)
        print((GREEN if ok else RED) + msg + RESET)
        storage.save(engine.state)
        return 0

    elif sub in ("step", "wait", "tick"):
        ticks = 1
        if len(argv) >= 2:
            try:
                ticks = max(1, int(argv[1]))
            except ValueError:
                print(f"{RED}Invalid tick count '{argv[1]}'. Must be an integer.{RESET}")
                return 1
        ok, msg, summary = engine.step_time(ticks)
        print((GREEN if ok else RED) + msg + RESET)
        if summary.get("shield_recharged", 0) > 0:
            print(f"{CYAN}⚡ Deflector shields restored +{summary['shield_recharged']} capacitance over time.{RESET}")
        storage.save(engine.state)
        return 0

    print(f"{RED}Unknown time command '{argv[0]}'. Use: time [status|pause|resume|speed <x>|step <n>]{RESET}")
    return 1


def cmd_chart(engine: SimulationEngine) -> int:
    """Print galaxy starmap and celestial bodies within current system."""
    cur_sys = engine.current_system
    print(f"\n{BOLD}{CYAN}=== GALAXY SECTOR HYPERLANE NETWORK ==={RESET}")
    for sid, s in engine.state.systems.items():
        marker = f"{YELLOW}▶ [FLAGSHIP]{RESET}" if sid == cur_sys.id else ("  [VISITED] " if sid in engine.state.visited_systems else "  [UNSEEN]  ")
        conns = ", ".join(s.connections)
        sec = f"{GREEN}SEC {s.security:.1f}{RESET}" if s.security > 0.5 else f"{RED}SEC {s.security:.1f}{RESET}"
        print(f"{marker} {BOLD}{s.name:<18}{RESET} ({sid}) | {sec} | Links: {conns}")

    print(f"\n{BOLD}{CYAN}=== CELESTIAL BODIES IN {cur_sys.name.upper()} ==={RESET}")
    for b in cur_sys.bodies:
        is_orb = " [IN ORBIT]" if engine.state.ship.orbiting_body_id == b.id else ""
        dock = f"{GREEN}[DOCKABLE]{RESET}" if b.station_dockable else f"{DIM}[NO DOCK]{RESET}"
        scan = f"{CYAN}[SCANNED]{RESET}" if b.scan_completed else f"{YELLOW}[UNSCANNED]{RESET}"
        print(f"  • {BOLD}{b.name:<24}{RESET} ({b.id}) | {b.body_type:<15} | Dist: {b.orbit_radius:.2f} AU | {dock} {scan}{is_orb}")

    return 0


def cmd_market(engine: SimulationEngine) -> int:
    """Display commodity prices and supply/demand at the current orbital body."""
    body = engine.orbiting_body
    if not body or not body.station_dockable:
        print(f"{RED}Error:{RESET} Ship must establish orbit around a station or colony to access trade network.")
        print(f"{YELLOW}Fix:{RESET} Run `voidfarer orbit <body_id>` to enter orbit first.")
        return 1

    quotes = [
        calculate_dynamic_market_quote(engine.current_system, body, comm, engine.state.economy)
        for comm in COMMODITY_MAP.values()
    ]
    sys_faction_id = get_faction_id_from_name(engine.current_system.faction)
    faction_mod = calculate_faction_market_modifier(
        sys_faction_id, engine.state.ship.faction_standings.get(sys_faction_id, 0)
    )
    print(f"\n{BOLD}{CYAN}=== LOCAL COMMODITY EXCHANGE: {body.name.upper()} ==={RESET}")
    print(f"Market Archetype: {BOLD}{body.market_archetype.upper()}{RESET} | Credits: {YELLOW}{engine.state.ship.credits} cr{RESET} | Trade Modifier: {BOLD}x{faction_mod:.2f}{RESET}")
    print(f"{'-' * 70}")
    print(f"{'COMMODITY':<22} {'BUY':>8} {'SELL':>8} {'SUPPLY':>8} {'DEMAND':>8} {'HOLD':>8}")
    print(f"{'-' * 70}")
    cargo = engine.state.ship.cargo
    for q in quotes:
        hold_qty = cargo.get(q.commodity_id, 0)
        effective_buy = int(q.buy_price * faction_mod)
        print(f"{q.name:<22} {GREEN}{effective_buy:>6} cr{RESET} {YELLOW}{q.sell_price:>6} cr{RESET} {q.supply:>8} {q.demand:>8} {BOLD}{hold_qty:>8}{RESET}")
    print(f"{'-' * 70}")
    return 0


def cmd_economy(engine: SimulationEngine) -> int:
    """Display galactic macroeconomic conditions, active events, and lucrative trade routes."""
    econ = engine.state.economy
    print(f"\n{BOLD}{CYAN}=== GALACTIC ECONOMY & MACROECONOMIC INTELLIGENCE ==={RESET}")
    print(f"Simulation Tick: {YELLOW}#{engine.state.time.tick}{RESET} | Known Systems: {CYAN}{len(engine.state.systems)}{RESET}\n")

    print(f"{BOLD}Active Macroeconomic Shocks & Galactic News:{RESET}")
    if not econ.active_events:
        print(f"  {DIM}Galaxy is currently in economic equilibrium. No major shortages or crises reported.{RESET}")
    else:
        for evt in econ.active_events:
            sys_name = engine.state.systems[evt.system_id].name if evt.system_id in engine.state.systems else evt.system_id
            badge = f"{RED}[CRISIS]{RESET}" if evt.price_multiplier > 1.2 else f"{GREEN}[BOOM]{RESET}"
            pct = int((evt.price_multiplier - 1.0) * 100)
            sign = f"+{pct}%" if pct > 0 else f"{pct}%"
            print(f"  • {badge} {BOLD}{evt.title}{RESET} ({sys_name})")
            print(f"    Impact: {YELLOW}{evt.commodity_id.upper()}{RESET} prices {YELLOW}{sign}{RESET} | Clocks: {CYAN}{evt.duration_ticks} ticks remaining{RESET}")
            print(f"    {DIM}{evt.description}{RESET}\n")

    print(f"{BOLD}Top Interstellar Trade Routes (Arbitrage Opportunities):{RESET}")
    routes = get_galactic_trade_routes(engine.state.systems, econ)
    if not routes:
        print(f"  {DIM}No trade routes found.{RESET}")
    else:
        print(f"  {'COMMODITY':<20} {'BUY FROM':<22} {'SELL TO':<22} {'PROFIT/U':>10} {'MARGIN':>8}")
        print(f"  {'-' * 86}")
        for r in routes[:6]:
            print(f"  {BOLD}{r['commodity_name']:<20}{RESET} {GREEN}{r['buy_system_name']} ({r['buy_price']} cr){RESET:<22} {YELLOW}{r['sell_system_name']} ({r['sell_price']} cr){RESET:<22} {GREEN}+{r['profit_per_unit']} cr{RESET:>10} {CYAN}{r['profit_margin_pct']}%{RESET:>8}")
        print(f"  {'-' * 86}")
    return 0


def cmd_inventory(engine: SimulationEngine, storage: StorageManager, parts: list[str]) -> int:
    """Display and manage ship cargo manifest, usable consumables, and hold capacity."""
    ship = engine.state.ship
    if len(parts) == 1 or parts[1].lower() in ("list", "status", "manifest"):
        print(f"\n{BOLD}{CYAN}=== FLAGSHIP INVENTORY & CARGO MANIFEST ==={RESET}")
        manifest = get_inventory_manifest(ship.cargo)
        used_vol = sum(item['total_volume'] for item in manifest)
        print(f"Hold Capacity: {_bar(used_vol, ship.cargo_capacity, 24, YELLOW if used_vol < ship.cargo_capacity else RED)} units")
        print(f"Credits:       {YELLOW}{ship.credits} cr{RESET}\n")

        if not manifest:
            print(f"{DIM}Cargo hold is currently empty.{RESET}")
            print(f"Purchase commodities at orbital markets (`market`), or buy consumables (`inventory buy`).")
            return 0

        print(f"{'ID':<24} {'NAME':<24} {'CATEGORY':<14} {'QTY':>6} {'TOTAL VOL':>10} {'USABLE':<8}")
        print(f"{'-' * 90}")
        for item in manifest:
            usable_str = f"{GREEN}YES{RESET}" if item['is_usable'] else f"{DIM}NO{RESET}"
            print(f"{item['id']:<24} {BOLD}{item['name']:<24}{RESET} {CYAN}{item['category']:<14}{RESET} {item['quantity']:>6} {item['total_volume']:>10} {usable_str:<8}")
            print(f"  {DIM}└─ {item['description']}{RESET}")
        print(f"{'-' * 90}")
        print(f"Subcommands: {BOLD}inventory buy <item_id> [qty]{RESET} | {BOLD}inventory use <item_id>{RESET} | {BOLD}inventory jettison <item_id> <quantity>{RESET}")
        return 0

    sub = parts[1].lower()
    if sub == "buy":
        if len(parts) < 3:
            consumables = ", ".join(sorted(k for k, v in ITEM_CATALOG.items() if v.category == "consumable"))
            print(f"{RED}Usage:{RESET} inventory buy <item_id> [quantity]")
            print(f"{DIM}Available consumables:{RESET} {consumables}")
            return 1
        item_id = parts[2].lower()
        try:
            qty = int(parts[3]) if len(parts) > 3 else 1
        except ValueError:
            print(f"{RED}Error:{RESET} Quantity must be an integer.")
            return 1
        ok, msg = engine.buy_item(item_id, qty)
        print((GREEN if ok else RED) + msg + RESET)
        if ok:
            storage.save(engine.state)
        return 0 if ok else 1

    if sub == "use":
        if len(parts) < 3:
            print(f"{RED}Usage:{RESET} inventory use <item_id>")
            return 1
        item_id = parts[2].lower()
        ok, msg = engine.use_item(item_id)
        print((GREEN if ok else RED) + msg + RESET)
        if ok:
            storage.save(engine.state)
        return 0 if ok else 1

    elif sub in ("jettison", "drop", "discard"):
        if len(parts) < 3:
            print(f"{RED}Usage:{RESET} inventory jettison <item_id> [quantity]")
            return 1
        item_id = parts[2].lower()
        try:
            qty = int(parts[3]) if len(parts) > 3 else 1
        except ValueError:
            print(f"{RED}Error:{RESET} Quantity must be an integer.")
            return 1
        ok, msg = engine.jettison_cargo(item_id, qty)
        print((GREEN if ok else RED) + msg + RESET)
        if ok:
            storage.save(engine.state)
        return 0 if ok else 1

    print(f"{RED}Unknown inventory command '{sub}'. Options: list, buy <id> [qty], use <id>, jettison <id> [qty].{RESET}")
    return 1


def cmd_shipyard(engine: SimulationEngine, storage: StorageManager, parts: list[str]) -> int:
    """Orbital shipyard: inspect ship chassis upgrades, purchase vessels, and sell modules."""
    ship = engine.state.ship
    body = engine.orbiting_body
    if not body or not body.station_dockable:
        print(f"{RED}Error:{RESET} Ship must dock at an orbital station or colony to access shipyard drydocks.")
        return 1

    if len(parts) == 1 or parts[1].lower() in ("list", "status", "catalog"):
        print(f"\n{BOLD}{CYAN}=== ORBITAL SHIPYARD & CHASSIS SHOWROOM ==={RESET}")
        print(f"Station: {BOLD}{body.name}{RESET} | Commander Vault: {YELLOW}{ship.credits} cr{RESET}")
        print(f"Current Class: {GREEN}{ship.ship_class}{RESET} ({ship.hull}/{ship.max_hull} Hull, {ship.shield}/{ship.max_shield} Shield, {ship.cargo_capacity} Cargo)\n")

        print(f"{BOLD}Available Ship Chassis for Purchase:{RESET}")
        print(f"{'ID':<20} {'NAME':<28} {'CLASS':<22} {'COST':>8} {'HULL':>6} {'SHD':>6} {'CARGO':>6}")
        print(f"{'-' * 100}")
        for c in CATALOG_CHASSIS:
            is_cur = c.ship_class == ship.ship_class
            marker = f"{GREEN}[CURRENT]{RESET}" if is_cur else f"{YELLOW}{c.cost} cr{RESET}"
            print(f"{c.id:<20} {BOLD}{c.name:<28}{RESET} {CYAN}{c.ship_class:<22}{RESET} {marker:>8} {c.max_hull:>6} {c.max_shield:>6} {c.cargo_capacity:>6}")
            print(f"  {DIM}Perk: {c.specialty_perk} - {c.description}{RESET}")
        print(f"{'-' * 100}")
        print(f"Subcommands: {BOLD}shipyard chassis <id>{RESET} | {BOLD}shipyard sell <slot>{RESET} | {BOLD}upgrades{RESET}")
        return 0

    sub = parts[1].lower()
    if sub in ("chassis", "buy_chassis"):
        if len(parts) < 3:
            print(f"{RED}Usage:{RESET} shipyard chassis <chassis_id>")
            return 1
        cid = parts[2].lower()
        ok, msg = engine.buy_ship_chassis(cid)
        print((GREEN if ok else RED) + msg + RESET)
        if ok:
            storage.save(engine.state)
        return 0 if ok else 1

    elif sub in ("sell", "uninstall"):
        if len(parts) < 3:
            print(f"{RED}Usage:{RESET} shipyard sell <slot>")
            return 1
        slot = parts[2].lower()
        ok, msg = engine.sell_upgrade(slot)
        print((GREEN if ok else RED) + msg + RESET)
        if ok:
            storage.save(engine.state)
        return 0 if ok else 1

    print(f"{RED}Unknown shipyard command '{sub}'. Options: catalog, chassis <id>, sell <slot>.{RESET}")
    return 1


def cmd_fleet(engine: SimulationEngine, storage: StorageManager, parts: list[str]) -> int:
    """Manage autonomous fleet drones, mining escorts, and harvest yields."""
    if len(parts) == 1:
        # Show fleet roster
        drones = engine.state.ship.fleet_drones
        print(f"\n{BOLD}{CYAN}=== AUTONOMOUS FLEET COMMAND ROSTER ==={RESET}")
        if not drones:
            print(f"{DIM}No fleet drones currently commissioned.{RESET}")
            print(f"Purchase drones at orbital drydocks using: {BOLD}fleet buy <mining|scout|combat_escort>{RESET}")
            return 0

        print(f"{'ID':<18} {'NAME':<24} {'TYPE':<14} {'SYSTEM':<16} {'STATUS':<12} {'YIELD':<12}")
        print(f"{'-' * 98}")
        for d in drones:
            yield_str = f"+{d.cargo_accumulated} ore / +{d.credits_accumulated} cr"
            print(f"{d.id:<18} {BOLD}{d.name:<24}{RESET} {CYAN}{d.drone_type:<14}{RESET} {d.assigned_system_id:<16} {GREEN}{d.status:<12}{RESET} {YELLOW}{yield_str:<12}{RESET}")
        print(f"{'-' * 98}")
        print(f"Subcommands: {BOLD}fleet harvest{RESET} | {BOLD}fleet buy <type>{RESET} | {BOLD}fleet deploy <id> <system>{RESET}")
        return 0

    sub = parts[1].lower()
    if sub in ("harvest", "collect"):
        drone_id = parts[2] if len(parts) > 2 else None
        ok, msg, _ = engine.collect_drone_yield(drone_id)
        print((GREEN if ok else RED) + msg + RESET)
        storage.save(engine.state)
        return 0 if ok else 1

    elif sub == "buy":
        if len(parts) < 3:
            print(f"{RED}Usage:{RESET} fleet buy <mining|scout|combat_escort> [assigned_system]")
            return 1
        d_type = parts[2].lower()
        sys_id = parts[3] if len(parts) > 3 else None
        ok, msg = engine.buy_drone(d_type, sys_id)
        print((GREEN if ok else RED) + msg + RESET)
        storage.save(engine.state)
        return 0 if ok else 1

    elif sub == "deploy":
        if len(parts) < 4:
            print(f"{RED}Usage:{RESET} fleet deploy <drone_id> <target_system>")
            return 1
        ok, msg = engine.deploy_drone(parts[2], parts[3])
        print((GREEN if ok else RED) + msg + RESET)
        storage.save(engine.state)
        return 0 if ok else 1

    else:
        print(f"{RED}Unknown fleet command '{sub}'. Options: list, harvest, buy, deploy.{RESET}")
        return 1




def cmd_quests(engine: SimulationEngine) -> int:
    print(f"\n{BOLD}{CYAN}=== QUEST PANEL ==={RESET}")
    for quest in engine.get_quests():
        print(f"{BOLD}{quest['title']}{RESET} [{quest['kind'].upper()}]")
        print(f"  {quest['description']}")
        print(f"  Progress: {quest['progress']}/{quest['target_count']} // Reward: {quest['reward']}")
    print()
    return 0


def cmd_ai(engine: SimulationEngine, storage: StorageManager, parts: list[str]) -> int:
    action = parts[1] if len(parts) > 1 else "list"
    if action == "list":
        print(f"\n{BOLD}{CYAN}=== AI CAPTAINS ==={RESET}")
        for c in engine.state.ai_captains:
            print(f"{c.id:<18} {BOLD}{c.name:<20}{RESET} {c.archetype:<10} {c.system_id:<14} trust={c.trust:<4} ally={c.ally}")
        return 0
    if len(parts) < 3:
        print(f"{RED}Usage:{RESET} ai <hail|buy|sell|hire|ally> <captain_id> [commodity] [qty]")
        return 1
    captain_id = parts[2]
    commodity = parts[3] if len(parts) > 3 else None
    quantity = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 1
    ok, msg = engine.interact_ai(captain_id, action, commodity, quantity)
    print((GREEN if ok else RED) + msg + RESET)
    storage.save(engine.state)
    return 0 if ok else 1


def cmd_messages(engine: SimulationEngine, storage: StorageManager, parts: list[str]) -> int:
    action = parts[1] if len(parts) > 1 else "list"
    if action == "list":
        print(f"\n{BOLD}{CYAN}=== QUANTUM INBOX ==={RESET}")
        for m in engine.state.messages:
            marker = " " if m.read else "*"
            print(f"{marker} {m.id:<24} {m.sender:<18} {m.subject}")
        return 0
    if action == "send":
        if len(parts) < 5:
            print(f"{RED}Usage:{RESET} messages send <recipient> <subject> <body>")
            return 1
        ok, msg = engine.send_quantum_message(parts[2], parts[3], " ".join(parts[4:]))
        print((GREEN if ok else RED) + msg + RESET)
        storage.save(engine.state)
        return 0 if ok else 1
    if action == "read":
        if len(parts) < 3:
            print(f"{RED}Usage:{RESET} messages read <message_id>")
            return 1
        ok, msg = engine.mark_message_read(parts[2])
        print((GREEN if ok else RED) + msg + RESET)
        storage.save(engine.state)
        return 0 if ok else 1
    print(f"{RED}Unknown messages action '{action}'.{RESET}")
    return 1


def cmd_depot(engine: SimulationEngine, storage: StorageManager, parts: list[str]) -> int:
    action = parts[1] if len(parts) > 1 else "status"
    depot = next((d for d in engine.state.depots if d.system_id == engine.state.ship.current_system_id), None)
    if action == "status":
        if not depot:
            print(f"{RED}No depot in this system.{RESET}")
            return 1
        print(f"\n{BOLD}{CYAN}{depot.name}{RESET} ({depot.capacity} capacity)")
        for item, qty in sorted(depot.cargo.items()):
            print(f"  {item:<20} x{qty}")
        return 0
    if len(parts) < 3:
        print(f"{RED}Usage:{RESET} depot <deposit|withdraw|sell> <item> [qty]")
        return 1
    qty = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 1
    handlers = {
        "deposit": engine.deposit_cargo,
        "withdraw": engine.withdraw_cargo,
        "sell": engine.sell_from_depot,
    }
    handler = handlers.get(action)
    if not handler:
        print(f"{RED}Unknown depot action '{action}'.{RESET}")
        return 1
    ok, msg = handler(parts[2], qty)
    print((GREEN if ok else RED) + msg + RESET)
    storage.save(engine.state)
    return 0 if ok else 1


def cmd_land(engine: SimulationEngine, storage: StorageManager, body_id: str) -> int:
    ok, msg = engine.land_on_body(body_id)
    print((GREEN if ok else RED) + msg + RESET)
    storage.save(engine.state)
    return 0 if ok else 1


def cmd_mercs(engine: SimulationEngine, storage: StorageManager, parts: list[str]) -> int:
    action = parts[1] if len(parts) > 1 else "list"
    if action == "list":
        print(f"\n{BOLD}{CYAN}=== MERCENARY CONTRACTS ==={RESET}")
        for merc in MERCENARY_CATALOG.values():
            print(f"{merc['id']:<16} {merc['name']:<20} {merc['cost']:>6} cr  {merc['description']}")
        return 0
    if len(parts) < 3:
        print(f"{RED}Usage:{RESET} mercs <hire> <merc_id> | mercs <dismiss|refit> <drone_id>")
        return 1
    if action == "hire":
        ok, msg = engine.hire_mercenary(parts[2])
    elif action == "dismiss":
        ok, msg = engine.dismiss_fleet_unit(parts[2])
    elif action == "refit":
        ok, msg = engine.refit_fleet_unit(parts[2])
    else:
        print(f"{RED}Unknown mercenary action '{action}'.{RESET}")
        return 1
    print((GREEN if ok else RED) + msg + RESET)
    storage.save(engine.state)
    return 0 if ok else 1


def cmd_allies(engine: SimulationEngine, storage: StorageManager, parts: list[str]) -> int:
    action = parts[1] if len(parts) > 1 else "list"
    if action == "list":
        print(f"\n{BOLD}{CYAN}=== ALLIANCES ==={RESET}")
        print("Allies:", ", ".join(engine.state.ship.allies) or "none")
        for c in engine.state.ai_captains:
            print(f"  {c.id:<18} {c.name:<20} trust={c.trust:<4} ally={c.ally}")
        return 0
    if action == "form" and len(parts) >= 3:
        ok, msg = engine.form_alliance(parts[2])
        print((GREEN if ok else RED) + msg + RESET)
        storage.save(engine.state)
        return 0 if ok else 1
    print(f"{RED}Usage:{RESET} allies form <captain_id>")
    return 1

def cmd_upgrades(engine: SimulationEngine, storage: StorageManager, parts: list[str]) -> int:
    """Inspect and purchase hardware modules from station arsenal."""
    if len(parts) == 1:
        installed = engine.state.ship.equipped_upgrades
        print(f"\n{BOLD}{CYAN}=== STATION ARSENAL & HARDWARE UPGRADES ==={RESET}")
        print(f"Commander Balance: {YELLOW}{engine.state.ship.credits} cr{RESET}\n")
        print(f"{'SLOT':<10} {'ID':<24} {'NAME':<28} {'COST':>8} {'STATUS':<12}")
        print(f"{'-' * 84}")
        for u in CATALOG_UPGRADES:
            is_inst = installed.get(u.slot) == u.id
            status = f"{GREEN}[INSTALLED]{RESET}" if is_inst else f"{YELLOW}[AVAILABLE]{RESET}"
            print(f"{u.slot.upper():<10} {u.id:<24} {BOLD}{u.name:<28}{RESET} {u.cost:>6} cr {status}")
            print(f"  {DIM}└─ {u.description}{RESET}")
        print(f"{'-' * 84}")
        print(f"To purchase and equip: {BOLD}upgrades buy <upgrade_id>{RESET}")
        return 0

    sub = parts[1].lower()
    if sub == "buy":
        if len(parts) < 3:
            print(f"{RED}Usage:{RESET} upgrades buy <upgrade_id>")
            return 1
        ok, msg = engine.buy_upgrade(parts[2])
        print((GREEN if ok else RED) + msg + RESET)
        storage.save(engine.state)
        return 0 if ok else 1
    else:
        print(f"{RED}Unknown upgrades command '{sub}'. Options: list, buy.{RESET}")
        return 1


def cmd_combat(engine: SimulationEngine, storage: StorageManager, parts: list[str]) -> int:
    """Execute tactical combat maneuvers during hostile intercepts."""
    if not engine.state.active_combat:
        print(f"{YELLOW}No active combat intercept detected in this sector.{RESET}")
        return 0

    if len(parts) < 2:
        c = engine.state.active_combat
        faction_badge = f"{YELLOW}[Faction: {c.faction_id}]{RESET}" if c.faction_id else ""
        print(f"\n{RED}{BOLD}⚔️  ACTIVE COMBAT: {c.enemy_name} ({c.enemy_class}) {faction_badge}{RESET}")
        if c.enemy_max_shield > 0:
            print(f"Enemy Shield:   {_bar(c.enemy_shield, c.enemy_max_shield, 20, CYAN)}")
        print(f"Enemy Hull:     {_bar(c.enemy_hull, c.enemy_max_hull, 20, RED)}")
        if c.special_ability and c.special_ability != "none":
            print(f"Hostile Tech:   {MAGENTA}{c.special_ability.replace('_', ' ').title()}{RESET}")
        if c.telegraphed_action:
            print(f"Hostile Action: {YELLOW}⚠ {c.telegraphed_action}{RESET}")
        print(f"\n{BOLD}Tactical maneuvers:{RESET}")
        print(f"  {BOLD}combat fire{RESET}    - Fire laser battery strike")
        print(f"  {BOLD}combat drone{RESET}   - Launch kinetic drone strike / sensor burn")
        print(f"  {BOLD}combat target{RESET}  - Target subsystem (e.g. combat target weapons)")
        print(f"  {BOLD}combat absorb{RESET}  - Overcharge shield capacitors")
        print(f"  {BOLD}combat evade{RESET}   - High-G thruster evasion")
        print(f"  {BOLD}combat flee{RESET}    - Emergency hyperspace jump (costs 8 fuel)")
        return 0

    sub = parts[1].lower()
    action_map = {
        "fire": "fire_lasers",
        "laser": "fire_lasers",
        "attack": "fire_lasers",
        "drone": "drone_strike",
        "dronestrike": "drone_strike",
        "strike": "drone_strike",
        "target": "target_weapons" if len(parts) <= 2 else ("target_shields" if "shield" in parts[2].lower() else "target_weapons"),
        "subsystem": "target_weapons",
        "absorb": "shield_absorb",
        "shield": "shield_absorb",
        "defend": "shield_absorb",
        "evade": "evasive_burn",
        "dodge": "evasive_burn",
        "flee": "flee",
        "escape": "flee",
    }
    action = action_map.get(sub, sub)
    ok, msg = engine.combat_action(action)
    print((GREEN if ok else RED) + msg + RESET)
    storage.save(engine.state)
    return 0 if ok else 1


def cmd_factions(engine: SimulationEngine, storage: StorageManager, parts: list[str]) -> int:
    """Inspect galactic sovereign factions, standings, active territory, and diplomatic perks."""
    print(f"\n{BOLD}{CYAN}╔════ GALACTIC FACTIONS & SOVEREIGN STANDINGS ═════════════════════════╗{RESET}")
    for fid, faction in CANONICAL_FACTIONS.items():
        standing = engine.state.ship.faction_standings.get(fid, 0)
        tier, perk = get_faction_standing_tier(standing)
        tier_color = RED if tier == "Hostile" else (YELLOW if tier == "Unfriendly" else (GREEN if tier in ("Friendly", "Allied") else WHITE))
        stand_bar = _bar(standing + 100, 200, 16, tier_color)
        print(f"║ {BOLD}{faction.name:<24}{RESET} Status: {tier_color}[{tier.upper()} ({standing:+d})]{RESET}  HQ: {faction.headquarters_system:<10} ║")
        print(f"║   Ideology: {DIM}{faction.ideology}{RESET}")
        print(f"║   Standing: {stand_bar}")
        print(f"║   Active Benefit/Tariff: {CYAN}{perk}{RESET}\n")
    print(f"{CYAN}╚══════════════════════════════════════════════════════════════════════╝{RESET}")
    return 0


def cmd_corporations(engine: SimulationEngine, storage: StorageManager, parts: list[str]) -> int:
    """Inspect interstellar megacorporations, commercial specialties, and corporate standing."""
    print(f"\n{BOLD}{YELLOW}╔════ INTERSTELLAR MEGACORPORATIONS & TRADE CONSORTIUMS ═══════════════╗{RESET}")
    for cid, corp in CANONICAL_CORPORATIONS.items():
        standing = engine.state.ship.corp_standings.get(cid, 0)
        stand_bar = _bar(standing + 100, 200, 16, YELLOW)
        print(f"║ {BOLD}{corp.name:<26}{RESET} Standing: {YELLOW}[{standing:+d}]{RESET}  HQ: {corp.headquarters_system:<10} ║")
        print(f"║   Specialty: {GREEN}{corp.specialty_commodity.replace('_', ' ').title()}{RESET} (+{int(corp.bonus_trade_margin*100)}% commercial sale profit)")
        print(f"║   Standing:  {stand_bar}")
        print(f"║   Perk:      {DIM}{corp.corporate_perk}{RESET}\n")
    print(f"{YELLOW}╚══════════════════════════════════════════════════════════════════════╝{RESET}")
    return 0


def cmd_contracts(engine: SimulationEngine, storage: StorageManager, parts: list[str]) -> int:
    """Inspect dynamic sector bounties, claim completed contracts, and trigger fresh assignments."""
    if len(parts) == 1 or parts[1].lower() in ("list", "show"):
        contracts = engine.state.ship.active_contracts
        print(f"\n{BOLD}{CYAN}=== ACTIVE SECTOR BOUNTIES & CONTRACTS ==={RESET}")
        if not contracts:
            print(f"{DIM}No active contracts in flight recorder.{RESET}")
            return 0

        for c in contracts:
            status_tag = f"{GREEN}[READY TO CLAIM]{RESET}" if c.completed else f"{YELLOW}[IN PROGRESS]{RESET}"
            prog_bar = _bar(c.current_count, c.target_count, 14, GREEN if c.completed else YELLOW)
            relic_tag = f" + Relic [{c.reward_relic_tier.upper()}]" if c.reward_relic_tier else ""
            print(f"• {BOLD}{c.title}{RESET} ({c.id}) - {CYAN}{c.category.upper()}{RESET} {status_tag}")
            print(f"  {DIM}{c.description}{RESET}")
            print(f"  Progress: {prog_bar} | Reward: {YELLOW}+{c.reward_credits} cr{RESET}, {CYAN}+{c.reward_xp} XP{RESET}{relic_tag}\n")

        ready = [c for c in contracts if c.completed]
        if ready:
            print(f"{GREEN}{BOLD}Claim completed assignment: contracts claim <id>{RESET}")
        else:
            print(f"{DIM}Advance contracts by exploring, scanning, trading, or defeating hostiles.{RESET}")
        return 0

    sub = parts[1].lower()
    if sub in ("claim", "complete"):
        if len(parts) < 3:
            ready = [c for c in engine.state.ship.active_contracts if c.completed]
            if len(ready) == 1:
                cid = ready[0].id
            else:
                print(f"{RED}Usage:{RESET} contracts claim <contract_id>")
                return 1
        else:
            cid = parts[2]

        ok, msg, _ = engine.claim_contract(cid)
        print((GREEN if ok else RED) + msg + RESET)
        if ok:
            storage.save(engine.state)
        return 0 if ok else 1

    print(f"{RED}Unknown contracts command '{sub}'. Options: list, claim <id>.{RESET}")
    return 1


def cmd_mastery(engine: SimulationEngine, storage: StorageManager, parts: list[str]) -> int:
    """Display pilot progression rank, talent tree specializations, and allocate perks."""
    ship = engine.state.ship
    mastery = ship.mastery

    if len(parts) == 1 or parts[1].lower() in ("list", "status"):
        print(f"\n{BOLD}{CYAN}=== PILOT MASTERY & SPECIALIZATION TREE ==={RESET}")
        print(f"Pilot Level: {YELLOW}{BOLD}Rank {mastery.level}{RESET} | Unspent Talent Points: {GREEN}{BOLD}{mastery.talent_points}{RESET}")
        print(f"Career XP:   {_bar(mastery.xp, mastery.next_level_xp, 24, YELLOW)}")
        print(f"{'-' * 70}")

        for tid, t in PILOT_TALENTS.items():
            is_unlocked = tid in mastery.specializations
            status = f"{GREEN}[UNLOCKED]{RESET}" if is_unlocked else f"{YELLOW}[LOCKED - 1 PT]{RESET}"
            print(f"• {BOLD}{t['name']:<24}{RESET} ({tid}) | {CYAN}{t['category'].upper():<12}{RESET} {status}")
            print(f"  {DIM}{t['description']}{RESET}\n")

        print(f"{'-' * 70}")
        if mastery.talent_points > 0:
            print(f"{GREEN}{BOLD}Unlock specialization: mastery unlock <talent_id>{RESET}")
        else:
            print(f"{DIM}Earn Pilot XP through contracts, jump streaks, and combat to earn Talent Points.{RESET}")
        return 0

    sub = parts[1].lower()
    if sub in ("unlock", "learn", "buy"):
        if len(parts) < 3:
            print(f"{RED}Usage:{RESET} mastery unlock <talent_id>")
            return 1

        tid = parts[2].lower()
        ok, msg = engine.unlock_talent(tid)
        print((GREEN if ok else RED) + msg + RESET)
        if ok:
            storage.save(engine.state)
        return 0 if ok else 1

    print(f"{RED}Unknown mastery command '{sub}'. Options: list, unlock <id>.{RESET}")
    return 1


def cmd_relics(engine: SimulationEngine) -> int:
    """Display recovered ancient Precursor relics and passive fleet bonuses."""
    relics = engine.state.ship.relics
    print(f"\n{BOLD}{CYAN}=== ANCIENT PRECURSOR RELICS VAULT ==={RESET}")
    if not relics:
        print(f"{DIM}No Precursor Relics recovered yet.{RESET}")
        print(f"Relics drop via sensor scans of planets, combat victories, and high-tier bounty contracts.")
        return 0

    rarity_colors = {
        "common": DIM,
        "rare": CYAN,
        "epic": MAGENTA,
        "legendary": YELLOW + BOLD,
    }

    for r in relics:
        color = rarity_colors.get(r.rarity, RESET)
        print(f"• {color}[{r.rarity.upper()}]{RESET} {BOLD}{r.name}{RESET} ({r.id})")
        print(f"  {DIM}{r.description}{RESET}\n")

    multipliers = calculate_passive_multipliers(engine.state.ship)
    print(f"{BOLD}Active Passive Fleet Modifiers:{RESET}")
    print(f"  Scan Bounty Boost:    +{int((multipliers['scan_bounty'] - 1.0) * 100)}%")
    print(f"  Trade Profit Margin:  +{int((multipliers['trade_margin'] - 1.0) * 100)}%")
    print(f"  Laser Strike Power:   +{int((multipliers['laser_dmg'] - 1.0) * 100)}%")
    print(f"  Shield Capacity:      +{int(multipliers['shield_cap'])} MW")
    print(f"  Hull Reinforcement:   +{int(multipliers['max_hull'])} HP")
    print(f"  Jump Fuel Efficiency: +{int((1.0 - multipliers['fuel_efficiency']) * 100)}%")
    print(f"  Fleet Drone Yield:    +{int((multipliers['drone_yield'] - 1.0) * 100)}%")
    return 0


def cmd_streak(engine: SimulationEngine) -> int:
    """Display current expedition jump streak and active loss aversion multiplier."""
    ship = engine.state.ship
    mult = 1.0 + min(1.5, (ship.streak - 1) * 0.15)
    print(f"\n{BOLD}{CYAN}=== EXPEDITION JUMP STREAK ==={RESET}")
    print(f"Current Streak: {RED}{BOLD}🔥 {ship.streak} consecutive jumps{RESET}")
    print(f"Streak Multiplier: {YELLOW}{BOLD}x{mult:.2f}{RESET} (+{int((mult - 1.0) * 100)}% to all trade, scan, and contract rewards)")
    print(f"\n{DIM}Mechanics (Loss Aversion):{RESET}")
    print(f"  • Every successful hyperlane jump increments streak by +1 (capped at x2.50).")
    print(f"  • All scan credits, trade profits, and pilot XP scale with this multiplier.")
    print(f"  • {RED}CAUTION:{RESET} Fleeing from hostile combat resets your streak back to 1!")
    return 0


def cmd_tutorial(engine: SimulationEngine, storage: StorageManager, parts: list[str]) -> int:
    """Cadet Flight Academy progressive tutorial system."""
    tut = engine.state.ship.tutorial
    if len(parts) > 1:
        sub = parts[1].lower()
        if sub == "skip":
            ok, msg = engine.skip_tutorial()
            print((GREEN if ok else RED) + msg + RESET)
            if ok:
                storage.save(engine.state)
            return 0 if ok else 1
        elif sub == "reset":
            ok, msg = engine.reset_tutorial()
            print((GREEN if ok else RED) + msg + RESET)
            if ok:
                storage.save(engine.state)
            return 0 if ok else 1
        else:
            print(f"{RED}Unknown tutorial command '{sub}'. Options: skip, reset.{RESET}")
            return 1

    print(f"\n{BOLD}{CYAN}=== CADET FLIGHT ACADEMY: ONBOARDING SCRIPT ==={RESET}")
    if tut.completed:
        print(f"{GREEN}★ Status: GRADUATED{RESET} - All academy milestones mastered.")
        print(f"{DIM}You hold the Cadet Wings relic granting permanent scan and XP bonuses.{RESET}")
        print(f"Type {CYAN}tutorial reset{RESET} if you wish to run through the academy again.")
        return 0

    if tut.skipped:
        print(f"{YELLOW}★ Status: SKIPPED{RESET} - Independent Pilot Protocol active.")
        print(f"Type {CYAN}tutorial reset{RESET} to reactivate Cadet Academy guidance.")
        return 0

    step = tut.current_step
    print(f"Current Milestone: {YELLOW}{tut.current_step_index + 1}/{len(tut.steps)}{RESET} - {BOLD}{step.title}{RESET}")
    print(f"{CYAN}Instruction:{RESET} {step.description}")
    print(f"{DIM}Hint / Goal:{RESET} {step.hint}")
    print(f"Reward on completion: {YELLOW}+{step.reward_credits} cr{RESET}, {CYAN}+{step.reward_xp} XP{RESET}\n")

    print(f"{BOLD}Curriculum Progress:{RESET}")
    for i, s in enumerate(tut.steps):
        marker = f"{GREEN}[✓]{RESET}" if s.completed else (f"{YELLOW}[▶]{RESET}" if i == tut.current_step_index else f"{DIM}[ ]{RESET}")
        print(f"  {marker} {i + 1}. {s.title} ({s.action_target})")
    print(f"\n{DIM}Tip: Perform the required action naturally (e.g. orbit, scan, power, trade, fleet, jump).{RESET}")
    print(f"{DIM}You can skip academy prompts at any time using: tutorial skip{RESET}")
    return 0


def cmd_story(engine: SimulationEngine, storage: StorageManager, parts: list[str]) -> int:
    """The Precursor Cipher: Branching episodic space opera campaign."""
    ship = engine.state.ship
    story = ship.story

    if len(parts) > 1 and parts[1].lower() in ("choose", "choice", "select"):
        if len(parts) < 3:
            print(f"{RED}Usage:{RESET} story choose <choice_id>")
            return 1
        cid = parts[2].lower()
        ok, msg = engine.make_story_choice(cid)
        print((GREEN if ok else RED) + msg + RESET)
        if ok:
            storage.save(engine.state)
        return 0 if ok else 1

    if story.completed:
        print(f"\n{BOLD}{MAGENTA}╔════ THE PRECURSOR CIPHER: NARRATIVE CAMPAIGN ════════════════════════╗{RESET}")
        print(f"║ {BOLD}{YELLOW}⭐ CAMPAIGN CONCLUDED: ALL NARRATIVE ACTS RESOLVED ⭐{RESET}               ║")
        print(f"║ Status: {GREEN}{'TRIUMPHANT VICTORY':<18}{RESET} Final Acts: {'3 / 3 COMPLETED':<26} ║")
        print(f"╠════ FACTION ALIGNMENT & REPUTATION ══════════════════════════════════╣{RESET}")
        rep = story.faction_reputation
        print(f"║ Sol Coalition: {CYAN}{rep.get('coalition', 0):>+4}{RESET}  │  Free Spacers Syndicate: {YELLOW}{rep.get('syndicate', 0):>+4}{RESET}  │  Precursor Watch: {MAGENTA}{rep.get('precursor', 0):>+4}{RESET} ║")
        print(f"╠════ EPILOGUE ════════════════════════════════════════════════════════╣{RESET}")
        print("  The Precursor Gateway pulses with radiant energy across the galaxy.")
        print("  Commander Astraea's name is etched into ancient cosmic starmaps.")
        print(f"\n{BOLD}Archived Subspace Transmissions ({len(story.transmission_log)} total):{RESET}")
        for tx in story.transmission_log[-3:]:
            speaker_color = CYAN if "Vance" in tx.speaker else (YELLOW if "Cipher" in tx.speaker else MAGENTA)
            print(f"\n  {speaker_color}[{tx.callsign.upper()} // {tx.speaker}]{RESET}")
            print(f"  \"{tx.message}\"")
        return 0

    chap = story.current_chapter
    print(f"\n{BOLD}{MAGENTA}╔════ THE PRECURSOR CIPHER: NARRATIVE CAMPAIGN ════════════════════════╗{RESET}")
    print(f"║ {BOLD}Act {story.active_act}: {chap.title:<58}{RESET} ║")
    target_str = str(chap.target_system_id or "DEEP SPACE")[:12]
    status_label = "COMPLETED" if chap.completed else f"TARGET: {target_str}"
    print(f"║ Sector Target: {CYAN}{target_str:<12}{RESET} Status: {status_label:<34} ║")
    print(f"╠════ FACTION ALIGNMENT & REPUTATION ══════════════════════════════════╣{RESET}")
    rep = story.faction_reputation
    print(f"║ Sol Coalition: {CYAN}{rep.get('coalition', 0):>+4}{RESET}  │  Free Spacers Syndicate: {YELLOW}{rep.get('syndicate', 0):>+4}{RESET}  │  Precursor Watch: {MAGENTA}{rep.get('precursor', 0):>+4}{RESET} ║")
    print(f"╠════ SYNOPSIS ════════════════════════════════════════════════════════╣{RESET}")
    print(f"  {chap.synopsis}")
    print(f"\n{BOLD}Subspace Transmissions Log ({len(story.transmission_log)} recorded):{RESET}")

    recent = story.transmission_log[-3:] if story.transmission_log else []
    for tx in recent:
        speaker_color = CYAN if "Vance" in tx.speaker else (YELLOW if "Cipher" in tx.speaker else MAGENTA)
        print(f"\n  {speaker_color}[{tx.callsign.upper()} // {tx.speaker}]{RESET}")
        print(f"  \"{tx.message}\"")

    if not chap.completed and chap.choices:
        print(f"\n{BOLD}{YELLOW}⚡ CRITICAL MORAL DECISION REQUIRED:{RESET}")
        for c in chap.choices:
            cost_str = f" [Cost: {c.cost_credits} cr]" if c.cost_credits > 0 else ""
            print(f"  • {BOLD}{c.id}{RESET}{cost_str}: {c.label}")
            print(f"    {DIM}{c.consequence_summary}{RESET}")
        print(f"\n{CYAN}Type: story choose <choice_id>{RESET} to resolve this encounter.")
    elif chap.completed:
        print(f"\n{GREEN}Chapter completed.{RESET} Follow navigational beacons to advance.")

    return 0


def cmd_repl(engine: SimulationEngine, storage: StorageManager) -> int:
    """Launch interactive terminal command session."""
    # Print status upon entry
    cmd_status(engine)
    print(f"\n{GREEN}Sub-space quantum link active. Type 'help' for command matrix, 'serve' for Web HUD.{RESET}\n")

    server_handle: BackgroundServer | None = None

    while True:
        try:
            line = input(f"{CYAN}voidfarer [{engine.state.ship.current_system_id}]> {RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting VoidFarer link.")
            break

        if not line:
            continue

        # Clean user-pasted shell invocations (e.g. `py -m voidfarer.cli serve` or `python ...`)
        if line.startswith("py -m voidfarer.cli ") or line.startswith("python -m voidfarer.cli "):
            line = line.split("voidfarer.cli ")[1].strip()
        elif line.startswith("py ") or line.startswith("python "):
            print(f"{YELLOW}Note:{RESET} You are inside the VoidFarer interactive REPL. Omit 'python' or 'py'.")
            parts = line.split()
            if len(parts) > 1 and parts[1] != "-m":
                line = " ".join(parts[1:])
            else:
                continue

        parts = line.split()
        cmd = parts[0].lower()

        if cmd in ("exit", "quit", "q"):
            break
        elif cmd == "status":
            cmd_status(engine)
        elif cmd in ("chart", "map"):
            cmd_chart(engine)
        elif cmd == "market":
            cmd_market(engine)
        elif cmd == "fleet":
            cmd_fleet(engine, storage, parts)
        elif cmd in ("upgrades", "upgrade", "arsenal", "shop"):
            cmd_upgrades(engine, storage, parts)
        elif cmd in ("combat", "fight", "battle"):
            cmd_combat(engine, storage, parts)
        elif cmd in ("contracts", "contract", "bounties", "bounty"):
            cmd_contracts(engine, storage, parts)
        elif cmd in ("claim",):
            cmd_contracts(engine, storage, ["contracts", "claim"] + parts[1:])
        elif cmd in ("mastery", "talents", "talent", "perks"):
            cmd_mastery(engine, storage, parts)
        elif cmd in ("unlock",):
            cmd_mastery(engine, storage, ["mastery", "unlock"] + parts[1:])
        elif cmd in ("relics", "relic", "vault", "artifacts"):
            cmd_relics(engine)
        elif cmd in ("streak", "fire"):
            cmd_streak(engine)
        elif cmd in ("tutorial", "academy", "cadet"):
            cmd_tutorial(engine, storage, parts)
        elif cmd in ("story", "campaign", "act", "lore", "comms"):
            cmd_story(engine, storage, parts)
        elif cmd in ("serve", "web", "gui", "hud"):
            if len(parts) > 1 and parts[1] in ("stop", "shutdown"):
                if server_handle is not None:
                    server_handle.stop()
                    server_handle = None
                    print(f"{GREEN}Holographic Web Cockpit stopped.{RESET}")
                else:
                    print(f"{YELLOW}Cockpit server is not running.{RESET}")
                continue

            port = 8080
            for i, p in enumerate(parts):
                if p in ("--port", "-p") and i + 1 < len(parts):
                    try:
                        port = int(parts[i + 1])
                    except ValueError:
                        print(f"{YELLOW}Invalid port '{parts[i + 1]}'; using {port}.{RESET}")
                elif p.isdigit():
                    port = int(p)

            if server_handle is None:
                server_handle = start_background_server(engine, storage, port=port)
                if server_handle is not None:
                    print(f"\n{GREEN}Holographic Web Cockpit HUD launched successfully!{RESET}")
                    print(f"{CYAN}Uplink URL: http://127.0.0.1:{server_handle.port}{RESET}")
                    print(f"{DIM}(Web HUD and simulation ticker are running concurrently; type 'serve stop' to stop.){RESET}\n")
                else:
                    print(f"{YELLOW}Cockpit server notice:{RESET} Could not bind port {port}. Choose another port with 'serve <port>'.")
            else:
                print(f"{CYAN}Holographic Web Cockpit is currently running at http://127.0.0.1:{server_handle.port}{RESET}")

        elif cmd == "jump":
            if len(parts) < 2:
                print(f"{RED}Usage:{RESET} jump <system_id>")
            else:
                ok, msg = engine.jump(parts[1])
                print((GREEN if ok else RED) + msg + RESET)
                storage.save(engine.state)
        elif cmd == "orbit":
            if len(parts) < 2:
                print(f"{RED}Usage:{RESET} orbit <body_id>")
            else:
                ok, msg = engine.orbit(parts[1])
                print((GREEN if ok else RED) + msg + RESET)
                storage.save(engine.state)
        elif cmd == "travel":
            if len(parts) < 2:
                print(f"{RED}Usage:{RESET} travel <body_id> [--mode sublight|quantum]")
            else:
                mode = "sublight"
                for idx, tok in enumerate(parts):
                    if tok == "--mode" and idx + 1 < len(parts):
                        mode = parts[idx + 1]
                    elif tok in ("sublight", "quantum"):
                        mode = tok
                ok, msg = engine.start_travel(parts[1], mode=mode)
                print((GREEN if ok else RED) + msg + RESET)
                storage.save(engine.state)
        elif cmd == "events":
            cmd_events(engine, storage, parts)
        elif cmd == "scan":
            ok, msg, _ = engine.scan()
            print((GREEN if ok else RED) + msg + RESET)
            storage.save(engine.state)
        elif cmd == "power":
            if len(parts) < 5:
                print(f"{RED}Usage:{RESET} power <engines> <shields> <sensors> <weapons>")
            else:
                try:
                    e, s, se, w = int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])
                    ok, msg = engine.route_power(e, s, se, w)
                    print((GREEN if ok else RED) + msg + RESET)
                    storage.save(engine.state)
                except ValueError:
                    print(f"{RED}Error:{RESET} Power values must be integers summing to 100.")
        elif cmd == "buy":
            if len(parts) < 3:
                print(f"{RED}Usage:{RESET} buy <commodity_id> <quantity>")
            else:
                try:
                    ok, msg = engine.trade(parts[1], int(parts[2]), is_buy=True)
                    print((GREEN if ok else RED) + msg + RESET)
                    storage.save(engine.state)
                except ValueError:
                    print(f"{RED}Error:{RESET} Quantity must be an integer.")
        elif cmd == "sell":
            if len(parts) < 3:
                print(f"{RED}Usage:{RESET} sell <commodity_id> <quantity>")
            else:
                try:
                    ok, msg = engine.trade(parts[1], int(parts[2]), is_buy=False)
                    print((GREEN if ok else RED) + msg + RESET)
                    storage.save(engine.state)
                except ValueError:
                    print(f"{RED}Error:{RESET} Quantity must be an integer.")
        elif cmd == "anomaly":
            if len(parts) < 2:
                print(f"{RED}Usage:{RESET} anomaly <choice_id>")
            else:
                ok, msg = engine.resolve_anomaly(parts[1])
                print((GREEN if ok else RED) + msg + RESET)
                storage.save(engine.state)
        elif cmd == "repair":
            try:
                amt = int(parts[1]) if len(parts) > 1 else 25
            except ValueError:
                print(f"{RED}Error:{RESET} Repair amount must be an integer.")
                continue
            ok, msg = engine.repair_hull(amt)
            print((GREEN if ok else RED) + msg + RESET)
            storage.save(engine.state)
        elif cmd == "refuel":
            try:
                amt = int(parts[1]) if len(parts) > 1 else 20
            except ValueError:
                print(f"{RED}Error:{RESET} Fuel amount must be an integer.")
                continue
            ok, msg = engine.refuel(amt)
            print((GREEN if ok else RED) + msg + RESET)
            storage.save(engine.state)
        elif cmd in ("factions", "faction"):
            cmd_factions(engine, storage, parts)
        elif cmd in ("corps", "corporations", "corp"):
            cmd_corporations(engine, storage, parts)
        elif cmd in ("time", "chrono", "tick", "wait"):
            cmd_time(engine, storage, parts[1:])
        elif cmd in ("economy", "econ"):
            cmd_economy(engine)
        elif cmd in ("inventory", "inv", "cargo"):
            cmd_inventory(engine, storage, parts)
        elif cmd in ("use",):
            cmd_inventory(engine, storage, ["inventory", "use"] + parts[1:])
        elif cmd in ("jettison", "drop"):
            cmd_inventory(engine, storage, ["inventory", "jettison"] + parts[1:])
        elif cmd in ("shipyard", "drydock"):
            cmd_shipyard(engine, storage, parts)
        elif cmd in ("chassis",):
            cmd_shipyard(engine, storage, ["shipyard", "chassis"] + parts[1:])
        elif cmd == "help":
            print(f"{BOLD}Available subcommands:{RESET}")
            print("  status                         - Telemetry, fleet roster, and subsystem readouts")
            print("  time [status|pause|speed|step] - Cosmic time, ticks, and temporal speed controls")
            print("  economy / econ                 - Galactic macroeconomic conditions and trade routes")
            print("  inventory [buy|use|jettison]   - Hold manifest, station consumables & usable items")
            print("  shipyard [chassis|sell]        - Orbital shipyard, chassis showroom, and drydocks")
            print("  chart / map                    - Hyperlane network & orbital bodies")
            print("  factions                       - Galactic factions, sovereign standings & perks")
            print("  corps / corporations           - Megacorporations, specialties & trade bonuses")
            print("  jump <system_id>               - Hyperspace jump to adjacent star")
            print("  orbit <body_id>                - Enter orbit around planet or station")
            print("  scan                           - Sensor sweep of orbiting body (relic discovery)")
            print("  contracts [claim <id>]         - Active sector bounty contracts (Zeigarnik loop)")
            print("  mastery [unlock <id>]          - Pilot rank, XP progression, and talent tree")
            print("  tutorial [skip|reset]          - Cadet Flight Academy onboarding and guidance")
            print("  story [choose <id>]            - The Precursor Cipher narrative campaign")
            print("  relics                         - Ancient Precursor Relic vault & passive fleet buffs")
            print("  streak                         - Expedition jump streak & multiplier status")
            print("  market                         - Check commodity trade prices")
            print("  buy <comm> <qty>               - Buy commodities from local exchange")
            print("  sell <comm> <qty>              - Sell commodities to local exchange")
            print("  fleet [harvest|buy|deploy]     - Autonomous fleet assets and drone yields")
            print("  upgrades [buy <id>]            - Station hardware upgrades and module shop")
            print("  combat <fire|drone|target|flee>- Tactical maneuvers during hostile intercepts")
            print("  power <e> <s> <se> <w>         - Distribute 100% reactor power")
            print("  anomaly <choice_id>            - Resolve active spatial encounter")
            print("  repair [amt]                   - Repair hull integrity at station")
            print("  refuel [amt]                   - Replenish quantum fuel at station")
            print("  serve [--port 8080|stop]       - Launch/stop concurrent Web Cockpit HUD")
            print("  quests                         - Unified story and contract quest panel")
            print("  ai [list|hail|buy|sell|hire|ally] - AI captain diplomacy and trade")
            print("  messages [list|send|read]      - Intergalactic quantum messaging")
            print("  depot [status|deposit|withdraw|sell] - System cargo depot operations")
            print("  land <body_id>                 - Land on a habitable body")
            print("  mercs [list|hire|dismiss|refit] - Mercenary contracts and fleet refits")
            print("  allies [list|form]             - Alliance roster and formation")
            print("  exit / quit                    - Close interactive link")
        else:
            print(f"{RED}Unknown command '{cmd}'. Type 'help' for command matrix.{RESET}")

    if server_handle is not None:
        server_handle.stop()
        server_handle = None
    return 0


def cmd_events(engine: SimulationEngine, storage: StorageManager, parts: Sequence[str]) -> int:
    """List or dismiss cockpit popup events."""
    action = parts[1].lower() if len(parts) > 1 else "list"
    if action == "dismiss":
        if len(parts) < 3 or not parts[2]:
            print(f"{RED}Usage:{RESET} events dismiss <event_id>")
            return 1
        ok, msg = engine.dismiss_event(parts[2])
        print((GREEN if ok else RED) + msg + RESET)
        storage.save(engine.state)
        return 0 if ok else 1

    undismissed = [e for e in engine.state.events if not e.dismissed]
    if not undismissed:
        print(f"{DIM}No active cockpit events.{RESET}")
        return 0
    print(f"\n{CYAN}{BOLD}=== ACTIVE COCKPIT EVENTS ({len(undismissed)}) ==={RESET}")
    for evt in undismissed:
        print(f"  [{evt.id}] ({evt.kind.upper()} @ Tick #{evt.tick}) {BOLD}{evt.title}{RESET}: {evt.message}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Main CLI entrypoint."""
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="voidfarer",
        description="VoidFarer: Autonomous Deep-Space Fleet, Procedural Galaxy & Holographic Cockpit Simulator",
    )
    parser.add_argument("--save-path", help="Custom save file or directory path")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("status", help="Print ship telemetry and navigation status")
    subparsers.add_parser("chart", help="Display star systems and orbital bodies")
    subparsers.add_parser("market", help="Display local commodity exchange quotes")
    subparsers.add_parser("economy", help="Display galactic economy shocks and trade routes")
    inv_p = subparsers.add_parser("inventory", help="Inspect cargo hold manifest, buy consumables, and use items")
    inv_p.add_argument("action", nargs="?", default="list", choices=["list", "buy", "use", "jettison"])
    inv_p.add_argument("arg1", nargs="?", help="Item ID")
    inv_p.add_argument("arg2", nargs="?", help="Quantity")
    shipyard_p = subparsers.add_parser("shipyard", help="Orbital shipyard chassis and module sales")
    shipyard_p.add_argument("action", nargs="?", default="list", choices=["list", "catalog", "status", "chassis", "buy_chassis", "sell", "uninstall"])
    shipyard_p.add_argument("target", nargs="?", help="Chassis ID or module slot")
    subparsers.add_parser("scan", help="Execute sensor scan on orbiting body")
    subparsers.add_parser("repl", help="Launch interactive terminal cockpit")

    fleet_p = subparsers.add_parser("fleet", help="Autonomous fleet and drone operations")
    fleet_p.add_argument("action", nargs="?", default="list", choices=["list", "harvest", "buy", "deploy"])
    fleet_p.add_argument("arg1", nargs="?", help="Drone type or drone ID")
    fleet_p.add_argument("arg2", nargs="?", help="Target star system ID")

    subparsers.add_parser("quests", help="Unified quest panel (story + contracts)")

    ai_p = subparsers.add_parser("ai", help="AI captain diplomacy, trade, hire, and alliances")
    ai_p.add_argument("action", nargs="?", default="list", choices=["list", "hail", "buy", "sell", "hire", "ally"])
    ai_p.add_argument("captain_id", nargs="?", help="AI captain ID")
    ai_p.add_argument("commodity_id", nargs="?", help="Commodity for buy/sell")
    ai_p.add_argument("quantity", nargs="?", type=int, default=1)

    msg_p = subparsers.add_parser("messages", help="Intergalactic quantum messaging")
    msg_p.add_argument("action", nargs="?", default="list", choices=["list", "send", "read"])
    msg_p.add_argument("args", nargs="*", help="Message arguments")

    depot_p = subparsers.add_parser("depot", help="System cargo depot operations")
    depot_p.add_argument("action", nargs="?", default="status", choices=["status", "deposit", "withdraw", "sell"])
    depot_p.add_argument("item_id", nargs="?", help="Item ID")
    depot_p.add_argument("quantity", nargs="?", type=int, default=1)

    land_p = subparsers.add_parser("land", help="Land on a habitable body")
    land_p.add_argument("body_id", help="Celestial body ID")

    merc_p = subparsers.add_parser("mercs", help="Mercenary contracts and fleet refits")
    merc_p.add_argument("action", nargs="?", default="list", choices=["list", "hire", "dismiss", "refit"])
    merc_p.add_argument("target_id", nargs="?", help="Mercenary catalog ID or fleet drone ID")

    allies_p = subparsers.add_parser("allies", help="Alliance roster and formation")
    allies_p.add_argument("action", nargs="?", default="list", choices=["list", "form"])
    allies_p.add_argument("captain_id", nargs="?", help="AI captain ID")

    upg_p = subparsers.add_parser("upgrades", help="Station hardware modules arsenal")
    upg_p.add_argument("action", nargs="?", default="list", choices=["list", "buy"])
    upg_p.add_argument("upgrade_id", nargs="?", help="Upgrade ID to purchase")

    combat_p = subparsers.add_parser("combat", help="Execute tactical combat maneuver")
    combat_p.add_argument(
        "action",
        choices=["fire", "laser", "attack", "drone", "strike", "target", "subsystem", "absorb", "shield", "defend", "evade", "dodge", "flee", "escape"],
        help="Tactical maneuver",
    )
    combat_p.add_argument("target", nargs="?", help="Subsystem target for 'combat target' (weapons or shields)")

    contracts_p = subparsers.add_parser("contracts", help="Inspect and claim dynamic sector bounty contracts")
    contracts_p.add_argument("action", nargs="?", default="list", choices=["list", "claim"])
    contracts_p.add_argument("contract_id", nargs="?", help="Contract ID to claim")

    mastery_p = subparsers.add_parser("mastery", help="Pilot rank progression and talent specializations")
    mastery_p.add_argument("action", nargs="?", default="status", choices=["status", "list", "unlock"])
    mastery_p.add_argument("talent_id", nargs="?", help="Talent ID to unlock")

    subparsers.add_parser("relics", help="Display ancient Precursor Relics and passive modifiers")
    subparsers.add_parser("streak", help="Display expedition jump streak and multiplier")

    tut_p = subparsers.add_parser("tutorial", help="Cadet Flight Academy onboarding and guidance")
    tut_p.add_argument("action", nargs="?", default="status", choices=["status", "skip", "reset"])

    story_p = subparsers.add_parser("story", help="The Precursor Cipher narrative campaign")
    story_p.add_argument("action", nargs="?", default="status", choices=["status", "choose"])
    story_p.add_argument("choice_id", nargs="?", help="Choice ID to select")

    jump_p = subparsers.add_parser("jump", help="Jump to adjacent star system")
    jump_p.add_argument("system_id", help="Target star system ID")

    orbit_p = subparsers.add_parser("orbit", help="Enter orbit around celestial body")
    orbit_p.add_argument("body_id", help="Target body ID")

    travel_p = subparsers.add_parser("travel", help="Initiate sublight or quantum in-system transit")
    travel_p.add_argument("body_id", help="Destination celestial body ID")
    travel_p.add_argument("--mode", default="sublight", choices=["sublight", "quantum"], help="Transit mode")

    events_p = subparsers.add_parser("events", help="List or dismiss cockpit popup events")
    events_p.add_argument("action", nargs="?", default="list", choices=["list", "dismiss"])
    events_p.add_argument("event_id", nargs="?", help="Event ID to dismiss")

    pwr_p = subparsers.add_parser("power", help="Route reactor power (must sum to 100)")
    pwr_p.add_argument("engines", type=int, help="Engines power percentage")
    pwr_p.add_argument("shields", type=int, help="Shields power percentage")
    pwr_p.add_argument("sensors", type=int, help="Sensors power percentage")
    pwr_p.add_argument("weapons", type=int, help="Weapons power percentage")

    buy_p = subparsers.add_parser("buy", help="Buy commodities")
    buy_p.add_argument("commodity_id", help="Commodity identifier")
    buy_p.add_argument("quantity", type=int, help="Quantity to purchase")

    sell_p = subparsers.add_parser("sell", help="Sell commodities")
    sell_p.add_argument("commodity_id", help="Commodity identifier")
    sell_p.add_argument("quantity", type=int, help="Quantity to sell")

    anom_p = subparsers.add_parser("anomaly", help="Resolve active anomaly encounter")
    anom_p.add_argument("choice_id", help="Selected choice ID")

    rep_p = subparsers.add_parser("repair", help="Repair hull integrity")
    rep_p.add_argument("amount_pos", nargs="?", type=int, help="Hull points to restore (default 25)")
    rep_p.add_argument("--amount", type=int, default=None, help="Hull points to restore")

    ref_p = subparsers.add_parser("refuel", help="Replenish quantum fuel")
    ref_p.add_argument("amount_pos", nargs="?", type=int, help="Fuel units to add (default 20)")
    ref_p.add_argument("--amount", type=int, default=None, help="Fuel units to add")

    serve_p = subparsers.add_parser("serve", help="Launch Holographic Web Cockpit server")
    serve_p.add_argument("--port", type=int, default=8080, help="HTTP server port")
    serve_p.add_argument("--host", default="127.0.0.1", help="HTTP server host")
    serve_p.add_argument("--open", action="store_true", help="Automatically launch web browser")

    subparsers.add_parser("factions", help="Inspect galactic sovereign factions and reputation")
    subparsers.add_parser("corps", help="Inspect interstellar megacorporations and trade perks")
    subparsers.add_parser("corporations", help="Alias for 'corps'")

    time_p = subparsers.add_parser("time", help="Inspect and control simulation time and ticks")
    time_p.add_argument("action", nargs="?", default="status", choices=["status", "pause", "resume", "play", "speed", "step", "wait", "tick"])
    time_p.add_argument("value", nargs="?", help="Speed multiplier or tick count")

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 0

    custom_dir = Path(args.save_path) if getattr(args, "save_path", None) else None
    engine, storage = _get_engine(custom_dir)

    if args.command == "status":
        return cmd_status(engine)
    elif args.command == "time":
        parts = [args.action]
        if args.value:
            parts.append(args.value)
        return cmd_time(engine, storage, parts)
    elif args.command == "factions":
        return cmd_factions(engine, storage, ["factions"])
    elif args.command == "corps":
        return cmd_corporations(engine, storage, ["corps"])
    elif args.command == "corporations":
        return cmd_corporations(engine, storage, ["corporations"])
    elif args.command == "chart":
        return cmd_chart(engine)
    elif args.command == "market":
        return cmd_market(engine)
    elif args.command == "economy":
        return cmd_economy(engine)
    elif args.command == "inventory":
        parts = ["inventory"]
        if args.action != "list":
            parts.append(args.action)
            if args.arg1:
                parts.append(args.arg1)
            if args.arg2:
                parts.append(args.arg2)
        return cmd_inventory(engine, storage, parts)
    elif args.command == "shipyard":
        parts = ["shipyard"]
        if args.action != "list":
            parts.append(args.action)
            if args.target:
                parts.append(args.target)
        return cmd_shipyard(engine, storage, parts)
    elif args.command == "fleet":
        parts = ["fleet"]
        if args.action != "list":
            parts.append(args.action)
            if args.arg1:
                parts.append(args.arg1)
            if args.arg2:
                parts.append(args.arg2)
        return cmd_fleet(engine, storage, parts)
    elif args.command == "quests":
        return cmd_quests(engine)
    elif args.command == "ai":
        parts = ["ai", args.action]
        if args.captain_id:
            parts.append(args.captain_id)
        if args.commodity_id:
            parts.append(args.commodity_id)
        if args.quantity is not None:
            parts.append(str(args.quantity))
        return cmd_ai(engine, storage, parts)
    elif args.command == "messages":
        return cmd_messages(engine, storage, ["messages", args.action] + list(args.args))
    elif args.command == "depot":
        parts = ["depot", args.action]
        if args.item_id:
            parts.append(args.item_id)
        if args.quantity is not None:
            parts.append(str(args.quantity))
        return cmd_depot(engine, storage, parts)
    elif args.command == "land":
        return cmd_land(engine, storage, args.body_id)
    elif args.command == "mercs":
        parts = ["mercs", args.action]
        if args.target_id:
            parts.append(args.target_id)
        return cmd_mercs(engine, storage, parts)
    elif args.command == "allies":
        parts = ["allies", args.action]
        if args.captain_id:
            parts.append(args.captain_id)
        return cmd_allies(engine, storage, parts)
    elif args.command == "upgrades":
        parts = ["upgrades"]
        if args.action != "list":
            parts.append(args.action)
            if args.upgrade_id:
                parts.append(args.upgrade_id)
        return cmd_upgrades(engine, storage, parts)
    elif args.command == "combat":
        parts = ["combat", args.action]
        if args.target:
            parts.append(args.target)
        return cmd_combat(engine, storage, parts)
    elif args.command == "contracts":
        parts = ["contracts"]
        if args.action != "list":
            parts.append(args.action)
            if args.contract_id:
                parts.append(args.contract_id)
        return cmd_contracts(engine, storage, parts)
    elif args.command == "mastery":
        parts = ["mastery"]
        if args.action not in ("status", "list"):
            parts.append(args.action)
            if args.talent_id:
                parts.append(args.talent_id)
        return cmd_mastery(engine, storage, parts)
    elif args.command == "relics":
        return cmd_relics(engine)
    elif args.command == "streak":
        return cmd_streak(engine)
    elif args.command == "tutorial":
        parts = ["tutorial"]
        if args.action != "status":
            parts.append(args.action)
        return cmd_tutorial(engine, storage, parts)
    elif args.command == "story":
        parts = ["story"]
        if args.action != "status":
            parts.append(args.action)
            if args.choice_id:
                parts.append(args.choice_id)
        return cmd_story(engine, storage, parts)
    elif args.command == "scan":
        ok, msg, _ = engine.scan()
        print((GREEN if ok else RED) + msg + RESET)
        storage.save(engine.state)
        return 0 if ok else 1
    elif args.command == "jump":
        ok, msg = engine.jump(args.system_id)
        print((GREEN if ok else RED) + msg + RESET)
        storage.save(engine.state)
        return 0 if ok else 1
    elif args.command == "orbit":
        ok, msg = engine.orbit(args.body_id)
        print((GREEN if ok else RED) + msg + RESET)
        storage.save(engine.state)
        return 0 if ok else 1
    elif args.command == "travel":
        ok, msg = engine.start_travel(args.body_id, mode=args.mode)
        print((GREEN if ok else RED) + msg + RESET)
        storage.save(engine.state)
        return 0 if ok else 1
    elif args.command == "events":
        parts = ["events", args.action]
        if args.event_id:
            parts.append(args.event_id)
        return cmd_events(engine, storage, parts)
    elif args.command == "power":
        ok, msg = engine.route_power(args.engines, args.shields, args.sensors, args.weapons)
        print((GREEN if ok else RED) + msg + RESET)
        storage.save(engine.state)
        return 0 if ok else 1
    elif args.command == "buy":
        ok, msg = engine.trade(args.commodity_id, args.quantity, is_buy=True)
        print((GREEN if ok else RED) + msg + RESET)
        storage.save(engine.state)
        return 0 if ok else 1
    elif args.command == "sell":
        ok, msg = engine.trade(args.commodity_id, args.quantity, is_buy=False)
        print((GREEN if ok else RED) + msg + RESET)
        storage.save(engine.state)
        return 0 if ok else 1
    elif args.command == "anomaly":
        ok, msg = engine.resolve_anomaly(args.choice_id)
        print((GREEN if ok else RED) + msg + RESET)
        storage.save(engine.state)
        return 0 if ok else 1
    elif args.command == "repair":
        amount = args.amount if args.amount is not None else (args.amount_pos if args.amount_pos is not None else 25)
        ok, msg = engine.repair_hull(amount)
        print((GREEN if ok else RED) + msg + RESET)
        storage.save(engine.state)
        return 0 if ok else 1
    elif args.command == "refuel":
        amount = args.amount if args.amount is not None else (args.amount_pos if args.amount_pos is not None else 20)
        ok, msg = engine.refuel(amount)
        print((GREEN if ok else RED) + msg + RESET)
        storage.save(engine.state)
        return 0 if ok else 1
    elif args.command == "repl":
        return cmd_repl(engine, storage)
    elif args.command == "serve":
        return run_server(engine, storage, port=args.port, host=args.host, open_browser=args.open)

    return 0


if __name__ == "__main__":
    sys.exit(main())

