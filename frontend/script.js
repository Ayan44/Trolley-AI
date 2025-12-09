const API_BASE = "";


// Default weights for custom mode (same as backend)
const DEFAULT_AGE_WEIGHTS = {
    "child": 4,
    "teen": 3,
    "young": 3,
    "adult": 2,
    "elder": 1
};

const DEFAULT_ROLE_WEIGHTS = {
    "doctor": 4,
    "nurse": 3,
    "teacher": 3,
    "engineer": 2,
    "student": 2,
    "unemployed": 1,
    "retired": 1,
    "pregnant": 3,
    "criminal": -1,
    "thief": 0,
    "other": 1
};

const DEFAULT_FLAG_WEIGHTS = {
    "pregnant": 3,
    "disabled": 2,
    "innocent": 1,
    "guilty": -2,
    "law_breaker": -1,
    "relative": 2,
    "friend": 1,
    "stranger": 0,
    "saves_lives": 2,
    "vulnerable": 2
};

const scenario = {
    track1: [],
    track2: [],
    deon_variant: "protect_children",
    manual_choice: null,
    custom_rules: null
};

let selectedMode = "utilitarian";
const historyEntries = [];

// Backend-compatible option arrays
const AGE_OPTIONS = [
    { value: "child", label: "Uşaq" },
    { value: "teen", label: "Gənc" },
    { value: "young", label: "Cavan" },
    { value: "adult", label: "Böyük" },
    { value: "elder", label: "Qoca" }
];

const ROLE_OPTIONS = [
    { value: "doctor", label: "Həkim" },
    { value: "nurse", label: "Tibb bacısı" },
    { value: "teacher", label: "Müəllim" },
    { value: "engineer", label: "Mühəndis" },
    { value: "student", label: "Tələbə/Şagird" },
    { value: "unemployed", label: "İşsiz" },
    { value: "retired", label: "Təqaüdçü" },
    { value: "pregnant", label: "Hamilə" },
    { value: "criminal", label: "Cinayətkar" },
    { value: "thief", label: "Oğru" },
    { value: "other", label: "Digər" }
];

const FLAG_OPTIONS = [
    { value: "disabled", label: "Əlil" },
    { value: "innocent", label: "Günahsız" },
    { value: "guilty", label: "Günahkar" },
    { value: "law_breaker", label: "Qanun pozanı" },
    { value: "relative", label: "Qohum" },
    { value: "friend", label: "Dost" },
    { value: "stranger", label: "Yad" },
    { value: "saves_lives", label: "Həyat xilas edir" },
    { value: "vulnerable", label: "Zəif qrup" }
];

// Current selection state for each track
let currentSelectionTrack1 = { age: null, role: null, flags: [] };
let currentSelectionTrack2 = { age: null, role: null, flags: [] };

document.addEventListener("DOMContentLoaded", () => {
    setupTabs();
    setupTrackPanels();
    setupControls();
    initializeScene();
    renderHistory(); // boş mesaj göstərsin
});

function setupTabs() {
    const tabButtons = document.querySelectorAll(".tab-btn");
    const views = document.querySelectorAll(".tab-view");

    tabButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const target = btn.getAttribute("data-tab");

            tabButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            views.forEach(view => {
                if (view.id === `${target}-view`) {
                    view.classList.add("active");
                } else {
                    view.classList.remove("active");
                }
            });
        });
    });
}

function setupTrackPanels() {
    // Setup Track 1 panel
    setupTrackPanel("track1", currentSelectionTrack1);
    // Setup Track 2 panel
    setupTrackPanel("track2", currentSelectionTrack2);
}

function setupTrackPanel(trackKey, currentSelection) {
    const panel = document.getElementById(`${trackKey}-panel`);
    if (!panel) return;

    // Create button rows container
    const buttonContainer = document.createElement("div");
    buttonContainer.className = "button-rows-container";

    // Row 1: Age buttons
    const ageRow = createButtonRow("Yaş", AGE_OPTIONS, "age", trackKey, currentSelection);
    buttonContainer.appendChild(ageRow);

    // Row 2: Role buttons
    const roleRow = createButtonRow("Rol", ROLE_OPTIONS, "role", trackKey, currentSelection);
    buttonContainer.appendChild(roleRow);

    // Row 3: Flag buttons
    const flagRow = createButtonRow("Atributlar", FLAG_OPTIONS, "flags", trackKey, currentSelection);
    buttonContainer.appendChild(flagRow);

    // Add to Track button
    const addBtn = document.createElement("button");
    addBtn.className = "btn btn-primary add-to-track-btn";
    addBtn.textContent = `Əlavə et: ${trackKey === "track1" ? "Rels 1" : "Rels 2"}`;
    addBtn.addEventListener("click", () => {
        addPersonToTrack(trackKey, currentSelection);
    });

    // Replace existing person-form with new structure
    const existingForm = panel.querySelector(".person-form");
    if (existingForm) {
        existingForm.remove();
    }

    buttonContainer.appendChild(addBtn);
    panel.insertBefore(buttonContainer, panel.querySelector(`#${trackKey}-list`));
}

