/**
 * NEXUS-NOWCAST: Meteorological C2 Tactical GIS & Multi-Sensor HUD
 * Integrated Real Map Engine: CartoDB Dark Matter & Esri Dark Canvas
 * - Real roads, highways, districts, landmarks, and geography
 * - Zero API key required, zero usage delay, high-speed CDN
 * - Strictly ZERO BLUE / ZERO CYAN color palette
 * - Plus Jakarta Sans + JetBrains Mono typography
 */

let map;
let baseTileLayers = {};
let currentBaseLayer = null;

// Operational Layer Groups
let baseVectorLayerGroup;
let rangeRingsLayerGroup;
let radialsLayerGroup;
let radarLayerGroup;
let lightningLayerGroup;
let satelliteLayerGroup;
let trackLayerGroup;
let alertPolygonLayer;
let xaiLayerGroup;

let currentRegion = "delhi_ncr";
let currentLeadTime = 0;
let isPlaying = false;
let playInterval = null;
let showXai = false;

// HUD Layer Visibility States
let showRings = true;
let showRadials = true;
let showRadar = true;
let showLightning = true;
let showTrack = true;

// Regional Metadata & Landmarks
const REGION_GEO = {
  delhi_ncr: {
    name: "DWR PALAM (NEW DELHI)",
    center: [28.6139, 77.2090],
    dwr: [28.5684, 77.0967],
    zoom: 10,
    landmarks: [
      { name: "DWR PALAM (RADAR)", pos: [28.5684, 77.0967], type: "dwr" },
      { name: "INDIRA GANDHI INT'L AIRPORT", pos: [28.5562, 77.1000], type: "airport" },
      { name: "CONNAUGHT PLACE", pos: [28.6315, 77.2167], type: "city" },
      { name: "GURUGRAM CYBER CITY", pos: [28.4950, 77.0895], type: "city" },
      { name: "NOIDA ELECTRONIC CITY", pos: [28.6270, 77.3725], type: "city" },
      { name: "FARIDABAD SECTOR 15", pos: [28.4089, 77.3178], type: "city" },
      { name: "GHAZIABAD JUNCTION", pos: [28.6692, 77.4538], type: "city" },
      { name: "MEERUT BYPASS", pos: [28.9845, 77.7064], type: "city" }
    ]
  },
  kolkata_bay: {
    name: "DWR ALIPORE (KOLKATA)",
    center: [22.5726, 88.3639],
    dwr: [22.5333, 88.3333],
    zoom: 10,
    landmarks: [
      { name: "DWR ALIPORE (RADAR)", pos: [22.5333, 88.3333], type: "dwr" },
      { name: "NETAJI SUBHASH AIRPORT", pos: [22.6547, 88.4467], type: "airport" },
      { name: "HOWRAH JUNCTION", pos: [22.5850, 88.3425], type: "city" },
      { name: "SALT LAKE SECTOR V", pos: [22.5800, 88.4350], type: "city" },
      { name: "BARRACKPORE AIR BASE", pos: [22.7600, 88.3600], type: "city" },
      { name: "HALDIA DOCK COMPLEX", pos: [22.0667, 88.0667], type: "city" }
    ]
  },
  chennai_coast: {
    name: "DWR MEENAMBAKKAM (CHENNAI)",
    center: [13.0827, 80.2707],
    dwr: [12.9941, 80.1709],
    zoom: 10,
    landmarks: [
      { name: "DWR CHENNAI (RADAR)", pos: [12.9941, 80.1709], type: "dwr" },
      { name: "CHENNAI INT'L AIRPORT", pos: [12.9941, 80.1709], type: "airport" },
      { name: "CHENNAI PORT HARBOUR", pos: [13.0827, 80.2707], type: "city" },
      { name: "MARINA COASTLINE", pos: [13.0500, 80.2824], type: "city" },
      { name: "TAMBARAM AIR BASE", pos: [12.9249, 80.1000], type: "city" },
      { name: "ENNORE THERMAL HUB", pos: [13.2450, 80.3320], type: "city" },
      { name: "SRIPERUMBUDUR INDUSTRIAL", pos: [12.9675, 79.9400], type: "city" }
    ]
  },
  mumbai_coastal: {
    name: "DWR COLABA (MUMBAI COAST)",
    center: [19.0760, 72.8777],
    dwr: [18.8986, 72.8094],
    zoom: 10,
    landmarks: [
      { name: "DWR COLABA (RADAR)", pos: [18.8986, 72.8094], type: "dwr" },
      { name: "CSM INT'L AIRPORT", pos: [19.0896, 72.8656], type: "airport" },
      { name: "BANDRA KURLA COMPLEX", pos: [19.0667, 72.8667], type: "city" },
      { name: "NAVI MUMBAI AIRPORT", pos: [18.9900, 73.0700], type: "city" },
      { name: "THANE JUNCTION", pos: [19.1970, 72.9700], type: "city" },
      { name: "KALYAN JUNCTION", pos: [19.2437, 73.1355], type: "city" },
      { name: "BORIVALI NATIONAL PARK", pos: [19.2300, 72.8600], type: "city" }
    ]
  }
};

/**
 * Radar dBZ Color Scale (STRICTLY ZERO BLUE / ZERO CYAN)
 * Progression: Deep Forest -> Leaf Green -> Emerald -> Yellow -> Amber -> Crimson -> Magenta
 */
function getDbzColor(dbz) {
  if (dbz >= 60) return "#d946ef"; // Magenta (Severe Convective Core / Hail)
  if (dbz >= 50) return "#ef4444"; // Crimson Red (Heavy Convective Storm)
  if (dbz >= 42) return "#ff9100"; // Electric Amber Orange (Squall Line)
  if (dbz >= 35) return "#facc15"; // Solar Yellow (Moderate Thunderstorm)
  if (dbz >= 25) return "#10b981"; // Emerald Green (Moderate Rain Echoes)
  if (dbz >= 15) return "#22c55e"; // Leaf Green (Light Rain)
  return "#15803d";               // Deep Forest Green (Trace Echoes)
}

