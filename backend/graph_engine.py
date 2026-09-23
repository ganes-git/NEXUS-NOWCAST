"""
NEXUS-NOWCAST: Heterogeneous Graph Constructor (HGC) & STGAT Engine
Constructs the multi-sensor dynamic atmospheric graph:
- Radar superpixel nodes
- Satellite cloud ROI nodes
- Lightning strike cluster nodes
- NWP thermodynamic grid nodes
Connected via Physics-Informed Edges (Wind Advection, CAPE Gradient, Cross-Modal Attention).
"""

import math
import networkx as nx
from typing import Dict, Any, List


class HeterogeneousGraphEngine:
    def __init__(self):
        self.graph = nx.DiGraph()

    def build_graph(
        self,
        radar_nodes: List[Dict[str, Any]],
        satellite_nodes: List[Dict[str, Any]],
        lightning_nodes: List[Dict[str, Any]],
        nwp_nodes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Builds the unified heterogeneous graph with physics-informed edges.
        """
        self.graph.clear()

        # 1. Add Radar Nodes
        for r in radar_nodes:
            node_id = r["id"]
            self.graph.add_node(
                node_id,
                node_type="radar",
                lat=r["lat"],
                lon=r["lon"],
                dbz_mean=r["dbz_mean"],
                dbz_max=r["dbz_max"],
                radial_vel=r.get("radial_vel_mps", 0.0),
                station=r.get("station", "DWR_GENERIC")
            )

        # 2. Add Satellite Nodes
        for s in satellite_nodes:
            node_id = s["id"]
            self.graph.add_node(
                node_id,
                node_type="satellite",
                lat=s["lat"],
                lon=s["lon"],
                bt_10_8=s["bt_10_8"],
                bt_12_0=s["bt_12_0"],
                bt_6_7=s["bt_6_7"],
                ci_score=s.get("ci_score", 0)
            )

        # 3. Add Lightning Nodes
        for l in lightning_nodes:
            node_id = l["id"]
            self.graph.add_node(
                node_id,
                node_type="lightning",
                lat=l["lat"],
                lon=l["lon"],
                flash_rate=l["cluster_flash_rate"],
                peak_current=l.get("peak_current_ka", 25.0),
                is_jump=l.get("is_lightning_jump", False)
            )

        # 4. Add NWP Nodes
        for n in nwp_nodes:
            node_id = n["id"]
            self.graph.add_node(
                node_id,
                node_type="nwp",
                lat=n["lat"],
                lon=n["lon"],
                cape=n["cape_j_kg"],
                wind_u=n["wind_u_700_mps"],
                wind_v=n["wind_v_700_mps"]
            )

        # 5. Construct Physics-Informed Edges
        edge_list = []

        # A. Wind Advection Edges (Radar to Radar along NWP 700 hPa wind vector)
        mean_u = sum(n["wind_u_700_mps"] for n in nwp_nodes) / max(1, len(nwp_nodes))
        mean_v = sum(n["wind_v_700_mps"] for n in nwp_nodes) / max(1, len(nwp_nodes))
        wind_angle = math.atan2(mean_v, mean_u)

        for i, r1 in enumerate(radar_nodes):
            for j, r2 in enumerate(radar_nodes):
                if i == j:
                    continue
                d_lat = r2["lat"] - r1["lat"]
                d_lon = r2["lon"] - r1["lon"]
                dist = math.sqrt(d_lat**2 + d_lon**2)

                if dist < 0.8: # within ~80km
                    bearing = math.atan2(d_lat, d_lon)
                    angle_diff = abs(bearing - wind_angle)
                    alignment = max(0.0, math.cos(angle_diff))

                    if alignment > 0.4:
                        w_adv = round(alignment * math.exp(-dist / 0.5), 3)
                        self.graph.add_edge(r1["id"], r2["id"], edge_type="wind_advection", weight=w_adv)
                        edge_list.append({
                            "source": r1["id"],
                            "target": r2["id"],
                            "type": "wind_advection",
                            "weight": w_adv,
                            "source_coord": [r1["lat"], r1["lon"]],
                            "target_coord": [r2["lat"], r2["lon"]]
                        })

        # B. Cross-Modal Teleconnection Edges (Satellite Cloud to Radar & Lightning)
        for s in satellite_nodes:
            for r in radar_nodes:
                dist = math.sqrt((s["lat"] - r["lat"])**2 + (s["lon"] - r["lon"])**2)
                if dist < 0.45: # overlapping column
                    w_cross = round(math.exp(-dist / 0.3) * (r["dbz_mean"] / 70.0), 3)
                    self.graph.add_edge(s["id"], r["id"], edge_type="cross_modal_teleconnection", weight=w_cross)
                    edge_list.append({
                        "source": s["id"],
                        "target": r["id"],
                        "type": "cross_modal_teleconnection",
                        "weight": w_cross,
                        "source_coord": [s["lat"], s["lon"]],
                        "target_coord": [r["lat"], r["lon"]]
                    })

        # C. Lightning to Radar Edges
        for l in lightning_nodes:
            for r in radar_nodes:
                dist = math.sqrt((l["lat"] - r["lat"])**2 + (l["lon"] - r["lon"])**2)
                if dist < 0.35:
                    w_light = round(math.exp(-dist / 0.2), 3)
                    self.graph.add_edge(l["id"], r["id"], edge_type="electrical_core", weight=w_light)
                    edge_list.append({
                        "source": l["id"],
                        "target": r["id"],
                        "type": "electrical_core",
                        "weight": w_light,
                        "source_coord": [l["lat"], l["lon"]],
                        "target_coord": [r["lat"], r["lon"]]
                    })

        # Extract top attention edges for XAI visualization
        top_xai_edges = sorted(edge_list, key=lambda x: x["weight"], reverse=True)[:15]

        return {
            "num_nodes": self.graph.number_of_nodes(),
            "num_edges": self.graph.number_of_edges(),
            "radar_count": len(radar_nodes),
            "satellite_count": len(satellite_nodes),
            "lightning_count": len(lightning_nodes),
            "nwp_count": len(nwp_nodes),
            "all_edges": edge_list,
            "xai_top_attention_edges": top_xai_edges
        }
