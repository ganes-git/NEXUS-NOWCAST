"""
NEXUS-NOWCAST: High-Fidelity Multi-Sensor Atmospheric Feeder
Generates realistic, meteorologically constrained observation snapshots
for 4 critical Indian Doppler Weather Radar (DWR) corridors:
- Delhi NCR (Convective supercell moving ENE)
- Kolkata / Bay of Bengal (Severe Nor'wester / Kalbaishakhi line)
- Chennai Coast (Maritime convective thunderstorm)
- Mumbai Coastal Corridor (Ghats-enhanced squall)
"""

import math
from typing import Dict, Any, List


REGIONS = {
    "delhi_ncr": {
        "name": "Delhi NCR (Indira Gandhi Int'l Airport DWR & Patiala DWR Mosaic)",
        "center": [28.6139, 77.2090],
        "primary_radar": {"id": "DWR_DELHI_PALAM", "name": "IMD Delhi Palam DWR"},
        "secondary_radar": {"id": "DWR_PATIALA_OVERLAP", "name": "IMD Patiala DWR (Overlapping Northwest)"},
        "districts": ["New Delhi", "North Delhi", "Ghaziabad", "Gautam Buddha Nagar (Noida)", "Meerut"],
        "wind_700_u": 12.5,   # m/s (West-to-East)
        "wind_700_v": 6.0,    # m/s (South-to-North)
        "cape_mean": 2650.0,  # J/kg (High Convective Instability)
        "cin_mean": 25.0
    },
    "kolkata_bay": {
        "name": "Kolkata (Alipore DWR & Paradeep DWR Mosaic - Kalbaishakhi Corridor)",
        "center": [22.5726, 88.3639],
        "primary_radar": {"id": "DWR_KOLKATA_ALIPORE", "name": "IMD Kolkata Alipore DWR"},
        "secondary_radar": {"id": "DWR_PARADEEP_OVERLAP", "name": "IMD Paradeep DWR (Overlapping Coastal)"},
        "districts": ["Kolkata", "Howrah", "North 24 Parganas", "South 24 Parganas", "Hooghly"],
        "wind_700_u": 14.0,
        "wind_700_v": -8.0,   # Moving SE toward Bay of Bengal
        "cape_mean": 3200.0,
        "cin_mean": 15.0
    },
    "chennai_coast": {
        "name": "Chennai (Meenambakkam DWR & Sriharikota DWR Mosaic)",
        "center": [13.0827, 80.2707],
        "primary_radar": {"id": "DWR_CHENNAI_MEENAMBAKKAM", "name": "IMD Chennai Meenambakkam DWR"},
        "secondary_radar": {"id": "DWR_SRIHARIKOTA_OVERLAP", "name": "IMD Sriharikota DWR (Overlapping North)"},
        "districts": ["Chennai", "Chengalpattu", "Kanchipuram", "Tiruvallur"],
        "wind_700_u": 8.0,
        "wind_700_v": 10.0,
        "cape_mean": 2100.0,
        "cin_mean": 40.0
    },
    "mumbai_coastal": {
        "name": "Mumbai (Colaba DWR & Veravali DWR Mosaic)",
        "center": [19.0760, 72.8777],
        "primary_radar": {"id": "DWR_MUMBAI_COLABA", "name": "IMD Mumbai Colaba DWR"},
        "secondary_radar": {"id": "DWR_MUMBAI_VERAVALI", "name": "IMD Mumbai Veravali DWR (Overlapping North)"},
        "districts": ["Mumbai City", "Mumbai Suburban", "Thane", "Raigad"],
        "wind_700_u": 16.0,
        "wind_700_v": 4.0,
        "cape_mean": 2800.0,
        "cin_mean": 20.0
    }
}


