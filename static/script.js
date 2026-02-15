/* ═══════════════════════════════════════════════════════════
   CyberShield AI — Dashboard Scripts (Gen Z Edition)
   ═══════════════════════════════════════════════════════════ */

document.addEventListener("DOMContentLoaded", () => {
    // ── Counters ──
    animateCounters();

    // ── Glow ripple on every .glow-target ──
    document.querySelectorAll(".glow-target").forEach(el => {
        el.addEventListener("click", e => {
            const ripple = document.createElement("span");
            ripple.classList.add("ripple");
            const rect = el.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            ripple.style.width = ripple.style.height = size + "px";
            ripple.style.left = (e.clientX - rect.left - size / 2) + "px";
            ripple.style.top = (e.clientY - rect.top - size / 2) + "px";
            el.appendChild(ripple);
            ripple.addEventListener("animationend", () => ripple.remove());
        });
    });

    // ── Quick-test chips ──
    document.querySelectorAll(".chip").forEach(chip => {
        chip.addEventListener("click", () => {
            document.getElementById("input-text").value = chip.dataset.text;
        });
    });

    // ── Analyze button ──
    document.getElementById("analyze-btn").addEventListener("click", analyzeText);

    // Allow Ctrl+Enter from textarea
    document.getElementById("input-text").addEventListener("keydown", e => {
        if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) analyzeText();
    });

    // ── Scroll-reveal ──
    const revealEls = document.querySelectorAll(".section, .how-card, .stat-card, .kindness-card");
    revealEls.forEach(el => el.classList.add("reveal"));
    const io = new IntersectionObserver((entries) => {
        entries.forEach(en => { if (en.isIntersecting) en.target.classList.add("visible"); });
    }, { threshold: 0.12 });
    revealEls.forEach(el => io.observe(el));

    // ── Smooth nav highlight ──
    const sections = document.querySelectorAll("section[id]");
    const navLinks = document.querySelectorAll(".nav-link");
    window.addEventListener("scroll", () => {
        let current = "";
        sections.forEach(s => {
            if (window.scrollY >= s.offsetTop - 120) current = s.id;
        });
        navLinks.forEach(l => {
            l.classList.toggle("active", l.getAttribute("href") === "#" + current);
        });
    });

    // ── Chat simulation ──
    document.getElementById("chat-send").addEventListener("click", chatSend);
    document.getElementById("chat-input").addEventListener("keydown", e => {
        if (e.key === "Enter") chatSend();
    });

    // ── Challenge mode ──
    document.getElementById("challenge-submit").addEventListener("click", submitChallenge);
    document.getElementById("challenge-next").addEventListener("click", nextChallenge);

    // ── Report modal ──
    document.getElementById("report-btn")?.addEventListener("click", () => {
        document.getElementById("report-modal").classList.add("active");
        // Pre-fill with last analyzed text
        const lastText = document.getElementById("input-text").value;
        document.getElementById("report-message").value = lastText;
    });
    document.getElementById("report-cancel")?.addEventListener("click", () => {
        document.getElementById("report-modal").classList.remove("active");
    });
    document.getElementById("report-submit")?.addEventListener("click", submitReport);

    // Close modal on overlay click
    document.getElementById("report-modal")?.addEventListener("click", e => {
        if (e.target === document.getElementById("report-modal")) {
            document.getElementById("report-modal").classList.remove("active");
        }
    });

    // ── Duplicate reel slides for infinite scroll ──
    const reelTrack = document.querySelector(".reel-track");
    if (reelTrack) {
        reelTrack.innerHTML += reelTrack.innerHTML;
    }
});

