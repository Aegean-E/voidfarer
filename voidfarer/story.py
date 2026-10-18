"""Interactive Cadet Flight Academy tutorial and branching narrative campaign systems."""

from __future__ import annotations

from typing import Any

from voidfarer.models import (
    PilotMastery,
    PrecursorRelic,
    ShipState,
    StoryChapter,
    StoryChoice,
    StoryState,
    StoryTransmission,
    TutorialState,
    TutorialStep,
)

# Initial 6-step progressive scaffolding for Cadet Flight Academy
INITIAL_TUTORIAL_STEPS: tuple[TutorialStep, ...] = (
    TutorialStep(
        id="step_orbit",
        title="Orbital Insertion",
        instruction="Establish an orbital trajectory around a local celestial body.",
        hint="Run `orbit sol_body_1` or click 'ENTER ORBIT' on the Radar HUD.",
        reward_credits=200,
        reward_xp=80,
    ),
    TutorialStep(
        id="step_scan",
        title="Planetary Sensor Sweep",
        instruction="Perform a deep sensor scan of your orbiting body to analyze resources and detect relics.",
        hint="Run `scan` or click 'SENSOR SCAN' on the top status deck.",
        reward_credits=250,
        reward_xp=100,
    ),
    TutorialStep(
        id="step_power",
        title="Reactor Power Routing",
        instruction="Re-route reactor core output across engines, shields, sensors, and weapons.",
        hint="Run `power 30 25 25 20` or adjust the reactor sliders in Web HUD.",
        reward_credits=200,
        reward_xp=80,
    ),
    TutorialStep(
        id="step_trade",
        title="Orbital Station Commerce",
        instruction="Access a station commodity exchange and execute a buy or sell trade.",
        hint="Run `buy fuel_cells 1` or click BUY on the Commerce terminal.",
        reward_credits=300,
        reward_xp=120,
    ),
    TutorialStep(
        id="step_drone",
        title="Autonomous Fleet Command",
        instruction="Commission an autonomous drone asset to begin harvesting remote star systems.",
        hint="Run `fleet buy mining` or commission an asset in the Fleet tab.",
        reward_credits=350,
        reward_xp=150,
    ),
    TutorialStep(
        id="step_jump",
        title="Hyperspace Jump Transit",
        instruction="Spin up quantum warp drives and execute a hyperlane jump to an adjacent star system.",
        hint="Run `jump alpha_centauri` or target Alpha Centauri on the Galaxy Map.",
        reward_credits=400,
        reward_xp=200,
    ),
)


def generate_initial_tutorial() -> TutorialState:
    """Construct a fresh Cadet Flight Academy tutorial state."""
    return TutorialState(
        active=True,
        current_step_index=0,
        steps=INITIAL_TUTORIAL_STEPS,
        completed=False,
        skipped=False,
    )


