# Codebase Map & Symbol Catalog 🗺️

> **AUTO-GENERATED & VERIFIED BY `scripts/update_knowledge_base.py`**
> This document provides an automated, up-to-date registry of all modules, classes, and exported functions across this repository.

---

## 📊 Codebase Metrics
- **Total Python Modules**: `35`
- **Total Classes**: `89`
- **Total Top-Level Functions**: `68`
- **Total Class Methods**: `478`
- **Total Source Lines**: `13655`

---

## 📦 Modules & Exported Symbols

### [`tests/__init__.py`](tests/__init__.py)
> *VoidFarer test suite package.*

**Size**: `1` lines (`36` bytes)

---

### [`tests/test_ai_and_calendar.py`](tests/test_ai_and_calendar.py)
> *Regression tests for adaptive enemy AI, expanded systems, and calendar dates.*

**Size**: `197` lines (`7587` bytes)

**Classes:**
- `class TestAdaptiveEnemyAI`
  - Method `.test_defensive_profile_braces_against_player_combo()`
  - Method `.test_opportunist_executes_wounded_player()`
  - Method `.test_adaptive_profile_disrupts_high_combo()`
  - Method `.test_warlord_regenerates_when_wounded()`
  - Method `.test_generated_enemies_carry_ai_profile_and_intent()`
  - Method `.test_ai_fields_round_trip_through_save_data()`
  - Method `._combat_engine(intent, profile, player_combo)`
  - Method `.test_brace_reduces_player_strike_damage()`
  - Method `.test_execute_increases_counter_battery_damage()`
  - Method `.test_evade_can_make_player_strike_miss()`
  - Method `.test_ai_chooses_next_intent_from_player_combo()`
- `class TestExpandedGalaxy`
  - Method `.test_every_system_has_at_least_five_planets_and_a_station()`
  - Method `.test_sol_station_id_remains_stable()`
- `class TestCalendarDate`
  - Method `.test_initial_calendar_date()`
  - Method `.test_calendar_date_advances_and_rolls_over_months()`
  - Method `.test_time_payload_exposes_date()`
  - Method `.test_engine_tick_updates_calendar_date()`

---

### [`tests/test_batch_launchers.py`](tests/test_batch_launchers.py)
> *Regression tests for the Windows batch launchers (``play.bat``, ``voidfarer.bat``).*

**Size**: `57` lines (`2141` bytes)

**Classes:**
- `class TestLauncherLineEndings` - *cmd.exe parses CRLF batches reliably; lone LF endings can abort a script mid-file.*
  - Method `._assert_crlf(path)`
  - Method `.test_play_bat_uses_crlf_line_endings()`
  - Method `.test_voidfarer_bat_uses_crlf_line_endings()`
- `class TestLauncherMenu` - *The interactive mission menu must survive its ASCII banner and exit cleanly.*
  - Method `.test_menu_choice_zero_renders_and_exits_cleanly()`

---

### [`tests/test_cli.py`](tests/test_cli.py)
> *Unit tests for command-line arguments and subcommands.*

**Size**: `198` lines (`8509` bytes)

**Classes:**
- `class _IsolatedCliTestCase` - *Base for CLI tests: redirect default storage away from the player's live save.*
  - Method `.setUp()`
- `class TestCLI`
  - Method `.test_cli_help()`
  - Method `.test_cli_status()`
  - Method `.test_cli_chart()`
  - Method `.test_cli_power()`
  - Method `.test_cli_combat_accepts_documented_actions()`
  - Method `.test_cli_shipyard_subcommands_parse()`
  - Method `.test_cli_corporations_alias()`
  - Method `.test_cli_repair_and_refuel_accept_positional_amounts()`
  - Method `.test_cli_fleet_list()`
  - Method `.test_cli_upgrades_list()`
  - Method `.test_cli_contracts_list()`
  - Method `.test_cli_mastery_status()`
  - Method `.test_cli_relics()`
  - Method `.test_cli_streak()`
- `class TestCLIStabilization` - *Regression tests for numeric guards and the station consumable terminal.*
  - Method `.setUp()`
  - Method `.test_inventory_jettison_non_numeric_quantity_is_handled()`
  - Method `.test_inventory_buy_usage_without_item_id()`
  - Method `.test_inventory_buy_consumable_at_station()`
  - Method `.test_repl_repair_and_refuel_reject_non_numeric_amounts()`
- `class TestCLIRelicsWithRecoveredRelics` - *A save that already has relics must render the vault and modifiers (regression).*
  - Method `.test_relics_command_with_recovered_relics()`
  - Method `.test_cli_frontier_commands()`

---

### [`tests/test_cockpit_layout.py`](tests/test_cockpit_layout.py)
> *Layout regression tests for the holographic web cockpit (index.html / style.css / app.js).*

**Size**: `327` lines (`13480` bytes)

**Classes:**
- `class _DomNode` - *Minimal element tree node built from html.parser events.*
  - Method `.__init__(tag, attrs)`
  - Method `.find_by_id(element_id)`
  - Method `.ancestors()`
  - Method `.has_class(name)`
- `class _TreeBuilder`
  - Method `.__init__()`
  - Method `._append(tag, attrs, closing)`
  - Method `.handle_starttag(tag, attrs)`
  - Method `.handle_startendtag(tag, attrs)`
  - Method `.handle_endtag(tag)`
- `class TestCockpitLayout`
  - Method `.setUpClass()`
  - Method `._rule_body(selector)`
  - Method `._ancestor_ids(node)`
  - Method `._document_order()`
  - Method `.test_telemetry_log_sits_in_the_lower_right_deck()`
  - Method `.test_lower_right_deck_contains_only_the_telemetry_log()`
  - Method `.test_lower_right_deck_anchors_its_content_to_the_bottom()`
  - Method `.test_telemetry_log_carries_a_hide_button()`
  - Method `.test_log_collapse_style_and_toggle_wiring_exist()`
  - Method `.test_chrono_deck_is_the_last_block_of_the_top_bar()`
  - Method `.test_chrono_deck_is_pushed_to_the_right_edge()`
  - Method `.test_terminal_lives_in_the_left_deck()`
  - Method `.test_terminal_uses_a_vertical_rail_beside_the_content()`
  - Method `.test_center_column_stacks_radar_above_reactor()`
  - Method `.test_context_alerts_live_in_the_center_column()`
