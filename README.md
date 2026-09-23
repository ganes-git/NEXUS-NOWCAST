# NEXUS-NOWCAST

An automated meteorological intelligence system that predicts the formation, trajectory, and severity of severe thunderstorms and lightning strikes up to 6 hours in advance by unifying multi-radar networks, geostationary satellite feeds, real-time lightning detection sensors, and numerical weather prediction models into a physics-constrained graph neural network.

---

## Smart India Hackathon (SIH 2026) Alignment

- **Problem Statement ID**: SIH26072
- **Official Problem Statement Title**: *"AIML based Nowcasting of thunderstorm and lightning using atmospheric observation including multiple radars, satellite, lightning and model data."*
- **Sponsoring Organization**: Ministry of Earth Sciences (MoES) / India Meteorological Department (IMD)
- **Theme**: Disaster Management
- **Category**: Software
- **Team Name**: NEXUS-NOWCAST

---

## Problem & Solution Summary

Thunderstorms, squall lines, downbursts, and cloud-to-ground lightning claim over 2,500 lives annually in India. Operational nowcasting (short-term forecasting from 0 to 6 hours) faces major challenges: storm cells rapidly initiate, split, and dissipate non-linearly; radar extrapolation collapses after 90–120 minutes; observational sensors operate asynchronously; and standard NWP models cannot resolve fast-moving convective cells at sub-kilometer scales.

**NEXUS-NOWCAST** solves this with **STGAT-PIE** (Spatio-Temporal Graph Attention Network with Physics-Informed Edges):
- **Heterogeneous Atmospheric Graph**: Ingests multi-radar Doppler sweeps, INSAT-3D/3DR multispectral thermal channels, and lightning sensor feeds at native physical coordinates without lossy grid interpolation.
- **Dynamic 0–6 Hour Lead-Time Blending**: Seamlessly transitions weight from high-resolution radar dynamics ($W_{\text{radar}} = \exp(-\Delta t / 120\text{min})$) to synoptic NWP thermodynamic forcing across the 0–360 min forecast window.
- **Early Genesis Detection**: Evaluates INSAT-3D split-window brightness temperature differences ($BT_{10.8} - BT_{12.0} < 0$) and rapid cooling rates to detect convective updrafts **30–45 minutes before radar echoes form**.
- **Dual-Aspect Lightning Forecasting**: Predicts 1 km strike probability fields (15–45 min pre-strike warning) and computes a $2\sigma$ Lightning Jump metric for severe downdraft alerts.
- **Automated Civil Dissemination**: Produces court-admissible ITU-T X.1303 / NDMA CAP v1.2 XML alert streams with SHA-256 digital seals for direct ingestion by NDMA *Sachet* and IMD *Damini*.

---

## Key Differentiators

| Capability / Feature | Conventional Systems | NEXUS-NOWCAST |
| :--- | :--- | :--- |
| **Observation Ingestion** | 2D raster grids with spatial interpolation artifacts | **Heterogeneous Graph (HGC)** preserving native sensor coordinates |
| **Forecast Horizon** | Linear extrapolation failing past 90 min | **Exponential Radar-NWP Blending** bridging 0 to 6 hours |
| **Pre-Genesis Detection** | Only triggers after radar reflectivity forms (>35 dBZ) | **Satellite Split-Window Precursor** 30–45 min before radar echo |
| **Lightning Warning** | Post-strike lightning presence detection | **Pre-strike onset probability** + **$2\sigma$ Lightning Jump** |
| **Dissemination Format** | Proprietary logs or custom JSON | **ITU-T X.1303 / NDMA CAP v1.2 XML** with digital seal |
| **Interpretability** | Black-box neural activations | **GATv2 Attention Maps** highlighting steering wind corridors |

---

## Technology Stack

- **Backend**: Python 3.10+, FastAPI, Uvicorn, Pydantic v2
- **Machine Learning & Graph Processing**: PyTorch, PyTorch Geometric, NetworkX, NumPy, SciPy
- **Frontend**: HTML5, Vanilla CSS3 (Tactical C2 Mission Control Dark Theme), Leaflet.js
- **Civil Alert Standards**: ITU-T X.1303 / OASIS CAP v1.2 XML, GeoJSON (WGS84)

---