# Narrative Campaign: "The Precursor Cipher"
CAMPAIGN_CHAPTERS: tuple[StoryChapter, ...] = (
    StoryChapter(
        chapter_index=0,
        title="Act I: The Ghost Transmission",
        target_system_id="sol",
        objective="Investigate the harmonic subspace pulse originating from Sol's asteroid belt.",
        transmission=StoryTransmission(
            speaker="Admiral Vance",
            callsign="SC-HighCommand",
            channel="Encrypted Coalition Command",
            message="Commander Astraea. Long-range sensor arrays on Mars detected an anomalous signal on 1420 MHz. It matches ancient Precursor mathematical constants. We need an autonomous scout to investigate immediately.",
            timestamp_system="sol",
        ),
        choices=(
            StoryChoice(
                id="choice_vance_telemetry",
                text="Transmit decoded telemetry directly to Coalition Naval High Command.",
                faction_alignment="coalition",
                reward_credits=800,
                outcome_text="Admiral Vance commends your loyalty. Coalition patrol corvettes bolster local system security.",
            ),
            StoryChoice(
                id="choice_cipher_leak",
                text="Leak encrypted telemetry to Cipher's Syndicate shadow-relay for heavy black-market credits.",
                faction_alignment="syndicate",
                reward_credits=1400,
                reward_relic_id="relic_cipher_key",
                outcome_text="Cipher transfers black-market credits and an ancient Decryption Key into your vault.",
            ),
        ),
        completed=False,
    ),
    StoryChapter(
        chapter_index=1,
        title="Act II: The Sirius Fabrication Reliquary",
        target_system_id="sirius",
        objective="Travel to Sirius System and establish orbit around the ancient orbital relic reliquary.",
        transmission=StoryTransmission(
            speaker="Cipher",
            callsign="Shadow-Relay",
            channel="Shadow Frequency 99.4",
            message="Impressive flying, Commander. The beacon telemetry revealed coordinates to a dormant Precursor nanite reliquary buried in the Sirius corona. The Coalition wants to weaponize it, but true explorers know its value.",
            timestamp_system="sirius",
        ),
        choices=(
            StoryChoice(
                id="choice_salvage_core",
                text="Extract the Precursor Core Matrix directly into your flagship reactor.",
                faction_alignment="precursor",
                reward_credits=1000,
                reward_relic_id="relic_core_matrix",
                outcome_text="Alien nanites synchronize with your core reactor, dramatically surging engine power and shields.",
            ),
            StoryChoice(
                id="choice_colony_power",
                text="Reconfigure the reliquary to power the struggling Sirius Frontier Colony orbital habitat.",
                faction_alignment="coalition",
                reward_credits=900,
                reward_relic_id="relic_humanitarian_medal",
                outcome_text="Thousands of frontier colonists celebrate your heroic deed. Station merchants grant permanent discounts.",
            ),
        ),
        completed=False,
    ),
    StoryChapter(
        chapter_index=2,
        title="Act III: The Gateway of Eternity",
        target_system_id="vega",
        objective="Navigate to Vega System to confront the Precursor AI guardian and decide the fate of the galaxy.",
        transmission=StoryTransmission(
            speaker="Archon Intelligence",
            callsign="Archon-Prime",
            channel="Subspace Void Broadcast",
            message="Organic entity verified. For 100,000 stellar cycles, this gate has slept. You carry our resonance keys. Choose: will humanity claim the hyperlane stars, or shall the gateways return to silence?",
            timestamp_system="vega",
        ),
        choices=(
            StoryChoice(
                id="choice_unleash_gateways",
                text="Activate the Precursor Hyperlane Super-Gateways for infinite galactic exploration.",
                faction_alignment="precursor",
                reward_credits=3000,
                reward_relic_id="relic_archon_crest",
                outcome_text="The galaxy blazes with iridescent hyperlane streams! You are hailed as the First VoidFarer of the New Age.",
            ),
            StoryChoice(
                id="choice_safeguard_lock",
                text="Seal the gateways behind an impenetrable quantum firewall to prevent extra-galactic incursions.",
                faction_alignment="coalition",
                reward_credits=2500,
                reward_relic_id="relic_sentinel_matrix",
                outcome_text="The gateway locks with a resonant hum. Galactic civilization enters an era of fortified defense.",
            ),
        ),
        completed=False,
    ),
)


def generate_initial_story() -> StoryState:
    """Construct fresh narrative campaign state."""
    first_ch = CAMPAIGN_CHAPTERS[0]
    return StoryState(
        campaign_title="The Precursor Cipher",
        current_chapter_index=0,
        chapters=CAMPAIGN_CHAPTERS,
        transmission_log=(first_ch.transmission,),
        reputation={"coalition": 0, "syndicate": 0, "precursor": 0},
        completed=False,
    )


# Unique Story Relics
STORY_RELICS: dict[str, PrecursorRelic] = {
    "relic_cadet_wings": PrecursorRelic(
        id="relic_cadet_wings",
        name="Cadet Honor Wings",
        rarity="rare",
        description="Awarded for graduating from the Cadet Flight Academy (+15 HP and +15% scan research bounty).",
        passive_stat="max_hull",
        stat_multiplier=15.0,
    ),
    "relic_cipher_key": PrecursorRelic(
        id="relic_cipher_key",
        name="Syndicate Cipher Key",
        rarity="epic",
        description="Decrypted alien quantum cipher granting +25% trade profit margins across all markets.",
        passive_stat="trade_margin",
        stat_multiplier=0.25,
    ),
    "relic_core_matrix": PrecursorRelic(
        id="relic_core_matrix",
        name="Precursor Core Matrix",
        rarity="legendary",
        description="Alien energy matrix increasing hyperlane jump fuel efficiency by +35% and laser power by +25%.",
        passive_stat="fuel_efficiency",
        stat_multiplier=0.35,
    ),
    "relic_humanitarian_medal": PrecursorRelic(
        id="relic_humanitarian_medal",
        name="Frontier Humanitarian Medal",
        rarity="epic",
        description="Conferred by grateful Sirius colonists (+35 MW maximum shield capacity).",
        passive_stat="shield_cap",
        stat_multiplier=35.0,
    ),
    "relic_archon_crest": PrecursorRelic(
        id="relic_archon_crest",
        name="Archon's Eternal Crest",
        rarity="legendary",
        description="The ultimate mark of the Precursor Architects (+40% laser strike power and +50% research bounty).",
        passive_stat="laser_dmg",
        stat_multiplier=0.40,
    ),
    "relic_sentinel_matrix": PrecursorRelic(
        id="relic_sentinel_matrix",
        name="Sentinel Aegis Matrix",
        rarity="legendary",
        description="Galactic defense seal reinforcing flagship structural integrity (+50 HP and +40 MW shields).",
        passive_stat="max_hull",
        stat_multiplier=50.0,
    ),
}

# Factory aliases
create_initial_tutorial_state = generate_initial_tutorial
create_initial_story_state = generate_initial_story
