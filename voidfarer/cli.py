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
    except Exception:
        pass

from voidfarer.engine import SimulationEngine
from voidfarer.galaxy import COMMODITY_MAP, GalaxyGenerator
from voidfarer.server import ThreadedHTTPServer, VoidFarerHandler, run_server
from voidfarer.storage import StorageManager
from voidfarer.upgrades import (
    CATALOG_DRONE_TEMPLATES,
    CATALOG_UPGRADES,
    UPGRADE_MAP,
)

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
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
        storage_dir = home / ".voidfarer"
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
    print(f"║ Credits:   {YELLOW}{ship.credits:>8} cr{RESET}       Cargo:    {sum(ship.cargo.values()):>2}/{ship.cargo_capacity:<2} units                     ║")
    print(f"╠════ VITAL TELEMETRY ════════════════════════════════════════════════╣{RESET}")
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

    # Fleet summary
    num_drones = len(ship.fleet_drones)
    drone_summary = f"{num_drones} active drones / escorts deployed" if num_drones > 0 else "No active drones"
    print(f"╠════ AUTONOMOUS FLEET ASSETS ════════════════════════════════════════╣{RESET}")
    print(f"║ {GREEN}{drone_summary:<67}{RESET} ║")

    print(f"╠════ NAVIGATION COORDINATES ═════════════════════════════════════════╣{RESET}")
    print(f"║ System:    {CYAN}{cur_sys.name:<22}{RESET} Faction:  {cur_sys.faction:<22} ║")
    print(f"║ Security:  {GREEN if cur_sys.security > 0.5 else RED}{cur_sys.security * 100:>5.1f}% [{('HIGH' if cur_sys.security > 0.7 else ('MED' if cur_sys.security > 0.3 else 'ANARCHY'))}]{RESET}       Corridors: {', '.join(cur_sys.connections):<22} ║")
    orb_name = f"{body.name} [{body.body_type}]" if body else "Deep Space Transit"
    print(f"║ Orbit:     {orb_name:<57} ║")
    print(f"╚═════════════════════════════════════════════════════════════════════╝{RESET}")

    if engine.state.active_combat:
        c = engine.state.active_combat
        print(f"\n{RED}{BOLD}⚔️  COMBAT INTERCEPT: {c.enemy_name.upper()} [{c.enemy_class.upper()}]{RESET}")
        print(f"   Enemy Hull: {_bar(c.enemy_hull, c.enemy_max_hull, 20, RED)}")
        print(f"   Tactical Options: {BOLD}combat fire{RESET} | {BOLD}combat absorb{RESET} | {BOLD}combat evade{RESET} | {BOLD}combat flee{RESET}")

    elif engine.state.active_anomaly:
        anom = engine.state.active_anomaly
        print(f"\n{RED}{BOLD}⚠️  PROXIMITY ALERT: {anom.title}{RESET}")
        print(f"{DIM}{anom.description}{RESET}")
        print(f"{YELLOW}Resolution Choices:{RESET}")
        for ch in anom.choices:
            req = f"[{ch.required_power.upper()} >= {ch.min_power_threshold}%]" if ch.required_power != "none" else "[No Check]"
            print(f"  • {BOLD}{ch.choice_id}{RESET}: {ch.text} {DIM}{req}{RESET}")

    return 0


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

    quotes = GalaxyGenerator.get_market_quotes(engine.current_system, body)
    print(f"\n{BOLD}{CYAN}=== LOCAL COMMODITY EXCHANGE: {body.name.upper()} ==={RESET}")
    print(f"Market Archetype: {BOLD}{body.market_archetype.upper()}{RESET} | Credits: {YELLOW}{engine.state.ship.credits} cr{RESET}")
    print(f"{'-' * 70}")
    print(f"{'COMMODITY':<22} {'BUY':>8} {'SELL':>8} {'SUPPLY':>8} {'DEMAND':>8} {'HOLD':>8}")
    print(f"{'-' * 70}")
    cargo = engine.state.ship.cargo
    for q in quotes:
        hold_qty = cargo.get(q.commodity_id, 0)
        print(f"{q.name:<22} {GREEN}{q.buy_price:>6} cr{RESET} {YELLOW}{q.sell_price:>6} cr{RESET} {q.supply:>8} {q.demand:>8} {BOLD}{hold_qty:>8}{RESET}")
    print(f"{'-' * 70}")
    return 0


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
        print(f"\n{RED}{BOLD}⚔️  ACTIVE COMBAT: {c.enemy_name} ({c.enemy_class}){RESET}")
        print(f"Enemy Hull: {_bar(c.enemy_hull, c.enemy_max_hull, 20, RED)}")
        print(f"{BOLD}Tactical maneuvers:{RESET}")
        print(f"  {BOLD}combat fire{RESET}    - Fire laser battery strike")
        print(f"  {BOLD}combat absorb{RESET}  - Overcharge shield capacitors")
        print(f"  {BOLD}combat evade{RESET}   - High-G thruster evasion")
        print(f"  {BOLD}combat flee{RESET}    - Emergency hyperspace jump (costs 8 fuel)")
        return 0

    sub = parts[1].lower()
    action_map = {
        "fire": "fire_lasers",
        "laser": "fire_lasers",
        "attack": "fire_lasers",
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


def cmd_repl(engine: SimulationEngine, storage: StorageManager) -> int:
    """Launch interactive terminal command session."""
    # Print status upon entry
    cmd_status(engine)
    print(f"\n{GREEN}Sub-space quantum link active. Type 'help' for command matrix, 'serve' for Web HUD.{RESET}\n")

    server_thread: threading.Thread | None = None
    server_running = False

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
        elif cmd in ("serve", "web", "gui", "hud"):
            port = 8080
            for i, p in enumerate(parts):
                if p in ("--port", "-p") and i + 1 < len(parts):
                    try:
                        port = int(parts[i + 1])
                    except ValueError:
                        pass
                elif p.isdigit():
                    port = int(p)

            if not server_running:
                static_dir = Path(__file__).parent / "static"
                VoidFarerHandler.engine = engine
                VoidFarerHandler.storage = storage
                VoidFarerHandler.static_dir = static_dir

                try:
                    server = ThreadedHTTPServer(("127.0.0.1", port), VoidFarerHandler)
                    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
                    server_thread.start()
                    server_running = True
                    print(f"\n{GREEN}🚀 Holographic Web Cockpit HUD launched successfully!{RESET}")
                    print(f"{CYAN}📡 Uplink URL: http://127.0.0.1:{port}{RESET}")
                    print(f"{DIM}(Web HUD is running concurrently in the background; you can continue typing REPL commands!){RESET}\n")
                except OSError as err:
                    print(f"{YELLOW}Cockpit server notice:{RESET} Port {port} already bound or accessible at http://127.0.0.1:{port}")
            else:
                print(f"{CYAN}Holographic Web Cockpit is currently running at http://127.0.0.1:{port}{RESET}")

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
            amt = int(parts[1]) if len(parts) > 1 else 25
            ok, msg = engine.repair_hull(amt)
            print((GREEN if ok else RED) + msg + RESET)
            storage.save(engine.state)
        elif cmd == "refuel":
            amt = int(parts[1]) if len(parts) > 1 else 20
            ok, msg = engine.refuel(amt)
            print((GREEN if ok else RED) + msg + RESET)
            storage.save(engine.state)
        elif cmd == "help":
            print(f"{BOLD}Available subcommands:{RESET}")
            print("  status                         - Telemetry, fleet roster, and subsystem readouts")
            print("  chart / map                    - Hyperlane network & orbital bodies")
            print("  jump <system_id>               - Hyperspace jump to adjacent star")
            print("  orbit <body_id>                - Enter orbit around planet or station")
            print("  scan                           - Sensor sweep of orbiting body")
            print("  market                         - Check commodity trade prices")
            print("  buy <comm> <qty>               - Buy commodities from local exchange")
            print("  sell <comm> <qty>              - Sell commodities to local exchange")
            print("  fleet [harvest|buy|deploy]     - Autonomous fleet assets and drone yields")
            print("  upgrades [buy <id>]            - Station hardware upgrades and module shop")
            print("  combat <fire|absorb|evade|flee>- Tactical maneuvers during hostile intercepts")
            print("  power <e> <s> <se> <w>         - Distribute 100% reactor power")
            print("  anomaly <choice_id>            - Resolve active spatial encounter")
            print("  repair [amt]                   - Repair hull integrity at station")
            print("  refuel [amt]                   - Replenish quantum fuel at station")
            print("  serve [--port 8080]            - Launch concurrent Web Cockpit HUD")
            print("  exit / quit                    - Close interactive link")
        else:
            print(f"{RED}Unknown command '{cmd}'. Type 'help' for command matrix.{RESET}")

    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Main CLI entrypoint."""
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="voidfarer",
        description="VoidFarer: Autonomous Deep-Space Fleet, Procedural Galaxy & Holographic Cockpit Simulator",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("status", help="Print ship telemetry and navigation status")
    subparsers.add_parser("chart", help="Display star systems and orbital bodies")
    subparsers.add_parser("market", help="Display local commodity exchange quotes")
    subparsers.add_parser("scan", help="Execute sensor scan on orbiting body")
    subparsers.add_parser("repl", help="Launch interactive terminal cockpit")

    fleet_p = subparsers.add_parser("fleet", help="Autonomous fleet and drone operations")
    fleet_p.add_argument("action", nargs="?", default="list", choices=["list", "harvest", "buy", "deploy"])
    fleet_p.add_argument("arg1", nargs="?", help="Drone type or drone ID")
    fleet_p.add_argument("arg2", nargs="?", help="Target star system ID")

    upg_p = subparsers.add_parser("upgrades", help="Station hardware modules arsenal")
    upg_p.add_argument("action", nargs="?", default="list", choices=["list", "buy"])
    upg_p.add_argument("upgrade_id", nargs="?", help="Upgrade ID to purchase")

    combat_p = subparsers.add_parser("combat", help="Execute tactical combat maneuver")
    combat_p.add_argument("action", choices=["fire", "absorb", "evade", "flee"], help="Tactical maneuver")

    jump_p = subparsers.add_parser("jump", help="Jump to adjacent star system")
    jump_p.add_argument("system_id", help="Target star system ID")

    orbit_p = subparsers.add_parser("orbit", help="Enter orbit around celestial body")
    orbit_p.add_argument("body_id", help="Target body ID")

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
    rep_p.add_argument("--amount", type=int, default=25, help="Hull points to restore")

    ref_p = subparsers.add_parser("refuel", help="Replenish quantum fuel")
    ref_p.add_argument("--amount", type=int, default=20, help="Fuel units to add")

    serve_p = subparsers.add_parser("serve", help="Launch Holographic Web Cockpit server")
    serve_p.add_argument("--port", type=int, default=8080, help="HTTP server port")
    serve_p.add_argument("--host", default="127.0.0.1", help="HTTP server host")

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 0

    engine, storage = _get_engine()

    if args.command == "status":
        return cmd_status(engine)
    elif args.command == "chart":
        return cmd_chart(engine)
    elif args.command == "market":
        return cmd_market(engine)
    elif args.command == "fleet":
        parts = ["fleet"]
        if args.action != "list":
            parts.append(args.action)
            if args.arg1:
                parts.append(args.arg1)
            if args.arg2:
                parts.append(args.arg2)
        return cmd_fleet(engine, storage, parts)
    elif args.command == "upgrades":
        parts = ["upgrades"]
        if args.action != "list":
            parts.append(args.action)
            if args.upgrade_id:
                parts.append(args.upgrade_id)
        return cmd_upgrades(engine, storage, parts)
    elif args.command == "combat":
        return cmd_combat(engine, storage, ["combat", args.action])
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
        ok, msg = engine.repair_hull(args.amount)
        print((GREEN if ok else RED) + msg + RESET)
        storage.save(engine.state)
        return 0 if ok else 1
    elif args.command == "refuel":
        ok, msg = engine.refuel(args.amount)
        print((GREEN if ok else RED) + msg + RESET)
        storage.save(engine.state)
        return 0 if ok else 1
    elif args.command == "repl":
        return cmd_repl(engine, storage)
    elif args.command == "serve":
        run_server(engine, storage, port=args.port, host=args.host)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