- `class TestCockpitRuntimeContracts` - *Static regression checks for runtime wiring that the DOM structure cannot exercise.*
  - Method `.setUpClass()`
  - Method `.test_pointer_coordinates_are_scaled_to_canvas_space()`
  - Method `.test_drag_suppresses_the_following_click()`
  - Method `.test_preload_renderers_guard_against_missing_state()`
  - Method `.test_power_sliders_sync_from_authoritative_state()`
  - Method `.test_cargo_meter_uses_manifest_volume()`
  - Method `.test_scan_sound_reads_discovery_contract()`
  - Method `.test_canvas_uses_literal_colors_not_css_variables()`
  - Method `.test_chrono_displays_calendar_date()`
- `class TestFrontierCockpitUI`
  - Method `.setUpClass()`
  - Method `.test_main_menu_and_windows_exist()`
  - Method `.test_frontier_tabs_and_radar_overlay_exist()`
  - Method `.test_frontier_renderers_are_wired()`
  - Method `.test_radar_background_is_black()`
- `class TestCockpitEscaping`
  - Method `.setUpClass()`
  - Method `.test_dynamic_server_data_is_escaped()`
  - Method `.test_faction_colors_are_whitelisted()`

---

### [`tests/test_economy.py`](tests/test_economy.py)
> *Unit tests for the dynamic galactic economy, stockpiles, events, and trade routes.*

**Size**: `106` lines (`4594` bytes)

**Classes:**
- `class TestInitialEconomy` - *Verify baseline economy generation across the galaxy.*
  - Method `.setUp()`
  - Method `.test_every_system_has_a_market()`
  - Method `.test_stockpiles_are_positive()`
  - Method `.test_initial_event_is_seeded()`
- `class TestTickGlobalEconomy` - *Verify production, consumption, event decay, and last-updated tracking.*
  - Method `.setUp()`
  - Method `.test_production_and_consumption_rates_apply()`
  - Method `.test_last_updated_tick_advances()`
  - Method `.test_events_decay_and_expire()`
- `class TestDynamicMarketQuotes` - *Verify localized quote computation and profitable route discovery.*
  - Method `.setUp()`
  - Method `.test_quote_has_positive_spread()`
  - Method `.test_events_shift_local_prices()`
  - Method `.test_trade_routes_are_sorted_and_cross_system()`

---

### [`tests/test_engine.py`](tests/test_engine.py)
> *Unit tests for simulation engine state transitions, flight, upgrades, fleet, and combat.*

**Size**: `367` lines (`15465` bytes)

**Classes:**
- `class TestEngine`
  - Method `.setUp()`
  - Method `.test_initial_state()`
  - Method `.test_jump_valid_and_invalid()`
  - Method `.test_orbit_and_scan()`
  - Method `.test_power_routing()`
  - Method `.test_trade_buy_and_sell()`
  - Method `.test_upgrades_purchase_and_bonus()`
  - Method `.test_fleet_drone_operations()`
  - Method `.test_combat_resolution_victory_and_flee()`
  - Method `.test_contracts_progression_and_claiming()`
  - Method `.test_pilot_mastery_and_talents()`
  - Method `.test_expedition_streak_and_combos()`
  - Method `.test_tick_decays_combat_ability_cooldown()`
  - Method `.test_trade_respects_cargo_volume_not_just_units()`
  - Method `.test_available_chassis_excludes_current_ship()`
  - Method `.test_starter_chassis_cannot_be_repurchased()`
  - Method `.test_sell_upgrade_removes_module_name_from_manifest()`
  - Method `.test_buy_item_requires_station_and_consumable()`

---

### [`tests/test_engine_hardening.py`](tests/test_engine_hardening.py)
> *Regression tests for audit-driven engine hardening.*

**Size**: `178` lines (`7324` bytes)

**Classes:**
- `class EngineHardeningTest`
  - Method `.setUp()`
  - Method `._set_ship(**kwargs)`
  - Method `._orbit_station()`
  - Method `.test_repair_rejects_zero_and_negative_amounts()`
  - Method `.test_refuel_rejects_zero_and_negative_amounts()`
  - Method `.test_upgrade_recompute_preserves_relic_max_hull()`
  - Method `.test_chassis_purchase_preserves_relic_max_shield()`
  - Method `.test_scan_awards_random_max_hull_relic_immediately()`
  - Method `.test_scan_and_step_preserve_dominant_corp()`
  - Method `.test_replacing_an_occupied_upgrade_slot_is_rejected()`
  - Method `.test_drone_harvest_rejects_when_cargo_hold_is_full()`
  - Method `.test_repeat_scan_of_surveyed_body_awards_no_bounty()`
  - Method `.test_story_choice_updates_faction_standing()`
  - Method `.test_buy_drone_rejects_unknown_system()`
  - Method `.test_cargo_grant_clamps_to_free_volume()`
  - Method `.test_combat_salvage_respects_full_cargo_hold()`

---

### [`tests/test_equipment_bonuses.py`](tests/test_equipment_bonuses.py)
> *Regression tests for hardware module stat bonuses and chassis specialty perks.*

**Size**: `173` lines (`7518` bytes)

**Classes:**
- `class TestEquipmentBonusAggregation` - *Verify the pure aggregation rules without touching engine state.*
  - Method `.setUp()`
  - Method `._bonuses(**ship_kwargs)`
  - Method `.test_bare_starter_ship_has_neutral_bonuses()`
  - Method `.test_engine_module_reduces_fuel_multiplier()`
  - Method `.test_sensor_modules_add_scan_and_relic_bonuses()`
  - Method `.test_utility_modules_expose_shield_and_ecm_bonuses()`
  - Method `.test_chassis_specialty_perks_are_mapped()`
- `class TestEngineEquipmentIntegration` - *Verify the engine actually consumes the aggregated bonuses.*
  - Method `._jump_fuel_used(equipped)`
  - Method `.test_warp_booster_reduces_jump_fuel_burn()`
  - Method `._scan_bounty(equipped)`
  - Method `.test_deep_core_scanner_increases_scan_bounty()`
  - Method `._sell_revenue(ship_class)`
  - Method `.test_freighter_chassis_boosts_trade_margin()`
  - Method `._enemy_hull_after_shot(equipped, ship_class)`
  - Method `.test_weapon_module_and_gunship_chassis_add_combat_damage()`
  - Method `._shield_recharged(equipped)`
  - Method `.test_reactive_shield_regenerator_adds_tick_recharge()`
  - Method `._combat_after_jump(equipped)`
  - Method `.test_ecm_scrambler_reduces_pirate_encounter_chance()`

