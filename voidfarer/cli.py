"""Command-line interface and interactive terminal REPL for VoidFarer."""

from __future__ import annotations

import argparse
import os
import sys
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
from voidfarer.server import run_server
from voidfarer.storage import StorageManager

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
{DIM}Autonomous Deep-Space Fleet & Procedural Galaxy Simulator v0.1.0{RESET}
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
    """Display current flagship telemetry and star system status."""
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
    print(f"╠════ NAVIGATION COORDINATES ═════════════════════════════════════════╣{RESET}")
    print(f"║ System:    {CYAN}{cur_sys.name:<22}{RESET} Faction:  {cur_sys.faction:<22} ║")
    print(f"║ Security:  {GREEN if cur_sys.security > 0.5 else RED}{cur_sys.security * 100:>5.1f}% [{('HIGH' if cur_sys.security > 0.7 else ('MED' if cur_sys.security > 0.3 else 'ANARCHY'))}]{RESET}       Corridors: {', '.join(cur_sys.connections):<22} ║")
    orb_name = f"{body.name} [{body.body_type}]" if body else "Deep Space Transit"
    print(f"║ Orbit:     {orb_name:<57} ║")
    print(f"╚═════════════════════════════════════════════════════════════════════╝{RESET}")

    if engine.state.active_anomaly:
        anom = engine.state.active_anomaly
        print(f"\n{RED}{BOLD}⚠️  PROXIMITY ALERT: {anom.title}{RESET}")
        print(f"{DIM}{anom.description}{RESET}")
        print(f"{YELLOW}Resolution Choices:{RESET}")
        for c in anom.choices:
            req = f"[{c.required_power.upper()} >= {c.min_power_threshold}%]" if c.required_power != "none" else "[No Check]"
            print(f"  • {BOLD}{c.choice_id}{RESET}: {c.text} {DIM}{req}{RESET}")

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


def cmd_repl(engine: SimulationEngine, storage: StorageManager) -> int:
    """Launch interactive terminal command session."""
    print(BANNER)
    print(f"{GREEN}Interactive sub-space link established. Type 'help' or 'exit'.{RESET}\n")
    while True:
        try:
            line = input(f"{CYAN}voidfarer [{engine.state.ship.current_system_id}]> {RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting VoidFarer link.")
            break

        if not line:
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
            print("  status                   - Telemetry and subsystem readouts")
            print("  chart / map              - Hyperlane network & orbital bodies")
            print("  jump <system_id>         - Hyperspace jump to adjacent star")
            print("  orbit <body_id>          - Enter orbit around planet or station")
            print("  scan                     - Sensor sweep of orbiting body")
            print("  market                   - Check commodity trade prices")
            print("  buy <comm> <qty>         - Buy commodities from local exchange")
            print("  sell <comm> <qty>        - Sell commodities to local exchange")
            print("  power <e> <s> <se> <w>   - Distribute 100% reactor power")
            print("  anomaly <choice_id>      - Resolve active spatial encounter")
            print("  repair [amt]             - Repair hull integrity at station")
            print("  refuel [amt]             - Replenish quantum fuel at station")
            print("  exit / quit              - Close interactive link")
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
