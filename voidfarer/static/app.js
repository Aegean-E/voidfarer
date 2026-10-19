/**
 * VOIDFARER // Tactical Cockpit & Autonomous Galaxy Simulator
 * Master Web Client: Canvas Radar, Procedural Web Audio Synth, Fleet/Arsenal Controller, and REST Link.
 */

class SoundController {
    constructor() {
        this.ctx = null;
        this.enabled = true;
    }

    init() {
        if (!this.ctx) {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (AudioContext) {
                this.ctx = new AudioContext();
            }
        }
        if (this.ctx && this.ctx.state === "suspended") {
            this.ctx.resume();
        }
    }

    toggle() {
        this.enabled = !this.enabled;
        return this.enabled;
    }

    playBeep(freq = 880, duration = 0.08, type = "sine") {
        if (!this.enabled || !this.ctx) return;
        try {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.type = type;
            osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
            gain.gain.setValueAtTime(0.12, this.ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + duration);
            osc.connect(gain);
            gain.connect(this.ctx.destination);
            osc.start();
            osc.stop(this.ctx.currentTime + duration);
        } catch (e) {}
    }

    playScan() {
        if (!this.enabled || !this.ctx) return;
        try {
            const now = this.ctx.currentTime;
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.type = "sine";
            osc.frequency.setValueAtTime(400, now);
            osc.frequency.exponentialRampToValueAtTime(1400, now + 0.35);
            gain.gain.setValueAtTime(0.15, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.38);
            osc.connect(gain);
            gain.connect(this.ctx.destination);
            osc.start(now);
            osc.stop(now + 0.4);
        } catch (e) {}
    }

    playJump() {
        if (!this.enabled || !this.ctx) return;
        try {
            const now = this.ctx.currentTime;
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.type = "sawtooth";
            osc.frequency.setValueAtTime(150, now);
            osc.frequency.exponentialRampToValueAtTime(40, now + 0.6);
            gain.gain.setValueAtTime(0.2, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.65);
            osc.connect(gain);
            gain.connect(this.ctx.destination);
            osc.start(now);
            osc.stop(now + 0.7);
        } catch (e) {}
    }

    playChime() {
        if (!this.enabled || !this.ctx) return;
        try {
            const now = this.ctx.currentTime;
            [523.25, 659.25, 783.99].forEach((freq, idx) => {
                const osc = this.ctx.createOscillator();
                const gain = this.ctx.createGain();
                osc.type = "triangle";
                osc.frequency.setValueAtTime(freq, now + idx * 0.06);
                gain.gain.setValueAtTime(0.12, now + idx * 0.06);
                gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.06 + 0.25);
                osc.connect(gain);
                gain.connect(this.ctx.destination);
                osc.start(now + idx * 0.06);
                osc.stop(now + idx * 0.06 + 0.28);
            });
        } catch (e) {}
    }

    playAlarm() {
        if (!this.enabled || !this.ctx) return;
        try {
            const now = this.ctx.currentTime;
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.type = "square";
            osc.frequency.setValueAtTime(320, now);
            osc.frequency.setValueAtTime(240, now + 0.15);
            gain.gain.setValueAtTime(0.12, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
            osc.connect(gain);
            gain.connect(this.ctx.destination);
            osc.start(now);
            osc.stop(now + 0.38);
        } catch (e) {}
    }

    playTransmission() {
        if (!this.enabled || !this.ctx) return;
        try {
            const now = this.ctx.currentTime;
            [880, 1174, 987, 1318].forEach((freq, idx) => {
                const osc = this.ctx.createOscillator();
                const gain = this.ctx.createGain();
                osc.type = "sine";
                osc.frequency.setValueAtTime(freq, now + idx * 0.05);
                gain.gain.setValueAtTime(0.12, now + idx * 0.05);
                gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.05 + 0.08);
                osc.connect(gain);
                gain.connect(this.ctx.destination);
                osc.start(now + idx * 0.05);
                osc.stop(now + idx * 0.05 + 0.09);
            });
        } catch (e) {}
    }

    playLaser() {
        if (!this.enabled || !this.ctx) return;
        try {
            const now = this.ctx.currentTime;
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.type = "sawtooth";
            osc.frequency.setValueAtTime(850, now);
            osc.frequency.exponentialRampToValueAtTime(80, now + 0.18);
            gain.gain.setValueAtTime(0.2, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.2);
            osc.connect(gain);
            gain.connect(this.ctx.destination);
            osc.start(now);
            osc.stop(now + 0.22);
        } catch (e) {}
    }

    playLevelUp() {
        if (!this.enabled || !this.ctx) return;
        try {
            const now = this.ctx.currentTime;
            [523.25, 659.25, 783.99, 1046.50].forEach((freq, idx) => {
                const osc = this.ctx.createOscillator();
                const gain = this.ctx.createGain();
                osc.type = "sine";
                osc.frequency.setValueAtTime(freq, now + idx * 0.08);
                gain.gain.setValueAtTime(0.18, now + idx * 0.08);
                gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.08 + 0.35);
                osc.connect(gain);
                gain.connect(this.ctx.destination);
                osc.start(now + idx * 0.08);
                osc.stop(now + idx * 0.08 + 0.38);
            });
        } catch (e) {}
    }

    playBountyChime() {
        if (!this.enabled || !this.ctx) return;
        try {
            const now = this.ctx.currentTime;
            [392.00, 523.25, 659.25].forEach((freq, idx) => {
                const osc = this.ctx.createOscillator();
                const gain = this.ctx.createGain();
                osc.type = "triangle";
                osc.frequency.setValueAtTime(freq, now + idx * 0.09);
                gain.gain.setValueAtTime(0.2, now + idx * 0.09);
                gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.09 + 0.4);
                osc.connect(gain);
                gain.connect(this.ctx.destination);
                osc.start(now + idx * 0.09);
                osc.stop(now + idx * 0.09 + 0.42);
            });
        } catch (e) {}
    }

    playCritHit() {
        if (!this.enabled || !this.ctx) return;
        try {
            const now = this.ctx.currentTime;
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.type = "sawtooth";
            osc.frequency.setValueAtTime(1200, now);
            osc.frequency.exponentialRampToValueAtTime(60, now + 0.35);
            gain.gain.setValueAtTime(0.35, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.38);
            osc.connect(gain);
            gain.connect(this.ctx.destination);
            osc.start(now);
            osc.stop(now + 0.4);
        } catch (e) {}
    }

    playNearMiss() {
        if (!this.enabled || !this.ctx) return;
        try {
            const now = this.ctx.currentTime;
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.type = "sine";
            osc.frequency.setValueAtTime(987.77, now);
            osc.frequency.linearRampToValueAtTime(1318.51, now + 0.2);
            osc.frequency.linearRampToValueAtTime(1174.66, now + 0.45);
            gain.gain.setValueAtTime(0.16, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.5);
            osc.connect(gain);
            gain.connect(this.ctx.destination);
            osc.start(now);
            osc.stop(now + 0.52);
        } catch (e) {}
    }
}

class CockpitApp {
    constructor() {
        this.sound = new SoundController();
        this.state = null;
        this.galaxySystems = {};
        this.viewMode = "ORBITS"; // "ORBITS" or "GALAXY"
        this.activeRightTab = "market"; // "market", "arsenal", "fleet"
        this.selectedTarget = null; // CelestialBody or StarSystem
        this.selectedType = null; // 'body' or 'system'

        // Canvas radar state
        this.canvas = document.getElementById("radarCanvas");
        this.ctx = this.canvas.getContext("2d");
        this.zoom = 1.0;
        this.panX = 0;
        this.panY = 0;
        this.isDragging = false;
        this.dragStartX = 0;
        this.dragStartY = 0;
        this.hoveredItem = null;
        this.radarGrid = true;
        this.radarLabels = true;
        this.travelAnimationEnabled = true;
        this.travelAnimation = null;
        this.loadSettings();

        this.initDOMElements();
        this.bindEvents();
        this.startAnimationLoop();
        this.refreshState();
        this.fetchGalaxy();

        // Polling interval for live sync (1000ms for responsive tick progression)
        setInterval(() => this.refreshState(true), 1000);
    }

    initDOMElements() {
        // Cosmic Chronometer & Time Controls
        this.chronoStardate = document.getElementById("chronoStardate");
        this.chronoTick = document.getElementById("chronoTick");
        this.timeStatusBadge = document.getElementById("timeStatusBadge");
        this.btnTimePause = document.getElementById("btnTimePause");
        this.btnTime1x = document.getElementById("btnTime1x");
        this.btnTime2x = document.getElementById("btnTime2x");
        this.btnTime5x = document.getElementById("btnTime5x");
        this.btnTime10x = document.getElementById("btnTime10x");
        this.btnTimeStep = document.getElementById("btnTimeStep");
        this.timeSpeedButtons = [this.btnTime1x, this.btnTime2x, this.btnTime5x, this.btnTime10x];

        // Vitals
        this.hullBar = document.getElementById("hullBar");
        this.hullVal = document.getElementById("hullVal");
        this.shieldBar = document.getElementById("shieldBar");
        this.shieldVal = document.getElementById("shieldVal");
        this.fuelBar = document.getElementById("fuelBar");
        this.fuelVal = document.getElementById("fuelVal");
        this.creditsVal = document.getElementById("creditsVal");
        this.cargoSummary = document.getElementById("cargoSummary");

        // Top actions
        this.audioToggleBtn = document.getElementById("audioToggleBtn");
        this.audioIcon = document.getElementById("audioIcon");
        this.quickScanBtn = document.getElementById("quickScanBtn");

        // Nav
        this.radarTitle = document.getElementById("radarTitle");
        this.viewOrbitBtn = document.getElementById("viewOrbitBtn");
        this.viewGalaxyBtn = document.getElementById("viewGalaxyBtn");
        this.radarCoords = document.getElementById("radarCoords");

        // Target Card
        this.targetType = document.getElementById("targetType");
        this.targetName = document.getElementById("targetName");
        this.targetDist = document.getElementById("targetDist");
        this.targetDesc = document.getElementById("targetDesc");
        this.btnOrbitTarget = document.getElementById("btnOrbitTarget");
        this.btnLandTarget = document.getElementById("btnLandTarget");
        this.btnJumpTarget = document.getElementById("btnJumpTarget");
        this.targetGravity = document.getElementById("targetGravity");
        this.targetAtmosphere = document.getElementById("targetAtmosphere");
        this.targetTemp = document.getElementById("targetTemp");
        this.targetMoons = document.getElementById("targetMoons");
        this.targetResources = document.getElementById("targetResources");

        // Power Matrix
        this.sliderEng = document.getElementById("sliderEng");
        this.sliderShd = document.getElementById("sliderShd");
        this.sliderSen = document.getElementById("sliderSen");
        this.sliderWep = document.getElementById("sliderWep");
        this.pwrEngVal = document.getElementById("pwrEngVal");
        this.pwrShdVal = document.getElementById("pwrShdVal");
        this.pwrSenVal = document.getElementById("pwrSenVal");
        this.pwrWepVal = document.getElementById("pwrWepVal");
        this.powerTotal = document.getElementById("powerTotal");
        this.applyPowerBtn = document.getElementById("applyPowerBtn");
        this.powerDirty = false;

        // Log
        this.flightLogStream = document.getElementById("flightLogStream");
        this.logPanel = document.getElementById("logPanel");
        this.btnToggleLog = document.getElementById("btnToggleLog");

        // Combat Card
        this.combatCard = document.getElementById("combatCard");
        this.combatEnemyTitle = document.getElementById("combatEnemyTitle");
        this.combatEnemyFaction = document.getElementById("combatEnemyFaction");
        this.combatEnemyHp = document.getElementById("combatEnemyHp");
        this.combatEnemyBar = document.getElementById("combatEnemyBar");
        this.combatShieldContainer = document.getElementById("combatShieldContainer");
        this.combatEnemyShield = document.getElementById("combatEnemyShield");
        this.combatEnemyShieldBar = document.getElementById("combatEnemyShieldBar");
        this.combatTelegraphBanner = document.getElementById("combatTelegraphBanner");
        this.combatTelegraphText = document.getElementById("combatTelegraphText");
        this.btnCombatFire = document.getElementById("btnCombatFire");
        this.btnCombatDrone = document.getElementById("btnCombatDrone");
        this.btnCombatTarget = document.getElementById("btnCombatTarget");
        this.btnCombatAbsorb = document.getElementById("btnCombatAbsorb");
        this.btnCombatEvade = document.getElementById("btnCombatEvade");
        this.btnCombatFlee = document.getElementById("btnCombatFlee");
        this.combatComboBadge = document.getElementById("combatComboBadge");
        this.combatComboCount = document.getElementById("combatComboCount");
        this.critReadyText = document.getElementById("critReadyText");

        // Anomaly Card
        this.anomalyCard = document.getElementById("anomalyCard");
        this.anomalyTitle = document.getElementById("anomalyTitle");
        this.anomalyDesc = document.getElementById("anomalyDesc");
        this.anomalyChoices = document.getElementById("anomalyChoices");

        // Vitals: Streak & Mastery
        this.vitalStreakCard = document.getElementById("vitalStreakCard");
        this.streakVal = document.getElementById("streakVal");
        this.streakSubtext = document.getElementById("streakSubtext");
        this.vitalMasteryCard = document.getElementById("vitalMasteryCard");
        this.masteryLevelVal = document.getElementById("masteryLevelVal");
        this.masteryBar = document.getElementById("masteryBar");
        this.masterySubtext = document.getElementById("masterySubtext");

        // Cadet Academy Ribbon
        this.cadetBanner = document.getElementById("cadetBanner");
        this.cadetMilestoneTitle = document.getElementById("cadetMilestoneTitle");
        this.cadetMilestoneDesc = document.getElementById("cadetMilestoneDesc");
        this.cadetMilestoneHint = document.getElementById("cadetMilestoneHint");
        this.cadetMilestoneReward = document.getElementById("cadetMilestoneReward");
        this.btnSkipCadet = document.getElementById("btnSkipCadet");
        this.btnResetCadetAcademy = document.getElementById("btnResetCadetAcademy");
        this.cadetGraduationDismissed = false;

        // Right Deck Tabs
        this.tabBtnMarket = document.getElementById("tabBtnMarket");
        this.tabBtnArsenal = document.getElementById("tabBtnArsenal");
        this.tabBtnFleet = document.getElementById("tabBtnFleet");
        this.tabBtnContracts = document.getElementById("tabBtnContracts");
        this.tabBtnMastery = document.getElementById("tabBtnMastery");
        this.tabBtnStory = document.getElementById("tabBtnStory");
        this.tabBtnFactions = document.getElementById("tabBtnFactions");
        this.tabBtnQuests = document.getElementById("tabBtnQuests");
        this.tabBtnAI = document.getElementById("tabBtnAI");
        this.tabBtnDepot = document.getElementById("tabBtnDepot");
        this.tabBtnMessages = document.getElementById("tabBtnMessages");
        this.contractsBadge = document.getElementById("contractsBadge");
        this.storyBadge = document.getElementById("storyBadge");
        this.messagesBadge = document.getElementById("messagesBadge");

        this.tabContentMarket = document.getElementById("tabContentMarket");
        this.tabContentArsenal = document.getElementById("tabContentArsenal");
        this.tabContentFleet = document.getElementById("tabContentFleet");
        this.tabContentContracts = document.getElementById("tabContentContracts");
        this.tabContentMastery = document.getElementById("tabContentMastery");
        this.tabContentStory = document.getElementById("tabContentStory");
        this.tabContentFactions = document.getElementById("tabContentFactions");
        this.tabContentQuests = document.getElementById("tabContentQuests");
        this.tabContentAI = document.getElementById("tabContentAI");
        this.tabContentDepot = document.getElementById("tabContentDepot");
        this.tabContentMessages = document.getElementById("tabContentMessages");
        this.questsList = document.getElementById("questsList");
        this.aiList = document.getElementById("aiList");
        this.depotSummary = document.getElementById("depotSummary");
        this.depotList = document.getElementById("depotList");
        this.messageList = document.getElementById("messageList");
        this.factionsGrid = document.getElementById("factionsGrid");
        this.corpsGrid = document.getElementById("corpsGrid");

        // Story Comms Elements
        this.storyChapterTitle = document.getElementById("storyChapterTitle");
        this.storyTargetBadge = document.getElementById("storyTargetBadge");
        this.scoreCoalition = document.getElementById("scoreCoalition");
        this.scoreSyndicate = document.getElementById("scoreSyndicate");
        this.scorePrecursor = document.getElementById("scorePrecursor");
        this.storySynopsisText = document.getElementById("storySynopsisText");
        this.storyChoiceContainer = document.getElementById("storyChoiceContainer");
        this.storyChoicesList = document.getElementById("storyChoicesList");
        this.transmissionsStream = document.getElementById("transmissionsStream");
        this.commsLogCount = document.getElementById("commsLogCount");

        // Contracts & Mastery Containers
        this.contractsList = document.getElementById("contractsList");
        this.availableTalentPoints = document.getElementById("availableTalentPoints");
        this.talentsGrid = document.getElementById("talentsGrid");
        this.relicsGrid = document.getElementById("relicsGrid");

        // Market
        this.marketTitle = document.getElementById("marketTitle");
        this.marketArch = document.getElementById("marketArch");
        this.marketTableBody = document.getElementById("marketTableBody");
        this.noMarketMsg = document.getElementById("noMarketMsg");
        this.cargoDetailed = document.getElementById("cargoDetailed");
        this.cargoMeterFill = document.getElementById("cargoMeterFill");
        this.btnDrydockRepair = document.getElementById("btnDrydockRepair");
        this.btnRefuelTanks = document.getElementById("btnRefuelTanks");

        // Arsenal & Fleet containers
        this.arsenalList = document.getElementById("arsenalList");
        this.fleetRoster = document.getElementById("fleetRoster");
        this.mercenaryRoster = document.getElementById("mercenaryRoster");
        this.btnHarvestFleet = document.getElementById("btnHarvestFleet");

        // Footer stats
        this.statJumps = document.getElementById("statJumps");
        this.statScans = document.getElementById("statScans");
        this.statTrades = document.getElementById("statTrades");
        this.statVictories = document.getElementById("statVictories");
        this.statAnomalies = document.getElementById("statAnomalies");
    }