---

### [`tests/test_factions_and_enemies.py`](tests/test_factions_and_enemies.py)
> *Unit tests for Factions, Corporations, and Enhanced Combat Enemies.*

**Size**: `255` lines (`10181` bytes)

**Classes:**
- `class TestFactionsAndCorporations` - *Test faction registries, corporations, standing calculations, and market modifiers.*
  - Method `.test_canonical_factions_exist()`
  - Method `.test_canonical_corporations_exist()`
  - Method `.test_faction_standing_tiers()`
  - Method `.test_market_modifiers()`
- `class TestEnemiesAndCombatModels` - *Test enemy archetypes, generation, and extended CombatEncounter model.*
  - Method `.test_enemy_archetypes()`
  - Method `.test_generate_system_enemy()`
  - Method `.test_combat_encounter_backward_compatibility()`
  - Method `.test_ship_state_faction_standings_migration()`
  - Method `.test_tactical_combat_shield_and_actions()`
  - Method `.test_combat_victory_faction_standing_shift()`

---

### [`tests/test_frontier_systems.py`](tests/test_frontier_systems.py)
> *Coverage for frontier systems: AI captains, depots, messages, landing, and fleets.*

**Size**: `253` lines (`10977` bytes)

**Classes:**
- `class FrontierBootstrapTest`
  - Method `.setUp()`
  - Method `.test_initial_state_has_captains_depots_and_messages()`
  - Method `.test_save_round_trip_preserves_frontier_state()`
  - Method `.test_quest_panel_contains_story_and_contracts()`
- `class AICaptainTest`
  - Method `.setUp()`
  - Method `.test_ai_trade_moves_captains_and_changes_stockpiles()`
  - Method `.test_hail_increases_trust()`
  - Method `.test_alliance_requires_trust_then_adds_ally()`
  - Method `.test_ai_trade_with_captain_changes_both_cargo_holds()`
- `class DepotTest`
  - Method `.setUp()`
  - Method `.test_deposit_withdraw_and_sell_from_depot()`
- `class QuantumMessageTest`
  - Method `.setUp()`
  - Method `.test_send_and_read_message()`
- `class LandingAndFleetTest`
  - Method `.setUp()`
  - Method `.test_landing_on_habitable_body()`
  - Method `.test_landing_rejected_on_uninhabitable_body()`
  - Method `.test_hire_refit_and_dismiss_mercenary()`
  - Method `.test_drone_stats_survive_ticks_and_deploy()`
- `class TalentBranchTest`
  - Method `.setUp()`
  - Method `.test_tier_two_requires_branch_root()`
  - Method `.test_every_talent_declares_branch_and_tier()`
- `class ProceduralGalaxyTest`
  - Method `.test_new_star_types_moons_and_planet_types()`
  - Method `.test_moon_model_round_trip()`
  - Method `.test_depot_model_round_trip()`
  - Method `.test_quantum_message_model_round_trip()`

---

### [`tests/test_galaxy.py`](tests/test_galaxy.py)
> *Unit tests for procedural galaxy generation, hyperlane mesh, and market quotes.*

**Size**: `52` lines (`1917` bytes)

**Classes:**
- `class TestGalaxy`
  - Method `.test_galaxy_generation_determinism()`
  - Method `.test_hyperlane_connectivity()`
  - Method `.test_market_quotes_calculation()`
  - Method `.test_random_anomaly_generation()`

---

### [`tests/test_inventory.py`](tests/test_inventory.py)
> *Unit tests for the item catalog, cargo manifest, and consumable usage.*

**Size**: `109` lines (`4115` bytes)

**Classes:**
- `class TestItemCatalog` - *Verify catalog integrity, consumable metadata, and fallbacks.*
  - Method `.test_catalog_keys_match_item_ids()`
  - Method `.test_consumables_are_usable_with_effects()`
  - Method `.test_commodities_are_not_usable()`
  - Method `.test_unknown_item_falls_back_to_generic_commodity()`
  - Method `.test_manifest_skips_empty_stacks_and_computes_volume()`
  - Method `.test_cargo_volume_sums_item_footprints()`
- `class TestUseItem` - *Verify consumable effects, clamping, and cargo bookkeeping.*
  - Method `.setUp()`
  - Method `._with_cargo(cargo, **ship_kwargs)`
  - Method `.test_repair_paste_restores_hull_and_consumes_one()`
  - Method `.test_last_repair_paste_leaves_cargo()`
  - Method `.test_repair_paste_clamps_to_max_hull()`
  - Method `.test_use_missing_item_fails()`
  - Method `.test_commodity_cannot_be_consumed()`
  - Method `.test_decoy_requires_active_combat()`

---

### [`tests/test_models.py`](tests/test_models.py)
> *Unit tests for domain state models and frozen DTO serialization.*

**Size**: `323` lines (`10912` bytes)

**Classes:**
- `class TestModels`
  - Method `.test_ship_power_validation()`
  - Method `.test_celestial_body_serialization()`
  - Method `.test_star_system_serialization()`
  - Method `.test_fleet_drone_serialization()`
  - Method `.test_ship_upgrade_serialization()`
  - Method `.test_combat_encounter_serialization()`
  - Method `.test_bounty_contract_serialization()`
  - Method `.test_precursor_relic_serialization()`
  - Method `.test_pilot_mastery_serialization()`
  - Method `.test_game_state_roundtrip()`
  - Method `.test_tutorial_and_story_models_serialization()`

---

### [`tests/test_perks_relics_rep.py`](tests/test_perks_relics_rep.py)
> *Regression tests for faction perks, enemy reputation rewards, and multi-stat relics.*

**Size**: `135` lines (`5862` bytes)

**Classes:**
- `class FactionPerkTest`
  - Method `.setUp()`
  - Method `._set_standing(faction_id, standing)`
  - Method `.test_friendly_faction_grants_repair_discount()`
  - Method `.test_allied_faction_grants_free_refuel()`
  - Method `.test_syndicate_standing_adds_trade_margin()`
  - Method `.test_faction_specific_tier_perks()`
- `class EnemyRepRewardTest`
  - Method `._victory(archetype_id)`
  - Method `.test_warlord_rep_rewards_are_applied()`
  - Method `.test_corporate_rep_rewards_update_corp_standings()`