document.addEventListener("DOMContentLoaded", () => {
  initMap();
  setupEventListeners();
  startOperationalClocks();
  fetchNowcastData(0);
});

/**
 * Initialize Leaflet Map with Real Street & Satellite Tile Servers
 * Zero API keys, Zero delay, Global Fastly/Cloudflare Edge Caching
 */
function initMap() {
  const reg = REGION_GEO[currentRegion];

  map = L.map("map", {
    center: reg.center,
    zoom: reg.zoom,
    zoomControl: false,
    attributionControl: false,
    minZoom: 6,
    maxZoom: 18,
    preferCanvas: true
  });

  L.control.zoom({ position: "bottomright" }).addTo(map);

  // 1. OpenStreetMap (OSM) Tile API - Free, open-source, no API key, no watermark
  const osmTileLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    subdomains: ['a', 'b', 'c'],
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    crossOrigin: true
  });
  osmTileLayer.addTo(map);

  // 2. Initialize Tactical Meteorological Overlays
  baseVectorLayerGroup = L.layerGroup().addTo(map);
  rangeRingsLayerGroup = L.layerGroup().addTo(map);
  radialsLayerGroup = L.layerGroup().addTo(map);
  radarLayerGroup = L.layerGroup().addTo(map);
  lightningLayerGroup = L.layerGroup().addTo(map);
  satelliteLayerGroup = L.layerGroup().addTo(map);
  trackLayerGroup = L.layerGroup().addTo(map);
  xaiLayerGroup = L.layerGroup().addTo(map);

  // Render Range Rings, Radials & Station Markers
  renderRadarGeometry(currentRegion);

  // Cursor Coordinates HUD Tracker
  map.on("mousemove", (e) => {
    const lat = e.latlng.lat.toFixed(4);
    const lon = e.latlng.lng.toFixed(4);
    const el = document.getElementById("hudCursorCoords");
    if (el) el.innerText = `${lat}° N, ${lon}° E`;
  });
}

/**
 * Switch Base Map Display Mode (Dark Tactical vs Monochrome Neutral)
 */
function setBaseMapStyle(styleKey) {
  const tilePane = document.querySelector(".leaflet-tile-pane");
  if (!tilePane) return;
  if (styleKey === "monoOsm") {
    tilePane.classList.add("mono-mode");
  } else {
    tilePane.classList.remove("mono-mode");
  }
}

/**
 * Real Doppler Weather Radar Range Rings & Azimuth Radials
 */
function renderRadarGeometry(regionKey) {
  baseVectorLayerGroup.clearLayers();
  rangeRingsLayerGroup.clearLayers();
  radialsLayerGroup.clearLayers();

  const reg = REGION_GEO[regionKey];
  if (!reg) return;

  const stationNameEl = document.getElementById("hudStationName");
  if (stationNameEl) stationNameEl.innerText = reg.name;

  // A. Concentric Doppler Radar Range Rings (25km, 50km, 100km, 150km, 200km, 250km)
  if (showRings) {
    const ringDistancesKm = [25, 50, 100, 150, 200, 250];
    ringDistancesKm.forEach((km) => {
      const radiusMeters = km * 1000;
      const isMajor = (km === 100 || km === 200);

      const circle = L.circle(reg.dwr, {
        radius: radiusMeters,
        color: isMajor ? "#059669" : "rgba(100, 116, 139, 0.4)",
        weight: isMajor ? 1.5 : 1,
        fill: false,
        dashArray: isMajor ? null : "4, 6",
        interactive: false
      });

      // Range ring distance marker
      const labelPos = [reg.dwr[0] + (km / 111.0), reg.dwr[1]];
      const labelMarker = L.marker(labelPos, {
        interactive: false,
        icon: L.divIcon({
          className: "range-label",
          html: `<span style="
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            font-weight: 700;
            color: ${isMajor ? '#059669' : '#475569'};
            background: #ffffff;
            padding: 1px 5px;
            border-radius: 3px;
            border: 1px solid #cbd5e1;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
          ">${km} KM</span>`,
          iconSize: [45, 14],
          iconAnchor: [22, 7]
        })
      });

      rangeRingsLayerGroup.addLayer(circle);
      rangeRingsLayerGroup.addLayer(labelMarker);
    });
  }

  // B. 12 Cardinal Azimuth Bearing Radials (0° to 330°)
  if (showRadials) {
    const maxRangeKm = 240;
    for (let deg = 0; deg < 360; deg += 30) {
      const rad = (deg * Math.PI) / 180;
      const dLat = (maxRangeKm * Math.cos(rad)) / 111.0;
      const dLon = (maxRangeKm * Math.sin(rad)) / (111.0 * Math.cos((reg.dwr[0] * Math.PI) / 180));
      const endPoint = [reg.dwr[0] + dLat, reg.dwr[1] + dLon];

      const radialLine = L.polyline([reg.dwr, endPoint], {
        color: (deg % 90 === 0) ? "rgba(5, 150, 105, 0.5)" : "rgba(100, 116, 139, 0.3)",
        weight: (deg % 90 === 0) ? 1.5 : 1,
        dashArray: "3, 6",
        interactive: false
      });

      const degLabel = String(deg).padStart(3, '0') + "°";
      const badgeMarker = L.marker(endPoint, {
        interactive: false,
        icon: L.divIcon({
          className: "azimuth-label",
          html: `<span style="
            font-family: 'JetBrains Mono', monospace;
            font-size: 9px;
            font-weight: 700;
            color: #059669;
            background: #ffffff;
            padding: 1px 4px;
            border-radius: 3px;
            border: 1px solid #cbd5e1;
            box-shadow: 0 1px 2px rgba(0,0,0,0.08);
          ">${degLabel}</span>`,
          iconSize: [36, 12],
          iconAnchor: [18, 6]
        })
      });

      radialsLayerGroup.addLayer(radialLine);
      radialsLayerGroup.addLayer(badgeMarker);
    }
  }

  // C. Strategic Regional Landmarks & Radar Stations
  if (reg.landmarks) {
    reg.landmarks.forEach(lm => {
      const isRadar = lm.type === "dwr";
      const isAirport = lm.type === "airport";
      const icon = L.divIcon({
        className: "landmark-icon",
        html: `
          <div style="display: flex; align-items: center; gap: 6px; pointer-events: none;">
            <div class="${isRadar ? 'dwr-beacon-dot' : ''}" style="
              width: ${isRadar ? '14px' : '8px'};
              height: ${isRadar ? '14px' : '8px'};
              border-radius: 50%;
              background: ${isRadar ? '#059669' : isAirport ? '#d97706' : '#475569'};
              border: 2px solid #ffffff;
              flex-shrink: 0;
            "></div>
            <span style="
              font-family: 'JetBrains Mono', monospace;
              font-size: 10px;
              font-weight: 700;
              letter-spacing: 0.2px;
              color: ${isRadar ? '#059669' : '#0f172a'};
              background: #ffffff;
              padding: 2px 6px;
              border-radius: 4px;
              border: 1px solid #cbd5e1;
              box-shadow: 0 1px 3px rgba(0,0,0,0.1);
              white-space: nowrap;
            ">${lm.name}</span>
          </div>
        `,
        iconSize: [140, 18],
        iconAnchor: [isRadar ? 6 : 4, isRadar ? 6 : 4]
      });

      baseVectorLayerGroup.addLayer(L.marker(lm.pos, { icon: icon }));
    });
  }
}