/* ═══════════ STAT COUNTER ANIMATION ═══════════ */
function animateCounters() {
    document.querySelectorAll(".stat-value[data-target]").forEach(el => {
        const target = +el.dataset.target;
        const suffix = el.dataset.suffix || "";
        const duration = 1800;
        const start = performance.now();
        const step = ts => {
            const progress = Math.min((ts - start) / duration, 1);
            const ease = 1 - Math.pow(1 - progress, 3);
            el.textContent = Math.round(target * ease) + suffix;
            if (progress < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
    });
}

/* ═══════════ ANALYZE TEXT VIA API ═══════════ */
const activityHistory = [];
const kindnessHistory = { empathy: [], respect: [], risk: [] };

async function analyzeText() {
    const text = document.getElementById("input-text").value.trim();
    if (!text) return;

    const btn = document.getElementById("analyze-btn");
    const btnText = btn.querySelector(".btn-text");
    const btnLoader = btn.querySelector(".btn-loader");

    btnText.hidden = true;
    btnLoader.hidden = false;
    btn.disabled = true;

    try {
        const res = await fetch("/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text }),
        });
        const data = await res.json();
        if (data.error) { alert(data.error); return; }
        renderResults(data);
        pushActivity(text, data);
        updateKindness(data);
    } catch (err) {
        console.error(err);
        alert("Could not reach the server. Is bully_detector.py running?");
    } finally {
        btnText.hidden = false;
        btnLoader.hidden = true;
        btn.disabled = false;
    }
}

/* ═══════════ RENDER RESULTS ═══════════ */
function renderResults(d) {
    document.getElementById("results-placeholder").hidden = true;
    const content = document.getElementById("results-content");
    content.hidden = false;
    // Re-trigger animation
    content.style.animation = "none";
    content.offsetHeight;
    content.style.animation = "";

    const pct = Math.round(d.risk * 100);

    // ── Roast Meter ──
    const roastFill = document.getElementById("roast-bar-fill");
    const roastNeedle = document.getElementById("roast-needle");
    // The fill shows the "safe" portion (inverted)
    roastFill.style.width = (100 - pct) + "%";
    roastFill.style.left = pct + "%";
    roastNeedle.style.left = pct + "%";

    // Highlight active roast level
    document.querySelectorAll(".rl").forEach(rl => rl.classList.remove("active"));
    const levelMap = {
        "Safe": "safe", "Sarcastic": "sarcastic", "Risky": "risky",
        "Toxic": "toxic", "Ultra Toxic": "ultra"
    };
    const activeLabel = document.querySelector(`.rl[data-level="${levelMap[d.level]}"]`);
    if (activeLabel) activeLabel.classList.add("active");

    // ── Meme reaction ──
    document.getElementById("meme-mood").textContent = d.mood;
    document.getElementById("meme-text").textContent = d.meme;
    // Re-trigger meme-pop
    const memeBox = document.getElementById("meme-box");
    memeBox.style.animation = "none";
    memeBox.offsetHeight;
    memeBox.style.animation = "";

    // ── Gauge ──
    const circle = document.getElementById("gauge-circle");
    const circumference = 2 * Math.PI * 52;
    circle.style.strokeDashoffset = circumference - (circumference * d.risk);

    const levelColors = {
        "Safe": "#00F5D4", "Sarcastic": "#facc15", "Risky": "#f97316",
        "Toxic": "#ef4444", "Ultra Toxic": "#9333ea"
    };
    const color = levelColors[d.level];
    circle.style.stroke = color;
    document.getElementById("gauge-label").textContent = pct + "%";
    document.getElementById("gauge-label").style.color = color;

    const riskLevel = document.getElementById("risk-level");
    riskLevel.textContent = d.roast_icon + " " + d.level;
    riskLevel.style.color = color;

    const ring = document.querySelector(".gauge-ring");
    ring.classList.toggle("pulse", d.level === "Toxic" || d.level === "Ultra Toxic");

    // ── Score bars ──
    document.getElementById("sarcasm-bar").style.width = (d.sarcasm_score * 100) + "%";
    document.getElementById("sarcasm-pct").textContent = Math.round(d.sarcasm_score * 100) + "%";
    document.getElementById("toxicity-bar").style.width = (d.toxicity_score * 100) + "%";
    document.getElementById("toxicity-pct").textContent = Math.round(d.toxicity_score * 100) + "%";

    // ── Explanation ──
    document.getElementById("mood-icon").textContent = d.mood;
    document.getElementById("explanation-text").textContent = d.explanation;

    // ── Mood Flip ──
    const flipBox = document.getElementById("mood-flip-box");
    if (d.polite_rewrite) {
        flipBox.hidden = false;
        document.getElementById("polite-rewrite").textContent = d.polite_rewrite;
        flipBox.style.animation = "none";
        flipBox.offsetHeight;
        flipBox.style.animation = "";
    } else {
        flipBox.hidden = true;
    }

    // ── Mental Health ──
    const mhBox = document.getElementById("mental-health-box");
    if (d.mental_health) {
        mhBox.hidden = false;
        document.getElementById("mental-health-text").textContent = d.mental_health;
    } else {
        mhBox.hidden = true;
    }

    // ── Report button (show for risky+) ──
    const reportBtn = document.getElementById("report-btn");
    if (reportBtn) {
        reportBtn.hidden = d.risk < 0.4;
    }
}

/* ═══════════ KINDNESS SCORE ═══════════ */
function updateKindness(d) {
    kindnessHistory.empathy.push(d.empathy_score);
    kindnessHistory.respect.push(d.respect_score);
    kindnessHistory.risk.push(d.risk);

    // Average
    const avg = arr => arr.reduce((a, b) => a + b, 0) / arr.length;
    const empathy = avg(kindnessHistory.empathy);
    const respect = avg(kindnessHistory.respect);
    const risk = avg(kindnessHistory.risk);

    // Kindness rings (circumference = 2π·34 ≈ 214)
    const circ = 2 * Math.PI * 34;

    document.getElementById("empathy-ring").style.strokeDashoffset = circ - (circ * empathy);
    document.getElementById("empathy-label").textContent = Math.round(empathy * 100) + "%";

    document.getElementById("respect-ring").style.strokeDashoffset = circ - (circ * respect);
    document.getElementById("respect-label").textContent = Math.round(respect * 100) + "%";

    document.getElementById("toxicity-risk-ring").style.strokeDashoffset = circ - (circ * risk);
    document.getElementById("toxicity-risk-label").textContent = Math.round(risk * 100) + "%";

    // Update kindness stat in hero
    const kindnessOverall = Math.round(((empathy + respect + (1 - risk)) / 3) * 100);
    document.getElementById("kindness-overall").textContent = kindnessOverall + "%";
}

/* ═══════════ ACTIVITY HISTORY ═══════════ */
function pushActivity(text, d) {
    activityHistory.unshift({ text, ...d });
    if (activityHistory.length > 10) activityHistory.pop();
    renderActivity();
    // Increment scanned counter
    const scannedEl = document.querySelector("#stat-scanned .stat-value");
    scannedEl.textContent = parseInt(scannedEl.textContent) + 1;
    if (d.level === "Toxic" || d.level === "Ultra Toxic") {
        const threatEl = document.querySelector("#stat-threats .stat-value");
        threatEl.textContent = parseInt(threatEl.textContent) + 1;
    }
}

function renderActivity() {
    const tbody = document.getElementById("activity-body");
    tbody.innerHTML = "";
    activityHistory.forEach((item, i) => {
        const tr = document.createElement("tr");
        tr.className = "row-enter";
        const badgeMap = {
            "Safe": "badge-safe", "Sarcastic": "badge-sarcastic",
            "Risky": "badge-risky", "Toxic": "badge-toxic", "Ultra Toxic": "badge-ultra"
        };
        const badgeClass = badgeMap[item.level] || "badge-safe";
        const truncated = item.text.length > 40 ? item.text.slice(0, 40) + "…" : item.text;
        tr.innerHTML = `
            <td>${i + 1}</td>
            <td>${escapeHtml(truncated)}</td>
            <td><span class="badge ${badgeClass}">${item.roast_icon} ${item.level}</span></td>
            <td>${Math.round(item.sarcasm_score * 100)}%</td>
            <td>${Math.round(item.toxicity_score * 100)}%</td>
            <td>${item.mood}</td>
        `;
        tbody.appendChild(tr);
    });
}

/* ═══════════ CHAT SIMULATION ═══════════ */
async function chatSend() {
    const input = document.getElementById("chat-input");
    const text = input.value.trim();
    if (!text) return;
    input.value = "";

    const chatBox = document.getElementById("chat-messages");

    // User message
    addChatMsg("user", "🧑", text);

    // Typing indicator
    const typing = addChatMsg("bot", "🤖", "Analyzing vibes…");
    typing.querySelector(".chat-bubble").style.opacity = "0.5";

    try {
        const res = await fetch("/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text }),
        });
        const data = await res.json();

        // Remove typing
        typing.remove();

        // Bot response
        let response = `${data.roast_icon} **${data.level}** (${Math.round(data.risk * 100)}%)\n\n`;
        response += data.meme;

        if (data.polite_rewrite) {
            response += `\n\n🎭 *${data.polite_rewrite}*`;
        }
        if (data.mental_health) {
            response += `\n\n💙 ${data.mental_health}`;
        }

        addChatMsg("bot", "🤖", response);
        pushActivity(text, data);
        updateKindness(data);
    } catch (err) {
        typing.remove();
        addChatMsg("bot", "🤖", "Oops, couldn't reach the AI. Is the server running? 🔌");
    }

    chatBox.scrollTop = chatBox.scrollHeight;
}