- `class MultiStatRelicTest`
  - Method `.test_relic_bonuses_round_trip()`
  - Method `.test_eye_of_void_boosts_laser_and_scan()`
  - Method `.test_core_matrix_boosts_fuel_and_laser()`
  - Method `.test_sentinel_matrix_applies_hull_and_shield()`
- `class BackgroundServerTest`
  - Method `.test_background_server_starts_and_stops()`

---

### [`tests/test_server.py`](tests/test_server.py)
> *Unit and integration tests for embedded HTTP server REST endpoints.*

**Size**: `239` lines (`9981` bytes)

**Classes:**
- `class TestServer`
  - Method `.setUpClass()`
  - Method `.tearDownClass()`
  - Method `.setUp()`
  - Method `._get(path)`
  - Method `._post(path, body)`
  - Method `._post_raw(path, payload, content_type)`
  - Method `.test_get_static_index()`
  - Method `.test_get_api_state()`
  - Method `.test_get_api_galaxy()`
  - Method `.test_post_power()`
  - Method `.test_post_orbit_and_scan()`
  - Method `.test_post_drone_and_upgrade_endpoints()`
  - Method `.test_contracts_and_relics_endpoints()`
  - Method `.test_malformed_json_is_rejected()`
  - Method `.test_non_object_json_is_rejected()`
  - Method `.test_wrong_field_type_is_rejected()`
  - Method `.test_negative_repair_and_refuel_are_rejected()`
  - Method `.test_trade_rejects_non_boolean_is_buy()`
  - Method `.test_step_rejects_negative_and_non_finite_delta()`
  - Method `.test_scan_response_exposes_relic_and_near_miss()`
  - Method `.test_reset_is_deterministic_for_a_seed()`
  - Method `.test_get_api_shipyard_excludes_current_chassis()`
  - Method `.test_post_inventory_buy_rejects_non_numeric_quantity()`
  - Method `.test_frontier_endpoints()`
  - Method `.test_landing_and_depot_endpoints()`
  - Method `.test_save_load_delete_endpoints()`

---

### [`tests/test_storage.py`](tests/test_storage.py)
> *Unit tests for atomic persistence, crash safety, and shadow backup recovery.*

**Size**: `106` lines (`4397` bytes)

**Classes:**
- `class TestStorage`
  - Method `.setUp()`
  - Method `.test_save_and_load()`
  - Method `.test_corrupt_file_quarantine_and_backup_recovery()`
  - Method `.test_failed_atomic_replace_raises_and_preserves_previous_save()`
  - Method `.test_schema_invalid_primary_falls_back_to_backup()`
  - Method `.test_invalid_utf8_does_not_crash_loading()`

---

### [`tests/test_story.py`](tests/test_story.py)
> *Unit and integration tests for Cadet Flight Academy and The Precursor Cipher story campaign.*

**Size**: `386` lines (`15599` bytes)

**Classes:**
- `class TestStoryAndTutorial`
  - Method `.setUp()`
  - Method `.tearDown()`
  - Method `.test_tutorial_initial_state()`
  - Method `.test_tutorial_progressive_milestones()`
  - Method `.test_tutorial_skip_and_reset()`
  - Method `.test_story_initialization_and_first_chapter()`
  - Method `.test_story_arrival_transmissions()`
  - Method `.test_story_choices_and_factions()`
  - Method `.test_story_serialization_roundtrip()`
  - Method `.test_story_target_system_enforcement_and_full_campaign()`
  - Method `.test_relic_passive_multipliers_integration()`
  - Method `.test_cli_tutorial_and_story_commands()`
  - Method `.test_cli_main_entrypoint()`
- `class TestServerStoryAndTutorial`
  - Method `.setUpClass()`
  - Method `.tearDownClass()`
  - Method `._get(path)`
  - Method `._post(path, body)`
  - Method `.test_server_tutorial_endpoints()`
  - Method `.test_server_story_endpoints()`

---

### [`tests/test_time_and_ticks.py`](tests/test_time_and_ticks.py)
> *Comprehensive automated test suite for Time, Ticks, and Temporal Controls in VoidFarer.*

**Size**: `318` lines (`12750` bytes)

**Classes:**
- `class TestTimeStateModel` - *Verify TimeState dataclass serialization, defaults, and legacy migration.*
  - Method `.test_default_values()`
  - Method `.test_to_dict_and_from_dict()`
  - Method `.test_gamestate_backward_compatibility()`
- `class TestSimulationEngineTimeAndTicks` - *Verify time progression, orbital dynamics, shield regen, and drone harvests.*
  - Method `.setUp()`
  - Method `.test_single_tick()`
  - Method `.test_multi_tick()`
  - Method `.test_orbital_angle_progression()`
  - Method `.test_passive_shield_recharge()`
  - Method `.test_fleet_drone_harvest_accumulation()`
  - Method `.test_time_control_pause_resume()`
  - Method `.test_time_speed_settings()`
  - Method `.test_step_time()`
  - Method `.test_status_snapshot_contains_time()`
  - Method `.test_pause_resume_speed_memory()` - *Verify speed rate (e.g. 5x) is retained across pause and resume cycles.*
  - Method `.test_jump_advances_transit_time()` - *Verify interstellar hyperspace jumps advance cosmic time and orbits by 2 ticks (12 hours).*
  - Method `.test_state_preservation_across_operations()` - *Verify operations like orbit, scan, and power routing never wipe temporal clock state.*
- `class TestServerTimeEndpoints` - *Verify REST API time endpoints: /api/time, /api/time/step, /api/time/speed, etc.*
  - Method `.setUpClass()`
  - Method `.tearDownClass()`
  - Method `._get(path)`
  - Method `._post(path, body)`
  - Method `.test_get_api_time()`
  - Method `.test_post_api_time_step()`
  - Method `.test_post_api_time_speed()`
  - Method `.test_post_api_time_pause_and_resume()`

---

### [`tests/test_transit_civ_events.py`](tests/test_transit_civ_events.py)
> *Tests for in-system transit (TravelState), planetary civilization metadata, and cockpit GameEvents.*

**Size**: `147` lines (`5998` bytes)