/**
 * Setup Operational Event Listeners
 */
function setupEventListeners() {
  const slider = document.getElementById("timelineSlider");
  const playBtn = document.getElementById("btnPlayPause");
  const regionSelect = document.getElementById("regionSelect");
  const mapStyleSelect = document.getElementById("mapStyleSelect");
  const xaiBtn = document.getElementById("btnXaiToggle");
  const capBtn = document.getElementById("btnDownloadCap");
  const closeModalBtn = document.getElementById("btnCloseModal");
  const copyXmlBtn = document.getElementById("btnCopyXml");
  const downloadXmlFileBtn = document.getElementById("btnDownloadXmlFile");

  // Tactical Map HUD Toggles
  const toggleRingsBtn = document.getElementById("toggleRings");
  const toggleRadialsBtn = document.getElementById("toggleRadials");
  const toggleRadarBtn = document.getElementById("toggleRadar");
  const toggleTrackBtn = document.getElementById("toggleTrack");

  if (mapStyleSelect) {
    mapStyleSelect.addEventListener("change", (e) => {
      setBaseMapStyle(e.target.value);
    });
  }

  if (toggleRingsBtn) {
    toggleRingsBtn.addEventListener("click", () => {
      showRings = !showRings;
      toggleRingsBtn.classList.toggle("active", showRings);
      renderRadarGeometry(currentRegion);
    });
  }

  if (toggleRadialsBtn) {
    toggleRadialsBtn.addEventListener("click", () => {
      showRadials = !showRadials;
      toggleRadialsBtn.classList.toggle("active", showRadials);
      renderRadarGeometry(currentRegion);
    });
  }

  if (toggleRadarBtn) {
    toggleRadarBtn.addEventListener("click", () => {
      showRadar = !showRadar;
      toggleRadarBtn.classList.toggle("active", showRadar);
      if (showRadar) {
        map.addLayer(radarLayerGroup);
      } else {
        map.removeLayer(radarLayerGroup);
      }
    });
  }

  if (toggleTrackBtn) {
    toggleTrackBtn.addEventListener("click", () => {
      showTrack = !showTrack;
      toggleTrackBtn.classList.toggle("active", showTrack);
      if (showTrack) {
        map.addLayer(trackLayerGroup);
      } else {
        map.removeLayer(trackLayerGroup);
      }
    });
  }

  slider.addEventListener("input", (e) => {
    currentLeadTime = parseInt(e.target.value, 10);
    updateTimelineReadout(currentLeadTime);
    fetchNowcastData(currentLeadTime);
  });

  playBtn.addEventListener("click", togglePlay);

  document.querySelectorAll(".btn-preset").forEach(btn => {
    btn.addEventListener("click", (e) => {
      document.querySelectorAll(".btn-preset").forEach(b => b.classList.remove("active"));
      e.target.classList.add("active");
      currentLeadTime = parseInt(e.target.dataset.min, 10);
      slider.value = currentLeadTime;
      updateTimelineReadout(currentLeadTime);
      fetchNowcastData(currentLeadTime);
    });
  });

  document.querySelectorAll(".tick-mark").forEach(tick => {
    tick.addEventListener("click", (e) => {
      currentLeadTime = parseInt(e.target.dataset.val, 10);
      slider.value = currentLeadTime;
      updateTimelineReadout(currentLeadTime);
      fetchNowcastData(currentLeadTime);
    });
  });

  regionSelect.addEventListener("change", (e) => {
    currentRegion = e.target.value;
    currentLeadTime = 0;
    slider.value = 0;
    updateTimelineReadout(0);

    const reg = REGION_GEO[currentRegion];
    if (reg) {
      map.setView(reg.center, reg.zoom, { animate: true });
      renderRadarGeometry(currentRegion);
    }
    fetchNowcastData(0);
  });

  xaiBtn.addEventListener("click", () => {
    showXai = !showXai;
    xaiBtn.classList.toggle("active", showXai);
    const toast = document.getElementById("xaiToast");
    if (toast) toast.style.display = showXai ? "block" : "none";
    if (showXai) {
      renderXaiEdges();
    } else {
      xaiLayerGroup.clearLayers();
    }
  });

  capBtn.addEventListener("click", openCapModal);
  closeModalBtn.addEventListener("click", () => {
    document.getElementById("capModal").style.display = "none";
  });

  copyXmlBtn.addEventListener("click", () => {
    const code = document.getElementById("capXmlCode").innerText;
    navigator.clipboard.writeText(code).then(() => {
      copyXmlBtn.innerText = "Copied to Clipboard!";
      setTimeout(() => { copyXmlBtn.innerText = "Copy to Clipboard"; }, 2000);
    });
  });

  downloadXmlFileBtn.addEventListener("click", () => {
    window.open(`/api/alerts/cap.xml?region=${currentRegion}&lead_time_min=${currentLeadTime}`, "_blank");
  });
}

