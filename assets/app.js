"use strict";

const $ = (id) => document.getElementById(id);
const state = {
  astros: { number: 0, people: [] },
  neo: null,
  solar: null,
  apod: null,
  neoAvg: null,
  issMap: null,
  busy: false,
};

const esc = (s) => String(s).replace(/[&<>"']/g, (c) => (
  { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]
));

const LOADER_HTML = `
  <div class="jload">
    <div class="jload-ring"></div>
    <div class="jload-txt">
      <span>J.A.R.V.I.S. INITIALIZING NASA CORE...</span>
      <span>ESTABLISHING LINK TO DEEP SPACE NETWORK...</span>
      <span>DOWNLOADING MISSION DATA...</span>
    </div>
  </div>`;

async function fetchFeed(name) {
  const r = await fetch(`/api/feeds?feed=${name}`);
  const body = await r.json();
  if (!r.ok) throw new Error(body.error || `Feed ${name} failed (${r.status})`);
  return body.data;
}

function liveContext() {
  const parts = [];
  if (state.astros.number) {
    parts.push(`${state.astros.number} humans in space (${state.astros.people.join(", ")}).`);
  }
  if (state.neo) {
    parts.push(`${state.neo.count} near-Earth objects tracked today, ${state.neo.hazardous} hazardous.`);
  }
  if (state.solar) {
    parts.push(`Solar activity: ${state.solar.count} flares past 7 days, latest class ${state.solar.class}.`);
  }
  return parts.join(" ") || "telemetry warming up";
}

async function askJarvis(prompt, displayLabel) {
  if (state.busy) return;
  state.busy = true;
  addChat("COMMANDER", esc(displayLabel || prompt));
  const thinking = addChat("JARVIS", LOADER_HTML);
  try {
    const r = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt, context: liveContext() }),
    });
    const body = await r.json();
    const reply = r.ok ? body.reply : (body.error || "Comms disruption — please retry, Commander.");
    thinking.querySelector(".chat-bbl").innerHTML = esc(reply).replace(/\n/g, "<br>");
    speak(reply);
  } catch (e) {
    thinking.querySelector(".chat-bbl").textContent = "Comms disruption — the relay to mission control failed. Please retry.";
  } finally {
    state.busy = false;
  }
}

function addChat(speaker, html) {
  const log = $("chatlog");
  const row = document.createElement("div");
  row.className = "chat-row";
  if (speaker === "COMMANDER") {
    row.innerHTML = `<div class="chat-sndr su">COMMANDER</div><div class="chat-bbl cbu">${html}</div>`;
  } else {
    row.innerHTML = `<div class="chat-sndr sj">J.A.R.V.I.S.</div><div class="chat-bbl cbj">${html}</div>`;
  }
  log.appendChild(row);
  log.scrollTop = log.scrollHeight;
  return row;
}

function speak(text) {
  if (!window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text.replace(/<[^>]*>/g, " "));
  const load = () => {
    const voices = window.speechSynthesis.getVoices();
    const v = voices.find((x) => x.lang.startsWith("en-GB") || x.name.includes("Daniel") || x.name.includes("Arthur"));
    if (v) u.voice = v;
    u.rate = 1.05; u.pitch = 0.9; u.volume = 1.0;
    window.speechSynthesis.speak(u);
  };
  if (window.speechSynthesis.getVoices().length === 0) {
    window.speechSynthesis.addEventListener("voiceschanged", load, { once: true });
  } else load();
}

function initMic() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  const btn = $("micbtn");
  if (!SR) { btn.style.display = "none"; return; }
  const rec = new SR();
  rec.lang = "en-US";
  rec.interimResults = false;
  rec.maxAlternatives = 1;
  let listening = false;
  rec.onresult = (e) => {
    const text = e.results[0][0].transcript;
    if (text) askJarvis(text);
  };
  rec.onend = () => { listening = false; btn.classList.remove("listening"); };
  rec.onerror = () => { listening = false; btn.classList.remove("listening"); };
  btn.addEventListener("click", () => {
    if (listening) { rec.stop(); return; }
    window.speechSynthesis && window.speechSynthesis.cancel();
    listening = true;
    btn.classList.add("listening");
    rec.start();
  });
}

function showImage(label, url, caption) {
  $("display").innerHTML = `
    <span class="slbl">${esc(label)}</span>
    <img src="${esc(url)}" alt="${esc(label)}">
    ${caption ? `<p class="dcapt">${esc(caption)}</p>` : ""}`;
}

