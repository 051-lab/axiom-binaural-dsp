const state = {
  tracks: [],
  filtered: [],
  current: null,
  jdspUi: "",
  jdspLoaded: false,
};

const $ = (id) => document.getElementById(id);

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const payload = await response.json();
  if (!payload.ok) throw new Error(payload.error || "request failed");
  return payload;
}

function formatTime(value) {
  if (!Number.isFinite(value) || value < 0) return "0:00";
  const total = Math.floor(value);
  const minutes = Math.floor(total / 60);
  const seconds = String(total % 60).padStart(2, "0");
  return `${minutes}:${seconds}`;
}

function trackLine(track) {
  const artist = track.artist || "Unknown artist";
  const album = track.album || track.albumFolder;
  return `${artist} - ${album}`;
}

function renderAlbums(albums) {
  $("albums").innerHTML = "";
  for (const album of albums) {
    const button = document.createElement("button");
    button.className = "album-pill";
    button.textContent = `${album.folder} (${album.trackCount})`;
    button.onclick = () => {
      $("search").value = album.folder;
      filterTracks();
    };
    $("albums").appendChild(button);
  }
}

function renderTracks() {
  $("tracks").innerHTML = "";
  for (const track of state.filtered) {
    const button = document.createElement("button");
    button.className = "track";
    const text = document.createElement("span");
    const title = document.createElement("strong");
    const meta = document.createElement("span");
    const ext = document.createElement("span");
    title.textContent = track.title;
    meta.textContent = trackLine(track);
    ext.textContent = track.extension.toUpperCase();
    text.append(title, meta);
    button.append(text, ext);
    button.onclick = async () => {
      await api("/api/play", { method: "POST", body: JSON.stringify({ id: track.id }) });
      state.current = track;
      renderNowPlaying();
      await refreshStatus();
    };
    $("tracks").appendChild(button);
  }
}

function filterTracks() {
  const query = $("search").value.trim().toLowerCase();
  state.filtered = query
    ? state.tracks.filter((track) => [track.title, track.artist, track.album, track.albumFolder, track.filename].join(" ").toLowerCase().includes(query))
    : state.tracks;
  renderTracks();
}

function renderNowPlaying() {
  if (!state.current) return;
  $("nowTitle").textContent = state.current.title;
  $("nowMeta").textContent = trackLine(state.current);
}

async function loadLibrary() {
  const payload = await api("/api/library");
  state.tracks = payload.tracks;
  state.filtered = state.tracks;
  renderAlbums(payload.albums);
  renderTracks();
}

async function refreshStatus() {
  const payload = await api("/api/status");
  const route = payload.route;
  $("routeStatus").textContent = route.jamesdspConnected
    ? `JamesDSP connected: ${route.sinks.join(", ")}`
    : "JamesDSP route is not connected";
  if (route.jamesdspUi && route.jamesdspUi !== state.jdspUi) {
    state.jdspUi = route.jamesdspUi;
    $("jdspOpen").href = route.jamesdspUi;
    if (state.jdspLoaded) $("jdspFrame").src = route.jamesdspUi;
  }

  const player = payload.player;
  const playerPath = player.sourcePath || player.path;
  if (playerPath) {
    const match = state.tracks.find((track) => track.path === playerPath);
    if (match) {
      state.current = match;
      renderNowPlaying();
    }
  }
  const pos = Number(player["time-pos"] || 0);
  const duration = Number(player.duration || 0);
  $("timeText").textContent = `${formatTime(pos)} / ${formatTime(duration)}`;
  $("seek").value = duration > 0 ? String(Math.round((pos / duration) * 1000)) : "0";
  if (Number.isFinite(Number(player.volume))) $("volume").value = String(Math.round(Number(player.volume)));
}

async function loadEelList() {
  const payload = await api("/api/eel");
  $("eelScripts").innerHTML = "";
  for (const script of payload.scripts) {
    const option = document.createElement("option");
    option.value = script.path;
    option.textContent = script.name;
    $("eelScripts").appendChild(option);
  }
}