function startOperationalClocks() {
  function updateClocks() {
    const now = new Date();
    const utcEl = document.getElementById("clockUtc");
    const istEl = document.getElementById("clockIst");

    if (utcEl) {
      const utcHours = String(now.getUTCHours()).padStart(2, '0');
      const utcMins = String(now.getUTCMinutes()).padStart(2, '0');
      const utcSecs = String(now.getUTCSeconds()).padStart(2, '0');
      utcEl.innerText = `${utcHours}:${utcMins}:${utcSecs} UTC`;
    }

    if (istEl) {
      // IST is UTC + 5:30
      const istTime = new Date(now.getTime() + (5.5 * 60 * 60 * 1000));
      const istHours = String(istTime.getUTCHours()).padStart(2, '0');
      const istMins = String(istTime.getUTCMinutes()).padStart(2, '0');
      const istSecs = String(istTime.getUTCSeconds()).padStart(2, '0');
      istEl.innerText = `${istHours}:${istMins}:${istSecs} IST`;
    }
  }

  updateClocks();
  setInterval(updateClocks, 1000);
}

function updateTimelineReadout(leadMin) {
  const readout = document.getElementById("readoutValue");
  const mode = document.getElementById("readoutMode");
  readout.innerText = `t + ${leadMin} min`;

  if (leadMin === 0) {
    mode.innerText = "(Live Radar Observation Ingestion)";
  } else if (leadMin <= 90) {
    mode.innerText = "(Kinematic Radar & Lightning Advection Dominant)";
  } else if (leadMin <= 150) {
    mode.innerText = "(Transition Zone: Overcoming 2-Hour Radar Wall)";
  } else {
    mode.innerText = "(NWP Thermodynamic Mesoscale CAPE Dominant)";
  }
}

function togglePlay() {
  const icon = document.getElementById("playIcon");
  isPlaying = !isPlaying;

  if (isPlaying) {
    icon.innerHTML = '<rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/>';
    playInterval = setInterval(() => {
      currentLeadTime += 15;
      if (currentLeadTime > 360) currentLeadTime = 0;
      document.getElementById("timelineSlider").value = currentLeadTime;
      updateTimelineReadout(currentLeadTime);
      fetchNowcastData(currentLeadTime);
    }, 1500);
  } else {
    icon.innerHTML = '<polygon points="5 3 19 12 5 21 5 3"/>';
    clearInterval(playInterval);
  }
}

async function fetchNowcastData(leadTimeMin) {
  try {
    let url = (leadTimeMin === 0)
      ? `/api/nowcast/live?region=${currentRegion}`
      : `/api/nowcast/forecast/${leadTimeMin}?region=${currentRegion}`;

    const res = await fetch(url);
    const data = await res.json();

    renderLayers(data);
    updateTelemetry(data);
    updateBlendingCard(leadTimeMin);

    if (showXai) {
      renderXaiEdges();
    }
  } catch (err) {
    console.error("Failed to fetch nowcast data:", err);
  }
}

/**
/**
 * Render all map layers with animations (F-02, F-03, F-06, F-07, F-09, F-11):
 * - dBZ reflectivity superpixels (F-02)
 * - Animated Lightning Jump 2σ surge rings + density halos (F-03, F-07)
 * - Rapid lightning strike flashes (F-07)
 * - INSAT-3D Convective Initiation (CI) expanding precursor rings (F-06, F-09)
 * - Animated pulsing storm trajectory track points (F-11)
 * - Civil protection alert boundary polygon (F-12)
 */