function showISS(lat, lon) {
  $("display").innerHTML = `
    <span class="slbl">ISS ORBITAL TRACKER — REAL-TIME POSITION</span>
    <div id="issmap"></div>
    <p class="dcapt">ISS POSITION · ${lat.toFixed(2)}°N ${lon.toFixed(2)}°E · ALTITUDE ~408 km · 27,600 km/h</p>`;
  if (typeof L === "undefined") return;
  const map = L.map("issmap", { zoomControl: false, attributionControl: false }).setView([lat, lon], 2);
  L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", { maxZoom: 8 }).addTo(map);
  L.circleMarker([lat, lon], {
    radius: 9, color: "#0EA5E9", weight: 2,
    fillColor: "#38BDF8", fillOpacity: 0.85,
  }).addTo(map).bindTooltip(`ISS ${lat.toFixed(2)}°, ${lon.toFixed(2)}°`);
  state.issMap = map;
}

function showEarthEvents(events) {
  const catCss = { "Wildfires": "ec-fire", "Severe Storms": "ec-storm", "Volcanoes": "ec-vol" };
  $("display").innerHTML = `
    <span class="slbl">EONET — NASA ACTIVE EARTH EVENTS</span>
    ${events.map((ev) => `
      <div class="ev-card">
        <span class="ev-cat ${catCss[ev.cat] || "ec-def"}">${esc(ev.cat)}</span>
        <span class="ev-ttl">${esc(ev.title)}</span>
      </div>`).join("")}`;
}

function showRadar() {
  const a = state.neo || { count: 0, hazardous: 0, objects: [] };
  const s = state.solar || { count: 0, class: "—", active: false };
  const threatColor = a.hazardous > 0 ? "#F87171" : "#34D399";
  const threatWord = a.hazardous > 0 ? "ELEVATED" : "NOMINAL";
  const tiles = `
    <span class="slbl">PLANETARY DEFENSE — LIVE RADAR</span>
    <div class="tiles">
      <div class="tile">
        <div class="tile-lbl">Objects Today</div>
        <div class="tile-val" style="color:#38BDF8;">${a.count}</div>
        <div class="tile-sub">Near-Earth flyby</div>
      </div>
      <div class="tile">
        <div class="tile-lbl">Threat Level</div>
        <div class="tile-val" style="color:${threatColor};">${a.hazardous}</div>
        <div class="tile-sub" style="color:${threatColor};opacity:.7;">${threatWord}</div>
      </div>
      <div class="tile">
        <div class="tile-lbl">Solar Flares 7D</div>
        <div class="tile-val" style="color:${s.active ? "#FBBF24" : "#34D399"};">${s.count}</div>
        <div class="tile-sub">${s.active ? "Class " + esc(s.class) : "Nominal"}</div>
      </div>
    </div>
    <span class="slbl">CLOSEST APPROACH — TODAY</span>`;

  const objects = (a.objects || []).slice(0, 5);
  const cards = objects.length
    ? objects.map((o) => `
        <div class="ast-card">
          <div class="ast-name">${esc(o.name)}</div>
          <div class="ast-data">
            <span>${o.dist_km.toLocaleString()} km</span>
            <span>${o.speed_kph.toLocaleString()} km/h</span>
            <span class="ast-badge ${o.hazardous ? "ast-haz" : "ast-safe"}">${o.hazardous ? "HAZARDOUS" : "SAFE"}</span>
          </div>
        </div>`).join("")
    : `<div class="starfield">
        <div class="sf-layer"></div>
        <div class="sf-layer sf-2"></div>
        <div class="sf-layer sf-3"></div>
        <div class="sf-center">
          <div class="sf-txt">DEEP SPACE SCAN ACTIVE</div>
          <div class="sf-sub">Awaiting radar telemetry — select a mission directive below</div>
        </div>
      </div>`;
  $("display").innerHTML = tiles + cards;
}