    bindEvents() {
        // Audio Toggle
        this.audioToggleBtn.addEventListener("click", () => {
            this.sound.init();
            const on = this.sound.toggle();
            this.audioIcon.textContent = on ? "🔊" : "🔇";
            this.audioToggleBtn.style.opacity = on ? "1" : "0.5";
            if (on) this.sound.playBeep(900);
        });

        // Quick Scan
        this.quickScanBtn.addEventListener("click", () => this.handleScan());

        // View Mode Switcher
        this.viewOrbitBtn.addEventListener("click", () => {
            this.sound.init();
            this.sound.playBeep(700);
            this.viewMode = "ORBITS";
            this.viewOrbitBtn.classList.add("active");
            this.viewGalaxyBtn.classList.remove("active");
            this.selectedTarget = null;
            this.updateTargetCard();
        });

        this.viewGalaxyBtn.addEventListener("click", () => {
            this.sound.init();
            this.sound.playBeep(700);
            this.viewMode = "GALAXY";
            this.viewGalaxyBtn.classList.add("active");
            this.viewOrbitBtn.classList.remove("active");
            this.selectedTarget = null;
            this.updateTargetCard();
        });

        // Radar controls
        document.getElementById("btnZoomIn").addEventListener("click", () => {
            this.zoom = Math.min(2.5, this.zoom + 0.2);
            this.sound.playBeep(1100, 0.04);
        });
        document.getElementById("btnZoomOut").addEventListener("click", () => {
            this.zoom = Math.max(0.4, this.zoom - 0.2);
            this.sound.playBeep(900, 0.04);
        });
        document.getElementById("btnResetView").addEventListener("click", () => {
            this.zoom = 1.0;
            this.panX = 0;
            this.panY = 0;
            this.sound.playBeep(1000, 0.05);
        });

        // Target actions
        this.btnOrbitTarget.addEventListener("click", () => this.handleOrbitAction());
        this.btnJumpTarget.addEventListener("click", () => this.handleJumpAction());

        // Power Sliders
        const sliders = [this.sliderEng, this.sliderShd, this.sliderSen, this.sliderWep];
        sliders.forEach(s => s.addEventListener("input", () => {
            this.powerDirty = true;
            this.updatePowerAllocationDisplay();
        }));
        this.applyPowerBtn.addEventListener("click", () => this.handleApplyPower());

        // Presets
        document.getElementById("presetBalanced").addEventListener("click", () => {
            this.setPowerSliders(25, 25, 25, 25);
            this.sound.playBeep(850);
        });
        document.getElementById("presetSprint").addEventListener("click", () => {
            this.setPowerSliders(45, 20, 20, 15);
            this.sound.playBeep(950);
        });
        document.getElementById("presetScience").addEventListener("click", () => {
            this.setPowerSliders(20, 20, 45, 15);
            this.sound.playBeep(1050);
        });

        // Station Services
        this.btnDrydockRepair.addEventListener("click", () => this.handleRepair());
        this.btnRefuelTanks.addEventListener("click", () => this.handleRefuel());

        // Right Deck Tabs
        this.tabBtnMarket.addEventListener("click", () => this.switchRightTab("market"));
        this.tabBtnArsenal.addEventListener("click", () => this.switchRightTab("arsenal"));
        this.tabBtnFleet.addEventListener("click", () => this.switchRightTab("fleet"));
        this.tabBtnContracts.addEventListener("click", () => this.switchRightTab("contracts"));
        this.tabBtnMastery.addEventListener("click", () => this.switchRightTab("mastery"));
        this.tabBtnStory.addEventListener("click", () => this.switchRightTab("story"));
        if (this.tabBtnFactions) {
            this.tabBtnFactions.addEventListener("click", () => this.switchRightTab("factions"));
        }
        if (this.tabBtnQuests) this.tabBtnQuests.addEventListener("click", () => this.switchRightTab("quests"));
        if (this.tabBtnAI) this.tabBtnAI.addEventListener("click", () => this.switchRightTab("ai"));
        if (this.tabBtnDepot) this.tabBtnDepot.addEventListener("click", () => this.switchRightTab("depot"));
        if (this.tabBtnMessages) this.tabBtnMessages.addEventListener("click", () => this.switchRightTab("messages"));

        // Main menu, settings, perks, and frontier actions
        document.getElementById("btnMainMenu")?.addEventListener("click", () => this.openMainMenu());
        document.getElementById("btnOpenPerks")?.addEventListener("click", () => this.openPerksWindow());
        document.getElementById("btnClosePerks")?.addEventListener("click", () => this.closePerksWindow());
        document.getElementById("btnCloseSettings")?.addEventListener("click", () => this.closeSettings());
        document.getElementById("btnMenuResume")?.addEventListener("click", () => this.closeMainMenu());
        document.getElementById("btnMenuSave")?.addEventListener("click", () => this.menuAction("/api/save", "Game saved."));
        document.getElementById("btnMenuLoad")?.addEventListener("click", () => this.menuAction("/api/load", "Game loaded."));
        document.getElementById("btnMenuDelete")?.addEventListener("click", () => {
            if (window.confirm("Delete the current save permanently?")) this.menuAction("/api/delete-save", "Save deleted.");
        });
        document.getElementById("btnMenuNew")?.addEventListener("click", () => {
            if (window.confirm("Start a new game? The current save will be replaced.")) this.menuAction("/api/new-game", "New game started.");
        });
        document.getElementById("btnMenuSettings")?.addEventListener("click", () => this.openSettings());
        document.getElementById("btnSendMessage")?.addEventListener("click", () => this.handleSendMessage());
        this.btnLandTarget?.addEventListener("click", () => this.handleLandAction());
        document.getElementById("btnToggleGrid")?.addEventListener("click", () => {
            this.radarGrid = !this.radarGrid;
            this.saveSettings();
        });
        document.getElementById("btnToggleLabels")?.addEventListener("click", () => {
            this.radarLabels = !this.radarLabels;
            this.saveSettings();
        });
        ["settingSound", "settingGrid", "settingLabels", "settingAnimation", "settingStarDensity"].forEach(id => {
            document.getElementById(id)?.addEventListener("input", () => this.applySettingsFromUI());
        });
        this.btnSkipCadet.addEventListener("click", () => this.handleSkipCadet());
        if (this.btnResetCadetAcademy) {
            this.btnResetCadetAcademy.addEventListener("click", () => this.handleResetCadet());
        }

        // Combat Buttons
        this.btnCombatFire.addEventListener("click", () => this.handleCombat("fire_lasers"));
        if (this.btnCombatDrone) {
            this.btnCombatDrone.addEventListener("click", () => this.handleCombat("drone_strike"));
        }
        if (this.btnCombatTarget) {
            this.btnCombatTarget.addEventListener("click", () => this.handleCombat("target_subsystem"));
        }
        this.btnCombatAbsorb.addEventListener("click", () => this.handleCombat("shield_absorb"));
        this.btnCombatEvade.addEventListener("click", () => this.handleCombat("evasive_burn"));
        this.btnCombatFlee.addEventListener("click", () => this.handleCombat("flee"));

        // Harvest Fleet
        this.btnHarvestFleet.addEventListener("click", () => this.handleHarvestFleet());

        // Drone Commission buttons
        document.querySelectorAll(".btn-drone-buy").forEach(btn => {
            btn.addEventListener("click", (e) => {
                const target = e.currentTarget;
                const dType = target.getAttribute("data-type");
                this.handleCommissionDrone(dType);
            });
        });

        // Canvas interactions & Drag Pan
        this.canvas.addEventListener("mousedown", (e) => {
            const point = this.pointerToCanvas(e);
            this.isDragging = true;
            this.dragMoved = false;
            this.suppressClick = false;
            this.dragStartX = point.x - this.panX;
            this.dragStartY = point.y - this.panY;
        });

        window.addEventListener("mouseup", () => {
            if (this.dragMoved) this.suppressClick = true;
            this.isDragging = false;
        });

        this.canvas.addEventListener("mousemove", (e) => {
            const point = this.pointerToCanvas(e);
            if (this.isDragging) {
                const nextX = point.x - this.dragStartX;
                const nextY = point.y - this.dragStartY;
                if (Math.hypot(nextX - this.panX, nextY - this.panY) > 3) {
                    this.dragMoved = true;
                }
                this.panX = nextX;
                this.panY = nextY;
            } else {
                this.handleCanvasMouseMove(e);
            }
        });

        this.canvas.addEventListener("wheel", (e) => {
            e.preventDefault();
            const delta = e.deltaY < 0 ? 0.1 : -0.1;
            this.zoom = Math.max(0.4, Math.min(2.5, this.zoom + delta));
        }, { passive: false });

        this.canvas.addEventListener("click", (e) => this.handleCanvasClick(e));

        // Clear Log
        document.getElementById("clearLogBtn").addEventListener("click", () => {
            this.flightLogStream.innerHTML = `<div class="log-line log-system">[SYS] Telemetry stream cleared.</div>`;
        });

        // Collapse / expand the telemetry log (layout rule G-001)
        if (this.btnToggleLog && this.logPanel) {
            this.btnToggleLog.addEventListener("click", () => {
                const collapsed = this.logPanel.classList.toggle("log-collapsed");
                this.btnToggleLog.textContent = collapsed ? "SHOW" : "HIDE";
                this.btnToggleLog.setAttribute("aria-expanded", String(!collapsed));
            });
        }

        // Time & Ticks Chrono Controls
        if (this.btnTimePause) {
            this.btnTimePause.addEventListener("click", () => this.handleToggleTimePause());
        }
        if (this.btnTimeStep) {
            this.btnTimeStep.addEventListener("click", () => this.handleTimeStep(1));
        }
        if (this.timeSpeedButtons) {
            this.timeSpeedButtons.forEach(btn => {
                if (btn) {
                    btn.addEventListener("click", (e) => {
                        const speed = parseFloat(e.currentTarget.getAttribute("data-speed") || "1.0");
                        this.handleSetTimeSpeed(speed);
                    });
                }
            });
        }

        // Global hotkeys for temporal controls (Space = Pause/Resume, 1-4 = Speeds, T = Step)
        window.addEventListener("keydown", (e) => {
            if (e.repeat) return;
            if (["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement?.tagName)) return;
            if (e.code === "Space") {
                e.preventDefault();
                this.handleToggleTimePause();
            } else if (e.key === "1") {
                this.handleSetTimeSpeed(1.0);
            } else if (e.key === "2") {
                this.handleSetTimeSpeed(2.0);
            } else if (e.key === "3") {
                this.handleSetTimeSpeed(5.0);
            } else if (e.key === "4") {
                this.handleSetTimeSpeed(10.0);
            } else if (e.key.toLowerCase() === "t") {
                this.handleTimeStep(1);
            }
        });
    }

    switchRightTab(tabName) {
        this.sound.playBeep(750, 0.05);
        if (tabName === "mastery") {
            this.openPerksWindow();
            return;
        }
        this.activeRightTab = tabName;

        const tabButtons = {
            market: this.tabBtnMarket, arsenal: this.tabBtnArsenal, fleet: this.tabBtnFleet,
            contracts: this.tabBtnContracts, story: this.tabBtnStory, factions: this.tabBtnFactions,
            quests: this.tabBtnQuests, ai: this.tabBtnAI, depot: this.tabBtnDepot, messages: this.tabBtnMessages,
        };
        Object.entries(tabButtons).forEach(([name, button]) => {
            if (button) button.classList.toggle("active", tabName === name);
        });

        const tabContents = {
            market: this.tabContentMarket, arsenal: this.tabContentArsenal, fleet: this.tabContentFleet,
            contracts: this.tabContentContracts, story: this.tabContentStory, factions: this.tabContentFactions,
            quests: this.tabContentQuests, ai: this.tabContentAI, depot: this.tabContentDepot, messages: this.tabContentMessages,
        };
        Object.entries(tabContents).forEach(([name, content]) => {
            if (content) content.style.display = (tabName === name) ? "flex" : "none";
        });

        if (tabName === "market") this.renderMarketTable();
        if (tabName === "arsenal") this.renderArsenal();
        if (tabName === "fleet") this.renderFleet();
        if (tabName === "contracts") this.renderContracts();
        if (tabName === "story") this.renderStory();
        if (tabName === "factions") this.renderFactions();
        if (tabName === "quests") this.renderQuests();
        if (tabName === "ai") this.renderAICaptains();
        if (tabName === "depot") this.renderDepots();
        if (tabName === "messages") this.renderMessages();
    }

    setPowerSliders(e, sh, se, w) {
        this.sliderEng.value = e;
        this.sliderShd.value = sh;
        this.sliderSen.value = se;
        this.sliderWep.value = w;
        this.powerDirty = true;
        this.updatePowerAllocationDisplay();
    }

    syncPowerSlidersFromState() {
        if (!this.state || this.powerDirty) return;
        const power = this.state.ship.power || { engines: 25, shields: 25, sensors: 25, weapons: 25 };
        this.sliderEng.value = power.engines;
        this.sliderShd.value = power.shields;
        this.sliderSen.value = power.sensors;
        this.sliderWep.value = power.weapons;
        this.updatePowerAllocationDisplay();
    }

    updatePowerAllocationDisplay() {
        const e = parseInt(this.sliderEng.value, 10);
        const sh = parseInt(this.sliderShd.value, 10);
        const se = parseInt(this.sliderSen.value, 10);
        const w = parseInt(this.sliderWep.value, 10);
        const total = e + sh + se + w;

        this.pwrEngVal.textContent = `${e}%`;
        this.pwrShdVal.textContent = `${sh}%`;
        this.pwrSenVal.textContent = `${se}%`;
        this.pwrWepVal.textContent = `${w}%`;

        this.powerTotal.textContent = `${total}% ALLOCATED`;
        if (total > 100) {
            this.powerTotal.style.color = "var(--neon-red)";
            this.applyPowerBtn.disabled = true;
        } else {
            this.powerTotal.style.color = "var(--neon-green)";
            this.applyPowerBtn.disabled = false;
        }
    }

    async refreshState(silent = false) {
        try {
            const res = await fetch("/api/state");
            const json = await res.json();
            if (json.ok && json.data) {
                this.state = json.data;
                this.renderHUD();
                if (!silent) {
                    this.appendLog(`Telemetry synchronized with ${this.state.current_system.name}.`);
                }
            }
        } catch (e) {
            console.error("Error refreshing state:", e);
        }
    }

    async fetchGalaxy() {
        try {
            const res = await fetch("/api/galaxy");
            const json = await res.json();
            if (json.ok && json.systems) {
                this.galaxySystems = json.systems;
            }
        } catch (e) {
            console.error("Error fetching galaxy:", e);
        }
    }

    renderHUD() {
        if (!this.state) return;
        const ship = this.state.ship;
        const curSys = this.state.current_system;
        const orbBody = this.state.orbiting_body;

        // Vitals
        const hullPct = Math.round((ship.hull / ship.max_hull) * 100);
        this.hullBar.style.width = `${hullPct}%`;
        this.hullVal.textContent = `${ship.hull}/${ship.max_hull}`;

        const shieldPct = Math.round((ship.shield / ship.max_shield) * 100);
        this.shieldBar.style.width = `${shieldPct}%`;
        this.shieldVal.textContent = `${ship.shield}/${ship.max_shield}`;

        const fuelPct = Math.round((ship.fuel / ship.max_fuel) * 100);
        this.fuelBar.style.width = `${fuelPct}%`;
        this.fuelVal.textContent = `${ship.fuel}/${ship.max_fuel}`;

        this.creditsVal.textContent = `${ship.credits.toLocaleString()} CR`;

        const manifest = this.state.inventory_manifest || [];
        const totalCargo = manifest.length
            ? manifest.reduce((sum, item) => sum + (item.total_volume || 0), 0)
            : Object.values(ship.cargo).reduce((a, b) => a + b, 0);
        this.cargoSummary.textContent = `HOLD: ${totalCargo}/${ship.cargo_capacity}`;
        this.cargoDetailed.textContent = `${totalCargo} / ${ship.cargo_capacity} VOLUME`;
        this.cargoMeterFill.style.width = `${Math.min(100, Math.round((totalCargo / ship.cargo_capacity) * 100))}%`;

        this.syncPowerSlidersFromState();

        // Streak render
        const streak = ship.streak || 1;
        const streakMult = 1.0 + Math.min(1.5, (streak - 1) * 0.15);
        this.streakVal.textContent = `🔥 ${streak} JUMP${streak > 1 ? 'S' : ''} (x${streakMult.toFixed(2)})`;
        this.vitalStreakCard.classList.toggle("high-streak", streak >= 3);
        this.streakSubtext.textContent = streak > 1 
            ? `+${Math.round((streakMult - 1.0) * 100)}% ALL REWARDS // FLEE RESETS`
            : "LOSS AVERSION: FLEE RESETS";

        // Mastery render
        const mastery = ship.mastery || { level: 1, xp: 0, next_level_xp: 500, talent_points: 0 };
        this.masteryLevelVal.textContent = `★ LVL ${mastery.level}`;
        const xpPct = Math.min(100, Math.round((mastery.xp / mastery.next_level_xp) * 100));
        this.masteryBar.style.width = `${xpPct}%`;
        this.masterySubtext.textContent = `${mastery.xp}/${mastery.next_level_xp} XP // ${mastery.talent_points} PERK${mastery.talent_points !== 1 ? 'S' : ''}`;

        // Contract ready notification badge
        const contracts = ship.active_contracts || [];
        const readyContracts = contracts.filter(c => c.completed);
        if (readyContracts.length > 0) {
            this.contractsBadge.style.display = "inline-block";
            this.contractsBadge.textContent = readyContracts.length;
        } else {
            this.contractsBadge.style.display = "none";
        }

        // Render Cosmic Chronometer & Time Controls
        if (this.state.time) {
            const t = this.state.time;
            if (this.chronoStardate) {
                this.chronoStardate.textContent = `DATE ${t.date || "01.01.3042"}`;
            }
            if (this.chronoTick) {
                this.chronoTick.textContent = `TICK #${t.tick}`;
            }
            if (this.btnTimePause && this.timeStatusBadge) {
                if (t.is_paused) {
                    this.btnTimePause.textContent = "▶";
                    this.btnTimePause.classList.add("paused");
                    this.btnTimePause.title = "Resume Chrono Stream (Hotkey: Space)";
                    this.timeStatusBadge.textContent = "PAUSED";
                    this.timeStatusBadge.className = "time-status-badge badge-paused";
                } else {
                    this.btnTimePause.textContent = "⏸";
                    this.btnTimePause.classList.remove("paused");
                    this.btnTimePause.title = "Pause Chrono Stream (Hotkey: Space)";
                    this.timeStatusBadge.textContent = `${t.speed}x SPEED`;
                    this.timeStatusBadge.className = "time-status-badge badge-active";
                }
            }
            if (this.timeSpeedButtons) {
                this.timeSpeedButtons.forEach(btn => {
                    if (btn) {
                        const s = parseFloat(btn.getAttribute("data-speed") || "1.0");
                        btn.classList.toggle("active", Math.abs(s - t.speed) < 0.01 && !t.is_paused);
                    }
                });
            }
        }

        // Nav titles
        this.radarTitle.textContent = this.viewMode === "ORBITS" 
            ? `${curSys.name.toUpperCase()} CELESTIAL ORBITS`
            : `SECTOR HYPERLANE GRID`;
        this.radarCoords.textContent = `COORDS: [${curSys.x.toFixed(1)}, ${curSys.y.toFixed(1)}] // ${curSys.faction.toUpperCase()}`;

        // Footer stats
        this.statJumps.textContent = this.state.stats.jumps || 0;
        this.statScans.textContent = this.state.stats.scans || 0;
        this.statTrades.textContent = this.state.stats.trades || 0;
        this.statVictories.textContent = this.state.stats.combat_victories || 0;
        this.statAnomalies.textContent = this.state.stats.anomalies_resolved || 0;

        // Render Combat Intercept Alert
        if (this.state.active_combat) {
            const c = this.state.active_combat;
            this.sound.playAlarm();
            this.combatCard.style.display = "flex";
            this.combatEnemyTitle.textContent = `${c.enemy_name} [${c.enemy_class}]`;
            if (this.combatEnemyFaction) {
                this.combatEnemyFaction.textContent = c.faction_id ? `FACTION: ${c.faction_id.replace('_', ' ').toUpperCase()}` : "";
            }
            this.combatEnemyHp.textContent = `${c.enemy_hull} / ${c.enemy_max_hull}`;
            const pct = Math.round((c.enemy_hull / c.enemy_max_hull) * 100);
            this.combatEnemyBar.style.width = `${pct}%`;

            if (this.combatShieldContainer) {
                if (c.enemy_max_shield > 0) {
                    this.combatShieldContainer.style.display = "flex";
                    this.combatEnemyShield.textContent = `${c.enemy_shield} / ${c.enemy_max_shield}`;
                    const shdPct = Math.round((c.enemy_shield / c.enemy_max_shield) * 100);
                    this.combatEnemyShieldBar.style.width = `${shdPct}%`;
                } else {
                    this.combatShieldContainer.style.display = "none";
                }
            }

            if (this.combatTelegraphBanner) {
                if (c.telegraphed_action) {
                    this.combatTelegraphBanner.style.display = "flex";
                    this.combatTelegraphText.textContent = c.telegraphed_action;
                } else {
                    this.combatTelegraphBanner.style.display = "none";
                }
            }

            // Tactical Combo Counter
            const combo = ship.tactical_combo || 0;
            if (combo > 0) {
                this.combatComboBadge.style.display = "flex";
                this.combatComboCount.textContent = `x${combo}`;
                this.critReadyText.style.display = (combo >= 2) ? "inline" : "none";
            } else {
                this.combatComboBadge.style.display = "none";
            }
        } else {
            this.combatCard.style.display = "none";
        }

        // Render Anomaly Alert
        if (this.state.active_anomaly && !this.state.active_combat) {
            this.sound.playAlarm();
            this.anomalyCard.style.display = "flex";
            this.anomalyTitle.textContent = this.state.active_anomaly.title;
            this.anomalyDesc.textContent = this.state.active_anomaly.description;
            this.anomalyChoices.innerHTML = "";
            this.state.active_anomaly.choices.forEach(ch => {
                const btn = document.createElement("button");
                btn.className = "anomaly-choice-btn";
                const checkInfo = ch.required_power !== "none" 
                    ? `[CHECK: ${ch.required_power.toUpperCase()} >= ${ch.min_power_threshold}%]`
                    : `[SAFE HARVEST]`;
                btn.innerHTML = `${ch.text} <span class="choice-check">${checkInfo}</span>`;
                btn.addEventListener("click", () => this.handleResolveAnomaly(ch.choice_id));
                this.anomalyChoices.appendChild(btn);
            });
        } else {
            this.anomalyCard.style.display = "none";
        }

        // Cadet Academy Ribbon render
        const tut = ship.tutorial;
        if (tut && !tut.completed && !tut.skipped && tut.steps && tut.steps.length > 0) {
            const step = tut.steps[tut.current_step_index] || tut.steps[0];
            this.cadetBanner.style.display = "flex";
            this.cadetMilestoneTitle.textContent = `Milestone ${tut.current_step_index + 1}/${tut.steps.length}: ${step.title}`;
            this.cadetMilestoneDesc.textContent = step.description;
            this.cadetMilestoneHint.textContent = step.hint;
            this.cadetMilestoneReward.textContent = `+${step.reward_credits} CR / +${step.reward_xp} XP`;
            this.btnSkipCadet.textContent = "SKIP TUTORIAL";
            this.btnSkipCadet.style.display = "inline-block";
        } else if (tut && tut.completed && !this.cadetGraduationDismissed) {
            this.cadetBanner.style.display = "flex";
            this.cadetMilestoneTitle.textContent = "🎓 ACADEMY GRADUATION: Flight Wings Conferred!";
            this.cadetMilestoneDesc.textContent = "Congratulations Commander Astraea! Full flight credentials unlocked. Cadet Honor Wings active.";
            this.cadetMilestoneHint.textContent = "+1,500 CR, +400 XP, and Cadet Honor Wings Precursor Relic awarded.";
            this.cadetMilestoneReward.textContent = "GRADUATED";
            this.btnSkipCadet.textContent = "DISMISS";
            this.btnSkipCadet.style.display = "inline-block";
        } else {
            this.cadetBanner.style.display = "none";
        }

        // Story Comms Badge
        const story = ship.story;
        if (story) {
            let curChap = null;
            if (this.state.story_chapters_map && this.state.story_chapters_map[story.current_chapter_id]) {
                curChap = this.state.story_chapters_map[story.current_chapter_id];
            } else if (Array.isArray(this.state.story_chapters)) {
                curChap = this.state.story_chapters.find(c => c.id === story.current_chapter_id);
            } else if (story.chapters && story.chapters[story.current_chapter_index]) {
                curChap = story.chapters[story.current_chapter_index];
            }
            const hasPendingChoices = curChap && !curChap.completed && curChap.choices && curChap.choices.length > 0;
            if (hasPendingChoices) {
                this.storyBadge.style.display = "inline-block";
                this.storyBadge.textContent = "!";
            } else {
                this.storyBadge.style.display = "none";
            }
        }

        if (this.messagesBadge) {
            const unread = (this.state.messages || []).filter(m => !m.read).length;
            this.messagesBadge.textContent = String(unread);
            this.messagesBadge.style.display = unread > 0 ? "inline-block" : "none";
        }

        // Render Active Tab Content
        if (this.activeRightTab === "market") {
            if (orbBody && orbBody.station_dockable) {
                this.noMarketMsg.style.display = "none";
                this.marketTitle.textContent = `${orbBody.name.toUpperCase()} EXCHANGE`;
                this.marketArch.textContent = orbBody.market_archetype.toUpperCase();
                this.renderMarketTable();
            } else {
                this.noMarketMsg.style.display = "flex";
                this.marketTableBody.innerHTML = "";
                this.marketTitle.textContent = orbBody ? orbBody.name : "DEEP SPACE";
                this.marketArch.textContent = "UNPOPULATED";
            }
        } else if (this.activeRightTab === "arsenal") {
            this.renderArsenal();
        } else if (this.activeRightTab === "fleet") {
            this.renderFleet();
        } else if (this.activeRightTab === "contracts") {
            this.renderContracts();
        } else if (this.activeRightTab === "mastery") {
            this.renderMastery();
        } else if (this.activeRightTab === "story") {
            this.renderStory();
        } else if (this.activeRightTab === "factions") {
            this.renderFactions();
        } else if (this.activeRightTab === "quests") {
            this.renderQuests();
        } else if (this.activeRightTab === "ai") {
            this.renderAICaptains();
        } else if (this.activeRightTab === "depot") {
            this.renderDepots();
        } else if (this.activeRightTab === "messages") {
            this.renderMessages();
        }

        this.updateTargetCard();
    }

    renderStory() {
        if (!this.state || !this.state.ship || !this.state.ship.story) return;
        const story = this.state.ship.story;

        // Resolve active chapter reliably across map, array, or embedded state
        let curChap = null;
        if (this.state.story_chapters_map && this.state.story_chapters_map[story.current_chapter_id]) {
            curChap = this.state.story_chapters_map[story.current_chapter_id];
        } else if (Array.isArray(this.state.story_chapters)) {
            curChap = this.state.story_chapters.find(c => c.id === story.current_chapter_id);
        } else if (story.chapters && story.chapters[story.current_chapter_index]) {
            curChap = story.chapters[story.current_chapter_index];
        }

        if (story.completed) {
            this.storyChapterTitle.textContent = "CAMPAIGN CONCLUDED: THE PRECURSOR CIPHER";
            this.storyTargetBadge.textContent = "⭐ ALL ACTS RESOLVED";
            this.storySynopsisText.textContent = "The mysteries of the ancient Precursor network have been unveiled. Your legacy echoes across the hyperlane corridors as First VoidFarer of the New Age.";
            this.storyChoiceContainer.style.display = "none";
        } else if (curChap) {
            this.storyChapterTitle.textContent = `ACT ${story.active_act}: ${curChap.title.toUpperCase()}`;
            const targetText = curChap.completed 
                ? "ACT OBJECTIVE COMPLETE" 
                : (curChap.target_system_id ? `TARGET: ${curChap.target_system_id.toUpperCase()}` : "TARGET: DEEP SPACE");
            this.storyTargetBadge.textContent = targetText;
            this.storySynopsisText.textContent = curChap.synopsis || curChap.objective || "";

            // Story Choices
            if (!curChap.completed && curChap.choices && curChap.choices.length > 0) {
                this.storyChoiceContainer.style.display = "flex";
                this.storyChoicesList.innerHTML = "";
                curChap.choices.forEach(c => {
                    const card = document.createElement("button");
                    card.className = "story-choice-card";
                    const costBadge = c.cost_credits > 0 ? `<span class="choice-cost-badge">COST: ${c.cost_credits} CR</span>` : "";
                    card.innerHTML = `
                        <div class="choice-header-row">
                            <span class="choice-label-text">${c.label || c.text}</span>
                            ${costBadge}
                        </div>
                        <p class="choice-consequence-preview">${c.consequence_summary || c.outcome_text}</p>
                    `;
                    card.addEventListener("click", () => this.handleStoryChoice(c.id));
                    this.storyChoicesList.appendChild(card);
                });
            } else {
                this.storyChoiceContainer.style.display = "none";
            }
        }

        // Faction alignment meters
        const rep = story.faction_reputation || story.reputation || { coalition: 0, syndicate: 0, precursor: 0 };
        this.scoreCoalition.textContent = (rep.coalition >= 0 ? "+" : "") + (rep.coalition || 0);
        this.scoreSyndicate.textContent = (rep.syndicate >= 0 ? "+" : "") + (rep.syndicate || 0);
        this.scorePrecursor.textContent = (rep.precursor >= 0 ? "+" : "") + (rep.precursor || 0);

        // Subspace Transmissions Feed
        const logs = story.transmission_log || [];
        this.commsLogCount.textContent = `${logs.length} TRANSMISSION${logs.length !== 1 ? 'S' : ''}`;
        const stream = this.transmissionsStream;
        const previousCount = this.storyTransmissionCount || 0;
        const wasAtBottom = stream.scrollHeight - stream.scrollTop - stream.clientHeight < 40;
        stream.innerHTML = "";

        logs.forEach(tx => {
            const item = document.createElement("div");
            item.className = "transmission-item";

            let avatarClass = "avatar-generic";
            let initials = "TX";
            const spk = tx.speaker || "";
            if (spk.includes("Vance")) {
                avatarClass = "avatar-vance";
                initials = "AV";
            } else if (spk.includes("Cipher")) {
                avatarClass = "avatar-cipher";
                initials = "CP";
            } else if (spk.includes("Archon")) {
                avatarClass = "avatar-archon";
                initials = "AP";
            }

            item.innerHTML = `
                <div class="speaker-avatar ${avatarClass}">${initials}</div>
                <div class="transmission-body">
                    <div class="transmission-header-row">
                        <span class="speaker-title">${tx.speaker}</span>
                        <span class="callsign-pill">${(tx.callsign || 'SECURE').toUpperCase()}</span>
                    </div>
                    <div class="transmission-bubble">"${tx.message}"</div>
                </div>
            `;
            stream.appendChild(item);
        });
        if (logs.length > previousCount || wasAtBottom) {
            stream.scrollTop = stream.scrollHeight;
        }
        this.storyTransmissionCount = logs.length;
    }

    async handleStoryChoice(choiceId) {
        this.sound.init();
        this.sound.playTransmission();
        try {
            const res = await fetch("/api/story/choice", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ choice_id: choiceId })
            });
            const json = await res.json();
            if (json.ok) {
                this.sound.playChime();
                this.appendLog(`[STORY] ${json.message}`, "reward");
                this.state = json.state;
                this.renderHUD();
                this.renderStory();
            } else {
                this.appendLog(`[STORY ERROR] ${json.message}`, "hazard");
            }
        } catch (e) {
            this.appendLog(`[ERROR] Transmission choice failed: ${e.message}`, "hazard");
        }
    }

    async handleSkipCadet() {
        this.sound.init();
        this.sound.playBeep(700);
        if (this.state && this.state.ship && this.state.ship.tutorial && this.state.ship.tutorial.completed) {
            this.cadetGraduationDismissed = true;
            this.cadetBanner.style.display = "none";
            return;
        }
        try {
            const res = await fetch("/api/tutorial/skip", { method: "POST" });
            const json = await res.json();
            if (json.ok) {
                this.appendLog(json.message, "system");
                this.state = json.state;
                this.renderHUD();
            }
        } catch (e) {
            console.error("Error skipping tutorial:", e);
        }
    }

    async handleResetCadet() {
        this.sound.init();
        this.sound.playBeep(850);
        this.cadetGraduationDismissed = false;
        try {
            const res = await fetch("/api/tutorial/reset", { method: "POST" });
            const json = await res.json();
            if (json.ok) {
                this.appendLog(json.message, "system");
                this.state = json.state;
                this.renderHUD();
                if (this.activeRightTab === "story") {
                    this.renderStory();
                }
            }
        } catch (e) {
            console.error("Error resetting tutorial:", e);
        }
    }

    renderMarketTable() {
        if (!this.state) return;
        this.marketTableBody.innerHTML = "";
        const quotes = this.state.market_quotes || [];
        const cargo = this.state.ship.cargo || {};

        quotes.forEach(q => {
            const tr = document.createElement("tr");
            const holdCount = cargo[q.commodity_id] || 0;

            tr.innerHTML = `
                <td><strong>${q.name}</strong><br><small style="color:var(--text-muted);">${q.category}</small></td>
                <td class="td-buy">${q.buy_price} cr</td>
                <td class="td-sell">${q.sell_price} cr</td>
                <td class="td-hold">${holdCount}</td>
                <td>
                    <div class="trade-btn-group">
                        <button class="btn-trade" data-comm="${q.commodity_id}" data-action="buy">BUY +1</button>
                        <button class="btn-trade btn-sell-trade" data-comm="${q.commodity_id}" data-action="sell" ${holdCount <= 0 ? 'disabled' : ''}>SELL 1</button>
                    </div>
                </td>
            `;

            tr.querySelectorAll(".btn-trade").forEach(b => {
                b.addEventListener("click", (e) => {
                    const cid = e.target.getAttribute("data-comm");
                    const act = e.target.getAttribute("data-action");
                    this.handleTrade(cid, 1, act === "buy");
                });
            });

            this.marketTableBody.appendChild(tr);
        });
    }

    renderArsenal() {
        if (!this.state) return;
        this.arsenalList.innerHTML = "";
        const upgrades = this.state.catalog_upgrades || [];
        const equipped = this.state.ship.equipped_upgrades || {};
        const credits = this.state.ship.credits;

        upgrades.forEach(u => {
            const isEquipped = equipped[u.slot] === u.id;
            const card = document.createElement("div");
            card.className = `arsenal-card ${isEquipped ? 'installed' : ''}`;

            card.innerHTML = `
                <div class="arsenal-info">
                    <div class="arsenal-title-row">
                        <span class="slot-tag">${u.slot.toUpperCase()}</span>
                        <strong class="arsenal-name">${u.name}</strong>
                    </div>
                    <p class="arsenal-desc">${u.description}</p>
                </div>
                <button class="btn-upgrade-buy" ${isEquipped || credits < u.cost ? 'disabled' : ''} data-id="${u.id}">
                    ${isEquipped ? 'EQUIPPED' : `${u.cost} CR`}
                </button>
            `;

            if (!isEquipped) {
                card.querySelector(".btn-upgrade-buy").addEventListener("click", () => this.handleBuyUpgrade(u.id));
            }

            this.arsenalList.appendChild(card);
        });
    }

    renderFleet() {
        if (!this.state) return;
        this.fleetRoster.innerHTML = "";
        const drones = this.state.ship.fleet_drones || [];

        if (drones.length === 0) {
            this.fleetRoster.innerHTML = `<p style="padding:12px;font-size:0.75rem;color:var(--text-muted);text-align:center;">No fleet drones active. Commission a drone below to start harvesting.</p>`;
            return;
        }

        drones.forEach(d => {
            const card = document.createElement("div");
            card.className = "drone-card";

            card.innerHTML = `
                <div class="drone-meta">
                    <strong class="drone-name">${this.escapeHtml(d.name)}</strong>
                    <span class="drone-sub">${this.escapeHtml(d.drone_type.toUpperCase())} // ${this.escapeHtml(d.assigned_system_id.toUpperCase())} [${this.escapeHtml(d.status.toUpperCase())}]</span>
                </div>
                <div class="drone-stats" style="font-family:var(--font-mono);font-size:0.65rem;color:var(--text-muted);margin:6px 0;">
                    LVL ${d.level ?? 1} // EFF ${(d.efficiency ?? 1).toFixed(2)} // INTEGRITY ${d.integrity ?? 100}% // SORTIES ${d.sorties ?? 0}${d.specialty ? " // " + this.escapeHtml(d.specialty.toUpperCase()) : ""}
                </div>
                <div class="drone-yield-badge">
                    +${d.cargo_accumulated} Ore / +${d.credits_accumulated} CR
                </div>
                <div class="drone-actions" style="display:flex;gap:5px;margin-top:6px;">
                    <button class="btn-hud" data-refit="${this.escapeHtml(d.id)}">REFIT (300 CR)</button>
                    <button class="btn-hud" data-dismiss="${this.escapeHtml(d.id)}">DISMISS</button>
                </div>
            `;
            card.querySelector("[data-refit]")?.addEventListener("click", () => this.postAction("/api/fleet/refit", { drone_id: d.id }, "fleet"));
            card.querySelector("[data-dismiss]")?.addEventListener("click", () => this.postAction("/api/fleet/dismiss", { drone_id: d.id }, "fleet"));
            this.fleetRoster.appendChild(card);
        });

        if (this.mercenaryRoster) {
            const catalog = Object.values(this.state.mercenary_catalog || {});
            const hired = new Set((this.state.ship.fleet_drones || []).filter(d => d.drone_type === "mercenary").map(d => d.specialty));
            this.mercenaryRoster.innerHTML = `<h4 class="commission-title">MERCENARY CONTRACTS</h4>` + catalog.map(m => `
                <div class="depot-card">
                    <h4>${this.escapeHtml(m.name)} // ${m.cost} CR</h4>
                    <div>${this.escapeHtml(m.description)}</div>
                    <div class="depot-actions">
                        <button class="btn-hud btn-cyan" data-merc="${this.escapeHtml(m.id)}" ${hired.has(m.specialty) ? "disabled" : ""}>${hired.has(m.specialty) ? "CONTRACTED" : "HIRE"}</button>
                    </div>
                </div>
            `).join("");
            this.mercenaryRoster.querySelectorAll("[data-merc]").forEach(btn => {
                btn.addEventListener("click", () => this.postAction("/api/mercenary/hire", { merc_id: btn.getAttribute("data-merc") }, "fleet"));
            });
        }
    }

    renderContracts() {
        if (!this.state) return;
        this.contractsList.innerHTML = "";
        const contracts = this.state.ship.active_contracts || [];

        if (contracts.length === 0) {
            this.contractsList.innerHTML = `<p style="padding:12px;font-size:0.75rem;color:var(--text-muted);text-align:center;">No active bounty contracts in flight log.</p>`;
            return;
        }

        contracts.forEach(c => {
            const card = document.createElement("div");
            card.className = `contract-card ${c.completed ? 'completed' : ''}`;

            const pct = Math.min(100, Math.round((c.current_count / c.target_count) * 100));
            const relicBadge = c.reward_relic_tier ? `<span class="reward-pill relic">+Relic [${c.reward_relic_tier.toUpperCase()}]</span>` : '';

            card.innerHTML = `
                <div class="contract-header">
                    <span class="contract-cat-badge cat-${c.category}">${c.category}</span>
                    <strong class="contract-title">${c.title}</strong>
                </div>
                <p class="contract-desc">${c.description}</p>
                <div class="contract-progress-box">
                    <div class="contract-progress-label">
                        <span>PROGRESS</span>
                        <span>${c.current_count} / ${c.target_count} (${pct}%)</span>
                    </div>
                    <div class="contract-progress-meter">
                        <div class="contract-progress-fill" style="width: ${pct}%;"></div>
                    </div>
                </div>
                <div class="contract-footer">
                    <div class="contract-rewards">
                        <span class="reward-pill">+${c.reward_credits.toLocaleString()} CR</span>
                        <span class="reward-pill xp">+${c.reward_xp} XP</span>
                        ${relicBadge}
                    </div>
                    ${c.completed ? `<button class="btn-claim-contract" data-id="${c.id}">CLAIM REWARD</button>` : `<span style="font-size:0.65rem;color:var(--text-muted);font-family:var(--font-mono);">IN PROGRESS</span>`}
                </div>
            `;

            if (c.completed) {
                card.querySelector(".btn-claim-contract").addEventListener("click", () => this.handleClaimContract(c.id));
            }

            this.contractsList.appendChild(card);
        });
    }

    renderMastery() {
        if (!this.state) return;
        const mastery = this.state.ship.mastery || { level: 1, xp: 0, next_level_xp: 500, talent_points: 0, specializations: [] };
        this.availableTalentPoints.textContent = mastery.talent_points;

        // Render Talents Grid
        this.talentsGrid.innerHTML = "";
        const talents = this.state.catalog_talents || {
            "void_cartographer": { id: "void_cartographer", name: "Void Cartographer", category: "exploration", description: "+30% sensor scan research credits and +20% Precursor Relic resonance detection." },
            "dreadnought_tactics": { id: "dreadnought_tactics", name: "Dreadnought Tactician", category: "combat", description: "+25% tactical laser damage and +25 MW shield overcharge absorption." },
            "swarm_commander": { id: "swarm_commander", name: "Swarm Fleet Overlord", category: "fleet", description: "+50% autonomous fleet drone harvest yields across all deployed systems." },
            "quantum_smuggler": { id: "quantum_smuggler", name: "Quantum Smuggler", category: "trade", description: "-25% hyperlane jump fuel burn and +20% commodity market profit margins." }
        };

        const specs = mastery.specializations || [];

        Object.values(talents).forEach(t => {
            const isUnlocked = specs.includes(t.id);
            const card = document.createElement("div");
            card.className = `talent-card ${isUnlocked ? 'unlocked' : ''}`;

            card.innerHTML = `
                <div class="talent-top">
                    <div class="talent-header-row">
                        <strong class="talent-name">${t.name}</strong>
                        <span class="contract-cat-badge cat-${t.category}">${t.category}</span>
                    </div>
                    <p class="talent-desc">${t.description}</p>
                </div>
                <button class="btn-talent-unlock" ${isUnlocked || mastery.talent_points <= 0 ? 'disabled' : ''} data-id="${t.id}">
                    ${isUnlocked ? 'ACQUIRED' : (mastery.talent_points > 0 ? 'UNLOCK PERK (1 PT)' : 'LOCKED (1 PT)')}
                </button>
            `;

            if (!isUnlocked && mastery.talent_points > 0) {
                card.querySelector(".btn-talent-unlock").addEventListener("click", () => this.handleUnlockTalent(t.id));
            }

            this.talentsGrid.appendChild(card);
        });

        // Render Precursor Relics Grid
        this.relicsGrid.innerHTML = "";
        const relics = this.state.ship.relics || [];

        if (relics.length === 0) {
            this.relicsGrid.innerHTML = `<p style="padding:10px;font-size:0.72rem;color:var(--text-muted);text-align:center;">No ancient Precursor Relics recovered yet. Recover them via planet sensor sweeps, anomalies, and contracts.</p>`;
            return;
        }

        relics.forEach(r => {
            const card = document.createElement("div");
            card.className = "relic-card";

            card.innerHTML = `
                <div class="relic-header-row">
                    <strong class="relic-name">${r.name}</strong>
                    <span class="relic-rarity-pill rarity-${r.rarity}">${r.rarity}</span>
                </div>
                <p class="relic-desc">${r.description}</p>
            `;
            this.relicsGrid.appendChild(card);
        });
    }

    appendLog(text, type = "system") {
        const line = document.createElement("div");
        line.className = `log-line log-${type}`;
        const timeStr = new Date().toLocaleTimeString();
        line.textContent = `[${timeStr}] ${text}`;
        this.flightLogStream.appendChild(line);
        this.flightLogStream.scrollTop = this.flightLogStream.scrollHeight;
    }

    // --- Actions ---

    async handleCombat(action) {
        this.sound.init();
        const currentCombo = (this.state && this.state.ship) ? (this.state.ship.tactical_combo || 0) : 0;
        if (action === "fire_lasers") {
            if (currentCombo >= 2) {
                this.sound.playCritHit();
            } else {
                this.sound.playLaser();
            }
        } else {
            this.sound.playBeep(600);
        }

        try {
            const res = await fetch("/api/combat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ action: action })
            });
            const json = await res.json();
            if (json.ok) {
                this.sound.playChime();
                this.appendLog(json.message, "reward");
            } else {
                this.appendLog(`[COMBAT] ${json.message}`, "hazard");
            }
            this.state = json.state;
            this.renderHUD();
        } catch (e) {
            this.appendLog(`[ERROR] Tactical maneuver failed: ${e.message}`, "hazard");
        }
    }

    async handleClaimContract(contractId) {
        this.sound.init();
        try {
            const res = await fetch("/api/contract/claim", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ contract_id: contractId })
            });
            const json = await res.json();
            if (json.ok) {
                this.sound.playBountyChime();
                this.appendLog(json.message, "reward");
                this.state = json.state;
                this.renderHUD();
            } else {
                this.appendLog(`[CONTRACT] ${json.message}`, "hazard");
            }
        } catch (e) {
            this.appendLog(`[ERROR] Contract claim failed: ${e.message}`, "hazard");
        }
    }

    async handleUnlockTalent(talentId) {
        this.sound.init();
        try {
            const res = await fetch("/api/mastery/unlock", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ talent_id: talentId })
            });
            const json = await res.json();
            if (json.ok) {
                this.sound.playLevelUp();
                this.appendLog(json.message, "reward");
                this.state = json.state;
                this.renderHUD();
            } else {
                this.appendLog(`[MASTERY] ${json.message}`, "hazard");
            }
        } catch (e) {
            this.appendLog(`[ERROR] Talent unlock failed: ${e.message}`, "hazard");
        }
    }

    async handleBuyUpgrade(upgradeId) {
        this.sound.init();
        try {
            const res = await fetch("/api/upgrade", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ upgrade_id: upgradeId })
            });
            const json = await res.json();
            if (json.ok) {
                this.sound.playChime();
                this.appendLog(json.message, "reward");
                this.state = json.state;
                this.renderHUD();
            } else {
                this.appendLog(`[ERROR] ${json.message}`, "hazard");
            }
        } catch (e) {
            this.appendLog(`[ERROR] Upgrade install failed: ${e.message}`, "hazard");
        }
    }

    async handleCommissionDrone(droneType) {
        this.sound.init();
        try {
            const res = await fetch("/api/drone/buy", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ drone_type: droneType })
            });
            const json = await res.json();
            if (json.ok) {
                this.sound.playChime();
                this.appendLog(json.message, "reward");
                this.state = json.state;
                this.renderHUD();
            } else {
                this.appendLog(`[ERROR] ${json.message}`, "hazard");
            }
        } catch (e) {
            this.appendLog(`[ERROR] Drone commissioning failed: ${e.message}`, "hazard");
        }
    }

    async handleHarvestFleet() {
        this.sound.init();
        try {
            const res = await fetch("/api/drone/collect", { method: "POST" });
            const json = await res.json();
            if (json.ok) {
                this.sound.playChime();
                this.appendLog(json.message, "reward");
                this.state = json.state;
                this.renderHUD();
            } else {
                this.appendLog(`[FLEET] ${json.message}`, "system");
            }
        } catch (e) {
            this.appendLog(`[ERROR] Fleet harvest failed: ${e.message}`, "hazard");
        }
    }

    async handleToggleTimePause() {
        this.sound.init();
        this.sound.playBeep(850, 0.05);
        if (!this.state || !this.state.time) return;
        const isPaused = this.state.time.is_paused;
        const endpoint = isPaused ? "/api/time/resume" : "/api/time/pause";
        try {
            const res = await fetch(endpoint, { method: "POST" });
            const json = await res.json();
            if (json.ok && json.state) {
                this.state = json.state;
                this.renderHUD();
                this.appendLog(json.message, isPaused ? "system" : "hazard");
            } else if (json.message) {
                this.appendLog(`[TIME] ${json.message}`, "system");
            }
        } catch (e) {
            this.appendLog(`[ERROR] Temporal flux error: ${e.message}`, "hazard");
        }
    }

    async handleSetTimeSpeed(speed) {
        this.sound.init();
        this.sound.playBeep(980, 0.05);
        try {
            const res = await fetch("/api/time/speed", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ speed })
            });
            const json = await res.json();
            if (json.ok && json.state) {
                this.state = json.state;
                this.renderHUD();
                this.appendLog(json.message, "system");
            } else if (json.message) {
                this.appendLog(`[TIME] ${json.message}`, "system");
            }
        } catch (e) {
            this.appendLog(`[ERROR] Temporal speed error: ${e.message}`, "hazard");
        }
    }

    async handleTimeStep(ticks = 1) {
        this.sound.init();
        this.sound.playBeep(1150, 0.04);
        try {
            const res = await fetch("/api/time/step", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ ticks })
            });
            const json = await res.json();
            if (json.ok && json.state) {
                this.state = json.state;
                this.renderHUD();
                this.appendLog(json.message, "system");
                if (json.summary) {
                    if (json.summary.shield_recharged > 0) {
                        this.appendLog(`[DEFLECTOR] Shields restored +${json.summary.shield_recharged} MW during time advance.`, "system");
                    }
                    if (json.summary.drone_cargo_harvested > 0 || json.summary.drone_credits_harvested > 0) {
                        this.appendLog(`[FLEET] Drones gathered +${json.summary.drone_cargo_harvested} ore, +${json.summary.drone_credits_harvested} cr over elapsed time.`, "reward");
                    }
                }
            } else if (json.message) {
                this.appendLog(`[TIME] ${json.message}`, "system");
            }
        } catch (e) {
            this.appendLog(`[ERROR] Temporal step error: ${e.message}`, "hazard");
        }
    }

    async handleScan() {
        this.sound.init();
        this.sound.playScan();
        try {
            const res = await fetch("/api/scan", { method: "POST" });
            const json = await res.json();
            if (json.ok) {
                const discovery = json.discovery || {};
                if (discovery.relic || discovery.near_miss) {
                    this.sound.playNearMiss();
                } else {
                    this.sound.playChime();
                }
                this.appendLog(json.message, "reward");
                this.state = json.state;
                this.renderHUD();
            } else {
                this.appendLog(`[ERROR] ${json.message}`, "hazard");
            }
        } catch (e) {
            this.appendLog(`[ERROR] Sensor telemetry link failed: ${e.message}`, "hazard");
        }
    }

    async handleOrbitAction() {
        if (!this.selectedTarget || this.selectedType !== "body") return;
        this.sound.init();
        this.sound.playBeep(920);
        const fromBodyId = this.state?.ship?.orbiting_body_id;
        const toBodyId = this.selectedTarget.id;
        try {
            const res = await fetch("/api/orbit", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ target: this.selectedTarget.id })
            });
            const json = await res.json();
            if (json.ok) {
                this.appendLog(json.message, "system");
                this.state = json.state;
                this.startTravelAnimation(fromBodyId, toBodyId);
                this.renderHUD();
                this.updateTargetCard();
            } else {
                this.appendLog(`[ERROR] ${json.message}`, "hazard");
            }
        } catch (e) {
            this.appendLog(`[ERROR] Orbit execution failed: ${e.message}`, "hazard");
        }
    }

    async handleJumpAction() {
        if (!this.selectedTarget || this.selectedType !== "system") return;
        this.sound.init();
        this.sound.playJump();
        try {
            const res = await fetch("/api/jump", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ target: this.selectedTarget.id })
            });
            const json = await res.json();
            if (json.ok) {
                this.appendLog(json.message, "system");
                this.state = json.state;
                this.renderHUD();
                this.updateTargetCard();
            } else {
                this.appendLog(`[ERROR] ${json.message}`, "hazard");
            }
        } catch (e) {
            this.appendLog(`[ERROR] Hyperspace jump aborted: ${e.message}`, "hazard");
        }
    }

    async handleApplyPower() {
        this.sound.init();
        this.sound.playBeep(1200);
        const eng = parseInt(this.sliderEng.value, 10);
        const shd = parseInt(this.sliderShd.value, 10);
        const sen = parseInt(this.sliderSen.value, 10);
        const wep = parseInt(this.sliderWep.value, 10);

        try {
            const res = await fetch("/api/power", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ engines: eng, shields: shd, sensors: sen, weapons: wep })
            });
            const json = await res.json();
            if (json.ok) {
                this.appendLog(json.message, "system");
                this.state = json.state;
                this.powerDirty = false;
                this.renderHUD();
            } else {
                this.appendLog(`[ERROR] ${json.message}`, "hazard");
            }
        } catch (e) {
            this.appendLog(`[ERROR] Power route failed: ${e.message}`, "hazard");
        }
    }

    async handleTrade(commId, qty, isBuy) {
        this.sound.init();
        try {
            const res = await fetch("/api/trade", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ commodity_id: commId, quantity: qty, is_buy: isBuy })
            });
            const json = await res.json();
            if (json.ok) {
                this.sound.playChime();
                this.appendLog(json.message, "reward");
                this.state = json.state;
                this.renderHUD();
            } else {
                this.appendLog(`[ERROR] ${json.message}`, "hazard");
            }
        } catch (e) {
            this.appendLog(`[ERROR] Trade failed: ${e.message}`, "hazard");
        }
    }

    async handleResolveAnomaly(choiceId) {
        this.sound.init();
        try {
            const res = await fetch("/api/anomaly", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ choice_id: choiceId })
            });
            const json = await res.json();
            if (json.ok) {
                this.sound.playChime();
                this.appendLog(`[RESOLVED] ${json.message}`, "reward");
            } else {
                this.appendLog(`[FAILURE] ${json.message}`, "hazard");
            }
            this.state = json.state;
            this.renderHUD();
        } catch (e) {
            this.appendLog(`[ERROR] Anomaly action failed: ${e.message}`, "hazard");
        }
    }

    async handleRepair() {
        this.sound.init();
        this.sound.playBeep(800);
        try {
            const res = await fetch("/api/repair", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ amount: 25 })
            });
            const json = await res.json();
            if (json.ok) {
                this.sound.playChime();
                this.appendLog(json.message, "reward");
                this.state = json.state;
                this.renderHUD();
            } else {
                this.appendLog(`[ERROR] ${json.message}`, "hazard");
            }
        } catch (e) {
            this.appendLog(`[ERROR] Repair failed: ${e.message}`, "hazard");
        }
    }

    async handleRefuel() {
        this.sound.init();
        this.sound.playBeep(850);
        try {
            const res = await fetch("/api/refuel", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ amount: 20 })
            });
            const json = await res.json();
            if (json.ok) {
                this.sound.playChime();
                this.appendLog(json.message, "reward");
                this.state = json.state;
                this.renderHUD();
            } else {
                this.appendLog(`[ERROR] ${json.message}`, "hazard");
            }
        } catch (e) {
            this.appendLog(`[ERROR] Refuel failed: ${e.message}`, "hazard");
        }
    }

    updateTargetCard() {
        if (!this.state) return;
        if (!this.selectedTarget) {
            this.targetType.textContent = "TARGET: NONE SELECTED";
            this.targetName.textContent = "Select a celestial body on radar";
            this.targetDist.textContent = "--";
            this.targetDesc.textContent = "Click on any planet, station, or star in the radar display to calculate orbital approach.";
            this.btnOrbitTarget.style.display = "inline-block";
            this.btnOrbitTarget.disabled = true;
            this.btnJumpTarget.style.display = "none";
            if (this.btnLandTarget) this.btnLandTarget.style.display = "none";
            this.targetGravity.textContent = "--";
            this.targetAtmosphere.textContent = "--";
            this.targetTemp.textContent = "--";
            this.targetMoons.textContent = "--";
            this.targetResources.innerHTML = "";
            return;
        }

        if (this.selectedType === "body") {
            const fresh = this.state.current_system.bodies.find(b => b.id === this.selectedTarget.id);
            if (!fresh) {
                this.selectedTarget = null;
                return this.updateTargetCard();
            }
            this.selectedTarget = fresh;
            const b = this.selectedTarget;
            this.targetType.textContent = `TARGET: ${b.body_type.toUpperCase()}`;
            this.targetName.textContent = b.name;
            this.targetDist.textContent = `${b.orbit_radius.toFixed(2)} AU`;
            this.targetDesc.textContent = b.scan_completed ? b.scan_discovery : "Uncharted body. Orbital sensor sweep required.";
            this.btnOrbitTarget.style.display = "inline-block";
            this.btnJumpTarget.style.display = "none";
            this.btnOrbitTarget.disabled = (this.state.ship.orbiting_body_id === b.id);
            this.btnOrbitTarget.textContent = (this.state.ship.orbiting_body_id === b.id) ? "ALREADY IN ORBIT" : "ENTER ORBIT";

            this.targetGravity.textContent = `${(b.gravity ?? 1).toFixed(2)} g`;
            this.targetAtmosphere.textContent = b.atmosphere || "none";
            this.targetTemp.textContent = `${b.temperature_c ?? 0} C`;
            this.targetMoons.textContent = `${(b.moons || []).length}`;
            this.targetResources.innerHTML = (b.resources || []).map(r => `<span>${this.escapeHtml(r)}</span>`).join("");
            if (this.btnLandTarget) {
                this.btnLandTarget.style.display = b.landable ? "inline-block" : "none";
                const canLand = b.landable && this.state.ship.orbiting_body_id === b.id && this.state.ship.landed_body_id !== b.id;
                this.btnLandTarget.disabled = !canLand;
                this.btnLandTarget.textContent = this.state.ship.landed_body_id === b.id ? "LANDED" : "LAND ON SURFACE";
            }
        } else if (this.selectedType === "system") {
            const fresh = this.galaxySystems[this.selectedTarget.id];
            if (!fresh) {
                this.selectedTarget = null;
                return this.updateTargetCard();
            }
            this.selectedTarget = fresh;
            const s = this.selectedTarget;
            const curSys = this.state.current_system;
            const isConn = curSys.connections.includes(s.id);
            this.targetType.textContent = `TARGET: STAR SYSTEM [${s.spectral_type}-TYPE]`;
            this.targetName.textContent = s.name;
            const dist = Math.hypot(s.x - curSys.x, s.y - curSys.y);
            this.targetDist.textContent = `${dist.toFixed(1)} LY`;
            this.targetDesc.textContent = `Faction: ${s.faction} // Security: ${(s.security * 100).toFixed(0)}% // Linked: ${isConn ? 'YES' : 'NO'}`;
            this.targetGravity.textContent = `${s.spectral_type}-class`;
            this.targetAtmosphere.textContent = `${(s.security * 100).toFixed(0)}% sec`;
            this.targetTemp.textContent = `${s.connections.length} links`;
            this.targetMoons.textContent = s.faction;
            this.targetResources.innerHTML = "";
            if (this.btnLandTarget) this.btnLandTarget.style.display = "none";
            this.btnOrbitTarget.style.display = "none";
            this.btnJumpTarget.style.display = "inline-block";
            this.btnJumpTarget.disabled = (!isConn || s.id === curSys.id);
            this.btnJumpTarget.textContent = (s.id === curSys.id) ? "CURRENT LOCATION" : (isConn ? "EXECUTE HYPERSPACE JUMP" : "OUT OF HYPERLANE RANGE");
        }
    }

    // --- Canvas Radar Rendering ---

    pointerToCanvas(e) {
        const rect = this.canvas.getBoundingClientRect();
        const scaleX = this.canvas.width / Math.max(1, rect.width);
        const scaleY = this.canvas.height / Math.max(1, rect.height);
        return {
            x: (e.clientX - rect.left) * scaleX,
            y: (e.clientY - rect.top) * scaleY,
        };
    }

    startAnimationLoop() {
        const render = () => {
            this.drawRadar();
            requestAnimationFrame(render);
        };
        requestAnimationFrame(render);
    }

    drawRadar() {
        const ctx = this.ctx;
        const w = this.canvas.width;
        const h = this.canvas.height;
        ctx.clearRect(0, 0, w, h);

        const cx = w / 2 + this.panX;
        const cy = h / 2 + this.panY;

        // Draw tactical radar grid rings
        ctx.save();
        ctx.strokeStyle = "rgba(0, 240, 255, 0.08)";
        ctx.lineWidth = 1;
        for (let r = 40; r < Math.max(w, h); r += 45 * this.zoom) {
            ctx.beginPath();
            ctx.arc(cx, cy, r, 0, Math.PI * 2);
            ctx.stroke();
        }
        ctx.restore();

        if (this.viewMode === "ORBITS") {
            this.drawOrbitsView(cx, cy);
        } else {
            this.drawGalaxyView(cx, cy);
        }
    }

    drawOrbitsView(cx, cy) {
        if (!this.state) return;
        const ctx = this.ctx;
        const curSys = this.state.current_system;
        const bodies = curSys.bodies;
        const ship = this.state.ship;
        const now = Date.now() * 0.001;

        const auScale = 45 * this.zoom;

        if (this.radarGrid) {
            ctx.strokeStyle = "rgba(0, 240, 255, 0.06)";
            ctx.lineWidth = 1;
            for (let radius = 60; radius < Math.max(this.canvas.width, this.canvas.height); radius += 60) {
                ctx.beginPath();
                ctx.arc(cx, cy, radius, 0, Math.PI * 2);
                ctx.stroke();
            }
            for (let x = 0; x < this.canvas.width; x += 60) {
                ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, this.canvas.height); ctx.stroke();
            }
            for (let y = 0; y < this.canvas.height; y += 60) {
                ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(this.canvas.width, y); ctx.stroke();
            }
        }

        bodies.forEach(b => {
            if (b.body_type === "star") {
                const pulse = 18 + Math.sin(now * 2) * 2.5;
                const grad = ctx.createRadialGradient(cx, cy, 5, cx, cy, pulse * 1.5);
                grad.addColorStop(0, "#ffffff");
                grad.addColorStop(0.3, b.color);
                grad.addColorStop(1, "transparent");

                ctx.beginPath();
                ctx.arc(cx, cy, pulse * 1.5, 0, Math.PI * 2);
                ctx.fillStyle = grad;
                ctx.fill();

                ctx.beginPath();
                ctx.arc(cx, cy, pulse * 0.7, 0, Math.PI * 2);
                ctx.fillStyle = b.color;
                ctx.fill();
                return;
            }

            // Orbital Ring
            const orbitR = b.orbit_radius * auScale;
            ctx.beginPath();
            ctx.arc(cx, cy, orbitR, 0, Math.PI * 2);
            ctx.strokeStyle = (this.selectedTarget && this.selectedTarget.id === b.id) 
                ? "rgba(0, 240, 255, 0.5)" 
                : "rgba(0, 240, 255, 0.12)";
            ctx.lineWidth = 1;
            ctx.setLineDash([4, 4]);
            ctx.stroke();
            ctx.setLineDash([]);

            // Live simulated planetary orbital angle
            const angle = b.current_angle || 0;
            const bx = cx + Math.cos(angle) * orbitR;
            const by = cy + Math.sin(angle) * orbitR;

            const bodyRadius = Math.max(4, Math.min(14, b.radius_km / 12000)) * this.zoom;

            ctx.beginPath();
            ctx.arc(bx, by, bodyRadius, 0, Math.PI * 2);
            ctx.fillStyle = b.color;
            ctx.shadowColor = b.color;
            ctx.shadowBlur = 8;
            ctx.fill();
            ctx.shadowBlur = 0;

            if (this.selectedTarget && this.selectedTarget.id === b.id) {
                ctx.strokeStyle = "#00f0ff";
                ctx.lineWidth = 1.5;
                ctx.strokeRect(bx - bodyRadius - 5, by - bodyRadius - 5, (bodyRadius + 5) * 2, (bodyRadius + 5) * 2);
            }

            if (ship.orbiting_body_id === b.id) {
                ctx.beginPath();
                ctx.arc(bx + bodyRadius + 8, by - bodyRadius - 8, 3.5, 0, Math.PI * 2);
                ctx.fillStyle = "#00ffaa";
                ctx.fill();
                ctx.font = "9px 'Share Tech Mono'";
                ctx.fillStyle = "#00ffaa";
                ctx.fillText("VF-FLAGSHIP", bx + bodyRadius + 14, by - bodyRadius - 4);
            }

            if (this.radarLabels) {
                ctx.font = "10px 'Rajdhani'";
                ctx.fillStyle = "#e6f1ff";
                ctx.fillText(b.name, bx + bodyRadius + 6, by + 3);
            }
        });

        this.drawTravelAnimation(ctx, cx, cy, auScale);
    }

    drawGalaxyView(cx, cy) {
        if (!this.state) return;
        const ctx = this.ctx;
        const curSys = this.state.current_system;
        const systems = Object.values(this.galaxySystems);
        if (!systems.length) return;

        const scale = 2.8 * this.zoom;

        ctx.strokeStyle = "rgba(0, 240, 255, 0.25)";
        ctx.lineWidth = 1;
        const drawnPairs = new Set();

        systems.forEach(s1 => {
            const x1 = cx + s1.x * scale;
            const y1 = cy + s1.y * scale;

            s1.connections.forEach(connId => {
                const pairKey = [s1.id, connId].sort().join("-");
                if (!drawnPairs.has(pairKey)) {
                    drawnPairs.add(pairKey);
                    const s2 = this.galaxySystems[connId];
                    if (s2) {
                        const x2 = cx + s2.x * scale;
                        const y2 = cy + s2.y * scale;
                        ctx.beginPath();
                        ctx.moveTo(x1, y1);
                        ctx.lineTo(x2, y2);
                        ctx.stroke();
                    }
                }
            });
        });

        systems.forEach(s => {
            const sx = cx + s.x * scale;
            const sy = cy + s.y * scale;
            const isCurrent = (s.id === curSys.id);
            const isSelected = (this.selectedTarget && this.selectedTarget.id === s.id);

            ctx.beginPath();
            ctx.arc(sx, sy, isCurrent ? 7 : 5, 0, Math.PI * 2);
            ctx.fillStyle = s.color || "#00f0ff";
            ctx.shadowColor = s.color || "#00f0ff";
            ctx.shadowBlur = 10;
            ctx.fill();
            ctx.shadowBlur = 0;

            if (isCurrent) {
                ctx.beginPath();
                ctx.arc(sx, sy, 12, 0, Math.PI * 2);
                ctx.strokeStyle = "#00ffaa";
                ctx.lineWidth = 1.5;
                ctx.stroke();
            }

            if (isSelected) {
                ctx.strokeStyle = "#00f0ff";
                ctx.lineWidth = 1.5;
                ctx.strokeRect(sx - 10, sy - 10, 20, 20);
            }

            ctx.font = "11px 'Rajdhani'";
            ctx.fillStyle = isCurrent ? "#00ffaa" : "#e6f1ff";
            ctx.fillText(s.name, sx + 10, sy + 3);
        });
    }

    handleCanvasMouseMove(e) {
        const point = this.pointerToCanvas(e);
        const mx = point.x;
        const my = point.y;
        const cx = this.canvas.width / 2 + this.panX;
        const cy = this.canvas.height / 2 + this.panY;

        let hit = null;

        if (this.viewMode === "ORBITS" && this.state) {
            const auScale = 45 * this.zoom;
            for (const b of this.state.current_system.bodies) {
                if (b.body_type === "star") continue;
                const orbitR = b.orbit_radius * auScale;
                const angle = b.current_angle || 0;
                const bx = cx + Math.cos(angle) * orbitR;
                const by = cy + Math.sin(angle) * orbitR;
                const dist = Math.hypot(mx - bx, my - by);
                if (dist < 18) {
                    hit = { item: b, type: "body" };
                    break;
                }
            }
        } else if (this.viewMode === "GALAXY") {
            const scale = 2.8 * this.zoom;
            for (const s of Object.values(this.galaxySystems)) {
                const sx = cx + s.x * scale;
                const sy = cy + s.y * scale;
                const dist = Math.hypot(mx - sx, my - sy);
                if (dist < 15) {
                    hit = { item: s, type: "system" };
                    break;
                }
            }
        }

        this.canvas.style.cursor = hit ? "pointer" : "crosshair";
    }

    handleCanvasClick(e) {
        if (this.suppressClick) {
            this.suppressClick = false;
            return;
        }
        if (this.isDragging) return;
        const point = this.pointerToCanvas(e);
        const mx = point.x;
        const my = point.y;
        const cx = this.canvas.width / 2 + this.panX;
        const cy = this.canvas.height / 2 + this.panY;

        if (this.viewMode === "ORBITS" && this.state) {
            const auScale = 45 * this.zoom;
            for (const b of this.state.current_system.bodies) {
                if (b.body_type === "star") continue;
                const orbitR = b.orbit_radius * auScale;
                const angle = b.current_angle || 0;
                const bx = cx + Math.cos(angle) * orbitR;
                const by = cy + Math.sin(angle) * orbitR;
                if (Math.hypot(mx - bx, my - by) < 18) {
                    this.selectedTarget = b;
                    this.selectedType = "body";
                    this.sound.playBeep(1000);
                    this.updateTargetCard();
                    return;
                }
            }
        } else if (this.viewMode === "GALAXY") {
            const scale = 2.8 * this.zoom;
            for (const s of Object.values(this.galaxySystems)) {
                const sx = cx + s.x * scale;
                const sy = cy + s.y * scale;
                if (Math.hypot(mx - sx, my - sy) < 15) {
                    this.selectedTarget = s;
                    this.selectedType = "system";
                    this.sound.playBeep(1000);
                    this.updateTargetCard();
                    return;
                }
            }
        }
    }
    renderFactions() {
        if (!this.state) return;
        if (!this.state.factions || !this.factionsGrid) return;

        this.factionsGrid.innerHTML = "";
        Object.entries(this.state.factions).forEach(([fid, f]) => {
            const card = document.createElement("div");
            card.className = "faction-card";
            card.style.borderColor = `${f.primary_color}44`;

            const tierClass = `tier-${f.standing_tier.toLowerCase()}`;
            const barPct = Math.max(0, Math.min(100, Math.round(((f.standing + 100) / 200) * 100)));

            card.innerHTML = `
                <div class="faction-top-row">
                    <span class="faction-name" style="color: ${f.primary_color};">${f.name}</span>
                    <span class="standing-badge ${tierClass}">${f.standing_tier.toUpperCase()} (${f.standing > 0 ? "+" : ""}${f.standing})</span>
                </div>
                <div class="faction-ideology">Ideology: ${f.ideology} // HQ: ${f.headquarters_system.toUpperCase()}</div>
                <div class="standing-bar-wrap">
                    <div class="standing-bar-fill" style="width: ${barPct}%; background: ${f.primary_color};"></div>
                </div>
                <div class="faction-perk">Diplomatic Status: <strong>${f.active_perk}</strong></div>
            `;
            this.factionsGrid.appendChild(card);
        });

        if (!this.state.corporations || !this.corpsGrid) return;

        this.corpsGrid.innerHTML = "";
        Object.entries(this.state.corporations).forEach(([cid, c]) => {
            const card = document.createElement("div");
            card.className = "corp-card";
            const commTitle = c.specialty_commodity.replace('_', ' ').toUpperCase();
            const barPct = Math.max(0, Math.min(100, Math.round(((c.standing + 100) / 200) * 100)));

            card.innerHTML = `
                <div class="corp-top-row">
                    <span class="corp-name">${c.name}</span>
                    <span class="standing-badge tier-friendly">STANDING: ${c.standing > 0 ? "+" : ""}${c.standing}</span>
                </div>
                <div class="corp-desc">HQ: ${c.headquarters_system.toUpperCase()} // Commercial Specialty: <strong style="color: var(--neon-cyan);">${commTitle}</strong> (+${Math.round(c.bonus_trade_margin * 100)}% Sale Profit)</div>
                <div class="standing-bar-wrap">
                    <div class="standing-bar-fill" style="width: ${barPct}%; background: #ffd700;"></div>
                </div>
                <div class="corp-perk">Sponsorship Benefit: <strong>${c.corporate_perk}</strong></div>
            `;
            this.corpsGrid.appendChild(card);
        });
    }
    escapeHtml(value) {
        return String(value ?? "").replace(/[&<>"']/g, ch => ({
            "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
        }[ch]));
    }

    loadSettings() {
        try {
            const saved = JSON.parse(localStorage.getItem("voidfarer_settings") || "{}");
            this.radarGrid = saved.radarGrid !== false;
            this.radarLabels = saved.radarLabels !== false;
            this.travelAnimationEnabled = saved.travelAnimation !== false;
            this.starDensity = Number(saved.starDensity || 140);
            if (saved.sound === false) {
                this.sound.enabled = false;
                const audioIcon = document.getElementById("audioIcon");
                if (audioIcon) audioIcon.textContent = "MUTED";
            }
        } catch (e) {
            this.radarGrid = true;
            this.radarLabels = true;
            this.travelAnimationEnabled = true;
            this.starDensity = 140;
        }
    }

    saveSettings() {
        const payload = {
            sound: this.sound.enabled,
            radarGrid: this.radarGrid,
            radarLabels: this.radarLabels,
            travelAnimation: this.travelAnimationEnabled,
            starDensity: this.starDensity,
        };
        try { localStorage.setItem("voidfarer_settings", JSON.stringify(payload)); } catch (e) {}
    }

    applySettingsFromUI() {
        this.sound.enabled = document.getElementById("settingSound")?.checked !== false;
        this.radarGrid = document.getElementById("settingGrid")?.checked !== false;
        this.radarLabels = document.getElementById("settingLabels")?.checked !== false;
        this.travelAnimationEnabled = document.getElementById("settingAnimation")?.checked !== false;
        this.starDensity = Number(document.getElementById("settingStarDensity")?.value || 140);
        const audioIcon = document.getElementById("audioIcon");
        if (audioIcon) audioIcon.textContent = this.sound.enabled ? "SFX" : "MUTED";
        this.saveSettings();
    }

    openSettings() {
        const sound = document.getElementById("settingSound");
        const grid = document.getElementById("settingGrid");
        const labels = document.getElementById("settingLabels");
        const animation = document.getElementById("settingAnimation");
        const density = document.getElementById("settingStarDensity");
        if (sound) sound.checked = this.sound.enabled;
        if (grid) grid.checked = this.radarGrid;
        if (labels) labels.checked = this.radarLabels;
        if (animation) animation.checked = this.travelAnimationEnabled;
        if (density) density.value = this.starDensity;
        const overlay = document.getElementById("settingsOverlay");
        if (overlay) overlay.style.display = "flex";
    }

    closeSettings() {
        const overlay = document.getElementById("settingsOverlay");
        if (overlay) overlay.style.display = "none";
    }

    openMainMenu() {
        const overlay = document.getElementById("mainMenuOverlay");
        if (overlay) overlay.classList.remove("hidden");
    }

    closeMainMenu() {
        const overlay = document.getElementById("mainMenuOverlay");
        if (overlay) overlay.classList.add("hidden");
    }

    async menuAction(endpoint, successMessage) {
        const status = document.getElementById("mainMenuStatus");
        if (status) status.textContent = "TRANSMITTING...";
        try {
            const res = await fetch(endpoint, { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
            const json = await res.json();
            if (json.state) {
                this.state = json.state;
                this.renderHUD();
            }
            if (status) status.textContent = (json.ok ? "OK: " : "ERROR: ") + (json.message || successMessage);
            if (json.ok && ["/api/load", "/api/new-game"].includes(endpoint)) {
                this.closeMainMenu();
                this.viewMode = "ORBITS";
                this.selectedTarget = null;
                this.fetchGalaxy();
            }
            if (json.ok) this.sound.playChime();
        } catch (e) {
            if (status) status.textContent = `ERROR: ${e.message}`;
        }
    }

    openPerksWindow() {
        this.renderPerksWindow();
        const overlay = document.getElementById("perksOverlay");
        if (overlay) overlay.style.display = "flex";
        this.sound.playBeep(820, 0.05);
    }

    closePerksWindow() {
        const overlay = document.getElementById("perksOverlay");
        if (overlay) overlay.style.display = "none";
    }

    renderPerksWindow() {
        if (!this.state) return;
        const container = document.getElementById("perksBranches");
        const pointsEl = document.getElementById("perksWindowPoints");
        if (!container) return;
        const mastery = this.state.ship.mastery || { talent_points: 0, specializations: [] };
        const specs = mastery.specializations || [];
        if (pointsEl) pointsEl.textContent = `${mastery.talent_points || 0} POINTS`;

        const talents = Object.values(this.state.catalog_talents || {});
        const branches = {};
        talents.forEach(t => {
            const branch = t.branch || (t.category || "OTHER").toUpperCase();
            (branches[branch] = branches[branch] || []).push(t);
        });
        container.innerHTML = Object.entries(branches).map(([branch, nodes]) => `
            <div class="perk-branch">
                <h4>${this.escapeHtml(branch)}</h4>
                ${nodes.sort((a, b) => (a.tier || 1) - (b.tier || 1)).map(t => {
                    const unlocked = specs.includes(t.id);
                    const requires = t.requires || [];
                    const requiresMet = requires.every(r => specs.includes(r));
                    const canUnlock = !unlocked && requiresMet && (mastery.talent_points || 0) > 0;
                    return `<div class="perk-node ${unlocked ? "unlocked" : "locked"}">
                        <strong>${this.escapeHtml(t.name)}</strong>
                        <div>${this.escapeHtml(t.description)}</div>
                        ${unlocked ? "<div>UNLOCKED</div>" : `<button class="btn-hud" data-talent="${this.escapeHtml(t.id)}" ${canUnlock ? "" : "disabled"}>${requiresMet ? "UNLOCK" : "REQUIRES " + requires.join(", ").toUpperCase()}</button>`}
                    </div>`;
                }).join("")}
            </div>
        `).join("");
        container.querySelectorAll("[data-talent]").forEach(btn => {
            btn.addEventListener("click", () => this.handleUnlockPerk(btn.getAttribute("data-talent")));
        });
    }

    async handleUnlockPerk(talentId) {
        try {
            const res = await fetch("/api/mastery/unlock", {
                method: "POST", headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ talent_id: talentId }),
            });
            const json = await res.json();
            if (json.ok) {
                this.state = json.state;
                this.renderHUD();
                this.renderPerksWindow();
                this.sound.playChime();
                this.appendLog(json.message, "reward");
            } else {
                this.appendLog(`[ERROR] ${json.message}`, "hazard");
            }
        } catch (e) {
            this.appendLog(`[ERROR] Perk unlock failed: ${e.message}`, "hazard");
        }
    }

    renderQuests() {
        if (!this.state || !this.questsList) return;
        const quests = this.state.quests || [];
        this.questsList.innerHTML = quests.length ? quests.map(q => {
            const pct = q.target_count > 0 ? Math.min(100, Math.round((q.progress / q.target_count) * 100)) : 0;
            return `<div class="quest-card">
                <h4>${this.escapeHtml(q.title)}</h4>
                <div>${this.escapeHtml(q.description)}</div>
                <div>TYPE: ${this.escapeHtml(q.kind.toUpperCase())} // REWARD: ${this.escapeHtml(q.reward)}</div>
                <div class="quest-progress"><div style="width:${pct}%"></div></div>
                <div>${q.progress}/${q.target_count} ${q.completed ? "// COMPLETE" : ""}</div>
            </div>`;
        }).join("") : '<div class="quest-card">No active quests.</div>';
    }

    renderAICaptains() {
        if (!this.state || !this.aiList) return;
        const captains = this.state.ai_captains || [];
        this.aiList.innerHTML = captains.map(c => `
            <div class="ai-card">
                <h4>${this.escapeHtml(c.name)} <small>[${this.escapeHtml(c.archetype.toUpperCase())}]</small></h4>
                <div>${this.escapeHtml(c.description)}</div>
                <div>SYSTEM: ${this.escapeHtml(c.system_id)} // TRUST: ${c.trust} // STANDING: ${c.standing}</div>
                <div>CARGO: ${Object.entries(c.cargo || {}).map(([k, v]) => `${this.escapeHtml(k)} x${v}`).join(", ") || "empty"}</div>
                <div class="ai-actions">
                    <button class="btn-hud" data-captain="${this.escapeHtml(c.id)}" data-action="hail">HAIL</button>
                    <button class="btn-hud" data-captain="${this.escapeHtml(c.id)}" data-action="buy">BUY FUEL</button>
                    <button class="btn-hud" data-captain="${this.escapeHtml(c.id)}" data-action="sell">SELL FUEL</button>
                    ${c.archetype === "mercenary" ? `<button class="btn-hud btn-cyan" data-captain="${this.escapeHtml(c.id)}" data-action="hire" ${c.hired ? "disabled" : ""}>HIRE</button>` : ""}
                    <button class="btn-hud btn-green" data-captain="${this.escapeHtml(c.id)}" data-action="ally" ${c.ally ? "disabled" : ""}>ALLY</button>
                </div>
            </div>
        `).join("") || '<div class="ai-card">No AI captains in range.</div>';
        this.aiList.querySelectorAll("[data-captain]").forEach(btn => {
            btn.addEventListener("click", () => this.handleAIAction(btn.getAttribute("data-captain"), btn.getAttribute("data-action")));
        });
    }

    async handleAIAction(captainId, action) {
        await this.postAction("/api/ai/interact", { captain_id: captainId, action, commodity_id: "fuel_cells", quantity: 1 }, "ai");
    }

    renderDepots() {
        if (!this.state || !this.depotList) return;
        const sysId = this.state.current_system?.id;
        const depot = (this.state.depots || []).find(d => d.system_id === sysId);
        if (!depot) {
            this.depotSummary.textContent = "No depot registered in this system.";
            this.depotList.innerHTML = "";
            return;
        }
        const used = Object.values(depot.cargo || {}).reduce((a, b) => a + b, 0);
        this.depotSummary.textContent = `${depot.name} // STORED UNITS: ${used}/${depot.capacity}`;
        const depotRows = Object.entries(depot.cargo || {}).map(([item, qty]) => `
            <div class="depot-card">
                <h4>${this.escapeHtml(item)} x${qty}</h4>
                <div class="depot-actions">
                    <button class="btn-hud" data-action="withdraw" data-item="${this.escapeHtml(item)}">WITHDRAW 1</button>
                    <button class="btn-hud btn-green" data-action="sell" data-item="${this.escapeHtml(item)}">SELL 1 FROM DEPOT</button>
                </div>
            </div>
        `).join("");
        const shipRows = (this.state.inventory_manifest || []).map(item => `
            <div class="depot-card">
                <h4>SHIP: ${this.escapeHtml(item.name || item.id)} x${item.total_quantity || item.quantity || 0}</h4>
                <div class="depot-actions">
                    <button class="btn-hud" data-action="deposit" data-item="${this.escapeHtml(item.id)}">DEPOSIT 1</button>
                </div>
            </div>
        `).join("");
        this.depotList.innerHTML = depotRows + shipRows || '<div class="depot-card">Depot and hold are empty.</div>';
        this.depotList.querySelectorAll("[data-action]").forEach(btn => {
            btn.addEventListener("click", () => this.handleDepotAction(btn.getAttribute("data-action"), btn.getAttribute("data-item")));
        });
    }

    async handleDepotAction(action, itemId) {
        await this.postAction(`/api/depot/${action}`, { item_id: itemId, quantity: 1 }, "depot");
    }

    renderMessages() {
        if (!this.state || !this.messageList) return;
        const messages = this.state.messages || [];
        this.messageList.innerHTML = messages.slice().reverse().map(m => `
            <div class="message-card ${m.read ? "" : "unread"}">
                <h4>${this.escapeHtml(m.subject)}</h4>
                <div>FROM: ${this.escapeHtml(m.sender)} // TO: ${this.escapeHtml(m.recipient)} // TICK ${m.tick}</div>
                <div>${this.escapeHtml(m.body)}</div>
                ${m.read ? "" : `<button class="btn-hud" data-message="${this.escapeHtml(m.id)}">MARK READ</button>`}
            </div>
        `).join("") || '<div class="message-card">Inbox is empty.</div>';
        this.messageList.querySelectorAll("[data-message]").forEach(btn => {
            btn.addEventListener("click", () => this.postAction("/api/messages/read", { message_id: btn.getAttribute("data-message") }, "messages"));
        });
        const unread = messages.filter(m => !m.read).length;
        if (this.messagesBadge) {
            this.messagesBadge.textContent = String(unread);
            this.messagesBadge.style.display = unread > 0 ? "inline-block" : "none";
        }
    }

    async handleSendMessage() {
        const recipient = document.getElementById("messageRecipient")?.value || "";
        const subject = document.getElementById("messageSubject")?.value || "";
        const body = document.getElementById("messageBody")?.value || "";
        await this.postAction("/api/messages/send", { recipient, subject, body }, "messages");
        ["messageRecipient", "messageSubject", "messageBody"].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.value = "";
        });
    }

    async handleLandAction() {
        if (!this.selectedTarget || this.selectedType !== "body") return;
        await this.postAction("/api/land", { target: this.selectedTarget.id });
    }

    startTravelAnimation(fromBodyId, toBodyId) {
        if (!this.travelAnimationEnabled || !this.state) return;
        const bodies = this.state.current_system?.bodies || [];
        const from = bodies.find(b => b.id === fromBodyId);
        const to = bodies.find(b => b.id === toBodyId);
        if (!to) return;
        this.travelAnimation = {
            fromAngle: from ? (from.current_angle || 0) : 0,
            fromRadius: from ? from.orbit_radius : to.orbit_radius,
            toAngle: to.current_angle || 0,
            toRadius: to.orbit_radius,
            start: performance.now(),
            duration: 1300,
        };
    }

    drawTravelAnimation(ctx, cx, cy, auScale) {
        if (!this.travelAnimation) return;
        const anim = this.travelAnimation;
        const progress = Math.min(1, (performance.now() - anim.start) / anim.duration);
        const eased = progress < 0.5 ? 2 * progress * progress : 1 - Math.pow(-2 * progress + 2, 2) / 2;
        let delta = anim.toAngle - anim.fromAngle;
        while (delta > Math.PI) delta -= Math.PI * 2;
        while (delta < -Math.PI) delta += Math.PI * 2;
        const angle = anim.fromAngle + delta * eased;
        const radius = (anim.fromRadius + (anim.toRadius - anim.fromRadius) * eased) * auScale;
        const x = cx + Math.cos(angle) * radius;
        const y = cy + Math.sin(angle) * radius;
        ctx.beginPath();
        ctx.arc(x, y, 5, 0, Math.PI * 2);
        ctx.fillStyle = "#00f0ff";
        ctx.shadowColor = "#00f0ff";
        ctx.shadowBlur = 18;
        ctx.fill();
        ctx.shadowBlur = 0;
        ctx.font = "9px 'Share Tech Mono'";
        ctx.fillStyle = "#00f0ff";
        ctx.fillText("VF-TRANSIT", x + 8, y - 8);
        if (progress >= 1) this.travelAnimation = null;
    }

    async postAction(endpoint, payload, refreshTab = null) {
        try {
            const res = await fetch(endpoint, {
                method: "POST", headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            const json = await res.json();
            if (json.ok) {
                this.appendLog(json.message, "system");
                this.state = json.state;
                this.renderHUD();
                if (refreshTab && this.activeRightTab === refreshTab) {
                    if (refreshTab === "ai") this.renderAICaptains();
                    if (refreshTab === "depot") this.renderDepots();
                    if (refreshTab === "messages") this.renderMessages();
                }
                this.sound.playBeep(980, 0.05);
            } else {
                this.appendLog(`[ERROR] ${json.message}`, "hazard");
            }
            return json;
        } catch (e) {
            this.appendLog(`[ERROR] ${e.message}`, "hazard");
            return { ok: false, message: e.message };
        }
    }
}

// Instantiate on load
window.addEventListener("DOMContentLoaded", () => {
    window.cockpit = new CockpitApp();
});
