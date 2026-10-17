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