function renderStatus() {
  const a = state.neo, s = state.solar;
  const pills = $("pills");
  const hazardous = a ? a.hazardous : 0;
  const threatTxt = hazardous > 0 ? `THREAT ELEVATED · ${hazardous} HAZARDOUS` : "THREAT NOMINAL";
  pills.innerHTML = `
    <span class="pill pb"><span class="pd db"></span>${state.astros.number} HUMANS IN SPACE</span>
    <span class="pill pb"><span class="pd db"></span>${a ? a.count : 0} NEAR-EARTH OBJECTS</span>
    <span class="pill ${hazardous > 0 ? "pr" : "pg"}"><span class="pd ${hazardous > 0 ? "dr" : "dg"}"></span>${threatTxt}</span>
    <span class="pill ${s && s.active ? "pa" : "pb"}"><span class="pd ${s && s.active ? "da" : "db"}"></span>${s && s.active ? "SOLAR CLASS " + esc(s.class) : "SOLAR NOMINAL"}</span>
    <div class="psep"></div>
    <span class="pill px" id="pill-clock">--:-- UTC</span>`;

  if (a) {
    $("ms-neo").textContent = a.count;
    $("ms-neo").className = "ms-val " + (hazardous > 0 ? "ms-r" : "ms-b");
    $("ms-neo-status").textContent = `${hazardous > 0 ? "ELEVATED" : "NOMINAL"} — ${hazardous} hazardous`;
    $("ms-neo-status").className = "ms-status " + (hazardous > 0 ? "ms-status-warn" : "ms-status-ok");
  }
  if (state.neoAvg && a) {
    const avg = state.neoAvg;
    const trend = a.count > avg * 1.15 ? `ABOVE 7-DAY AVG (${avg}/day)`
      : a.count < avg * 0.85 ? `BELOW 7-DAY AVG (${avg}/day)`
      : `NEAR 7-DAY AVG (${avg}/day)`;
    $("ms-neo-trend").textContent = trend;
  }

  const crew = state.astros.number;
  let crewLevel = "BELOW NORMAL", crewCls = "ms-status-dim";
  if (crew === 0) { crewLevel = "FEED OFFLINE"; }
  else if (crew > 13) { crewLevel = "ABOVE NORMAL"; crewCls = "ms-status-amber"; }
  else if (crew >= 7) { crewLevel = "NORMAL"; crewCls = "ms-status-ok"; }
  $("ms-crew").textContent = crew;
  $("ms-crew-level").textContent = crewLevel;
  $("ms-crew-level").className = "ms-status " + crewCls;
  $("ms-crew-status").textContent = crew >= 10 ? "ISS + TIANGONG" : "ISS ACTIVE";

  if (s) {
    const threat = s.threat || "NOMINAL";
    $("ms-solar").textContent = s.count;
    $("ms-solar").className = "ms-val " + ({ HIGH: "ms-r", ELEVATED: "ms-a" }[threat] || "ms-g");
    $("ms-solar-status").textContent = `THREAT ${threat}`;
    $("ms-solar-status").className = "ms-status " + ({ HIGH: "ms-status-warn", ELEVATED: "ms-status-amber" }[threat] || "ms-status-ok");
    $("ms-solar-detail").textContent = s.active ? `PEAK CLASS ${s.strongest}` : "QUIET SUN";
  }
}

function tickClock() {
  const now = new Date();
  const hh = String(now.getUTCHours()).padStart(2, "0");
  const mm = String(now.getUTCMinutes()).padStart(2, "0");
  const ss = String(now.getUTCSeconds()).padStart(2, "0");
  $("ms-clock").textContent = `${hh}:${mm}:${ss}`;
  $("ms-date").textContent = `${now.toISOString().slice(0, 10)} · MISSION CLOCK`;
  const pc = $("pill-clock");
  if (pc) pc.textContent = `${hh}:${mm} UTC`;
}

const DIRECTIVES = {
  async apod() {
    const apod = await fetchFeed("apod");
    if (apod && apod.media_type === "image") {
      state.apod = apod;
      showImage("NASA ASTRONOMY PICTURE OF THE DAY", apod.url, `${apod.title} · ${apod.date}`);
    }
    return {
      prompt: `Special Directive: Optical Briefing. Title: ${apod.title}. Detail: ${apod.explanation}`,
      label: "Requesting Deep Space Optical Briefing...",
    };
  },
  async mars() {
    let mars = null;
    try { mars = await fetchFeed("mars"); } catch (e) { /* upstream offline */ }
    if (!mars) {
      return {
        prompt: "Special Directive: The Mars rover imaging relay is currently offline (NASA upstream feed unavailable). Give a 1-sentence acknowledgment and recommend another active feed.",
        label: "Synchronizing Martian Surface Camera...",
      };
    }
    showImage("MARS CURIOSITY ROVER — LIVE SURFACE", mars.img, `${mars.rover} — Sol ${mars.sol} · ${mars.date}`);
    return {
      prompt: `Special Directive: Mars Surface. Live imaging from ${mars.rover} rover. Sol ${mars.sol}, earth date ${mars.date}. Camera: ${mars.camera}. Status: ${mars.status}. Give a crisp 2-sentence tactical surface report.`,
      label: "Synchronizing Martian Surface Camera...",
    };
  },
  async neo() {
    const [ast, sol] = await Promise.all([fetchFeed("neo"), fetchFeed("solar")]);
    state.neo = ast; state.solar = sol;
    renderStatus();
    showRadar();
    const threat = ast.hazardous > 0 ? "ELEVATED" : "NOMINAL";
    const solarLine = sol.active ? `${sol.count} solar flares (7d), latest class ${sol.class}` : "no significant solar activity";
    return {
      prompt: `Special Directive: Multi-source planetary defense correlation. ASTEROID RADAR: ${ast.count} NEOs today. Hazardous: ${ast.hazardous}. Closest: ${ast.closest_name} at ${ast.closest_km.toLocaleString()} km. Threat: ${threat}. SOLAR WEATHER: ${solarLine}. Deliver a 3-sentence integrated threat assessment correlating both datasets.`,
      label: "Running Near-Earth Threat Correlation...",
    };
  },
  async iss() {
    const pos = await fetchFeed("iss");
    showISS(pos.lat, pos.lon);
    return {
      prompt: `Special Directive: ISS position report. Station at ${pos.lat.toFixed(2)}° latitude, ${pos.lon.toFixed(2)}° longitude. Orbital altitude ~408 km, speed ~27,600 km/h. Give a 2-sentence tactical position report.`,
      label: "Executing ISS Live Position Scan...",
    };
  },
  async solar() {
    const sol = await fetchFeed("solar");
    state.solar = sol;
    renderStatus();
    return {
      prompt: `Special Directive: DONKI Solar Activity. ${sol.count} solar flare events past 7 days. Latest class: ${sol.class}. Peak: ${sol.peak}. Give a 2-sentence space weather briefing and mission advisory.`,
      label: "Analyzing Solar Activity Data...",
    };
  },
  async earth() {
    const events = await fetchFeed("earth_events");
    if (events && events.length) {
      showEarthEvents(events);
      const summary = events.map((e) => `${e.title} (${e.cat})`).join("; ");
      return {
        prompt: `Special Directive: EONET Earth Monitoring. NASA satellites detected: ${summary}. Give a 3-sentence Earth systems status briefing.`,
        label: "Scanning Earth Events Monitor...",
      };
    }
    return {
      prompt: "Special Directive: EONET shows no active natural events. Give a 1-sentence all-clear.",
      label: "Scanning Earth Events Monitor...",
    };
  },
};

