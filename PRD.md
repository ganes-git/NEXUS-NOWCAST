# Product Requirements Document (PRD)
## NEXUS-NOWCAST: AI/ML-Powered Multi-Sensor Thunderstorm & Lightning Nowcasting System
**SIH 2026 Problem Statement ID**: SIH26072  
**Theme**: Disaster Management  
**Sponsoring Agency**: Ministry of Earth Sciences (MoES) / India Meteorological Department (IMD)  
**Version**: 2.0 (Competition & Operational Specification)

---

## 1. Problem Definition & Strategic Objectives

### 1.1 Background
Thunderstorms, squall lines, downbursts, and cloud-to-ground lightning represent India’s deadliest meteorological hazards, claiming over 2,500 lives annually (predominantly agricultural workers, rural dwellers, and construction laborers). Lightning-related casualties alone outnumber deaths from floods and cyclones combined in most years.

Operational nowcasting (short-term forecasting from 0 to 6 hours) faces severe systemic hurdles:
1. **The 2-Hour Radar Advection Wall**: Current Doppler Weather Radar (DWR) extrapolation techniques (e.g., TITAN, TREC, WDSS-II) treat storm cells as semi-rigid advected objects. Beyond 90–120 minutes, cells dynamically initiate, split, merge, and collapse, rendering linear extrapolation useless.
2. **Multi-Source Asynchrony**: India possesses 37+ operational DWR stations (10-minute polar volume scans), INSAT-3D/3DR geostationary satellites (15–30 min multispectral imagery), Indian Lightning Detection Networks (real-time point streams), and Numerical Weather Prediction (GFS/WRF models updated every 6 hours). No unified operational pipeline currently ingests all four streams into a single spatiotemporal AI engine.
3. **Failure of "Pre-Genesis" Detection**: Conventional radar nowcasting only tracks clouds *after* precipitation particles have already grown large enough to reflect radar beams ($>30$ dBZ). This gives near-zero lead time for newly forming convective cells.
4. **Dissemination Format Mismatch**: Forecasters need analytical tools, while disaster authorities require standardized machine-readable warning streams (CAP XML) integrated into public mobile broadcast networks (NDMA *Sachet*).

### 1.2 Official Problem Statement Alignment
**Official Problem Statement (SIH26072)**:
> *"AIML based Nowcasting of thunderstorm and lightning using atmospheric observation including multiple radars, satellite, lightning and model data."*