**Classes:**
- `class TestTransitCivEvents` - *Verify TravelState, planetary faction/population/government, and GameEvent lifecycles.*
  - Method `.setUp()`
  - Method `.test_gamestate_roundtrip_preserves_events_travel_and_civ_metadata()`
  - Method `.test_galaxy_generates_planetary_civilization_metadata()`
  - Method `.test_sublight_transit_progresses_and_completes_on_tick()`
  - Method `.test_quantum_in_system_transit_consumes_fuel_and_arrives_next_tick()`
  - Method `.test_start_travel_validation_guards()`
  - Method `.test_event_emission_and_dismissal()`
  - Method `.test_cli_travel_and_events()`

---

### [`voidfarer/__init__.py`](voidfarer/__init__.py)
> *VoidFarer: Autonomous deep-space fleet, procedural galaxy, and holographic cockpit simulation engine.*

**Size**: `4` lines (`159` bytes)

---

### [`voidfarer/cli.py`](voidfarer/cli.py)
> *Command-line interface and interactive terminal REPL for VoidFarer.*

**Size**: `1623` lines (`83173` bytes)

**Functions:**
- `def _get_engine(storage_dir)` - *Initialize or restore simulation engine from disk.*
- `def _bar(current, maximum, length, color)` - *Generate ANSI filled progress bar.*
- `def cmd_status(engine)` - *Display current flagship telemetry, fleet roster, and star system status.*
- `def cmd_time(engine, storage, argv)` - *Manage simulation cosmic time, ticks, and speed controls.*
- `def cmd_chart(engine)` - *Print galaxy starmap and celestial bodies within current system.*
- `def cmd_market(engine)` - *Display commodity prices and supply/demand at the current orbital body.*
- `def cmd_economy(engine)` - *Display galactic macroeconomic conditions, active events, and lucrative trade routes.*
- `def cmd_inventory(engine, storage, parts)` - *Display and manage ship cargo manifest, usable consumables, and hold capacity.*
- `def cmd_shipyard(engine, storage, parts)` - *Orbital shipyard: inspect ship chassis upgrades, purchase vessels, and sell modules.*
- `def cmd_fleet(engine, storage, parts)` - *Manage autonomous fleet drones, mining escorts, and harvest yields.*
- `def cmd_quests(engine)`
- `def cmd_ai(engine, storage, parts)`
- `def cmd_messages(engine, storage, parts)`
- `def cmd_depot(engine, storage, parts)`
- `def cmd_land(engine, storage, body_id)`
- `def cmd_mercs(engine, storage, parts)`
- `def cmd_allies(engine, storage, parts)`
- `def cmd_upgrades(engine, storage, parts)` - *Inspect and purchase hardware modules from station arsenal.*
- `def cmd_combat(engine, storage, parts)` - *Execute tactical combat maneuvers during hostile intercepts.*
- `def cmd_factions(engine, storage, parts)` - *Inspect galactic sovereign factions, standings, active territory, and diplomatic perks.*
- `def cmd_corporations(engine, storage, parts)` - *Inspect interstellar megacorporations, commercial specialties, and corporate standing.*
- `def cmd_contracts(engine, storage, parts)` - *Inspect dynamic sector bounties, claim completed contracts, and trigger fresh assignments.*
- `def cmd_mastery(engine, storage, parts)` - *Display pilot progression rank, talent tree specializations, and allocate perks.*
- `def cmd_relics(engine)` - *Display recovered ancient Precursor relics and passive fleet bonuses.*
- `def cmd_streak(engine)` - *Display current expedition jump streak and active loss aversion multiplier.*
- `def cmd_tutorial(engine, storage, parts)` - *Cadet Flight Academy progressive tutorial system.*
- `def cmd_story(engine, storage, parts)` - *The Precursor Cipher: Branching episodic space opera campaign.*
- `def cmd_repl(engine, storage)` - *Launch interactive terminal command session.*
- `def cmd_events(engine, storage, parts)` - *List or dismiss cockpit popup events.*
- `def main(argv)` - *Main CLI entrypoint.*

---

### [`voidfarer/economy.py`](voidfarer/economy.py)
> *Dynamic Global Economy, supply/demand simulation, economic events, and galactic trade network.*

**Size**: `390` lines (`14651` bytes)

**Functions:**
- `def generate_initial_economy(systems, rng)` - *Construct baseline economy state with localized stockpiles and initial macroeconomic conditions.*
- `def tick_global_economy(state, num_ticks, systems, rng)` - *Advance economic simulation: update stockpiles, decrement event clocks, spawn emergent news.*
- `def calculate_dynamic_market_quote(system, body, commodity, economy, faction_standing)` - *Compute precision localized pricing reflecting global stockpile supply/demand and macroeconomic events.*
- `def get_galactic_trade_routes(systems, economy)` - *Compute the most profitable interstellar trade routes across all explored star systems.*

---

### [`voidfarer/enemies.py`](voidfarer/enemies.py)
> *Hostile Enemy Archetypes, Tactical Combat AI, and Procedural Intercept Generation.*

**Size**: `250` lines (`9753` bytes)

**Classes:**
- `class EnemyArchetype` - *Blueprint for procedural hostile intercepts across galactic territories.*

**Functions:**
- `def choose_enemy_intent(profile, special_ability, ability_ready, enemy_hull, enemy_max_hull, enemy_shield, enemy_max_shield, player_hull, player_max_hull, player_shield, player_max_shield, player_combo)` - *Pick the next hostile maneuver from hull, shield, combo, and AI profile state.*
- `def generate_system_enemy(system_id, security, faction, seed)` - *Generate a procedurally balanced CombatEncounter matching star system characteristics.*

---

### [`voidfarer/engine.py`](voidfarer/engine.py)
> *Deterministic state machine and simulation engine for VoidFarer.*

**Size**: `3062` lines (`148156` bytes)