function addChatMsg(type, avatar, text) {
    const chatBox = document.getElementById("chat-messages");
    const div = document.createElement("div");
    div.className = `chat-msg ${type}`;
    div.innerHTML = `
        <span class="chat-avatar">${avatar}</span>
        <div class="chat-bubble">${escapeHtml(text).replace(/\n/g, '<br>')}</div>
    `;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
    return div;
}

/* ═══════════ CHALLENGE MODE ═══════════ */
const CHALLENGES = [
    "You are so useless, just give up already.",
    "Nobody likes you, go away.",
    "You're the worst player ever lmao.",
    "Shut up, nobody asked for your opinion.",
    "That's the dumbest thing I've ever heard.",
    "You look terrible today ngl.",
    "You're such a loser 😂",
    "Why are you even here? Just leave.",
];
let currentChallenge = 0;

function nextChallenge() {
    currentChallenge = (currentChallenge + 1) % CHALLENGES.length;
    document.getElementById("challenge-toxic-text").textContent = `"${CHALLENGES[currentChallenge]}"`;
    document.getElementById("challenge-input").value = "";
    document.getElementById("challenge-result").hidden = true;
}

async function submitChallenge() {
    const text = document.getElementById("challenge-input").value.trim();
    if (!text) return;

    try {
        const res = await fetch("/challenge", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text }),
        });
        const data = await res.json();

        const resultBox = document.getElementById("challenge-result");
        resultBox.hidden = false;
        resultBox.className = `challenge-result ${data.passed ? "passed" : "failed"}`;
        document.getElementById("challenge-feedback").textContent = data.feedback;

        // Re-trigger animation
        resultBox.style.animation = "none";
        resultBox.offsetHeight;
        resultBox.style.animation = "";
    } catch (err) {
        alert("Could not reach server.");
    }
}

