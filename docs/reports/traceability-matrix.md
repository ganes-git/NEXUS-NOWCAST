# Traceability Matrix
## Multi-Sensor Thunderstorm & Lightning Nowcasting (SIH26072)

| Requirement ID | Requirement Description | PRD Section | TRD Section | Implementation File(s) | Verification Test | Status |
|---|---|---|---|---|---|---|
| **R1** | AI/ML-based Graph Neural Core | Section 3 (R1) | Section 2 | `backend/torch_model.py`, `backend/graph_engine.py` | `scripts/verify_system.py::test_model` | **Verified** |
| **R2** | 0–6 Hour Thunderstorm Nowcasting | Section 3 (R2) | Section 3.1 | `backend/meteorology.py`, `backend/main.py` | `scripts/verify_system.py::test_nowcast` | **Verified** |
| **R3** | 0–6 Hour Lightning Nowcasting | Section 3 (R3) | Section 3.3 | `backend/meteorology.py`, `backend/graph_engine.py` | `scripts/verify_system.py::test_lightning_jump` | **Verified** |
| **R4** | Atmospheric Observation Ingestion | Section 3 (R4) | Section 1.1 | `backend/ingest_real.py`, `backend/mock_feeder.py` | `scripts/verify_system.py::test_ingestion` | **Verified** |
| **R5** | Multiple Radar Integration | Section 3 (R5) | Section 1.1A | `backend/graph_engine.py`, `backend/mock_feeder.py` | `scripts/verify_system.py::test_multi_radar` | **Verified** |
| **R6** | Satellite Data Integration | Section 3 (R6) | Section 1.1B | `backend/meteorology.py`, `backend/ingest_real.py` | `scripts/verify_system.py::test_satellite_ci` | **Verified** |
| **R7** | Lightning Data Integration | Section 3 (R7) | Section 1.1C | `backend/graph_engine.py`, `backend/mock_feeder.py` | `scripts/verify_system.py::test_lightning_cluster` | **Verified** |
| **R8** | NWP Model Data Integration | Section 3 (R8) | Section 1.1D | `backend/graph_engine.py`, `backend/meteorology.py` | `scripts/verify_system.py::test_nwp_integration` | **Verified** |
| **R9** | Predict Onset (Convective Initiation) | Section 3 (R9) | Section 3.2 | `backend/meteorology.py` | `scripts/verify_system.py::test_convective_initiation` | **Verified** |
| **R10** | Predict Intensity Evolution | Section 3 (R10) | Section 2.1 | `backend/meteorology.py`, `backend/torch_model.py` | `scripts/verify_system.py::test_intensity_evolution` | **Verified** |
| **R11** | Predict Trajectory & Movement | Section 3 (R11) | Section 1.2 | `backend/graph_engine.py`, `backend/mock_feeder.py` | `scripts/verify_system.py::test_trajectory` | **Verified** |
| **R12** | Timely Early Warnings (CAP v1.2) | Section 3 (R12) | Section 4.2 | `backend/cap_generator.py`, `backend/main.py` | `scripts/verify_system.py::test_cap_xml` | **Verified** |
| **R13** | Pure Software Category Solution | Section 3 (R13) | Section 4.1 | `backend/main.py`, `frontend/index.html` | `scripts/verify_system.py::test_end_to_end` | **Verified** |