**Classes:**
- `class SimulationEngine` - *Coordinates space flight, star navigation, fleet drones, upgrades, and tactical combat.*
  - Method `.__init__(seed, state)`
  - Method `._bootstrap_frontier()` - *Backfill frontier systems for legacy saves without changing the save schema.*
  - Method `._clone_ship(**kwargs)` - *Create a new ShipState preserving all unspecified telemetry and inventory attributes.*
  - Method `._clone_state(**kwargs)` - *Create a new GameState preserving time, stats, economy, and all unspecified universe fields.*
  - Method `._grant_cargo(cargo, commodity_id, quantity)` - *Add as many units as the hold allows, returning (granted, overflow).*
  - Method `._apply_relic_stat_bonuses(hull, max_hull, shield, max_shield, relics)` - *Raise current and maximum hull/shield for newly acquired permanent relics.*
  - Method `._progress_tutorial(action_type)` - *Advance the Cadet Flight Academy if current step requirement is satisfied.*
  - Method `._award_pilot_xp(amount, current_mastery)` - *Award experience points and compute level promotions and talent points.*
  - Method `._progress_contracts(category, amount)` - *Advance matching active contracts toward completion objectives.*
  - Method `.reset(seed)` - *Reset the simulation to a fresh galaxy with an isolated deterministic RNG stream.*
  - Method `.load_state(state)` - *Replace the live universe with a loaded save and reseed its RNG stream.*
  - Method `._create_initial_state(seed)` - *Construct a fresh universe state rooted at Sol System.*
  - Property `.current_system`
  - Property `.orbiting_body`
  - Method `._process_drone_cycle(ship)` - *Advance autonomous drone harvest cycle across star systems.*
  - Method `.jump(target_system_id)` - *Execute a hyperspace jump to an adjacent star system.*
  - Method `.orbit(body_id)` - *Establish orbital trajectory around a celestial body in the current system.*
  - Method `.start_travel(body_id, mode)` - *Initiate sublight or quantum in-system transit toward a celestial body.*
  - Method `.scan()` - *Perform sensor sweep of current body or local space.*
  - Method `.route_power(engines, shields, sensors, weapons)` - *Adjust reactor power distribution across ship subsystems.*
  - Method `.trade(commodity_id, quantity, is_buy)` - *Execute buy or sell commodity order at orbiting market.*
  - Method `.buy_upgrade(upgrade_id)` - *Purchase and install a hardware upgrade module at an orbital station.*
  - Method `.sell_upgrade(slot)` - *Uninstall and sell an equipped hardware module back to shipyard for credits.*
  - Method `.buy_ship_chassis(chassis_id)` - *Purchase and commission a new spacecraft hull chassis at an orbital shipyard.*
  - Method `.use_item(item_id)` - *Consume a usable item from cargo (nanite repair paste, shield battery, fuel canister, decoy).*
  - Method `.buy_item(item_id, quantity)` - *Purchase consumable items from an orbital station terminal.*
  - Method `.jettison_cargo(item_id, quantity)` - *Jettison cargo into the cosmic vacuum to free hold space.*
  - Method `.buy_drone(drone_type, assigned_system_id)` - *Purchase and commission an autonomous fleet drone.*
  - Method `.deploy_drone(drone_id, target_system_id)` - *Redeploy an autonomous fleet asset to a different star system.*
  - Method `.collect_drone_yield(drone_id)` - *Collect accumulated cargo and research credits from fleet drones.*
  - Method `.combat_action(action)` - *Execute a tactical combat maneuver against an active hostile intercept.*
  - Method `.resolve_anomaly(choice_id)` - *Resolve current deep-space anomaly encounter with power-check validation.*
  - Method `.repair_hull(amount)` - *Repair ship hull integrity at orbital station.*
  - Method `.refuel(amount)` - *Refuel quantum drive at orbital station.*
  - Method `.step_orbits(delta_time)` - *Advance celestial bodies along orbital mechanics paths and cycle fleet drones.*
  - Method `.claim_contract(contract_id)` - *Claim rewards for a fulfilled contract and immediately draw a new assignment.*
  - Method `.unlock_talent(talent_id)` - *Unlock a Pilot Specialization Perk using available talent points.*
  - Method `.make_story_choice(choice_id)` - *Resolve a branching story dilemma in the active campaign chapter.*
  - Method `.skip_tutorial()` - *Skip Cadet Flight Academy and unlock unrestricted operational status.*
  - Method `.reset_tutorial()` - *Reset Cadet Flight Academy to step 1 for revision or retraining.*
  - Property `.current_chassis_id` - *Id of the chassis matching the ship's commissioned class (falls back to the class name).*
  - Method `.get_status_snapshot()` - *Produce a comprehensive JSON serializable telemetry snapshot for the HUD.*
  - Method `.get_quests()` - *Return a unified quest panel view of the story chapter and active contracts.*
  - Method `._find_ai_captain(captain_id)`
  - Method `._replace_ai_captain(captain)`
  - Method `.interact_ai(captain_id, action, commodity_id, quantity)` - *Hail, trade with, hire, or ally with an autonomous captain.*
  - Method `.send_quantum_message(recipient, subject, body)` - *Send an intergalactic quantum-encrypted message.*
  - Method `.mark_message_read(message_id)`
  - Method `._depot_for_current_system()`
  - Method `._require_docked()`
  - Method `.deposit_cargo(item_id, quantity)`
  - Method `.withdraw_cargo(item_id, quantity)`
  - Method `.sell_from_depot(item_id, quantity)`
  - Method `.land_on_body(body_id)` - *Land on a habitable body and collect surface discovery rewards.*
  - Method `.hire_mercenary(merc_id)`
  - Method `.dismiss_fleet_unit(drone_id)`
  - Method `.refit_fleet_unit(drone_id)`
  - Method `.form_alliance(captain_id)`
  - Method `.tick(num_ticks)` - *Advance the simulation universe by num_ticks.*
  - Method `.emit_event(kind, title, message)` - *Create and append a cockpit popup GameEvent.*
  - Method `.dismiss_event(event_id)` - *Mark a cockpit popup GameEvent as dismissed.*
  - Method `.pause_time()` - *Pause simulation temporal clock while preserving current playback rate.*
  - Method `.resume_time()` - *Resume simulation temporal clock restoring previous speed multiplier.*
  - Method `.set_time_speed(speed)` - *Set simulation speed multiplier (0.0x to 10.0x).*
  - Method `.step_time(num_ticks)` - *Advance simulation by a discrete number of ticks.*

---

### [`voidfarer/factions.py`](voidfarer/factions.py)
> *Galactic Factions, Megacorporations, Standings, and Geopolitical Mechanics.*

**Size**: `250` lines (`9842` bytes)

**Classes:**
- `class Faction` - *Sovereign faction or interstellar coalition.*
  - Method `.to_dict()`
  - Method `.from_dict(data)`
- `class Corporation` - *Interstellar megacorporation shaping sector commerce and industrial technology.*
  - Method `.to_dict()`
  - Method `.from_dict(data)`