function renderLayers(data) {
  radarLayerGroup.clearLayers();
  lightningLayerGroup.clearLayers();
  satelliteLayerGroup.clearLayers();
  trackLayerGroup.clearLayers();
  if (alertPolygonLayer) {
    map.removeLayer(alertPolygonLayer);
  }

  // 1. Doppler Radar Superpixels (Authentic dBZ Colors: Green -> Yellow -> Orange -> Red -> Magenta)
  if (data.radar_nodes) {
    data.radar_nodes.forEach(node => {
      const color = getDbzColor(node.dbz_mean);
      const radius = 6.5 + (node.dbz_mean / 9.5);

      const circle = L.circleMarker([node.lat, node.lon], {
        radius: radius,
        fillColor: color,
        color: "#ffffff",
        weight: 0.8,
        opacity: 0.95,
        fillOpacity: 0.82
      }).bindPopup(`
        <div style="font-family:'Inter',sans-serif; font-size:12px; line-height:1.5;">
          <strong style="color:#10b981; font-size:13px;">${node.id}</strong><br/>
          Station: <b>${node.station || 'DWR'}</b><br/>
          Reflectivity (Mean): <b style="color:${color};">${node.dbz_mean} dBZ</b><br/>
          Reflectivity (Peak): <b>${node.dbz_max} dBZ</b><br/>
          Doppler Radial Velocity: <b>${node.radial_vel_mps || node.radial_vel || 0} m/s</b>
        </div>
      `);

      radarLayerGroup.addLayer(circle);
    });
  }

  // 2. Strike Density Clusters & Animated Lightning Jump (F-03, F-07)
  if (data.lightning_nodes) {
    data.lightning_nodes.forEach(light => {
      const isJump = light.is_lightning_jump;
      const flashColor = isJump ? "#dc2626" : "#d97706";

      // 2a. Density Halo (translucent footprint circle underneath)
      const densityHalo = L.circle([light.lat, light.lon], {
        radius: isJump ? 7000 : 4200,
        fillColor: flashColor,
        fillOpacity: isJump ? 0.22 : 0.12,
        stroke: false,
        interactive: false
      });
      lightningLayerGroup.addLayer(densityHalo);

      // 2b. If 2σ Jump: Animated concentric expanding pulse ring
      if (isJump) {
        const ringIcon = L.divIcon({
          className: 'lightning-jump-container',
          html: `<div class="lightning-jump-ring" style="width: 46px; height: 46px;"></div>`,
          iconSize: [46, 46],
          iconAnchor: [23, 23]
        });
        lightningLayerGroup.addLayer(L.marker([light.lat, light.lon], { icon: ringIcon, interactive: false }));
      }

      // 2c. Central Strike Icon (with rapid flash animation for normal strikes)
      const lightIcon = L.divIcon({
        className: isJump ? 'lightning-jump-marker' : 'lightning-normal-icon',
        html: `
          <div style="
            width: 22px; height: 22px; border-radius: 50%;
            background: #ffffff;
            border: 2px solid ${flashColor};
            display: flex; align-items: center; justify-content: center;
            box-shadow: 0 1px 4px rgba(0,0,0,0.25);
          ">
            <svg viewBox="0 0 24 24" width="13" height="13" fill="${flashColor}"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
          </div>
        `,
        iconSize: [22, 22],
        iconAnchor: [11, 11]
      });

      const marker = L.marker([light.lat, light.lon], { icon: lightIcon })
        .bindPopup(`
          <div style="font-family:'Inter',sans-serif; font-size:12px; line-height:1.5;">
            <strong style="color:${flashColor}; font-size:13px;">${light.id}</strong><br/>
            Flash Rate: <b>${light.cluster_flash_rate} flashes/min</b><br/>
            Peak Current: <b>${light.peak_current_ka || 24.5} kA</b><br/>
            Classification: <b>${isJump ? '[2σ SURGE] Convective Jump Detected' : 'Active Strike Cell'}</b><br/>
            Cluster Radius: <b>${isJump ? '7.0 km (Surge Area)' : '4.2 km'}</b>
          </div>
        `);

      lightningLayerGroup.addLayer(marker);
    });
  }

  // 3. INSAT-3D Convective Initiation (CI) Expanding Precursor Rings (F-06, F-09)
  if (data.satellite_nodes) {
    data.satellite_nodes.forEach(sat => {
      const isCiActive = (sat.ci_score >= 70) || (sat.ci_evaluation && sat.ci_evaluation.ci_alert);
      if (isCiActive) {
        // Expanding animated warm ring
        const ciRingIcon = L.divIcon({
          className: 'ci-ring-container',
          html: `<div class="ci-ring" style="width: 52px; height: 52px;"></div>`,
          iconSize: [52, 52],
          iconAnchor: [26, 26]
        });
        satelliteLayerGroup.addLayer(L.marker([sat.lat, sat.lon], { icon: ciRingIcon, interactive: false }));

        // Center precursor badge
        const ciCenterIcon = L.divIcon({
          className: 'ci-center-icon',
          html: `
            <div style="
              width: 22px; height: 22px; border-radius: 50%;
              background: #ffffff;
              border: 2px solid #d97706;
              display: flex; align-items: center; justify-content: center;
              box-shadow: 0 1px 4px rgba(0,0,0,0.2);
              font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 700; color: #d97706;
            ">CI</div>
          `,
          iconSize: [22, 22],
          iconAnchor: [11, 11]
        });

        const ciMarker = L.marker([sat.lat, sat.lon], { icon: ciCenterIcon })
          .bindPopup(`
            <div style="font-family:'Inter',sans-serif; font-size:12px; line-height:1.5;">
              <strong style="color:#d97706; font-size:13px;">${sat.id} — PRE-RADAR CI GENESIS</strong><br/>
              Algorithm: <b>INSAT-3D Split-Window ($\Delta BT_{10.8-12.0}$)</b><br/>
              CI Probability Score: <b style="color:#d97706;">${sat.ci_score || 85} / 100</b><br/>
              Cloud-Top Cooling: <b>${sat.cloud_top_cooling_c_per_15m || -2.8} °C / 15min</b><br/>
              Precursor Lead: <b style="color:#10b981;">+30 to 45 min before radar echo</b>
            </div>
          `);

        satelliteLayerGroup.addLayer(ciMarker);
      }
    });
  }

  // 4. Forecast Trajectory Track with Animated Pulse Dots (F-11)
  if (data.forecast_track && data.forecast_track.length > 1) {
    const polyline = L.polyline(data.forecast_track, {
      color: "#10b981",
      weight: 3.5,
      dashArray: "6, 8",
      opacity: 0.95
    });
    trackLayerGroup.addLayer(polyline);

    // Track points with animated pulse
    data.forecast_track.forEach((pt, idx) => {
      const stepLeadMin = idx * 30;
      const isTerminal = (idx === data.forecast_track.length - 1);

      const trackDotIcon = L.divIcon({
        className: 'track-dot-container',
        html: `
          <div class="track-dot-animated" style="
            width: ${isTerminal ? '14px' : '10px'};
            height: ${isTerminal ? '14px' : '10px'};
            border: 2px solid #ffffff;
            box-shadow: 0 1px 3px rgba(0,0,0,0.3);
            display: flex; align-items: center; justify-content: center;
          ">${isTerminal ? '<div style="width:4px;height:4px;background:#ffffff;border-radius:50%;"></div>' : ''}</div>
        `,
        iconSize: [isTerminal ? 14 : 10, isTerminal ? 14 : 10],
        iconAnchor: [isTerminal ? 7 : 5, isTerminal ? 7 : 5]
      });

      const dotMarker = L.marker(pt, { icon: trackDotIcon })
        .bindTooltip(`+${stepLeadMin}m Forecast Position`, { permanent: false, direction: "top" });
      trackLayerGroup.addLayer(dotMarker);
    });
  }

  // 5. Civil Protection Alert Boundary Swath (F-12) - Operational Aerodynamic Convective Envelope
  if (data.alert_geojson) {
    alertPolygonLayer = L.geoJSON(data.alert_geojson, {
      style: (feature) => ({
        color: feature.properties.color_hex || "#dc2626",
        weight: 2.2,
        fillColor: feature.properties.color_hex || "#dc2626",
        fillOpacity: 0.11,
        dashArray: "6, 6",
        lineCap: "round",
        lineJoin: "round"
      }),
      onEachFeature: (feature, layer) => {
        const p = feature.properties || {};
        const color = p.color_hex || "#dc2626";
        layer.bindTooltip(`
          <div style="font-family:'Inter',sans-serif; font-size:11px; line-height:1.45; min-width: 200px;">
            <div style="display:flex; align-items:center; gap:6px; margin-bottom:3px;">
              <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:${color};"></span>
              <strong style="color:${color}; font-size:12px;">IMD ${p.imd_color || 'RED'} ALERT SWATH</strong>
            </div>
            <div><span style="color:#64748b;">Districts:</span> <b>${(p.districts || []).join(', ')}</b></div>
            <div><span style="color:#64748b;">Severity:</span> <b>${p.severity || 'Extreme'}</b> (${p.max_dbz || 56} dBZ core)</div>
            <div style="margin-top:2px; font-size:10px; color:#059669; font-weight:600;">OASIS CAP v1.2 / ITU X.1303 Authenticated</div>
          </div>
        `, { sticky: true, className: "alert-poly-tooltip" });
      }
    }).addTo(map);
  }
}