/* ═══════════ ANONYMOUS REPORT ═══════════ */
async function submitReport() {
    const message = document.getElementById("report-message").value.trim();
    const context = document.getElementById("report-context").value.trim();

    if (!message) return;

    try {
        const res = await fetch("/report", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message, context }),
        });
        const data = await res.json();

        const success = document.getElementById("report-success");
        success.hidden = false;
        success.textContent = data.response || "Report submitted! 🛡️";

        // Auto-close after 2s
        setTimeout(() => {
            document.getElementById("report-modal").classList.remove("active");
            success.hidden = true;
        }, 2500);
    } catch (err) {
        alert("Could not submit report.");
    }
}

/* ═══════════ HELPERS ═══════════ */
function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}


/* ═══════════════════════════════════════════════════════════
   PLATFORM MONITOR — Social Media Feed Scanner
   ═══════════════════════════════════════════════════════════ */

let currentPlatformFilter = "all";
let platformFeedData = [];

// Platform tab switching
document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".platform-tab").forEach(tab => {
        tab.addEventListener("click", () => {
            document.querySelectorAll(".platform-tab").forEach(t => t.classList.remove("active"));
            tab.classList.add("active");
            currentPlatformFilter = tab.dataset.platform;
            renderFeed();
        });
    });

    // Scan button
    document.getElementById("scan-btn")?.addEventListener("click", scanPlatforms);
});