async function loadBookmarks() {
  const payload = await api("/api/bookmarks");
  $("bookmarks").innerHTML = "";
  for (const bookmark of payload.bookmarks.slice().reverse()) {
    const div = document.createElement("div");
    div.className = "bookmark-item";
    const label = document.createElement("span");
    const position = document.createElement("span");
    label.textContent = bookmark.label;
    position.textContent = formatTime(Number(bookmark.position || 0));
    div.append(label, position);
    $("bookmarks").appendChild(div);
  }
}

async function playerCommand(command, value = null) {
  await api("/api/player/command", { method: "POST", body: JSON.stringify({ command, value }) });
  await refreshStatus();
}

async function loadJdspFrame() {
  if (!state.jdspUi || state.jdspUi === "#") {
    $("jdspPlaceholder").textContent = "Starting JamesDSP UI...";
    const payload = await api("/api/jdsp-ui/start", { method: "POST", body: "{}" });
    state.jdspUi = payload.url;
    $("jdspOpen").href = payload.url;
  }
  if (!state.jdspUi) return;
  state.jdspLoaded = true;
  $("jdspFrame").src = state.jdspUi;
  $("jdspFrame").classList.add("loaded");
  $("jdspPlaceholder").classList.add("hidden");
}

function unloadJdspFrame() {
  state.jdspLoaded = false;
  $("jdspFrame").src = "about:blank";
  $("jdspFrame").classList.remove("loaded");
  $("jdspPlaceholder").classList.remove("hidden");
  $("jdspPlaceholder").textContent = "JamesDSP UI is unloaded.";
}

function bindEvents() {
  $("search").addEventListener("input", filterTracks);
  $("reloadLibrary").onclick = loadLibrary;
  $("startRoute").onclick = async () => {
    $("routeStatus").textContent = "Starting JamesDSP route...";
    await api("/api/route/start", { method: "POST", body: "{}" });
    await refreshStatus();
  };
  $("toggle").onclick = () => playerCommand("toggle");
  $("previous").onclick = () => playerCommand("previous");
  $("next").onclick = () => playerCommand("next");
  $("seek").onchange = async () => {
    const status = await api("/api/status");
    const duration = Number(status.player.duration || 0);
    if (duration > 0) await playerCommand("seek", (Number($("seek").value) / 1000) * duration);
  };
  $("volume").onchange = () => playerCommand("volume", Number($("volume").value));
  $("loopA").onclick = () => playerCommand("loop-a");
  $("loopB").onclick = () => playerCommand("loop-b");
  $("clearLoop").onclick = () => playerCommand("loop-clear");
  $("jdspLoad").onclick = () => loadJdspFrame().catch((error) => {
    $("jdspPlaceholder").textContent = error.message;
  });
  $("jdspUnload").onclick = unloadJdspFrame;
  $("bookmark").onclick = async () => {
    const label = state.current ? state.current.title : "Listening bookmark";
    await api("/api/bookmarks", { method: "POST", body: JSON.stringify({ label }) });
    await loadBookmarks();
  };
  $("loadEel").onclick = async () => {
    const path = $("eelPath").value.trim() || $("eelScripts").value;
    $("eelStatus").textContent = "Validating and loading...";
    try {
      const payload = await api("/api/eel/load", { method: "POST", body: JSON.stringify({ path }) });
      $("eelStatus").textContent = `Loaded: ${payload.path}`;
    } catch (error) {
      $("eelStatus").textContent = error.message;
    }
  };
}

async function init() {
  bindEvents();
  await loadLibrary();
  await loadEelList();
  await loadBookmarks();
  await refreshStatus();
  setInterval(refreshStatus, 1500);
}

init().catch((error) => {
  $("routeStatus").textContent = error.message;
});