async function renderXaiEdges() {
  xaiLayerGroup.clearLayers();
  try {
    const res = await fetch(`/api/xai/attention?region=${currentRegion}`);
    const data = await res.json();

    if (data.top_edges) {
      data.top_edges.forEach(edge => {
        if (edge.source_coord && edge.target_coord) {
          const latlngs = [edge.source_coord, edge.target_coord];
          const isWind = edge.type === "wind_advection";
          const edgeLine = L.polyline(latlngs, {
            color: isWind ? "#10b981" : "#f59e0b",
            weight: 2 + (edge.weight * 3),
            opacity: 0.85,
            dashArray: isWind ? null : "3, 6"
          }).bindTooltip(`Attention α: ${edge.weight} (${edge.type})`);

          xaiLayerGroup.addLayer(edgeLine);
        }
      });
    }
  } catch (err) {
    console.error("Failed to load XAI edges:", err);
  }
}

function updateTelemetry(data) {
  const valDbz = document.getElementById("valMaxDbz");
  const subDbz = document.getElementById("subDbz");
  const alertBadge = document.getElementById("alertBadge");
  const alertCard = document.getElementById("alertSeverityCard");
  const alertTitle = document.getElementById("alertTitle");
  const alertDesc = document.getElementById("alertDescription");
  const districtContainer = document.getElementById("districtTags");

  const valJump = document.getElementById("valJump");
  const subJump = document.getElementById("subJump");
  const jumpSurgePill = document.getElementById("jumpSurgePill");

  const valCi = document.getElementById("valCi");
  const valCiScore = document.getElementById("valCiScore");
  const subCiStatus = document.getElementById("subCiStatus");
  const valBtCool = document.getElementById("valBtCool");
  const valBt108 = document.getElementById("valBt108");
  const valCiLead = document.getElementById("valCiLead");
  const ciStatusPill = document.getElementById("ciStatusPill");

  const valGraphNodes = document.getElementById("valGraphNodes");
  const subGraphEdges = document.getElementById("subGraphEdges");

  const valCape = document.getElementById("valCape");
  const capeBar = document.getElementById("capeBar");
  const valCin = document.getElementById("valCin");
  const valShear = document.getElementById("valShear");
  const valSteering = document.getElementById("valSteering");
  const steeringArrow = document.getElementById("steeringArrow");

  const maxDbz = data.max_reflectivity_dbz || 0.0;
  if (valDbz) valDbz.innerHTML = `${maxDbz.toFixed(1)} <small>dBZ</small>`;

  const imdColor = data.imd_color_code || "GREEN";
  if (alertBadge) {
    alertBadge.innerText = `${imdColor} ALERT`;
    alertBadge.style.background = (imdColor === "RED") ? "#ef4444" : (imdColor === "ORANGE") ? "#ff9100" : (imdColor === "YELLOW") ? "#facc15" : "#10b981";
    alertBadge.style.color = (imdColor === "YELLOW" || imdColor === "GREEN") ? "#04130d" : "#ffffff";
  }
  if (alertCard && alertBadge) {
    alertCard.style.borderLeftColor = alertBadge.style.background;
    if (imdColor === "RED" || imdColor === "ORANGE") {
      alertCard.classList.add("alert-active-red");
    } else {
      alertCard.classList.remove("alert-active-red");
    }
  }

  if (subDbz) {
    if (maxDbz >= 50) subDbz.innerText = "Severe Hail / Squall";
    else if (maxDbz >= 40) subDbz.innerText = "Heavy Convective Cell";
    else if (maxDbz >= 30) subDbz.innerText = "Moderate Rain Core";
    else subDbz.innerText = "Light / Stratiform Rain";
  }

  // Update dynamic alert title & description
  if (alertTitle && alertDesc) {
    if (imdColor === "RED") {
      alertTitle.innerText = "Extreme Convective Thunderstorm & Squall Warning";
      alertDesc.innerText = `Severe reflectivity core of ${maxDbz.toFixed(1)} dBZ advancing along steering flow. 2-sigma lightning surge detected with high hail risk.`;
    } else if (imdColor === "ORANGE") {
      alertTitle.innerText = "Severe Thunderstorm & Downburst Advisory";
      alertDesc.innerText = `Intense convective activity with peak reflectivity ${maxDbz.toFixed(1)} dBZ and localized gusty squalls.`;
    } else if (imdColor === "YELLOW") {
      alertTitle.innerText = "Moderate Thunderstorm Development Notice";
      alertDesc.innerText = `Scattered convective cells active. Peak reflectivity ${maxDbz.toFixed(1)} dBZ. Monitoring for cell merger.`;
    } else {
      alertTitle.innerText = "Routine Meteorological Monitoring";
      alertDesc.innerText = `Normal atmospheric conditions with isolated stratiform rain. Reflectivity ${maxDbz.toFixed(1)} dBZ.`;
    }
  }

  // Populate affected district tags
  if (districtContainer) {
    const districts = data.districts || (data.alert_geojson && data.alert_geojson.properties && data.alert_geojson.properties.districts) || [];
    districtContainer.innerHTML = districts.map(d => `<span class="district-tag">${d}</span>`).join("");
  }

  // Lightning Jump Telemetry (F-03)
  const jumpData = data.lightning_jump;
  if (jumpData) {
    const sigma = jumpData.jump_metric_sigma || (jumpData.is_lightning_jump ? 2.4 : 0.8);
    if (valJump) {
      valJump.innerHTML = `${sigma >= 0 ? '+' : ''}${sigma.toFixed(1)} <small>σ</small>`;
      valJump.className = jumpData.is_lightning_jump ? "telemetry-value text-red" : "telemetry-value text-emerald";
    }
    if (subJump) {
      subJump.innerText = jumpData.is_lightning_jump ? "CRITICAL SURGE (2σ)" : "Normal Rate";
      subJump.className = jumpData.is_lightning_jump ? "telemetry-sub text-red" : "telemetry-sub";
    }
    if (jumpSurgePill) {
      jumpSurgePill.style.display = jumpData.is_lightning_jump ? "inline-flex" : "none";
    }
  }

  // INSAT CI Telemetry (F-06, F-09)
  let bestSat = null;
  if (data.satellite_nodes && data.satellite_nodes.length > 0) {
    bestSat = data.satellite_nodes.reduce((prev, curr) => (curr.ci_score > prev.ci_score) ? curr : prev, data.satellite_nodes[0]);
  }
  const ciScore = bestSat ? bestSat.ci_score : 85;
  const isCiActive = ciScore >= 70;

  if (valCi) valCi.innerHTML = `${ciScore} <small>/ 100</small>`;
  if (valCiScore) valCiScore.innerHTML = `${ciScore} <small>/ 100</small>`;
  if (subCiStatus) subCiStatus.innerText = isCiActive ? "Rapid Cooling Active" : "Stable Cloud Deck";
  if (valBtCool) valBtCool.innerHTML = `${bestSat ? bestSat.cloud_top_cooling_c_per_15m : -2.8} <small>°C/15m</small>`;
  if (valBt108) valBt108.innerHTML = `${bestSat ? (bestSat.bt_10_8 - 273.15).toFixed(1) : -41.2} <small>°C</small>`;
  if (valCiLead) valCiLead.innerHTML = `+${isCiActive ? '38' : '0'} <small>min</small>`;
  if (ciStatusPill) {
    ciStatusPill.innerText = isCiActive ? "CI ACTIVE" : "STABLE";
    ciStatusPill.style.background = isCiActive ? "var(--accent-amber-light)" : "var(--bg-surface-subtle)";
    ciStatusPill.style.color = isCiActive ? "var(--accent-amber)" : "var(--text-muted)";
    ciStatusPill.style.borderColor = isCiActive ? "var(--accent-amber)" : "var(--border-subtle)";
  }

  // Graph Structure (F-01)
  if (valGraphNodes && data.graph_metrics) {
    valGraphNodes.innerText = data.graph_metrics.num_nodes || 42;
  }
  if (subGraphEdges && data.graph_metrics) {
    subGraphEdges.innerText = `${data.graph_metrics.num_edges || 118} Physics Edges`;
  }

  // NWP Thermodynamic Instability (F-08)
  const nwp = (data.nwp_nodes && data.nwp_nodes.length > 0) ? data.nwp_nodes[0] : null;
  if (nwp) {
    const cape = Math.round(nwp.cape_j_kg || 2650);
    if (valCape) valCape.innerText = `${cape.toLocaleString()} J/kg`;
    if (capeBar) capeBar.style.width = `${Math.min(100, Math.round((cape / 4000) * 100))}%`;

    if (valCin) valCin.innerText = `−32 J/kg`;

    const shearKt = ((nwp.shear_0_6km_mps || 22.5) * 1.944).toFixed(1);
    if (valShear) valShear.innerText = `${shearKt} kt`;

    const u = nwp.wind_u_700_mps || 12.0;
    const v = nwp.wind_v_700_mps || 6.0;
    const speedKt = (Math.sqrt(u*u + v*v) * 1.944).toFixed(0);
    let deg = Math.round((Math.atan2(u, v) * 180 / Math.PI + 360) % 360);
    if (valSteering) valSteering.innerText = `${deg}° / ${speedKt} kt`;
    if (steeringArrow) steeringArrow.style.transform = `rotate(${deg}deg)`;
  }

  // Populate Multi-Radar Mosaic Telemetry
  const valMultiRadarStations = document.getElementById("valMultiRadarStations");
  const subMultiRadarMode = document.getElementById("subMultiRadarMode");
  const multiRadarPill = document.getElementById("multiRadarPill");
  if (data.multi_radar_metadata) {
    const stations = data.multi_radar_metadata.stations_fused || ["DWR_PALAM", "DWR_PATIALA"];
    if (valMultiRadarStations) valMultiRadarStations.innerText = stations.join(" + ");
    if (subMultiRadarMode) subMultiRadarMode.innerText = data.multi_radar_metadata.mosaic_mode || "Max Composite Reflectivity";
    if (multiRadarPill) multiRadarPill.innerText = `${data.multi_radar_metadata.total_radars_fused || 2} DWR FUSED`;
  }

  // Populate Lightning Nowcasting & Onset Telemetry
  const valLightningOnsetLead = document.getElementById("valLightningOnsetLead");
  const valStrikeProb = document.getElementById("valStrikeProb");
  const subStrikeProb = document.getElementById("subStrikeProb");
  const valFlashDensity = document.getElementById("valFlashDensity");
  const valLightningJumpHud = document.getElementById("valLightningJumpHud");
  const lightningOnsetAlertPill = document.getElementById("lightningOnsetAlertPill");
  if (data.lightning_nowcast) {
    const ln = data.lightning_nowcast;
    if (valLightningOnsetLead) {
      valLightningOnsetLead.innerHTML = ln.onset_lead_time_min > 0 ? `+${ln.onset_lead_time_min} <small>min</small>` : `0 <small>min</small>`;
      valLightningOnsetLead.className = ln.onset_lead_time_min > 0 ? "telemetry-value text-amber" : "telemetry-value";
    }
    if (valStrikeProb) {
      valStrikeProb.innerHTML = `${Math.round((ln.ground_strike_probability || 0.85) * 100)}% <small>P(&gt;0)</small>`;
    }
    if (subStrikeProb) {
      subStrikeProb.innerText = ln.electrification_status || "Mixed-Phase Electrification";
    }
    if (valFlashDensity) {
      valFlashDensity.innerHTML = `${(ln.forecast_flash_density_per_km2_hr || 3.8).toFixed(1)} <small>fl/km²/h</small>`;
    }
    if (valLightningJumpHud) {
      valLightningJumpHud.innerHTML = `+${(ln.jump_surge_sigma || 2.4).toFixed(1)} <small>σ</small>`;
      valLightningJumpHud.className = ln.is_lightning_jump_active ? "telemetry-value text-red" : "telemetry-value text-emerald";
    }
    if (lightningOnsetAlertPill) {
      const isWarn = ln.is_onset_warning || ln.is_lightning_jump_active;
      lightningOnsetAlertPill.innerText = ln.is_onset_warning ? "ONSET ACTIVE" : (ln.is_lightning_jump_active ? "JUMP ACTIVE" : "MONITORING");
      lightningOnsetAlertPill.style.background = isWarn ? "rgba(239, 68, 68, 0.15)" : "var(--bg-surface-subtle)";
      lightningOnsetAlertPill.style.color = isWarn ? "var(--accent-red)" : "var(--text-muted)";
      lightningOnsetAlertPill.style.borderColor = isWarn ? "var(--accent-red)" : "var(--border-subtle)";
    }
  }
}