async function scanPlatforms() {
    const btn = document.getElementById("scan-btn");
    const btnText = btn.querySelector(".btn-text");
    const btnLoader = btn.querySelector(".btn-loader");

    btnText.hidden = true;
    btnLoader.hidden = false;
    btn.disabled = true;

    try {
        const res = await fetch("/api/platform/scan", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ platform: currentPlatformFilter }),
        });
        const data = await res.json();
        platformFeedData = data.feed;

        // Update scan stats
        document.getElementById("scan-stats").hidden = false;
        animateValue("scan-total", data.total);
        animateValue("scan-threats", data.threats_found);
        animateValue("scan-actions", data.auto_actions);

        renderFeed();

        // After scan, refresh Cyber Hub
        setTimeout(loadCyberHubReports, 500);
    } catch (err) {
        console.error(err);
        alert("Could not reach the server. Is bully_detector.py running?");
    } finally {
        btnText.hidden = false;
        btnLoader.hidden = true;
        btn.disabled = false;
    }
}

function animateValue(elementId, target) {
    const el = document.getElementById(elementId);
    const duration = 800;
    const start = performance.now();
    const step = ts => {
        const progress = Math.min((ts - start) / duration, 1);
        const ease = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.round(target * ease);
        if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
}

function renderFeed() {
    const placeholder = document.getElementById("feed-placeholder");
    const feedList = document.getElementById("feed-list");

    let filtered = platformFeedData;
    if (currentPlatformFilter !== "all") {
        filtered = platformFeedData.filter(item => item.platform === currentPlatformFilter);
    }

    if (filtered.length === 0) {
        placeholder.hidden = false;
        feedList.hidden = true;
        return;
    }

    placeholder.hidden = true;
    feedList.hidden = false;
    feedList.innerHTML = "";

    filtered.forEach((item, index) => {
        const card = document.createElement("div");
        card.className = `feed-card glass glow-target ${item.analysis.primary_category}`;
        card.style.animationDelay = `${index * 0.06}s`;

        const platformIcons = { whatsapp: "💬", instagram: "📸", twitter: "🐦" };
        const platformColors = { whatsapp: "#25D366", instagram: "#E1306C", twitter: "#1DA1F2" };
        const categoryBadgeMap = {
            safe: { class: "badge-safe", label: "✅ Safe" },
            toxicity: { class: "badge-toxic", label: "☠️ Toxic" },
            fraud: { class: "badge-fraud", label: "🎣 Fraud" },
            fake_media: { class: "badge-fake", label: "🎭 Fake Media" },
            harassment: { class: "badge-ultra", label: "⚠️ Harassment" },
        };
        const actionStyleMap = {
            monitor: { class: "action-monitor", icon: "👁️" },
            flag: { class: "action-flag", icon: "🚩" },
            block: { class: "action-block", icon: "🛑" },
            report_to_cyberhub: { class: "action-report", icon: "🚨" },
        };

        const badge = categoryBadgeMap[item.analysis.primary_category] || categoryBadgeMap.safe;
        const actionStyle = actionStyleMap[item.action.action] || actionStyleMap.monitor;

        // Threat badges — show all if multiple
        let threatBadges = `<span class="badge ${badge.class}">${badge.label}</span>`;
        if (item.analysis.fraud && item.analysis.fraud.is_fraud) {
            threatBadges += ` <span class="badge badge-fraud">🎣 Fraud</span>`;
        }
        if (item.analysis.fake_media && item.analysis.fake_media.is_fake) {
            threatBadges += ` <span class="badge badge-fake">🎭 Fake</span>`;
        }

        card.innerHTML = `
            <div class="feed-card-header">
                <div class="feed-platform-badge" style="color: ${platformColors[item.platform]}">
                    <span class="feed-platform-icon">${platformIcons[item.platform]}</span>
                    <span class="feed-platform-name">${item.platform}</span>
                </div>
                <span class="feed-type-badge">${item.type}</span>
            </div>
            <div class="feed-card-body">
                <div class="feed-user">${escapeHtml(item.user)}</div>
                <div class="feed-content">${escapeHtml(item.content)}</div>
            </div>
            <div class="feed-card-footer">
                <div class="feed-threats">${threatBadges}</div>
                <div class="feed-action ${actionStyle.class}">
                    <span>${actionStyle.icon}</span>
                    <span class="feed-action-label">${item.action.action.replace(/_/g, ' ')}</span>
                </div>
            </div>
            <div class="feed-action-explanation">${escapeHtml(item.action.explanation)}</div>
            ${item.action.report_id ? `<div class="feed-report-id">📋 Report: ${item.action.report_id}</div>` : ""}
        `;
        feedList.appendChild(card);
    });
}


/* ═══════════════════════════════════════════════════════════
   CYBER HUB — Reports Dashboard
   ═══════════════════════════════════════════════════════════ */

async function loadCyberHubReports() {
    try {
        const res = await fetch("/api/cyberhub/reports");
        const data = await res.json();

        // Update stats
        animateValue("ch-total", data.total);
        animateValue("ch-critical", data.critical);
        animateValue("ch-high", data.high);
        animateValue("ch-medium", data.medium);

        // Render reports
        const placeholder = document.getElementById("cyberhub-placeholder");
        const reportsList = document.getElementById("reports-list");

        if (data.reports.length === 0) {
            placeholder.hidden = false;
            reportsList.hidden = true;
            return;
        }

        placeholder.hidden = true;
        reportsList.hidden = false;
        reportsList.innerHTML = "";

        data.reports.forEach((report, index) => {
            const card = document.createElement("div");
            card.className = `report-card glass glow-target priority-${report.priority}`;
            card.style.animationDelay = `${index * 0.08}s`;

            const priorityColors = { critical: "#ef4444", high: "#f97316", medium: "#facc15" };
            const platformIcons = { whatsapp: "💬", instagram: "📸", twitter: "🐦", unknown: "🌐" };

            const threatTags = report.threats.map(t =>
                `<span class="report-threat-tag">${t.type} (${Math.round(t.severity * 100)}%)</span>`
            ).join("");

            card.innerHTML = `
                <div class="report-card-header">
                    <div class="report-id-badge">${report.status_icon} ${report.id}</div>
                    <div class="report-priority" style="color: ${priorityColors[report.priority]}">
                        ${report.priority.toUpperCase()}
                    </div>
                </div>
                <div class="report-card-body">
                    <div class="report-meta">
                        <span>${platformIcons[report.platform] || "🌐"} ${report.platform}</span>
                        <span>👤 ${escapeHtml(report.reported_user)}</span>
                    </div>
                    <div class="report-threats-row">${threatTags}</div>
                    <div class="report-severity-bar">
                        <div class="report-severity-fill" style="width: ${report.overall_severity * 100}%; background: ${priorityColors[report.priority]}"></div>
                    </div>
                    <div class="report-action-taken">
                        Action: <strong>${report.action_taken.replace(/_/g, ' ')}</strong>
                    </div>
                </div>
                <div class="report-card-footer">
                    <span class="report-timestamp">${new Date(report.timestamp).toLocaleString()}</span>
                    <span class="report-status">${report.status_icon} ${report.status}</span>
                </div>
            `;
            reportsList.appendChild(card);
        });
    } catch (err) {
        console.error("Failed to load Cyber Hub reports:", err);
    }
}