## Quickstart & Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/ganes-git/NEXUS-NOWCAST.git
cd NEXUS-NOWCAST
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch Mission Control Server
```bash
python run_server.py
```
*(Or run `uvicorn backend.main:app --port 8000 --reload`)*

### 4. Access the Application
Open your web browser and navigate to:
```
http://127.0.0.1:8000
```

- **Interactive Timeline**: Scrub from T+0 to T+360 minutes to view dynamic radar-NWP nowcast transitions.
- **Explainable AI (XAI)**: Toggle GAT attention edge overlays to inspect cross-sensor physical correlations.
- **Disaster CAP XML**: View and export live NDMA CAP v1.2 XML payloads.
- **Corridor Switching**: Toggle between Delhi NCR, Kolkata Bay, Chennai Coast, and Mumbai Coastal zones.

---

## System Architecture

```text
 ┌────────────────────────────────────────────────────────────────────────┐
 │                    1. MULTI-SENSOR INGESTION LAYER                     │
 ├────────────────┬─────────────────┬───────────────────┬────────────────┤
 │   37 IMD DWR   │  INSAT-3D / 3DR │   Lightning Net   │    NWP GFS/WRF │
 │ Doppler Radars │ Satellite Multispec│ Sensor Point Data │ Thermodynamics │
 │  (dBZ, Vr, σv) │ (10.8µ, 12µ, 6.7µ)│ (Flash Rate, DBSCAN)│ (CAPE, CIN, V700)│
 └───────┬────────┴────────┬────────┴─────────┬─────────┴────────┬───────┘
         │                 │                  │                  │
         ▼                 ▼                  ▼                  ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │            2. HETEROGENEOUS GRAPH CONSTRUCTOR (HGC)                    │
 │ • SLIC radar superpixels with 3D beam height geometry compensation     │
 │ • Convective cloud ROI extraction via adaptive thermal thresholding    │
 │ • Rolling DBSCAN strike clustering (ε = 12 km, min_pts = 3)            │
 │ • Physics-Informed Edges: 700 hPa Wind Advection + CAPE Gradients     │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                  3. STGAT-PIE AI NOWCASTING CORE                       │
 │ • Dynamic GATv2 cross-attention across heterogeneous sensor nodes       │
 │ • GConvGRU spatio-temporal recurrent memory over 12 history timesteps  │
 │ • Physics Advection Loss penalizing non-physical cell displacements    │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │            4. DYNAMIC 0–6 HOUR LEAD-TIME BLENDING ENGINE               │
 │ • W_radar(t) = exp(-t / 120 min)  |  W_nwp(t) = 1 - W_radar(t)        │
 │ • Smoothly bridges high-resolution advection (0-90m) to NWP (3-6h)     │
 └───────────────────┬───────────────────────────────┬────────────────────┘
                     │                               │
                     ▼                               ▼
       ┌───────────────────────────┐   ┌───────────────────────────┐
       │   HEAD A: THUNDERSTORM    │   │     HEAD B: LIGHTNING     │
       │ • 0-6h dBZ Reflectivity   │   │ • 1km Strike Probability  │
       │ • IMD 4-Color Severity    │   │ • Pre-Strike Onset (15-45m)│
       │ • Centroid Trajectory     │   │ • 2σ Lightning Jump Alert │
       └─────────────┬─────────────┘   └─────────────┬─────────────┘
                     └───────────────┬───────────────┘
                                     │
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                   5. CIVIL DISSEMINATION & OUTPUT                      │
 │ • Automated ITU-T X.1303 / NDMA CAP v1.2 XML Early Warning Feeds       │
 │ • Direct machine-to-machine integration for NDMA Sachet & IMD Damini   │
 │ • Tactical Mission Control C2 HUD with timeline scrub and XAI overlays │
 └────────────────────────────────────────────────────────────────────────┘
```

---

## Team Members

| # | Name | Role | Institutional Email |
| :---: | :--- | :--- | :--- |
| 1 | Ganesh S | Team Lead | 25ec034@rmd.ac.in |
| 2 | Hemavarshini M | | 25ec050@rmd.ac.in |
| 3 | Deepika N | | 25ec020@rmd.ac.in |
| 4 | Kavi Vadhana R | | 25ec071@rmd.ac.in |
| 5 | Harshitha R | | 25ec047@rmd.ac.in |
| 6 | Khavyaa D | | 25ec078@rmd.ac.in |

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