**Functions:**
- `def get_faction(faction_id)` - *Retrieve canonical faction by ID.*
- `def get_corporation(corp_id)` - *Retrieve canonical corporation by ID.*
- `def get_faction_standing_tier(standing)` - *Calculate standing tier label and active perk description.*
- `def calculate_faction_market_modifier(faction_id, standing)` - *Calculate purchase price multiplier based on faction standing.*
- `def get_faction_id_from_name(name)` - *Resolve faction name to normalized faction ID.*
- `def get_faction_service_perks(faction_id, standing)` - *Return concrete service modifiers for the current standing tier and faction.*

---

### [`voidfarer/frontier.py`](voidfarer/frontier.py)
> *Frontier systems: autonomous captains, depots, mercenaries, and quantum messages.*

**Size**: `176` lines (`6939` bytes)

**Functions:**
- `def generate_ai_captains(systems, seed)` - *Create a deterministic roster of autonomous captains distributed across the galaxy.*
- `def generate_depots(systems)` - *Create one system-local depot per star system.*
- `def generate_welcome_messages(tick)` - *Seed the inbox with onboarding quantum messages.*
- `def _adjust_stock(market, commodity_id, delta)`
- `def simulate_ai_trade(captains, economy, systems, rng)` - *Move AI traders between systems and mutate local stockpiles through buys and sells.*

---

### [`voidfarer/galaxy.py`](voidfarer/galaxy.py)
> *Procedural galaxy generator, celestial orbital mechanics, and market economy.*

**Size**: `545` lines (`25177` bytes)

**Classes:**
- `class GalaxyGenerator` - *Generates deterministic star systems, celestial bodies, and hyperlane corridors.*
  - Method `.__init__(seed)`
  - Method `.generate_galaxy()` - *Generate connected star systems across the sector.*
  - Method `._generate_bodies(sys_id, sys_name, spectral, faction)` - *Generate central star and orbiting planetary bodies.*
  - Method `._build_hyperlanes(systems)` - *Calculate hyperlane network ensuring a fully connected graph.*
  - Method `.get_market_quotes(system, body)` - *Compute localized commodity market pricing based on archetype and security.*
  - Method `.get_random_anomaly(seed)` - *Select and instantiate a deep-space anomaly event.*

---

### [`voidfarer/inventory.py`](voidfarer/inventory.py)
> *Inventory items, consumables, and cargo management.*

**Size**: `180` lines (`5784` bytes)

**Classes:**
- `class InventoryItem` - *Itemized inventory item manifest (trade commodity or usable space consumable).*
  - Method `.to_dict()`

**Functions:**
- `def get_item_info(item_id)` - *Retrieve item metadata, falling back to a default commodity if unlisted.*
- `def calculate_cargo_volume(cargo)` - *Total hold volume currently occupied by inventory cargo.*
- `def get_inventory_manifest(cargo)` - *Compute detailed inventory manifest itemizing quantities, volume footprint, and usability.*

---

### [`voidfarer/models.py`](voidfarer/models.py)
> *Domain state models and frozen data transfer objects for VoidFarer.*

**Size**: `1267` lines (`45031` bytes)

**Classes:**
- `class Moon` - *Natural satellite orbiting a planet.*
  - Method `.to_dict()`
  - Method `.from_dict(data)`
- `class CelestialBody` - *Represents a planetary, stellar, or orbital body in a star system.*
  - Method `.to_dict()`
  - Method `.from_dict(data)`
- `class StarSystem` - *Represents a star system with celestial bodies and hyperlane links.*
  - Method `.to_dict()`
  - Method `.from_dict(data)`
- `class Commodity` - *Trade goods and planetary resources.*
- `class MarketQuote` - *Current price quotation for a commodity at a local market.*
- `class ShipPower` - *Reactor power distribution across primary subsystems (sum <= 100).*
  - Method `.__post_init__()`
  - Method `.to_dict()`
  - Method `.from_dict(data)`
- `class AnomalyChoice` - *Player decision branch for resolving a deep-space anomaly encounter.*
  - Method `.to_dict()`
  - Method `.from_dict(data)`
- `class AnomalyEncounter` - *Procedurally triggered deep-space anomaly event.*
  - Method `.to_dict()`
  - Method `.from_dict(data)`
- `class FleetDrone` - *Autonomous fleet asset deployed to star systems for mining, scouting, or escort.*
  - Method `.to_dict()`
  - Method `.from_dict(data)`
- `class AICaptain` - *Persistent autonomous captain that trades, hails, allies, or fights.*
  - Method `.to_dict()`
  - Method `.from_dict(data)`
- `class Depot` - *System-local cargo depot that can hold and sell commodities.*
  - Method `.to_dict()`
  - Method `.from_dict(data)`
- `class QuantumMessage` - *Intergalactic quantum-encrypted message stored in the ship inbox.*
  - Method `.to_dict()`
  - Method `.from_dict(data)`
- `class ShipUpgrade` - *Modular hardware upgrade installed on flagship.*
  - Method `.to_dict()`
  - Method `.from_dict(data)`
- `class CombatEncounter` - *Hostile deep-space pirate or automated intercept encounter.*
  - Method `.to_dict()`
  - Method `.from_dict(data)`
- `class BountyContract` - *Dynamic mission contract leveraging Zeigarnik task completion tension.*
  - Method `.to_dict()`
  - Method `.from_dict(data)`
- `class PrecursorRelic` - *Ancient artifact dropped via variable ratio schedule with passive multipliers.*
  - Method `.to_dict()`
  - Method `.from_dict(data)`
- `class PilotMastery` - *Self-Determination Theory competence framework: XP, levels, and talent specs.*
  - Method `.to_dict()`
  - Method `.from_dict(data)`
- `class TutorialStep` - *A progressive instructional milestone in the Cadet Flight Academy.*
  - Method `.__post_init__()`
  - Method `.to_dict()`
  - Method `.from_dict(data)`
- `class TutorialState` - *State of the Cadet Flight Academy onboarding progression.*
  - Property `.is_active`
  - Property `.current_step`
  - Method `.to_dict()`
  - Method `.from_dict(data)`
- `class StoryChoice` - *Branching story decision impacting faction alignment, rewards, and narrative path.*
  - Property `.label`
  - Property `.consequence_summary`
  - Method `.to_dict()`
  - Method `.from_dict(data)`
- `class StoryTransmission` - *Character audio dispatch received across the subspace radio array.*
  - Method `.to_dict()`
  - Method `.from_dict(data)`