class MockAtmosphericFeeder:
    """
    Generates multi-sensor observation records for testing, validation, and zero-dependency offline demos.
    """
    @staticmethod
    def get_snapshot(region_key: str = "delhi_ncr", time_offset_min: int = 0) -> Dict[str, Any]:
        if region_key not in REGIONS:
            region_key = "delhi_ncr"
        reg = REGIONS[region_key]
        c_lat, c_lon = reg["center"]

        # Calculate cell centroid advection based on 700 hPa winds
        # 1 deg lat ~ 111 km, 1 deg lon ~ 111 * cos(lat)
        dt_sec = time_offset_min * 60
        dx_km = (reg["wind_700_u"] * dt_sec) / 1000.0
        dy_km = (reg["wind_700_v"] * dt_sec) / 1000.0

        d_lon = dx_km / (111.32 * math.cos(math.radians(c_lat)))
        d_lat = dy_km / 110.57

        storm_center_lat = c_lat + d_lat
        storm_center_lon = c_lon + d_lon

        # 1. Generate Multi-Radar Mosaic Superpixels (Fused from Primary + Secondary Overlapping DWR)
        radar_nodes = []
        node_idx = 1
        p_radar = reg.get("primary_radar", {"id": "DWR_PRIMARY", "name": "Primary DWR"})
        s_radar = reg.get("secondary_radar", {"id": "DWR_SECONDARY", "name": "Secondary DWR"})

        for dlat_offset in [-0.25, -0.15, -0.05, 0.05, 0.15, 0.25]:
            for dlon_offset in [-0.25, -0.15, -0.05, 0.05, 0.15, 0.25]:
                lat = round(storm_center_lat + dlat_offset, 4)
                lon = round(storm_center_lon + dlon_offset, 4)
                dist_core = math.sqrt(dlat_offset**2 + dlon_offset**2)

                # Primary radar reflectivity profile
                z_primary = max(12.0, 58.0 * math.exp(-(dist_core**2) / 0.04))
                # Secondary overlapping radar with slight distance attenuation & geometry difference
                dist_secondary = math.sqrt((dlat_offset - 0.08)**2 + (dlon_offset + 0.12)**2)
                z_secondary = max(10.0, 54.0 * math.exp(-(dist_secondary**2) / 0.045))

                # Multi-Radar Mosaic: Maximum Composite Reflectivity with range-blockage weight
                dbz_composite = max(z_primary, z_secondary * 0.96)

                if dbz_composite > 18.0:
                    assigned_station = p_radar["id"] if z_primary >= z_secondary else s_radar["id"]
                    radar_nodes.append({
                        "id": f"RADAR_{reg['name'][:3]}_{node_idx:03d}",
                        "station": assigned_station,
                        "primary_dbz": round(z_primary, 1),
                        "secondary_dbz": round(z_secondary, 1),
                        "is_multi_radar_mosaic": True,
                        "fused_stations": [p_radar["id"], s_radar["id"]],
                        "lat": lat,
                        "lon": lon,
                        "alt_m": 1200 + int(dist_core * 1000),
                        "dbz_mean": round(dbz_composite, 1),
                        "dbz_max": round(min(70.0, dbz_composite + 5.8), 1),
                        "radial_vel_mps": round(reg["wind_700_u"] * 0.8 + (dist_core * 5.0), 1)
                    })
                    node_idx += 1

        # 2. Generate Satellite Cloud ROIs (INSAT-3D Split Window)
        satellite_nodes = []
        for i, (sla, slo) in enumerate([
            (storm_center_lat + 0.1, storm_center_lon + 0.1),
            (storm_center_lat - 0.1, storm_center_lon + 0.15),
            (storm_center_lat + 0.2, storm_center_lon - 0.05),
            (storm_center_lat + 0.35, storm_center_lon + 0.3) # Flanking CI region
        ]):
            is_ci_region = (i == 3)
            # Cold cloud top (210K - 235K)
            bt_10_8 = 214.5 if not is_ci_region else 232.0
            bt_12_0 = 216.0 if not is_ci_region else 233.8
            bt_6_7 = 222.0 if not is_ci_region else 236.5
            cooling_rate = -2.8 if is_ci_region else -1.2

            satellite_nodes.append({
                "id": f"SAT_INSAT3D_{i+1:02d}",
                "lat": round(sla, 4),
                "lon": round(slo, 4),
                "bt_10_8": bt_10_8,
                "bt_12_0": bt_12_0,
                "bt_6_7": bt_6_7,
                "cloud_top_cooling_c_per_15m": cooling_rate,
                "ci_score": 85 if is_ci_region else 40
            })

        # 3. Generate Lightning Strike Clusters (DBSCAN Clusters)
        lightning_nodes = []
        for j, (lla, llo, fr, jump) in enumerate([
            (storm_center_lat + 0.02, storm_center_lon + 0.03, 38.5, True),   # Core Lightning Jump
            (storm_center_lat - 0.08, storm_center_lon + 0.06, 18.2, False),
            (storm_center_lat + 0.12, storm_center_lon + 0.18, 9.4, False)
        ]):
            lightning_nodes.append({
                "id": f"LIGHT_CLUST_{j+1:02d}",
                "lat": round(lla, 4),
                "lon": round(llo, 4),
                "cluster_flash_rate": fr,
                "peak_current_ka": 38.4 if jump else 22.0,
                "is_lightning_jump": jump
            })

        # 4. Generate NWP Grid Points
        nwp_nodes = []
        for k, (nla, nlo) in enumerate([
            (storm_center_lat - 0.3, storm_center_lon - 0.3),
            (storm_center_lat + 0.3, storm_center_lon - 0.3),
            (storm_center_lat - 0.3, storm_center_lon + 0.3),
            (storm_center_lat + 0.3, storm_center_lon + 0.3)
        ]):
            nwp_nodes.append({
                "id": f"NWP_WRF_{k+1:02d}",
                "lat": round(nla, 4),
                "lon": round(nlo, 4),
                "cape_j_kg": reg["cape_mean"] + (k * 150),
                "shear_0_6km_mps": 22.5,
                "wind_u_700_mps": reg["wind_700_u"],
                "wind_v_700_mps": reg["wind_700_v"]
            })

        # Meteorological Convective Warning Swath Envelope (Aerodynamic hazard envelope aligned to steering flow)
        heading_rad = math.atan2(reg["wind_700_v"], reg["wind_700_u"])
        r_lat_km = 110.57
        r_lon_km = 111.32 * math.cos(math.radians(storm_center_lat))
        alert_poly = []
        num_pts = 24
        for i in range(num_pts):
            phi = (2 * math.pi * i) / num_pts
            angle_diff = phi - heading_rad
            # Forward extension ~32km along steering flow, lateral flank ~22km, rear flank ~16km
            forward_factor = math.cos(angle_diff)
            if forward_factor > 0:
                r_km = 21.0 + (12.0 * forward_factor)
            else:
                r_km = 21.0 + (5.0 * forward_factor)
            dx_km = r_km * math.cos(phi)
            dy_km = r_km * math.sin(phi)
            alert_poly.append([
                round(storm_center_lat + (dy_km / r_lat_km), 4),
                round(storm_center_lon + (dx_km / r_lon_km), 4)
            ])

        # Forecast Track Points over 0 to 6 Hours (every 30 mins)
        track = []
        for lead_step in [0, 30, 60, 120, 180, 240, 360]:
            t_sec = lead_step * 60
            trk_dx = (reg["wind_700_u"] * t_sec) / 1000.0
            trk_dy = (reg["wind_700_v"] * t_sec) / 1000.0
            trk_dlon = trk_dx / (111.32 * math.cos(math.radians(c_lat)))
            trk_dlat = trk_dy / 110.57
            track.append([round(c_lat + trk_dlat, 4), round(c_lon + trk_dlon, 4)])

        # Pre-strike lightning onset & strike density nowcasting
        max_radar_dbz = max([r["dbz_max"] for r in radar_nodes]) if radar_nodes else 20.0
        current_fr = sum([l["cluster_flash_rate"] for l in lightning_nodes]) if lightning_nodes else 0.0
        has_jump = any([l.get("is_lightning_jump", False) for l in lightning_nodes])

        # Onset strike probability model
        strike_prob = round(min(0.98, max(0.15, (max_radar_dbz - 25.0) / 35.0 + (reg["cape_mean"] / 4000.0) * 0.4)), 3)
        onset_advance_min = 30 if strike_prob >= 0.70 and current_fr < 15.0 else 0

        return {
            "region_key": region_key,
            "region_name": reg["name"],
            "districts": reg["districts"],
            "center": [c_lat, c_lon],
            "lead_time_min": time_offset_min,
            "storm_center": [round(storm_center_lat, 4), round(storm_center_lon, 4)],
            "forecast_track": track,
            "alert_polygon": alert_poly,
            "multi_radar_metadata": {
                "stations_fused": [p_radar["id"], s_radar["id"]],
                "network": "IMD 37-DWR National Doppler Radar Network",
                "mosaic_mode": "Maximum Composite Reflectivity with Range-Weighted Deconfliction",
                "beam_blockage_mitigation": True,
                "total_radars_fused": 2,
                "description": f"Mosaicked from {p_radar['name']} and {s_radar['name']}"
            },
            "lightning_nowcast": {
                "target_lead_time_min": time_offset_min,
                "is_onset_warning": onset_advance_min > 0,
                "onset_lead_time_min": onset_advance_min,
                "ground_strike_probability": strike_prob,
                "forecast_flash_density_per_km2_hr": round(max(0.1, strike_prob * 4.5 * math.exp(-time_offset_min / 180.0)), 2),
                "is_lightning_jump_active": has_jump,
                "jump_surge_sigma": 2.6 if has_jump else 0.8,
                "electrification_status": "PRE_STRIKE_ONSET_ACTIVE" if onset_advance_min > 0 else ("CRITICAL_JUMP_SURGE" if has_jump else "STEADY_ELECTRIFICATION")
            },
            "radar_nodes": radar_nodes,
            "satellite_nodes": satellite_nodes,
            "lightning_nodes": lightning_nodes,
            "nwp_nodes": nwp_nodes
        }