**Theme**: Disaster Management | **Category**: Software | **Ministry**: Ministry of Earth Sciences (MoES)  
**Team Name**: NEXUS-NOWCAST | **Team ID**: SIH2026-NEXUS-72  
**Public Repository**: [GitHub: NEXUS-NOWCAST](https://github.com/ganes-git/SEMATIC-GARPAGE-COLLECTION) | **Demonstration Video**: [Video Walkthrough](https://youtu.be/nexus-nowcast-sih2026)  
**Sustainable Development Goals (SDGs)**:
- **SDG 11: Sustainable Cities and Communities (Target 11.5)** — Significantly reduce mortality and direct economic loss caused by extreme convective weather hazards and urban lightning squalls.
- **SDG 13: Climate Action (Target 13.1)** — Strengthen resilience and adaptive capacity to climate-induced severe thunderstorms and sudden convective lightning in vulnerable rural and agricultural zones.

### 1.3 Core Objectives
- Construct an end-to-end **AIML based** software platform utilizing **atmospheric observation** foundation data including **multiple radars** (mosaicking overlapping IMD DWR network stations), **INSAT satellite** imagery, **lightning** detection streams, and numerical **model data** (NWP thermodynamic fields).
- Deliver accurate **nowcasting of thunderstorm and lightning** across a **0 to 6 hour** lead time horizon at 15-minute intervals.
- Deliver dual-aspect **lightning nowcasting**: (1) Pre-strike onset warning (15–45 min lead time with 1km spatial strike probability field $P(\text{strike} > 0)$ and flash density) before cloud-to-ground strikes occur; (2) Operational 2-sigma Lightning Jump surge detection for severe microburst and squall escalation.
- Resolve multi-site radar challenges across **multiple radars**: handle beam blockage, differing beam elevations, cone-of-silence coverage gaps, and overlapping returns via dynamic cross-radar graph attention and maximum composite reflectivity.
- Incorporate operational meteorological mechanisms: **Dynamic Lead-Time Blending** ($W(t) = e^{-t/\tau}$ bridging multi-radar advection to NWP model data), **Convective Initiation Split-Window Detection**, and **Lightning Jump Algorithm**.
- Automatically generate **ITU-T X.1303 / NDMA CAP v1.2 XML** early warning feeds mapped to administrative districts with SHA-256 digital seals.

---

## 2. User Personas & Use Cases

### 2.1 Personas
1. **Dr. Arvind Sharma (IMD Lead Nowcaster / Duty Meteorologist)**:
   - *Goal*: Wants to interrogate the model's physical reasoning, see lead-time confidence, and review spatial attention before issuing high-impact public warnings.
   - *Pain Point*: Distrusts black-box CNNs; needs to know *why* a storm is forecast (e.g., strong CAPE gradient vs. radar advection).
2. **Pooja Deshmukh (SDMA Control Room Officer / Emergency Director)**:
   - *Goal*: Needs automated, geographically bounded alerts with explicit severity (Yellow/Orange/Red), lead time, and impacted district boundaries for cell broadcasts.
   - *Pain Point*: Receives fragmented raw meteorological charts that require manual interpretation during emergencies.
3. **District Field Emergency Services / Public**:
   - *Goal*: Timely, reliable sirens, SMS alerts, and app notifications (via *Damini* / *Sachet*) at least 30 minutes before severe lightning strikes or squalls occur.

---

## 3. Functional Requirements (R1 – R13 Traceability)

| ID | Requirement Statement | Priority | Operational Implementation in NEXUS-NOWCAST |
|---|---|---|---|
| **R1** | **AIML-based System**: The engine must leverage modern AI/ML architectures rather than purely empirical or static heuristics. | P0 (Mandatory) | Spatio-Temporal Graph Attention Network with Physics-Informed Edges (STGAT-PIE) with GATv2 and GConvGRU. |
| **R2** | **Thunderstorm Nowcasting (0–6 Hours)**: Output storm presence probability, dBZ reflectivity, and severity categories across a 0–360 min horizon. | P0 (Mandatory) | Dual-head decoder Head A outputs per-node reflectivity (dBZ) and categorical severity (Weak $<35$, Moderate $35-45$, Severe $>45$ dBZ). |
| **R3** | **Lightning Nowcasting (0–6 Hours)**: Output lightning strike probability density and flash rate evolution. | P0 (Mandatory) | Head B predicts flash density (flashes/$\text{km}^2$/hr) and triggers Lightning Jump alerts. |
| **R4** | **Atmospheric Observation Ingestion**: Ingest multi-modal real-time meteorological observations. | P0 (Mandatory) | Native HGC parser ingesting Doppler radar volume scans, satellite channels, lightning sensors, and NWP fields. |
| **R5** | **Multiple Radar Integration**: Support simultaneous multi-radar inputs without forcing coordinate reprojection into a rigid global pixel grid. | P0 (Mandatory) | Graph architecture treats each DWR station as an autonomous subgraph cluster linked by geographic distance and overlapping beam edges. |
| **R6** | **Satellite Data Integration**: Ingest INSAT-3D/3DR geostationary multispectral data (Thermal IR, Water Vapor, Visible). | P0 (Mandatory) | Satellite nodes represent convective cloud regions with cloud-top temperatures, $BT_{10.8}$, $BT_{12.0}$, and $BT_{6.7}$. |
| **R7** | **Lightning Data Integration**: Ingest real-time lightning detection sensor streams (lat, lon, peak current, polarity). | P0 (Mandatory) | Real-time strike events clustered via sliding-window DBSCAN into active storm electrical center nodes. |
| **R8** | **NWP Model Data Integration**: Ingest thermodynamic and kinematic fields from mesoscale NWP models (WRF / GFS). | P0 (Mandatory) | NWP grid nodes supply CAPE, CIN, 0–6km wind shear, and 700 hPa wind steering vectors as graph edge constraints. |
| **R9** | **Predict Onset (Convective Initiation)**: Identify storm genesis before significant radar echoes develop. | P0 (Mandatory) | INSAT-3D Split-Window Convective Initiation (CI) module calculating $BT_{10.8} - BT_{12.0}$ rapid cloud-top cooling ($<-1.5^\circ\text{C}/15\text{min}$). |
| **R10** | **Predict Intensity Evolution**: Predict whether storms will intensify, plateau, or dissipate. | P0 (Mandatory) | Multi-task loss combining Smooth L1 dBZ regression with Focal Loss for categorical severity classification. |
| **R11** | **Predict Trajectory & Movement**: Track cell centroid displacement over 6 hours. | P0 (Mandatory) | Vector displacement regression constrained by Physics-Informed Advection Consistency Loss ($\lambda \cdot \mathcal{L}_{\text{advection}}$). |
| **R12** | **Timely Early Warnings**: Issue actionable, standard disaster alerts. | P0 (Mandatory) | Automated ITU X.1303 / NDMA CAP v1.2 XML alert builder with GeoJSON district overlays and IMD color codes. |
| **R13** | **Pure Software Solution**: Prototype-ready software architecture runnable without dedicated proprietary hardware. | P0 (Mandatory) | Python-based microservice architecture (FastAPI backend + Leaflet.js frontend) deployable on standard cloud or edge servers. |

---

## 4. Operational Ingestion & Pipeline Specifications

### 4.1 Temporal Cadence & Ingestion Synchronization
Atmospheric observations arrive at disparate frequencies:
- **Radar (DWR)**: Every 10 minutes.
- **INSAT-3D Satellite**: Every 15–30 minutes.
- **Lightning Sensors**: Continuous streaming (sub-second timestamps).
- **NWP WRF/GFS**: Updated every 6 hours (with 1-hour forecast steps).

**Synchronization Strategy**:
The engine maintains a sliding **10-minute epoch buffer**:
- Lightning strikes in $[t-10\text{m}, t]$ are clustered via DBSCAN into strike centroid nodes.
- Radar scans are sampled at the latest available PPI/CAPPI volume scan.
- Satellite frames are forward-filled if the scan is within 30 minutes of $t$.
- NWP 700 hPa winds and CAPE fields are linearly interpolated to timestep $t$.

### 4.2 Dynamic Lead-Time Blending ($0 \to 6$ Hours)
To overcome the 2-Hour Radar Wall:
$$\text{Nowcast}(x, y, t + \Delta t) = W_{\text{radar}}(\Delta t) \cdot \hat{Y}_{\text{extrap}} + W_{\text{NWP}}(\Delta t) \cdot \hat{Y}_{\text{thermo}}$$
Where:
$$W_{\text{radar}}(\Delta t) = \exp\left(-\frac{\Delta t}{\tau}\right), \quad \tau = 120\text{ minutes}$$
$$W_{\text{NWP}}(\Delta t) = 1 - W_{\text{radar}}(\Delta t)$$
- At $\Delta t = 30\text{ min}$: Radar weight $\approx 78\%$, NWP weight $\approx 22\%$.
- At $\Delta t = 120\text{ min}$: Radar weight $\approx 37\%$, NWP weight $\approx 63\%$.
- At $\Delta t = 360\text{ min}$: Radar weight $< 5\%$, NWP weight $> 95\%$.

---

## 5. Non-Functional Requirements (NFR)

1. **Inference Latency**:
   - Total end-to-end execution (graph construction + STGAT inference + blending + alert generation) must complete in **$< 60$ seconds** on a standard GPU (NVIDIA T4 or equivalent) and **$< 5$ seconds** for pre-processed graph snapshots.
2. **Explainability & Transparency**:
   - The system must expose GAT attention weights ($\alpha_{ij}$) across graph edges so meteorologists can inspect which spatial features and physical forces drove the nowcast.
3. **Fault-Tolerant Offline Operation**:
   - If internet connectivity or live external APIs fail during a hackathon evaluation, the system must seamlessly fall back to an internal **Mock/Synthetic Replay Engine** providing continuous live simulation data.
4. **Compliance**:
   - Alert payloads must strictly validate against the **W3C XML Schema for Common Alerting Protocol v1.2** and follow NDMA guidelines for administrative district mapping.

---
*Signed off for SIH 2026 Competition Deployment*
