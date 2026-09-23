# Feature Checklist
## Multi-Sensor Thunderstorm & Lightning Nowcasting System (SIH26072)
**Theme**: Disaster Management | **Sponsoring Agency**: Ministry of Earth Sciences (MoES) / IMD

### Core Functional Feature Requirements (R1 – R13)

- [x] **F-01 [R1] AI/ML-Based Graph Neural Core**: Spatio-Temporal Graph Attention Network with dynamic edge weighting (`torch_model.py`, `graph_engine.py`).
- [x] **F-02 [R2] 0–6 Hour Thunderstorm Nowcasting**: Probabilistic dBZ reflectivity regression and 4-tier IMD severity classification (Green, Yellow, Orange, Red) at 15-min steps (`meteorology.py`).
- [x] **F-03 [R3] 0–6 Hour Lightning Nowcasting**: Strike density forecasting and operational $2\sigma$ Lightning Jump surge detection (`meteorology.py`).
- [x] **F-04 [R4] Atmospheric Observation Ingestion**: Ingests multi-modal observations from radar, satellite, lightning, and NWP (`ingest_real.py`, `mock_feeder.py`).
- [x] **F-05 [R5] Multiple Radar Integration**: Multi-DWR station ingestion with 3D beam curvature geometry compensation ($h = r\sin\theta + r^2 / (2 k_e R_E)$) (`graph_engine.py`).
- [x] **F-06 [R6] Satellite Multispectral Data Integration**: INSAT-3D thermal infrared (10.8µm, 12.0µm) and water vapor (6.7µm) channel ingestion with cloud texture filtering (`meteorology.py`).
- [x] **F-07 [R7] Lightning Detection Network Integration**: Real-time strike point ingestion with rolling DBSCAN spatial clustering ($\epsilon=12$ km) (`graph_engine.py`).
- [x] **F-08 [R8] NWP Model Data Integration**: GFS/WRF thermodynamic instability (CAPE, CIN, 0-6km bulk shear, 700 hPa wind steering vectors) integrated as graph edge constraints (`graph_engine.py`).
- [x] **F-09 [R9] Pre-Radar Convective Initiation (CI)**: Split-window brightness temperature difference ($BT_{10.8} - BT_{12.0} < 0$) and rapid cooling ($<-1.5^\circ\text{C}/15\text{min}$) detecting storm genesis 30–45 min before radar echoes (`meteorology.py`).
- [x] **F-10 [R10] Intensity Evolution Prediction**: Multi-horizon severity progression forecasting storm cell strengthening, plateauing, or dissipation (`meteorology.py`).
- [x] **F-11 [R11] Trajectory & Movement Prediction**: Storm centroid displacement tracking along 700 hPa steering vectors (`graph_engine.py`).
- [x] **F-12 [R12] Timely Early Warnings & Alert Feeds**: Automated generation of court-admissible ITU X.1303 / OASIS CAP v1.2 XML alerts with SHA-256 signatures mapped to administrative districts (`cap_generator.py`).
- [x] **F-13 [R13] Pure Software Architecture**: Open-source microservice stack (FastAPI, Leaflet.js, PyTorch/NetworkX) running on standard commodity hardware with 100% offline simulation capability (`main.py`, `run_server.py`).

### Operational Extensions & Validation
- [x] **F-14 Dynamic Lead-Time Blending Engine**: Smooth transition ($W_{\text{radar}} = \exp(-\Delta t / 120\text{min})$) resolving the 2-Hour Radar Wall (`meteorology.py`).
- [x] **F-15 Meteorological Contingency Verification**: Automated calculation of Critical Success Index (CSI), Probability of Detection (POD), False Alarm Ratio (FAR), and Equitable Threat Score (ETS) (`meteorology.py`).
- [x] **F-16 Mission Control GIS C2 Dashboard**: Leaflet.js map with timeline scrubbing (0–360 min), dBZ contours, strike density heatmaps, and XAI edge attention inspection (`frontend/`).