- `class StoryChapter` - *An episodic narrative chapter in the Precursor Cipher campaign.*
  - Property `.id`
  - Property `.synopsis`
  - Method `.to_dict()`
  - Method `.from_dict(data)`
- `class StoryState` - *Master progression tracker for narrative campaign and faction standings.*
  - Property `.active_act`
  - Property `.current_chapter_id`
  - Property `.current_chapter`
  - Property `.faction_reputation`
  - Method `.to_dict()`
  - Method `.from_dict(data)`
- `class TravelState` - *In-system transit between two celestial bodies.*
  - Method `.progress(current_tick)`
  - Method `.to_dict()`
  - Method `.from_dict(data)`
- `class GameEvent` - *Realtime popup event delivered to the cockpit.*
  - Method `.to_dict()`
  - Method `.from_dict(data)`
- `class ShipState` - *Complete telemetry, resource inventory, and status of the player's flagship.*
  - Method `.to_dict()`
  - Method `.from_dict(data)`
- `class TimeState` - *Universal cosmic stardate, simulation ticks, and time control state.*
  - Property `.current_date` - *In-game calendar date (DD.MM.YYYY), starting 01.01.3042 at tick zero.*
  - Method `.to_dict()`
  - Method `.from_dict(data)`
- `class EconomicEvent` - *Cosmic economic shock, boom, crisis, or embargo shifting commodity supply and prices.*
  - Method `.to_dict()`
  - Method `.from_dict(data)`
- `class SystemMarketState` - *Localized commodity supply stockpiles, demand pressures, and local production.*
  - Method `.to_dict()`
  - Method `.from_dict(data)`
- `class GlobalEconomyState` - *Galactic economy simulation tracking localized market states and macro-economic events.*
  - Method `.to_dict()`
  - Method `.from_dict(data)`
- `class GameState` - *Master simulation universe state container.*
  - Method `.to_dict()`
  - Method `.from_dict(data)`

---

### [`voidfarer/retention.py`](voidfarer/retention.py)
> *Psychological retention mechanics, Precursor relics, dynamic contracts, and pilot mastery.*

**Size**: `385` lines (`13627` bytes)

**Functions:**
- `def generate_contract(rng, category)` - *Procedurally instantiate a fresh BountyContract following Zeigarnik task loops.*
- `def generate_initial_contracts(rng)` - *Generate the starter trio of active contracts across distinct categories.*
- `def roll_relic_drop(rng, bonus_prob, forced_tier, current_system)` - *Execute a Variable Ratio drop roll for Precursor Relics.*
- `def calculate_passive_multipliers(ship)` - *Calculate aggregate multipliers across streak, installed relics, and pilot talents.*

---

### [`voidfarer/server.py`](voidfarer/server.py)
> *Zero-dependency embedded HTTP server and REST API for the VoidFarer Web Cockpit.*

**Size**: `820` lines (`33237` bytes)

**Classes:**
- `class ThreadedHTTPServer` - *Multi-threaded HTTP server handling concurrent HUD telemetry requests.*
- `class VoidFarerHandler` - *Handles REST API actions and serves static cockpit assets.*
  - Method `.log_message(format, *args)` - *Suppress standard access logs for clean terminal output.*
  - Method `._send_json(data, status)`
  - Method `._send_error_json(message, status)`
  - Method `._read_body_json()`
  - Method `.do_OPTIONS()`
  - Method `.do_GET()`
  - Method `.do_POST()`
  - Method `._do_post()`
- `class BackgroundServer` - *Handle for a concurrent server + simulation ticker launched from the REPL.*
  - Method `.__init__(server, server_thread, ticker, stop_event, engine, storage)`
  - Property `.port`
  - Method `.stop()`

**Functions:**
- `def _int_field(body, key, default, minimum)`
- `def _float_field(body, key, default, minimum)`
- `def _bool_field(body, key, default)`
- `def start_background_server(engine, storage, port, host)` - *Launch the cockpit server and simulation ticker without blocking the REPL.*
- `def run_server(engine, storage, port, host, open_browser, enable_ticker)` - *Start local cockpit HTTP server daemon with background temporal ticker.*

---

### [`voidfarer/storage.py`](voidfarer/storage.py)
> *Crash-resilient storage engine and atomic persistence for VoidFarer.*

**Size**: `114` lines (`4255` bytes)

**Classes:**
- `class StorageManager` - *Manages power-loss safe atomic persistence and shadow backups.*
  - Method `.__init__(data_dir)`
  - Method `._write_atomic(target_path, data)` - *Write JSON payload atomically using a unique temporary file, fsync, and shadow backup.*
  - Method `._read_json_file(target_path)`
  - Method `._quarantine(target_path)`
  - Method `.save(state)` - *Atomically persist universe and ship state.*
  - Method `.load()` - *Load game state from disk, quarantining corrupt primary data and trying the backup.*
  - Method `.clear()` - *Remove save file and shadow backup.*

---

### [`voidfarer/story.py`](voidfarer/story.py)
> *Interactive Cadet Flight Academy tutorial and branching narrative campaign systems.*

**Size**: `254` lines (`10405` bytes)

**Functions:**
- `def generate_initial_tutorial()` - *Construct a fresh Cadet Flight Academy tutorial state.*
- `def generate_initial_story()` - *Construct fresh narrative campaign state.*

---

### [`voidfarer/upgrades.py`](voidfarer/upgrades.py)
> *Hardware upgrade catalog, fleet drone definitions, shipyard chassis, and equipment registry.*

**Size**: `408` lines (`14075` bytes)

**Classes:**
- `class ShipChassis` - *Pre-configured spacecraft hull chassis available for purchase at orbital shipyards.*
  - Method `.to_dict()`
  - Method `.from_dict(data)`

**Functions:**
- `def get_upgrade(upgrade_id)`
- `def get_available_upgrades(installed)` - *Return upgrades that have not yet been installed.*
- `def get_chassis(chassis_id)`
- `def get_chassis_for_ship_class(ship_class)` - *Resolve the commissioned chassis from the ship class recorded in the save.*
- `def calculate_equipment_bonuses(ship)` - *Aggregate equipped module and chassis stat bonuses into effective multipliers.*
- `def get_available_chassis(current_chassis_id)` - *Return ship chassis available for purchase (excluding current ship).*
- `def get_sell_value(upgrade_id)` - *Calculate credit trade-in value when selling or uninstalling a hardware module (60% of base cost).*

---
