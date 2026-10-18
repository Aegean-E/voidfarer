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

        this.initDOMElements();
        this.bindEvents();
        this.startAnimationLoop();
        this.refreshState();
        this.fetchGalaxy();

        // Polling interval for live sync
        setInterval(() => this.refreshState(true), 3000);
    }

    initDOMElements() {
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
        this.btnJumpTarget = document.getElementById("btnJumpTarget");

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

        // Log
        this.flightLogStream = document.getElementById("flightLogStream");

        // Combat Card
        this.combatCard = document.getElementById("combatCard");
        this.combatEnemyTitle = document.getElementById("combatEnemyTitle");
        this.combatEnemyHp = document.getElementById("combatEnemyHp");
        this.combatEnemyBar = document.getElementById("combatEnemyBar");
        this.btnCombatFire = document.getElementById("btnCombatFire");
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
        this.contractsBadge = document.getElementById("contractsBadge");
        this.storyBadge = document.getElementById("storyBadge");

        this.tabContentMarket = document.getElementById("tabContentMarket");
        this.tabContentArsenal = document.getElementById("tabContentArsenal");
        this.tabContentFleet = document.getElementById("tabContentFleet");
        this.tabContentContracts = document.getElementById("tabContentContracts");
        this.tabContentMastery = document.getElementById("tabContentMastery");
        this.tabContentStory = document.getElementById("tabContentStory");

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
        sliders.forEach(s => s.addEventListener("input", () => this.updatePowerAllocationDisplay()));
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
        this.btnSkipCadet.addEventListener("click", () => this.handleSkipCadet());
        if (this.btnResetCadetAcademy) {
            this.btnResetCadetAcademy.addEventListener("click", () => this.handleResetCadet());
        }

        // Combat Buttons
        this.btnCombatFire.addEventListener("click", () => this.handleCombat("fire_lasers"));
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
            this.isDragging = true;
            this.dragStartX = e.clientX - this.panX;
            this.dragStartY = e.clientY - this.panY;
        });

        window.addEventListener("mouseup", () => {
            this.isDragging = false;
        });

        this.canvas.addEventListener("mousemove", (e) => {
            if (this.isDragging) {
                this.panX = e.clientX - this.dragStartX;
                this.panY = e.clientY - this.dragStartY;
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
    }

    switchRightTab(tabName) {
        this.sound.playBeep(750, 0.05);
        this.activeRightTab = tabName;

        this.tabBtnMarket.classList.toggle("active", tabName === "market");
        this.tabBtnArsenal.classList.toggle("active", tabName === "arsenal");
        this.tabBtnFleet.classList.toggle("active", tabName === "fleet");
        this.tabBtnContracts.classList.toggle("active", tabName === "contracts");
        this.tabBtnMastery.classList.toggle("active", tabName === "mastery");
        this.tabBtnStory.classList.toggle("active", tabName === "story");

        this.tabContentMarket.style.display = (tabName === "market") ? "flex" : "none";
        this.tabContentArsenal.style.display = (tabName === "arsenal") ? "flex" : "none";
        this.tabContentFleet.style.display = (tabName === "fleet") ? "flex" : "none";
        this.tabContentContracts.style.display = (tabName === "contracts") ? "flex" : "none";
        this.tabContentMastery.style.display = (tabName === "mastery") ? "flex" : "none";
        this.tabContentStory.style.display = (tabName === "story") ? "flex" : "none";

        if (tabName === "arsenal") this.renderArsenal();
        if (tabName === "fleet") this.renderFleet();
        if (tabName === "contracts") this.renderContracts();
        if (tabName === "mastery") this.renderMastery();
        if (tabName === "story") this.renderStory();
    }

    setPowerSliders(e, sh, se, w) {
        this.sliderEng.value = e;
        this.sliderShd.value = sh;
        this.sliderSen.value = se;
        this.sliderWep.value = w;
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

        const totalCargo = Object.values(ship.cargo).reduce((a, b) => a + b, 0);
        this.cargoSummary.textContent = `HOLD: ${totalCargo}/${ship.cargo_capacity}`;
        this.cargoDetailed.textContent = `${totalCargo} / ${ship.cargo_capacity} UNITS`;
        this.cargoMeterFill.style.width = `${Math.min(100, Math.round((totalCargo / ship.cargo_capacity) * 100))}%`;

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
            this.combatEnemyHp.textContent = `${c.enemy_hull} / ${c.enemy_max_hull}`;
            const pct = Math.round((c.enemy_hull / c.enemy_max_hull) * 100);
            this.combatEnemyBar.style.width = `${pct}%`;

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
        }
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
        this.transmissionsStream.innerHTML = "";

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
            this.transmissionsStream.appendChild(item);
        });
        this.transmissionsStream.scrollTop = this.transmissionsStream.scrollHeight;
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
                this.appendLog(json.message, "reward");
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
                    <strong class="drone-name">${d.name}</strong>
                    <span class="drone-sub">${d.drone_type.toUpperCase()} // ${d.assigned_system_id.toUpperCase()} [${d.status.toUpperCase()}]</span>
                </div>
                <div class="drone-yield-badge">
                    +${d.cargo_accumulated} Ore / +${d.credits_accumulated} CR
                </div>
            `;
            this.fleetRoster.appendChild(card);
        });
    }

    renderContracts() {
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

    async handleScan() {
        this.sound.init();
        this.sound.playScan();
        try {
            const res = await fetch("/api/scan", { method: "POST" });
            const json = await res.json();
            if (json.ok) {
                if (json.relic || json.near_miss) {
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
        if (!this.selectedTarget) {
            this.targetType.textContent = "TARGET: NONE SELECTED";
            this.targetName.textContent = "Select a celestial body on radar";
            this.targetDist.textContent = "--";
            this.targetDesc.textContent = "Click on any planet, station, or star in the radar display to calculate orbital approach.";
            this.btnOrbitTarget.style.display = "inline-block";
            this.btnOrbitTarget.disabled = true;
            this.btnJumpTarget.style.display = "none";
            return;
        }

        if (this.selectedType === "body") {
            const b = this.selectedTarget;
            this.targetType.textContent = `TARGET: ${b.body_type.toUpperCase()}`;
            this.targetName.textContent = b.name;
            this.targetDist.textContent = `${b.orbit_radius.toFixed(2)} AU`;
            this.targetDesc.textContent = b.scan_completed ? b.scan_discovery : "Uncharted body. Orbital sensor sweep required.";
            this.btnOrbitTarget.style.display = "inline-block";
            this.btnJumpTarget.style.display = "none";
            this.btnOrbitTarget.disabled = (this.state.ship.orbiting_body_id === b.id);
            this.btnOrbitTarget.textContent = (this.state.ship.orbiting_body_id === b.id) ? "ALREADY IN ORBIT" : "ENTER ORBIT";
        } else if (this.selectedType === "system") {
            const s = this.selectedTarget;
            const curSys = this.state.current_system;
            const isConn = curSys.connections.includes(s.id);
            this.targetType.textContent = `TARGET: STAR SYSTEM [${s.spectral_type}-TYPE]`;
            this.targetName.textContent = s.name;
            const dist = Math.hypot(s.x - curSys.x, s.y - curSys.y);
            this.targetDist.textContent = `${dist.toFixed(1)} LY`;
            this.targetDesc.textContent = `Faction: ${s.faction} // Security: ${(s.security * 100).toFixed(0)}% // Linked: ${isConn ? 'YES' : 'NO'}`;
            this.btnOrbitTarget.style.display = "none";
            this.btnJumpTarget.style.display = "inline-block";
            this.btnJumpTarget.disabled = (!isConn || s.id === curSys.id);
            this.btnJumpTarget.textContent = (s.id === curSys.id) ? "CURRENT LOCATION" : (isConn ? "EXECUTE HYPERSPACE JUMP" : "OUT OF HYPERLANE RANGE");
        }
    }

    // --- Canvas Radar Rendering ---

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

            // Live planetary angle
            const angle = b.current_angle + b.orbit_speed * now * 0.5;
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
                ctx.strokeStyle = "var(--neon-cyan)";
                ctx.lineWidth = 1.5;
                ctx.strokeRect(bx - bodyRadius - 5, by - bodyRadius - 5, (bodyRadius + 5) * 2, (bodyRadius + 5) * 2);
            }

            if (ship.orbiting_body_id === b.id) {
                ctx.beginPath();
                ctx.arc(bx + bodyRadius + 8, by - bodyRadius - 8, 3.5, 0, Math.PI * 2);
                ctx.fillStyle = "var(--neon-green)";
                ctx.fill();
                ctx.font = "9px 'Share Tech Mono'";
                ctx.fillStyle = "var(--neon-green)";
                ctx.fillText("VF-FLAGSHIP", bx + bodyRadius + 14, by - bodyRadius - 4);
            }

            ctx.font = "10px 'Rajdhani'";
            ctx.fillStyle = "#e6f1ff";
            ctx.fillText(b.name, bx + bodyRadius + 6, by + 3);
        });
    }

    drawGalaxyView(cx, cy) {
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
                ctx.strokeStyle = "var(--neon-green)";
                ctx.lineWidth = 1.5;
                ctx.stroke();
            }

            if (isSelected) {
                ctx.strokeStyle = "var(--neon-cyan)";
                ctx.lineWidth = 1.5;
                ctx.strokeRect(sx - 10, sy - 10, 20, 20);
            }

            ctx.font = "11px 'Rajdhani'";
            ctx.fillStyle = isCurrent ? "var(--neon-green)" : "#e6f1ff";
            ctx.fillText(s.name, sx + 10, sy + 3);
        });
    }

    handleCanvasMouseMove(e) {
        const rect = this.canvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;
        const cx = this.canvas.width / 2 + this.panX;
        const cy = this.canvas.height / 2 + this.panY;

        let hit = null;

        if (this.viewMode === "ORBITS" && this.state) {
            const auScale = 45 * this.zoom;
            const now = Date.now() * 0.001;
            for (const b of this.state.current_system.bodies) {
                if (b.body_type === "star") continue;
                const orbitR = b.orbit_radius * auScale;
                const angle = b.current_angle + b.orbit_speed * now * 0.5;
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
        if (this.isDragging) return;
        const rect = this.canvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;
        const cx = this.canvas.width / 2 + this.panX;
        const cy = this.canvas.height / 2 + this.panY;

        if (this.viewMode === "ORBITS" && this.state) {
            const auScale = 45 * this.zoom;
            const now = Date.now() * 0.001;
            for (const b of this.state.current_system.bodies) {
                if (b.body_type === "star") continue;
                const orbitR = b.orbit_radius * auScale;
                const angle = b.current_angle + b.orbit_speed * now * 0.5;
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
}

// Instantiate on load
window.addEventListener("DOMContentLoaded", () => {
    window.cockpit = new CockpitApp();
});