function createButtonRow(label, options, type, trackKey, currentSelection) {
    const row = document.createElement("div");
    row.className = "button-row";

    const labelEl = document.createElement("div");
    labelEl.className = "button-row-label";
    labelEl.textContent = label;
    row.appendChild(labelEl);

    const buttonGroup = document.createElement("div");
    buttonGroup.className = "button-group";

    options.forEach(option => {
        const btn = document.createElement("button");
        btn.className = "option-btn";
        btn.textContent = option.label;
        btn.dataset.value = option.value;
        btn.dataset.type = type;
        btn.dataset.track = trackKey;

        // Set initial active state
        if (type === "age" && currentSelection.age === option.value) {
            btn.classList.add("active");
        } else if (type === "role" && currentSelection.role === option.value) {
            btn.classList.add("active");
        } else if (type === "flags" && currentSelection.flags.includes(option.value)) {
            btn.classList.add("active");
        }

        btn.addEventListener("click", () => {
            handleButtonClick(type, option.value, trackKey, currentSelection);
            updateButtonStates(trackKey, currentSelection);
        });

        buttonGroup.appendChild(btn);
    });

    row.appendChild(buttonGroup);
    return row;
}

function handleButtonClick(type, value, trackKey, currentSelection) {
    if (type === "age") {
        currentSelection.age = currentSelection.age === value ? null : value;
    } else if (type === "role") {
        currentSelection.role = currentSelection.role === value ? null : value;
    } else if (type === "flags") {
        const index = currentSelection.flags.indexOf(value);
        if (index > -1) {
            currentSelection.flags.splice(index, 1);
        } else {
            currentSelection.flags.push(value);
        }
    }
}

function updateButtonStates(trackKey, currentSelection) {
    const panel = document.getElementById(`${trackKey}-panel`);
    if (!panel) return;

    // Update age buttons
    panel.querySelectorAll(`.option-btn[data-type="age"]`).forEach(btn => {
        btn.classList.toggle("active", btn.dataset.value === currentSelection.age);
    });

    // Update role buttons
    panel.querySelectorAll(`.option-btn[data-type="role"]`).forEach(btn => {
        btn.classList.toggle("active", btn.dataset.value === currentSelection.role);
    });

    // Update flag buttons
    panel.querySelectorAll(`.option-btn[data-type="flags"]`).forEach(btn => {
        btn.classList.toggle("active", currentSelection.flags.includes(btn.dataset.value));
    });
}

function addPersonToTrack(trackKey, currentSelection) {
    if (!currentSelection.age || !currentSelection.role) {
        alert("Yaş və rol seçmək məcburidir.");
        return;
    }

    const person = {
        age: currentSelection.age,
        role: currentSelection.role,
        flags: [...currentSelection.flags]
    };

    scenario[trackKey].push(person);

    // Reset selection
    currentSelection.age = null;
    currentSelection.role = null;
    currentSelection.flags = [];
    updateButtonStates(trackKey, currentSelection);

    renderTrack(trackKey);
    renderScene();
}

function summarizeTrack(persons) {
    const map = new Map();

    persons.forEach(p => {
        const flagsKey = (p.flags && p.flags.length > 0) ? p.flags.slice().sort().join("|") : "";
        const key = `${p.age}__${p.role}__${flagsKey}`;
        const current = map.get(key) || { person: p, count: 0 };
        current.count += 1;
        map.set(key, current);
    });

    return Array.from(map.values());
}

function getPersonIcon(person) {
    const { age, role, flags } = person;

    // Check flags first (except pregnant, which is now only a role)
    if (flags && flags.includes("disabled")) return "🦽";

    // Check role (pregnancy is now only a role, not a flag)
    if (role === "pregnant") return "🤰";
    if (role === "doctor" || role === "nurse") return "🧑‍⚕️";
    if (role === "teacher") return "👩‍🏫";
    if (role === "engineer") return "👷";
    if (role === "criminal" || role === "thief") return "🚨";
    if (role === "student") return "🎓";
    if (role === "retired") return "👴";
    if (role === "unemployed") return "🧍";

    // Check age
    if (age === "child") return "👶";
    if (age === "teen" || age === "young") return "🧑";
    if (age === "elder") return "🧓";

    return "👤";
}

