# Data Contracts & Schemas
## NEXUS-NOWCAST: Multi-Modal Graph & Disaster Alert Specifications
**Standard**: ITU-T X.1303 / OASIS CAP v1.2 / W3C GeoJSON

---

## 1. Heterogeneous Atmospheric Graph Schema (HGC)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "HeterogeneousAtmosphericGraph",
  "type": "object",
  "required": ["timestamp", "epoch_id", "nodes", "edges"],
  "properties": {
    "timestamp": { "type": "string", "format": "date-time" },
    "epoch_id": { "type": "string", "example": "EPOCH-20260920-1200Z" },
    "nodes": {
      "type": "object",
      "required": ["radar", "satellite", "lightning", "nwp"],
      "properties": {
        "radar": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["id", "station", "lat", "lon", "alt_m", "dbz_mean", "dbz_max", "radial_vel_mps"],
            "properties": {
              "id": { "type": "string" },
              "station": { "type": "string", "example": "DWR_DELHI" },
              "lat": { "type": "number" },
              "lon": { "type": "number" },
              "alt_m": { "type": "number" },
              "dbz_mean": { "type": "number", "minimum": 0, "maximum": 75 },
              "dbz_max": { "type": "number", "minimum": 0, "maximum": 80 },
              "radial_vel_mps": { "type": "number" }
            }
          }
        },
        "satellite": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["id", "lat", "lon", "bt_10_8", "bt_12_0", "bt_6_7", "cloud_top_cooling_c_per_15m"],
            "properties": {
              "id": { "type": "string" },
              "lat": { "type": "number" },
              "lon": { "type": "number" },
              "bt_10_8": { "type": "number", "description": "Brightness temp 10.8um (K)" },
              "bt_12_0": { "type": "number", "description": "Brightness temp 12.0um (K)" },
              "bt_6_7": { "type": "number", "description": "Water vapor 6.7um (K)" },
              "cloud_top_cooling_c_per_15m": { "type": "number" }
            }
          }
        },
        "lightning": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["id", "lat", "lon", "cluster_flash_rate", "peak_current_ka", "is_lightning_jump"],
            "properties": {
              "id": { "type": "string" },
              "lat": { "type": "number" },
              "lon": { "type": "number" },
              "cluster_flash_rate": { "type": "number" },
              "peak_current_ka": { "type": "number" },
              "is_lightning_jump": { "type": "boolean" }
            }
          }
        },
        "nwp": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["id", "lat", "lon", "cape_j_kg", "shear_0_6km_mps", "wind_u_700_mps", "wind_v_700_mps"],
            "properties": {
              "id": { "type": "string" },
              "lat": { "type": "number" },
              "lon": { "type": "number" },
              "cape_j_kg": { "type": "number" },
              "shear_0_6km_mps": { "type": "number" },
              "wind_u_700_mps": { "type": "number" },
              "wind_v_700_mps": { "type": "number" }
            }
          }
        }
      }
    },
    "edges": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["source", "target", "type", "weight"],
        "properties": {
          "source": { "type": "string" },
          "target": { "type": "string" },
          "type": { "type": "string", "enum": ["wind_advection", "cape_gradient", "cross_modal_teleconnection", "spatial_proximity"] },
          "weight": { "type": "number" }
        }
      }
    }
  }
}
```

---

## 2. Dynamic Nowcast Forecast Response Schema

```json
{
  "lead_time_min": 60,
  "blending_weights": {
    "radar_stgat_weight": 0.607,
    "nwp_thermo_weight": 0.393
  },
  "storm_cells": [
    {
      "cell_id": "CELL-042",
      "centroid": [28.6139, 77.209],
      "future_track": [
        [28.6139, 77.209],
        [28.6912, 77.315],
        [28.7845, 77.428]
      ],
      "max_dbz": 54.2,
      "severity": "RED",
      "lightning_threat": "HIGH",
      "lightning_jump_active": true,
      "convective_initiation_flag": false,
      "districts_impacted": ["New Delhi", "Ghaziabad", "Noida"]
    }
  ],
  "xai_attention_top_edges": [
    {
      "source_node": "DWR_DELHI_SP_12",
      "target_node": "CELL-042",
      "attention_score": 0.842,
      "physical_basis": "Downwind 700 hPa advection steering corridor"
    }
  ]
}
```

---

## 3. ITU X.1303 / NDMA CAP v1.2 XML Alert Schema

```xml
<?xml version="1.0" encoding="UTF-8"?>
<alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
  <identifier>NEXUS-ALERT-20260920-001</identifier>
  <sender>imd-nowcast-engine@moes.gov.in</sender>
  <sent>2026-09-20T12:00:00+05:30</sent>
  <status>Actual</status>
  <msgType>Alert</msgType>
  <scope>Public</scope>
  <info>
    <category>Met</category>
    <event>Severe Thunderstorm &amp; Lightning Warning</event>
    <urgency>Immediate</urgency>
    <severity>Extreme</severity>
    <certainty>Observed</certainty>
    <eventCode>
      <valueName>IMD_COLOR_CODE</valueName>
      <value>RED</value>
    </eventCode>
    <expires>2026-09-20T14:00:00+05:30</expires>
    <headline>Severe Convective Storm with Rapid Lightning Surges Detected</headline>
    <description>STGAT-PIE Nowcasting system detected cell centroid moving east-northeast at 42 km/h. Reflectivity exceeding 52 dBZ with active 2-sigma lightning jump.</description>
    <instruction>Take shelter immediately in a substantial building. Avoid open fields, tall trees, and electrical poles.</instruction>
    <area>
      <areaDesc>NCR Delhi, Ghaziabad, Gautam Buddha Nagar</areaDesc>
      <polygon>28.52,77.10 28.75,77.15 28.78,77.48 28.48,77.42 28.52,77.10</polygon>
    </area>
  </info>
</alert>
```

---
*End of Schemas Document*
