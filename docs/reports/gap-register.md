# Adversarial Gap Register: SIH 2026 Problem Statement SIH26072
### Rigorous Technical Audit & Vulnerability Assessment
**Reviewer Perspective**: Senior SIH Technical Jury Member & Devil's Advocate Atmospheric/ML Engineer  
**System Evaluated**: NEXUS-NOWCAST (STGAT-PIE AI Engine)  
**Corpus / Workspace**: `c:\Users\ganes\Desktop\PS72`  
**Date**: September 20, 2026

---

## 🔍 Executive Reviewer Summary

A critical, skeptical evaluation of the project's claims was conducted against the official Ministry of Earth Sciences (MoES) problem statement:
> *"AIML based Nowcasting of thunderstorm and lightning using atmospheric observation including multiple radars, satellite, lightning and model data."*

While the **STGAT-PIE** architecture is fundamentally superior to naive ConvLSTM grid baselines, several critical and moderate gaps exist between the theoretical documentation and operational reality. A sharp MoES/IMD judging panel would aggressively probe these vulnerabilities.

Gaps are categorized into:
- **Type (a) - PROTOTYPE Gap**: The documentation promises a capability, but the live prototype build currently substitutes an approximation, mock, or placeholder.
- **Type (b) - SOLUTION Gap**: A genuine architectural or meteorological vulnerability in the design itself, regardless of code implementation.

---

## 📋 Numbered Gap Register

| Gap ID | Description | Type | Severity | Threatens Requirement | Reviewer's Sceptical Critique ("The Judge's Trap") |
|---|---|---|---|---|---|
| **GAP-01** | **Synthetic Feeder vs. Live/Raw File Ingestion** | (a) PROTOTYPE | **Moderate** | **R4, R5, R6, R7, R8** | *"You built a slick dashboard, but where is your actual parser for IMD NetCDF/IRIS radar scans or MOSDAC HDF5 satellite granules? Can your backend ingest a real binary file right now, or only your clean mock arrays?"* |
| **GAP-02** | **Analytical Graph vs. Trained PyTorch Checkpoint Execution** | (a) PROTOTYPE | **Moderate** | **R1** | *"Your TRD describes GATv2 and GConvGRU equations, but your live FastAPI server executes an analytical NetworkX graph engine. Where is the actual `.pt` neural checkpoint inference running during this demo?"* |
| **GAP-03** | **Convective Initiation (CI) False Alarms from Cirrus Shields** | (b) SOLUTION | **Moderate** | **R9, R12** | *"Split-window $BT_{10.8} - BT_{12.0} < 0$ occurs over cold, non-precipitating, decaying cirrus clouds blown off from old storms. Without spatial texture or optical thickness filtering, your CI engine will sound false alarms across hundreds of square kilometers."* |
| **GAP-04** | **Multi-Radar Beam Curvature, Overlap & Cone of Silence** | (b) SOLUTION | **Moderate** | **R5, R11** | *"Radar beams curve with the Earth ($4/3 R_E$). At 150 km, the lowest beam is 2 km above ground, completely overshooting low-level initiation. Over the radar tower, you have a 15-degree cone of silence. How does your graph resolve conflicting reflectivity from two radars scanning the same storm at different vertical altitudes?"* |
| **GAP-05** | **NWP Forecast Latency & Spin-up Degradation** | (b) SOLUTION | **Moderate** | **R8, R2** | *"You blend NWP linearly with radar from $t=0$ to $6\text{h}$. But WRF/GFS runs take 90–120 minutes to process and download. In real-time at 12:00Z, your NWP data is already 2 hours old ($t_{\text{age}} = 120\text{m}$). How does your blending curve prevent stale NWP fields from corrupting the 2–4 hour nowcast?"* |
| **GAP-06** | **Lightning Detection Efficiency Range Falloff** | (b) SOLUTION | **Minor** | **R3, R10** | *"Ground lightning networks suffer from distance-dependent detection efficiency (e.g., 90% at 50 km, dropping to $<55\%$ at 200 km). Your DBSCAN cluster and 2-sigma jump detectors assume uniform sensor sensitivity. Distant storms will never trigger a jump alert."* |
| **GAP-07** | **Arbitrary Bounding Box vs. Real Administrative District GeoJSON** | (a) PROTOTYPE | **Minor** | **R12** | *"Your CAP alert lists district names, but the map polygon is a simple four-point bounding box around the storm. District collectors need precise polygon intersection against their taluk/district boundaries."* |
| **GAP-08** | **CAP Alert Cryptographic Tamper-Proofing (XML-DSig)** | (b) SOLUTION | **Minor** | **R12** | *"Civil defense warning systems (NDMA Sachet) mandate digital signatures to prevent malicious actors from injecting false thunderstorm sirens into public cell broadcasts. The CAP generator emits plaintext unsigned XML."* |

---

## 🎯 Detailed Requirement-by-Requirement Vulnerability Audit

### R1: AIML-Based System
- **Current State**: TRD defines full PyG GATv2Conv + GConvGRU equations. Live backend utilizes NetworkX with analytical physics weighting.
- **Judge Attack Vector**: If judges inspect `backend/graph_engine.py`, they will see `nx.DiGraph()` instead of `torch.nn.Module`.
- **Verdict**: **GAP-02 (Moderate)**. Needs explicit operational justification and a working PyTorch model inference bridge.

### R2 & R3: Nowcasting of Thunderstorms & Lightning (0–6 Hours)
- **Current State**: Blending curve smoothly transitions from radar to NWP.
- **Judge Attack Vector**: The 3–6 hour forecast is heavily reliant on NWP ($>75\%$). If NWP is 3 hours old, forecast accuracy deteriorates unless corrected for model initialization age.
- **Verdict**: **GAP-05 (Moderate)**.

### R4, R5, R6, R7, R8: Multi-Sensor Observation Ingestion
- **Current State**: Ingestion schema and data contracts are defined in `SCHEMA.md`. Feeder supplies synthetic multi-sensor snapshots.
- **Judge Attack Vector**: *"Show me you can parse a real Py-ART radar object or HDF5 file from disk."*
- **Verdict**: **GAP-01 (Moderate)**. Must provide a verified raw file parser module for real sample data.

### R9: Predict Onset (Convective Initiation)
- **Current State**: Uses $BT_{10.8} - BT_{12.0} < 0$ and cooling rate $<-1.5^\circ\text{C}/15\text{min}$.
- **Judge Attack Vector**: Known operational meteorological flaw—non-convective cirrus advection triggers false positives.
- **Verdict**: **GAP-03 (Moderate)**. Must incorporate spatial variance / cloud texture mask ($\sigma_{T_B} \ge 2.5\text{ K}$).

### R10 & R11: Predict Intensity & Trajectory
- **Current State**: Predicts max dBZ, cell centroid trajectory, and 2-sigma lightning jumps.
- **Judge Attack Vector**: Dual-radar beam heights differ at overlapping points. Which altitude is the node representing?
- **Verdict**: **GAP-04 (Moderate)**. Must define 3D beam height modeling and altitude normalization.

### R12: Timely Early Warnings
- **Current State**: Generates ITU X.1303 CAP XML and GeoJSON polygons.
- **Judge Attack Vector**: XML is unsigned; polygons are bounding boxes.
- **Verdict**: **GAP-07, GAP-08 (Minor)**.

---
*End of Adversarial Gap Register*