function renderTrack(trackKey) {
    const listEl = document.getElementById(`${trackKey}-list`);
    const persons = scenario[trackKey];

    listEl.innerHTML = "";

    const groups = summarizeTrack(persons);

    if (groups.length === 0) {
        const p = document.createElement("p");
        p.className = "placeholder-text";
        p.textContent = "Hələ heç kim əlavə edilməyib.";
        listEl.appendChild(p);
        return;
    }

    groups.forEach(group => {
        const p = group.person;
        const count = group.count;

        const li = document.createElement("li");
        li.className = "person-chip";

        const icon = getPersonIcon(p);

        // Find labels for display
        const ageLabel = AGE_OPTIONS.find(o => o.value === p.age)?.label || p.age;
        const roleLabel = ROLE_OPTIONS.find(o => o.value === p.role)?.label || p.role;
        const flagLabels = p.flags && p.flags.length > 0
            ? p.flags.map(f => FLAG_OPTIONS.find(o => o.value === f)?.label || f).join(" · ")
            : "";

        const iconSpan = document.createElement("span");
        iconSpan.className = "person-chip-icon";
        iconSpan.textContent = icon;

        const infoSpan = document.createElement("span");
        if (flagLabels) {
            infoSpan.innerHTML = `${ageLabel} ${roleLabel} · ${flagLabels}`;
        } else {
            infoSpan.innerHTML = `${ageLabel} ${roleLabel}`;
        }

        const countSpan = document.createElement("span");
        countSpan.style.opacity = "0.7";
        countSpan.textContent = ` × ${count}`;

        const removeBtn = document.createElement("button");
        removeBtn.title = "Bu qrupu sil";
        removeBtn.textContent = "✕";
        removeBtn.className = "remove-chip-btn";

        removeBtn.addEventListener("click", () => {
            const flagsKey = (p.flags && p.flags.length > 0) ? p.flags.slice().sort().join("|") : "";
            const key = `${p.age}__${p.role}__${flagsKey}`;
            const filtered = persons.filter(pp => {
                const fk = (pp.flags && pp.flags.length > 0) ? pp.flags.slice().sort().join("|") : "";
                const kk = `${pp.age}__${pp.role}__${fk}`;
                return kk !== key;
            });
            scenario[trackKey] = filtered;
            renderTrack(trackKey);
            renderScene();
        });

        li.appendChild(iconSpan);
        li.appendChild(infoSpan);
        li.appendChild(countSpan);
        li.appendChild(removeBtn);

        listEl.appendChild(li);
    });

    renderScene();
}

function setupControls() {
    const deonSelect = document.getElementById("deon-variant");
    const manualButtons = document.querySelectorAll("[data-manual]");
    const manualLabel = document.getElementById("manual-choice-label");
    const runCompareBtn = document.getElementById("run-compare-btn");
    const runSingleBtn = document.getElementById("run-single-btn");

    // Mode radio-ları
    const modeRadios = document.querySelectorAll('input[name="mode-radio"]');
    modeRadios.forEach(r => {
        r.addEventListener("change", () => {
            selectedMode = r.value;
        });
    });

    // Custom dropdown functionality for deontological variant
    setupCustomDropdown();

    deonSelect.addEventListener("change", () => {
        scenario.deon_variant = deonSelect.value;
    });

    manualButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const choice = parseInt(btn.getAttribute("data-manual"), 10);
            scenario.manual_choice = choice;

            manualButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            manualLabel.textContent =
                choice === 1
                    ? "Sənin qərarın: Rels 1 qurban verilsin."
                    : "Sənin qərarın: Rels 2 qurban verilsin.";
        });
    });

    runSingleBtn.addEventListener("click", () => {
        if (scenario.track1.length === 0 || scenario.track2.length === 0) {
            alert("Hər iki track üçün ən azı 1 nəfər əlavə et.");
            return;
        }
        runSingleDecision();
    });

    runCompareBtn.addEventListener("click", () => {
        if (scenario.track1.length === 0 || scenario.track2.length === 0) {
            alert("Hər iki track üçün ən azı 1 nəfər əlavə et.");
            return;
        }
        runCompare();
    });
}