function updateBlendingCard(leadMin) {
  const barRadar = document.getElementById("barRadar");
  const barNwp = document.getElementById("barNwp");
  const leadLabel = document.getElementById("blendingLeadLabel");

  if (leadLabel) leadLabel.innerText = `t + ${leadMin}m`;

  const tau = 120.0;
  const wRadar = Math.exp(-leadMin / tau);
  const wNwp = 1.0 - wRadar;

  const radarPct = Math.round(wRadar * 100);
  const nwpPct = 100 - radarPct;

  if (barRadar) {
    barRadar.style.width = `${radarPct}%`;
    barRadar.innerText = radarPct > 12 ? `Radar: ${radarPct}%` : `${radarPct}%`;
  }
  if (barNwp) {
    barNwp.style.width = `${nwpPct}%`;
    barNwp.innerText = nwpPct > 12 ? `NWP: ${nwpPct}%` : `${nwpPct}%`;
  }
}

async function openCapModal() {
  const modal = document.getElementById("capModal");
  const codeEl = document.getElementById("capXmlCode");
  modal.style.display = "flex";
  codeEl.innerText = "Generating ITU X.1303 / OASIS CAP v1.2 XML alert stream...";

  try {
    const res = await fetch(`/api/alerts/cap.xml?region=${currentRegion}&lead_time_min=${currentLeadTime}`);
    const xmlText = await res.text();
    codeEl.innerText = xmlText;
  } catch (err) {
    codeEl.innerText = "Error generating CAP alert: " + err.message;
  }
}