function initDirectives() {
  document.querySelectorAll(".dbtn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      if (state.busy) return;
      btn.disabled = true;
      try {
        const result = await DIRECTIVES[btn.dataset.dir]();
        if (result) await askJarvis(result.prompt, result.label);
      } catch (e) {
        showError(e.message);
      } finally {
        btn.disabled = false;
      }
    });
  });
}

function showError(msg) {
  const banner = $("errbanner");
  banner.textContent = msg;
  banner.classList.add("show");
  setTimeout(() => banner.classList.remove("show"), 12000);
}

async function boot() {
  $("display").innerHTML = LOADER_HTML;
  addChat("JARVIS", LOADER_HTML);

  const [astros, neo, solar, apod, trend] = await Promise.allSettled([
    fetchFeed("astros"), fetchFeed("neo"), fetchFeed("solar"),
    fetchFeed("apod"), fetchFeed("neo_trend"),
  ]);

  if (astros.status === "fulfilled") state.astros = astros.value;
  if (neo.status === "fulfilled") state.neo = neo.value;
  if (solar.status === "fulfilled") state.solar = solar.value;
  if (apod.status === "fulfilled") state.apod = apod.value;
  if (trend.status === "fulfilled") state.neoAvg = trend.value.avg;

  const failure = [astros, neo, solar, apod].find((r) => r.status === "rejected");
  if (failure && !state.neo && !state.astros.number) {
    showError(failure.reason.message);
  }

  renderStatus();

  if (state.apod && state.apod.media_type === "image") {
    showImage("NASA ASTRONOMY PICTURE OF THE DAY", state.apod.url, `${state.apod.title} · ${state.apod.date}`);
  } else {
    showRadar();
  }

  const a = state.neo || { count: 0, hazardous: 0 };
  const s = state.solar || { count: 0, class: "—", active: false };
  const threat = a.hazardous > 0 ? "ELEVATED" : "NOMINAL";
  const solarLine = s.active ? `${s.count} flare events, latest class ${s.class}` : "space weather nominal";
  $("chatlog").innerHTML = "";
  addChat("JARVIS",
    `<b>ALL SYSTEMS ONLINE — NASA CORE ACTIVE</b><br><br>` +
    `Good day. I am J.A.R.V.I.S., your Joint Artificial Reconnaissance &amp; Vigilance Intelligence System, ` +
    `designed and built by Prajith.<br><br>` +
    `<b>LIVE MISSION STATUS</b><br>` +
    `· <b>${state.astros.number} humans</b> currently in space<br>` +
    `· <b>${a.count} near-Earth objects</b> tracked today — threat level: <b>${threat}</b><br>` +
    `· Solar activity: ${esc(solarLine)}<br><br>` +
    `Today's deep space image is loaded. Use the mission directives below to query any active feed.`);
}

$("chatform").addEventListener("submit", (e) => {
  e.preventDefault();
  const input = $("chatinput");
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  askJarvis(text);
});

initDirectives();
initMic();
tickClock();
setInterval(tickClock, 1000);
boot();