async function runSingleDecision() {
    const payload = {
        track1: scenario.track1,
        track2: scenario.track2,
        mode: selectedMode
    };

    if (selectedMode === "deontological") {
        payload.deon_variant = scenario.deon_variant;
    }
    if (selectedMode === "custom" && scenario.custom_rules) {
        payload.custom_rules = scenario.custom_rules;
    }

    try {
        const res = await fetch(`${API_BASE}/decide_v2`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        if (!res.ok) {
            throw new Error(`Server error: ${res.status}`);
        }

        const data = await res.json();
        renderSingleResult(data, selectedMode);

        // Animate trolley to chosen track
        animateTrolley(data.chosen_track);

        addHistoryEntry({
            type: "single",
            mode: selectedMode,
            scenario: cloneScenario(),
            result: data,
            manual_choice: scenario.manual_choice,
            timestamp: new Date().toISOString()
        });
        renderHistory();
    } catch (err) {
        console.error(err);
        alert("Mod işə düşərkən xəta baş verdi. Konsolu yoxla.");
    }
}

async function runCompare() {
    const compareModeCheckboxes = document.querySelectorAll(".compare-mode");
    const enabledModes = Array.from(compareModeCheckboxes)
        .filter(cb => cb.checked)
        .map(cb => cb.value);

    if (enabledModes.length === 0) {
        alert("Ən azı bir modu compare üçün seç.");
        return;
    }

    // Prepare custom rules - use defaults if custom is enabled but no custom rules set
    let customRulesToSend = scenario.custom_rules;
    if (enabledModes.includes("custom") && !customRulesToSend) {
        customRulesToSend = {
            age_weights: DEFAULT_AGE_WEIGHTS,
            role_weights: DEFAULT_ROLE_WEIGHTS,
            flag_weights: DEFAULT_FLAG_WEIGHTS
        };
    }

    const payload = {
        track1: scenario.track1,
        track2: scenario.track2,
        mode: "utilitarian",
        deon_variant: scenario.deon_variant,
        custom_rules: customRulesToSend,
        include_ml: enabledModes.includes("ml")
    };

    if (scenario.manual_choice === 1 || scenario.manual_choice === 2) {
        payload.manual_choice = scenario.manual_choice;
    }

    try {
        const res = await fetch(`${API_BASE}/compare`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        if (!res.ok) {
            throw new Error(`Server error: ${res.status}`);
        }

        const data = await res.json();
        renderCompareResults(data, enabledModes);

        addHistoryEntry({
            type: "compare",
            modes: enabledModes,
            scenario: cloneScenario(),
            results: data.results,
            manual_choice: scenario.manual_choice,
            stats: data.stats,
            timestamp: new Date().toISOString()
        });
        renderHistory();
    } catch (err) {
        console.error(err);
        alert("Müqayisə sorğusu zamanı xəta baş verdi. Konsolu yoxla.");
    }
}

function setupCustomDropdown() {
    const customSelect = document.getElementById('deon-variant-select');
    const trigger = customSelect.querySelector('.custom-select-trigger');
    const options = customSelect.querySelectorAll('.custom-option');
    const hiddenInput = document.getElementById('deon-variant');
    const selectText = customSelect.querySelector('.custom-select-text');

    // Toggle dropdown
    trigger.addEventListener('click', function() {
        customSelect.classList.toggle('open');
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!customSelect.contains(e.target)) {
            customSelect.classList.remove('open');
        }
    });

    // Handle option selection
    options.forEach(option => {
        option.addEventListener('click', function() {
            const value = this.getAttribute('data-value');
            const text = this.textContent;

            // Update hidden input
            hiddenInput.value = value;

            // Update display text
            selectText.textContent = text;

            // Update selected state
            options.forEach(opt => opt.classList.remove('selected'));
            this.classList.add('selected');

            // Close dropdown
            customSelect.classList.remove('open');

            // Trigger change event for compatibility
            const event = new Event('change', { bubbles: true });
            hiddenInput.dispatchEvent(event);
        });
    });

    // Initialize with first option selected
    if (options.length > 0) {
        options[0].classList.add('selected');
    }
}

function renderSingleResult(res, modeName) {
    const container = document.getElementById("single-result-container");
    if (!container) return;
    
    container.innerHTML = "";

    // Chosen track
    const trackDiv = document.createElement("div");
    trackDiv.style.marginBottom = "1rem";
    trackDiv.style.fontSize = "1.2rem";
    trackDiv.style.fontWeight = "600";
    trackDiv.innerHTML = `Chosen Track: <span style="color: #4fe1c1;">Track ${res.chosen_track}</span>`;
    container.appendChild(trackDiv);

    // Reason
    const reasonDiv = document.createElement("div");
    reasonDiv.style.marginBottom = "1rem";
    reasonDiv.style.padding = "0.75rem";
    reasonDiv.style.background = "rgba(255,255,255,0.03)";
    reasonDiv.style.borderRadius = "8px";
    reasonDiv.style.border = "1px solid rgba(255,255,255,0.1)";
    reasonDiv.textContent = res.reason || "No reason provided";
    container.appendChild(reasonDiv);

    // Counts and loss (if available)
    if (res.track1_count !== undefined || res.track2_count !== undefined) {
        const countsDiv = document.createElement("div");
        countsDiv.style.marginBottom = "0.5rem";
        countsDiv.style.fontSize = "0.9rem";
        countsDiv.style.opacity = "0.8";
        countsDiv.innerHTML = `Rels 1: ${res.track1_count ?? "-"} nəfər | Rels 2: ${res.track2_count ?? "-"} nəfər`;
        container.appendChild(countsDiv);
    }

    if (res.track1_loss !== undefined || res.track2_loss !== undefined) {
        const lossDiv = document.createElement("div");
        lossDiv.style.fontSize = "0.9rem";
        lossDiv.style.opacity = "0.8";
        lossDiv.innerHTML = `Rels 1 itkisi: ${res.track1_loss ?? "-"} | Rels 2 itkisi: ${res.track2_loss ?? "-"}`;
        container.appendChild(lossDiv);
    }
}

function renderCompareResults(data, enabledModes) {
    const compareContainer = document.getElementById("compare-results-container");
    const statsContainer = document.getElementById("stats-summary");
    
    if (!compareContainer || !statsContainer) return;

    // Clear compare results
    compareContainer.innerHTML = "";

    const results = data.results || {};
    const manual = data.manual || {};

    if (Object.keys(results).length === 0) {
        compareContainer.innerHTML = '<p class="placeholder-text">Nəticə mövcud deyil.</p>';
    } else {
        // Show manual choice first if it exists
        if (manual.manual_choice) {
            const manualCard = document.createElement("div");
            manualCard.className = "compare-result-card";
            manualCard.style.marginBottom = "0.75rem";
            manualCard.style.padding = "0.75rem";
            manualCard.style.background = "rgba(255,255,255,0.05)";
            manualCard.style.borderRadius = "8px";
            manualCard.style.border = "2px solid rgba(255, 193, 7, 0.3)";

            const header = document.createElement("div");
            header.style.display = "flex";
            header.style.justifyContent = "space-between";
            header.style.alignItems = "center";
            header.style.marginBottom = "0.5rem";

            const modeTitle = document.createElement("div");
            modeTitle.style.fontWeight = "600";
            modeTitle.style.textTransform = "capitalize";
            modeTitle.style.color = "#ffc107";
            modeTitle.textContent = "Manual Choice";

            const trackBadge = document.createElement("div");
            trackBadge.style.padding = "0.25rem 0.5rem";
            trackBadge.style.borderRadius = "4px";
            trackBadge.style.background = manual.manual_choice === 1 ? "rgba(255, 107, 107, 0.2)" : "rgba(77, 171, 247, 0.2)";
            trackBadge.style.border = `1px solid ${manual.manual_choice === 1 ? "#ff6b6b" : "#4dabf7"}`;
            trackBadge.style.fontSize = "0.85rem";
            trackBadge.textContent = `Rels ${manual.manual_choice}`;

            header.appendChild(modeTitle);
            header.appendChild(trackBadge);

            const reasonDiv = document.createElement("div");
            reasonDiv.style.fontSize = "0.85rem";
            reasonDiv.style.opacity = "0.85";
            reasonDiv.style.lineHeight = "1.4";
            reasonDiv.textContent = "Sizin şəxsi qərarınız";

            manualCard.appendChild(header);
            manualCard.appendChild(reasonDiv);
            compareContainer.appendChild(manualCard);
        }

        // Show AI mode results
        Object.entries(results).forEach(([modeName, res]) => {
            if (!enabledModes.includes(modeName)) return;

            const card = document.createElement("div");
            card.className = "compare-result-card";
            card.style.marginBottom = "0.75rem";
            card.style.padding = "0.75rem";
            card.style.background = "rgba(255,255,255,0.03)";
            card.style.borderRadius = "8px";
            card.style.border = "1px solid rgba(255,255,255,0.1)";

            // Mode name and chosen track
            const header = document.createElement("div");
            header.style.display = "flex";
            header.style.justifyContent = "space-between";
            header.style.alignItems = "center";
            header.style.marginBottom = "0.5rem";

            const modeTitle = document.createElement("div");
            modeTitle.style.fontWeight = "600";
            modeTitle.style.textTransform = "capitalize";
            modeTitle.textContent = modeName;

            const trackBadge = document.createElement("div");
            trackBadge.style.padding = "0.25rem 0.5rem";
            trackBadge.style.borderRadius = "4px";
            trackBadge.style.background = res.chosen_track === 1 ? "rgba(255, 107, 107, 0.2)" : "rgba(77, 171, 247, 0.2)";
            trackBadge.style.border = `1px solid ${res.chosen_track === 1 ? "#ff6b6b" : "#4dabf7"}`;
            trackBadge.style.fontSize = "0.85rem";
            trackBadge.textContent = `Rels ${res.chosen_track}`;

            header.appendChild(modeTitle);
            header.appendChild(trackBadge);

            // Reason summary (first sentence or truncated)
            const reasonDiv = document.createElement("div");
            reasonDiv.style.fontSize = "0.85rem";
            reasonDiv.style.opacity = "0.85";
            reasonDiv.style.lineHeight = "1.4";
            const reasonText = res.reason || "Səbəb göstərilməyib";
            // Take first sentence or first 100 characters
            const shortReason = reasonText.split('.')[0] || reasonText.substring(0, 100);
            reasonDiv.textContent = shortReason.length < reasonText.length ? shortReason + "..." : shortReason;

            card.appendChild(header);
            card.appendChild(reasonDiv);

            compareContainer.appendChild(card);
        });
    }

    // Update STATS panel
    const stats = data.stats || {};

    if (!manual.manual_choice) {
        statsContainer.innerHTML = '<p class="placeholder-text">Yuxarıdan şəxsi qərarını seç (Rels 1 və ya Rels 2), sonra müqayisə etməklə statistikaları gör.</p>';
        return;
    }

    if (!stats || stats.total_manual_decisions === 0 || stats.agreement_rate === null) {
        statsContainer.innerHTML = '<p class="placeholder-text">Not enough data yet. Make manual choices and run Compare a few times to see statistics.</p>';
    } else {
        const ratePercent = (stats.agreement_rate * 100).toFixed(1);
        
        statsContainer.innerHTML = `
            <div style="margin-bottom: 0.75rem;">
                <div style="font-size: 0.9rem; opacity: 0.8; margin-bottom: 0.25rem;">Scenarios with manual choice:</div>
                <div style="font-size: 1.2rem; font-weight: 600; color: #4fe1c1;">${stats.total_manual_decisions}</div>
            </div>
            <div style="margin-bottom: 0.75rem;">
                <div style="font-size: 0.9rem; opacity: 0.8; margin-bottom: 0.25rem;">Agreements (at least one mode):</div>
                <div style="font-size: 1.2rem; font-weight: 600; color: #4fe1c1;">${stats.total_ai_agreements}</div>
            </div>
            <div style="padding-top: 0.75rem; border-top: 1px solid rgba(255,255,255,0.1);">
                <div style="font-size: 0.9rem; opacity: 0.8; margin-bottom: 0.25rem;">Agreement Rate:</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: #4fe1c1;">${ratePercent}%</div>
            </div>
        `;
    }
}

/* History */

function addHistoryEntry(entry) {
    historyEntries.unshift(entry);
    if (historyEntries.length > 20) {
        historyEntries.pop();
    }
}

function renderHistory() {
    const container = document.getElementById("history-list");
    container.innerHTML = "";

    if (historyEntries.length === 0) {
        const p = document.createElement("p");
        p.className = "placeholder-text";
        p.textContent =
            "Hələ heç bir ssenari oynanmamış kimi görünür. Simulyasiya tabında test etdikcə nəticələr burada görünəcək.";
        container.appendChild(p);
        return;
    }

    historyEntries.forEach((entry, index) => {
        const card = document.createElement("div");
        card.className = "history-card";

        const header = document.createElement("div");
        header.className = "history-card-header";

        const title = document.createElement("span");
        title.textContent =
            entry.type === "single"
                ? `#${historyEntries.length - index} – Tək mod`
                : `#${historyEntries.length - index} – Compare`;

        const chip = document.createElement("span");
        chip.className = "history-chip";
        chip.textContent =
            entry.type === "single"
                ? `${entry.mode} modu`
                : (entry.modes || []).join(" · ");

        header.appendChild(title);
        header.appendChild(chip);

        const meta = document.createElement("div");
        meta.className = "history-meta";
        const date = new Date(entry.timestamp);
        meta.textContent = `Tarix: ${date.toLocaleString()}`;

        const decisionsDiv = document.createElement("div");
        decisionsDiv.className = "history-decisions";

        if (entry.type === "single") {
            const aiSpan = document.createElement("span");
            aiSpan.textContent = `AI: Track ${entry.result.chosen_track}`;
            decisionsDiv.appendChild(aiSpan);

            if (entry.manual_choice) {
                const youSpan = document.createElement("span");
                const agree = entry.result.chosen_track === entry.manual_choice;
                youSpan.textContent =
                    `Sən: Track ${entry.manual_choice} (${agree ? "uyğundur" : "fərqlidir"})`;
                decisionsDiv.appendChild(youSpan);
            }
        } else if (entry.type === "compare") {
            const results = entry.results || {};
            Object.entries(results).forEach(([modeName, res]) => {
                const span = document.createElement("span");
                span.textContent = `${modeName}: Track ${res.chosen_track}`;
                decisionsDiv.appendChild(span);
            });

            if (entry.manual_choice) {
                const youSpan = document.createElement("span");
                youSpan.textContent = `Sən: Track ${entry.manual_choice}`;
                decisionsDiv.appendChild(youSpan);
            }
        }

        // Replay button
        const replayBtn = document.createElement("button");
        replayBtn.className = "btn btn-outline";
        replayBtn.textContent = "Təkrarla";
        replayBtn.style.marginTop = "0.5rem";
        replayBtn.style.fontSize = "0.75rem";
        replayBtn.addEventListener("click", () => {
            replayScenario(entry.scenario);
        });

        card.appendChild(header);
        card.appendChild(meta);
        card.appendChild(decisionsDiv);
        card.appendChild(replayBtn);

        container.appendChild(card);
    });
}

/* Utilities */

function cloneScenario() {
    return {
        track1: scenario.track1.map(p => ({ ...p, flags: [...(p.flags || [])] })),
        track2: scenario.track2.map(p => ({ ...p, flags: [...(p.flags || [])] })),
        deon_variant: scenario.deon_variant,
        manual_choice: scenario.manual_choice
    };
}

function capitalize(str) {
    if (!str) return "";
    return str.charAt(0).toUpperCase() + str.slice(1);
}

/* Replay Functionality */

function replayScenario(savedScenario) {
    if (!savedScenario) return;
    
    // Restore scenario
    scenario.track1 = savedScenario.track1.map(p => ({
        ...p,
        flags: [...(p.flags || [])]
    }));
    scenario.track2 = savedScenario.track2.map(p => ({
        ...p,
        flags: [...(p.flags || [])]
    }));
    scenario.deon_variant = savedScenario.deon_variant || "protect_children";
    scenario.manual_choice = savedScenario.manual_choice || null;
    
    // Re-render tracks and scene
    renderTrack("track1");
    renderTrack("track2");
    renderScene();
    
    // Reset trolley position
    resetTrolley();
    
    // Switch to simulation tab if not already there
    const simTab = document.querySelector('[data-tab="sim"]');
    if (simTab) {
        simTab.click();
    }
}

/* Trolley Animation */

function resetTrolley() {
    const trolleyGroup = document.getElementById("trolley-group");
    const track1 = document.getElementById("track1-path");
    const track2 = document.getElementById("track2-path");
    
    if (trolleyGroup) {
        trolleyGroup.setAttribute("transform", "translate(100, 225)");
        trolleyGroup.style.transition = "none";
    }
    
    if (track1) {
        track1.classList.remove("track-chosen", "track-safe");
        track1.setAttribute("stroke", "#ff6b6b");
        track1.setAttribute("stroke-width", "4");
    }
    
    if (track2) {
        track2.classList.remove("track-chosen", "track-safe");
        track2.setAttribute("stroke", "#4dabf7");
        track2.setAttribute("stroke-width", "4");
    }
}

function animateTrolley(chosenTrack) {
    const trolleyGroup = document.getElementById("trolley-group");
    const track1 = document.getElementById("track1-path");
    const track2 = document.getElementById("track2-path");
    
    if (!trolleyGroup || !track1 || !track2) return;
    
    // Reset position and highlighting first
    resetTrolley();
    
    // Wait a tiny bit for reset to apply
    setTimeout(() => {
        // Enable transitions
        trolleyGroup.style.transition = "transform 1.2s cubic-bezier(0.4, 0, 0.2, 1)";
        
        // Step 1: Move along main rail to split point (x: 100 -> 400, y stays at 225)
        trolleyGroup.setAttribute("transform", "translate(400, 225)");
        
        setTimeout(() => {
            // Step 2: Move along chosen track
            if (chosenTrack === 1) {
                // Track 1: upper branch (ends at x=750, y=100)
                trolleyGroup.setAttribute("transform", "translate(750, 100)");
                
                // Highlight tracks
                track1.classList.add("track-chosen");
                track2.classList.add("track-safe");
            } else if (chosenTrack === 2) {
                // Track 2: lower branch (ends at x=750, y=350)
                trolleyGroup.setAttribute("transform", "translate(750, 350)");
                
                // Highlight tracks
                track1.classList.add("track-safe");
                track2.classList.add("track-chosen");
            }
        }, 600); // Halfway through animation
    }, 50);
}

/* Trolley Scene Rendering */

function initializeScene() {
    const board = document.getElementById("trolley-board");
    if (!board) return;

    board.innerHTML = "";

    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 800 450");
    svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
    svg.style.width = "100%";
    svg.style.height = "100%";

    // Main rail (horizontal, from left to right)
    const mainRail = document.createElementNS("http://www.w3.org/2000/svg", "line");
    mainRail.setAttribute("x1", "50");
    mainRail.setAttribute("y1", "225");
    mainRail.setAttribute("x2", "400");
    mainRail.setAttribute("y2", "225");
    mainRail.setAttribute("stroke", "#4fe1c1");
    mainRail.setAttribute("stroke-width", "4");
    mainRail.setAttribute("stroke-linecap", "round");
    mainRail.setAttribute("id", "main-rail");
    svg.appendChild(mainRail);

    // Split point circle
    const splitPoint = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    splitPoint.setAttribute("cx", "400");
    splitPoint.setAttribute("cy", "225");
    splitPoint.setAttribute("r", "8");
    splitPoint.setAttribute("fill", "#4fe1c1");
    splitPoint.setAttribute("stroke", "#ffffff");
    splitPoint.setAttribute("stroke-width", "2");
    svg.appendChild(splitPoint);

    // Track 1 (upper branch)
    const track1Path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    track1Path.setAttribute("d", "M 400 225 Q 500 150 750 100");
    track1Path.setAttribute("stroke", "#ff6b6b");
    track1Path.setAttribute("stroke-width", "4");
    track1Path.setAttribute("fill", "none");
    track1Path.setAttribute("stroke-linecap", "round");
    track1Path.setAttribute("id", "track1-path");
    svg.appendChild(track1Path);

    // Track 2 (lower branch)
    const track2Path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    track2Path.setAttribute("d", "M 400 225 Q 500 300 750 350");
    track2Path.setAttribute("stroke", "#4dabf7");
    track2Path.setAttribute("stroke-width", "4");
    track2Path.setAttribute("fill", "none");
    track2Path.setAttribute("stroke-linecap", "round");
    track2Path.setAttribute("id", "track2-path");
    svg.appendChild(track2Path);

    // Trolley group (for animation)
    const trolleyGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
    trolleyGroup.setAttribute("id", "trolley-group");
    trolleyGroup.setAttribute("transform", "translate(0, 0)");

    // Trolley car (simple rectangle)
    const trolley = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    trolley.setAttribute("x", "-30");
    trolley.setAttribute("y", "-15");
    trolley.setAttribute("width", "60");
    trolley.setAttribute("height", "30");
    trolley.setAttribute("rx", "4");
    trolley.setAttribute("fill", "#ff6b6b");
    trolley.setAttribute("stroke", "#ffffff");
    trolley.setAttribute("stroke-width", "2");
    trolley.setAttribute("id", "trolley-car");

    // Trolley windows
    const window1 = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    window1.setAttribute("x", "-22");
    window1.setAttribute("y", "-7");
    window1.setAttribute("width", "12");
    window1.setAttribute("height", "14");
    window1.setAttribute("rx", "2");
    window1.setAttribute("fill", "#1e3a8a");

    const window2 = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    window2.setAttribute("x", "10");
    window2.setAttribute("y", "-7");
    window2.setAttribute("width", "12");
    window2.setAttribute("height", "14");
    window2.setAttribute("rx", "2");
    window2.setAttribute("fill", "#1e3a8a");

    trolleyGroup.appendChild(trolley);
    trolleyGroup.appendChild(window1);
    trolleyGroup.appendChild(window2);
    svg.appendChild(trolleyGroup);

    // Set initial trolley position (on main rail, before split)
    trolleyGroup.setAttribute("transform", "translate(100, 225)");

    // Groups for people on tracks
    const track1People = document.createElementNS("http://www.w3.org/2000/svg", "g");
    track1People.setAttribute("id", "track1-people");
    svg.appendChild(track1People);

    const track2People = document.createElementNS("http://www.w3.org/2000/svg", "g");
    track2People.setAttribute("id", "track2-people");
    svg.appendChild(track2People);

    board.appendChild(svg);

    // Initial render
    renderScene();
}

function renderScene() {
    const track1PeopleGroup = document.getElementById("track1-people");
    const track2PeopleGroup = document.getElementById("track2-people");

    if (!track1PeopleGroup || !track2PeopleGroup) return;

    // Clear existing people
    track1PeopleGroup.innerHTML = "";
    track2PeopleGroup.innerHTML = "";

    // Render Track 1 people (at end of upper branch: x=750, y=100)
    const track1Groups = summarizeTrack(scenario.track1);
    const track1BaseX = 750;
    const track1BaseY = 100;
    const track1Spacing = 35;
    
    track1Groups.forEach((group, index) => {
        const person = group.person;
        const count = group.count;
        const icon = getPersonIcon(person);

        // Create a group for this person type
        const personGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
        const xPos = track1BaseX;
        const yPos = track1BaseY + (index * track1Spacing);
        personGroup.setAttribute("transform", `translate(${xPos}, ${yPos})`);

        // Background circle
        const bg = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        bg.setAttribute("cx", "0");
        bg.setAttribute("cy", "0");
        bg.setAttribute("r", "20");
        bg.setAttribute("fill", "rgba(255, 107, 107, 0.15)");
        bg.setAttribute("stroke", "#ff6b6b");
        bg.setAttribute("stroke-width", "2");
        personGroup.appendChild(bg);

        // Emoji icon
        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.setAttribute("x", "0");
        text.setAttribute("y", "5");
        text.setAttribute("text-anchor", "middle");
        text.setAttribute("font-size", "24");
        text.setAttribute("dominant-baseline", "middle");
        text.textContent = icon;
        personGroup.appendChild(text);

        // Count label
        if (count > 1) {
            const countText = document.createElementNS("http://www.w3.org/2000/svg", "text");
            countText.setAttribute("x", "0");
            countText.setAttribute("y", "28");
            countText.setAttribute("text-anchor", "middle");
            countText.setAttribute("font-size", "10");
            countText.setAttribute("fill", "#ff6b6b");
            countText.setAttribute("font-weight", "bold");
            countText.textContent = `×${count}`;
            personGroup.appendChild(countText);
        }

        // Tooltip
        const flagsLabel = person.flags && person.flags.length > 0 ? person.flags.join(", ") : "no flags";
        const tooltipText = `${capitalize(person.age)}, ${person.role}${count > 1 ? ` (×${count})` : ""}\nFlags: ${flagsLabel}`;
        personGroup.setAttribute("title", tooltipText);
        personGroup.style.cursor = "help";

        track1PeopleGroup.appendChild(personGroup);
    });

    // Render Track 2 people (at end of lower branch: x=750, y=350)
    const track2Groups = summarizeTrack(scenario.track2);
    const track2BaseX = 750;
    const track2BaseY = 350;
    const track2Spacing = 35;
    
    track2Groups.forEach((group, index) => {
        const person = group.person;
        const count = group.count;
        const icon = getPersonIcon(person);

        // Create a group for this person type
        const personGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
        const xPos = track2BaseX;
        const yPos = track2BaseY + (index * track2Spacing);
        personGroup.setAttribute("transform", `translate(${xPos}, ${yPos})`);

        // Background circle
        const bg = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        bg.setAttribute("cx", "0");
        bg.setAttribute("cy", "0");
        bg.setAttribute("r", "20");
        bg.setAttribute("fill", "rgba(77, 171, 247, 0.15)");
        bg.setAttribute("stroke", "#4dabf7");
        bg.setAttribute("stroke-width", "2");
        personGroup.appendChild(bg);

        // Emoji icon
        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.setAttribute("x", "0");
        text.setAttribute("y", "5");
        text.setAttribute("text-anchor", "middle");
        text.setAttribute("font-size", "24");
        text.setAttribute("dominant-baseline", "middle");
        text.textContent = icon;
        personGroup.appendChild(text);

        // Count label
        if (count > 1) {
            const countText = document.createElementNS("http://www.w3.org/2000/svg", "text");
            countText.setAttribute("x", "0");
            countText.setAttribute("y", "28");
            countText.setAttribute("text-anchor", "middle");
            countText.setAttribute("font-size", "10");
            countText.setAttribute("fill", "#4dabf7");
            countText.setAttribute("font-weight", "bold");
            countText.textContent = `×${count}`;
            personGroup.appendChild(countText);
        }

        // Tooltip
        const flagsLabel = person.flags && person.flags.length > 0 ? person.flags.join(", ") : "no flags";
        const tooltipText = `${capitalize(person.age)}, ${person.role}${count > 1 ? ` (×${count})` : ""}\nFlags: ${flagsLabel}`;
        personGroup.setAttribute("title", tooltipText);
        personGroup.style.cursor = "help";

        track2PeopleGroup.appendChild(personGroup);
    });
}
