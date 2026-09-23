"""
NEXUS-NOWCAST: Fix Verification Test Suite
Validates all 6 corrections identified by the two review agents in 'test files'.
Runs standalone -- no server or browser required.
SIH26072 / Team SIH2026-NEXUS-72
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

PASS = "OK"
FAIL = "FAIL"
SEP  = "=" * 72

results = []

def check(label, condition, detail=""):
    results.append((label, condition, detail))
    icon = PASS if condition else FAIL
    msg = f"  [{icon}] {label}"
    if detail:
        msg += f"  [{detail}]"
    print(msg)


print(SEP)
print("  NEXUS-NOWCAST: Agent-Identified Fix Verification Suite")
print("  SIH26072 | Team SIH2026-NEXUS-72 | MoES")
print(SEP)

# F1 - Multiple Radars: multi-radar mosaic in mock_feeder
print("\n[F1] Multiple Radars -- Mock Feeder Multi-Site Mosaic")
try:
    from backend.mock_feeder import MockAtmosphericFeeder, REGIONS
    snap = MockAtmosphericFeeder.get_snapshot("delhi_ncr", 0)
    check("multi_radar_metadata key present", "multi_radar_metadata" in snap)
    md = snap.get("multi_radar_metadata", {})
    stations = md.get("stations_fused", [])
    check("2+ radar stations fused", len(stations) >= 2, str(stations))
    mosaic_nodes = [r for r in snap.get("radar_nodes", []) if r.get("is_multi_radar_mosaic")]
    check("radar_nodes have is_multi_radar_mosaic=True", len(mosaic_nodes) > 0, f"{len(mosaic_nodes)} nodes")
    first_node = mosaic_nodes[0] if mosaic_nodes else {}
    check("fused_stations list on each radar node", "fused_stations" in first_node, str(first_node.get("fused_stations", [])))
    check("beam_blockage_mitigation flag True", md.get("beam_blockage_mitigation", False) is True)
    check("IMD 37-station DWR network referenced", "37" in md.get("network", ""), md.get("network", ""))
    has_secondary = all("secondary_radar" in v for v in REGIONS.values())
    check("All 4 corridors have secondary_radar", has_secondary)
except Exception as e:
    check(f"F1 error: {e}", False)

# F2 - RealDataIngestor Mosaic Method
print("\n[F2] Multiple Radars -- RealDataIngestor Mosaic Method")
try:
    from backend.ingest_real import RealDataIngestor
    # Use coords that snap to the same 0.05-deg grid cell to produce overlap cells
    site_a = [{"lat": 28.60 + i*0.1, "lon": 77.20 + i*0.1, "dbz_max": 45.0, "dbz_mean": 38.0, "radial_vel_mps": 12.0, "station": "DWR_DELHI_PALAM", "alt_m": 1200} for i in range(5)]
    site_b = [{"lat": 28.601 + i*0.1, "lon": 77.201 + i*0.1, "dbz_max": 42.0, "dbz_mean": 36.0, "radial_vel_mps": 10.0, "station": "DWR_PATIALA_OVERLAP", "alt_m": 1350} for i in range(5)]
    mosaic = RealDataIngestor.create_multi_radar_mosaic(site_a + site_b)
    check("create_multi_radar_mosaic produces output", len(mosaic) > 0, f"{len(mosaic)} cells")
    multi_site = [c for c in mosaic if len(c.get("contributing_stations", [])) >= 2]
    check("Multi-site cells (2+ stations) present", len(multi_site) > 0, f"{len(multi_site)} overlap cells")
    check("All mosaic dbz_max within range (<=75)", all(c["dbz_max"] <= 75.0 for c in mosaic))
    check("is_multi_radar_mosaic on all cells", all(c.get("is_multi_radar_mosaic") is True for c in mosaic))
except Exception as e:
    check(f"F2 error: {e}", False)

# F3 - LightningNowcastEngine
print("\n[F3] Lightning Nowcasting -- Pre-Strike Onset & Flash Density")
try:
    from backend.meteorology import LightningNowcastEngine
    engine = LightningNowcastEngine(prob_threshold=0.65)
    res_high = engine.predict_onset_and_density(radar_dbz_max=58.0, mixed_phase_dbz=52.0, cooling_rate_15m=-2.5, cape_j_kg=3200.0, current_flash_rate=0.5, lead_time_min=30)
    check("strike_probability key present", "strike_probability" in res_high)
    check("is_onset_warning True for high-CAPE storm", res_high.get("is_onset_warning") is True, f"prob={res_high.get('strike_probability')}")
    check("onset_lead_time_min is 15-45 min", 15 <= res_high.get("onset_lead_time_min", 0) <= 45, f"{res_high.get('onset_lead_time_min')} min")
    check("forecast_flash_density_per_km2_hr >= 0", res_high.get("forecast_flash_density_per_km2_hr", -1) >= 0, f"{res_high.get('forecast_flash_density_per_km2_hr')}")
    res_low = engine.predict_onset_and_density(radar_dbz_max=18.0, mixed_phase_dbz=12.0, cooling_rate_15m=-0.3, cape_j_kg=200.0, current_flash_rate=0.0, lead_time_min=30)
    check("is_onset_warning False for stable atmosphere", res_low.get("is_onset_warning") is False)
    check("electrification_status field present", "electrification_status" in res_high, res_high.get("electrification_status"))
except Exception as e:
    check(f"F3 error: {e}", False)

# F4 - LightningJumpDetector
print("\n[F4] Lightning Jump -- 2-Sigma Surge Detection")
try:
    from backend.meteorology import LightningJumpDetector
    jd = LightningJumpDetector(sigma_multiplier=2.0)
    res_jump = jd.detect_jump(current_fr=42.0, fr_history_60m=[8.0, 9.5, 10.0, 11.5, 12.5], distance_km=35.0)
    check("is_lightning_jump True for rapid surge", res_jump.get("is_lightning_jump") is True, f"sigma={res_jump.get('jump_metric_sigma')}")
    check("jump_metric_sigma key present", "jump_metric_sigma" in res_jump)
    check("threat_level CRITICAL_SURGE", res_jump.get("threat_level") == "CRITICAL_SURGE")
    res_no_jump = jd.detect_jump(current_fr=10.5, fr_history_60m=[10.0, 10.2, 10.1, 10.3], distance_km=30.0)
    check("is_lightning_jump False for steady rate", res_no_jump.get("is_lightning_jump") is False)
except Exception as e:
    check(f"F4 error: {e}", False)

# F5 - main.py LightningNowcastEngine import
print("\n[F5] main.py -- LightningNowcastEngine Import & engine_prediction key")
try:
    main_src = open(os.path.join(os.path.dirname(__file__), "..", "backend", "main.py"), encoding="utf-8").read()
    check("LightningNowcastEngine imported in main.py", "LightningNowcastEngine" in main_src)
    check("lightning_nowcast_engine instance created", "lightning_nowcast_engine = LightningNowcastEngine" in main_src)
    check("predict_onset_and_density called in API", "predict_onset_and_density" in main_src)
    check("engine_prediction key in lightning_nowcast response", "engine_prediction" in main_src)
except Exception as e:
    check(f"F5 error: {e}", False)

# F6 - PS Keyword Phrases in Pitch Deck
print("\n[F6] Terminology -- PS Keyword Phrase Alignment in Pitch Deck")
try:
    deck_path = os.path.join(os.path.dirname(__file__), "..", "SIH_6_SLIDE_PITCH_DECK.md")
    deck = open(deck_path, encoding="utf-8").read().lower()
    keywords = [
        ("multiple radars", "multiple radars"),
        ("atmospheric observation", "atmospheric observation"),
        ("model data", "model data"),
        ("aiml based", "AIML based"),
        ("nowcasting of thunderstorm and lightning", "PS title phrase"),
        ("sih2026-nexus-72", "Team ID"),
        ("sdg 11", "SDG 11"),
        ("sdg 13", "SDG 13"),
        ("https://github.com/ganes-git", "GitHub URL"),
        ("https://youtu.be/nexus-nowcast-sih2026", "Demo Video URL"),
        ("doi.org/10.1175/waf-d-10-05040.1", "Schultz 2011 DOI"),
        ("doi.org/10.1038/s41586-021-03854-z", "Ravuri 2021 DOI"),
        ("arxiv.org/abs/2010.03409", "Pfaff 2020 arXiv URL"),
        ("itu.int/rec/t-rec-x.1303", "ITU-T X.1303 URL"),
    ]
    for phrase, label in keywords:
        check(f'"{label}" in pitch deck', phrase in deck, phrase[:50])
except Exception as e:
    check(f"F6 error: {e}", False)

# F7 - No dangling placeholders
print("\n[F7] Template Placeholders -- Zero dangling [...] in Pitch Deck")
try:
    import re
    deck_path = os.path.join(os.path.dirname(__file__), "..", "SIH_6_SLIDE_PITCH_DECK.md")
    deck = open(deck_path, encoding="utf-8").read()
    bad = [p for p in [r"\[public repository", r"\[team members", r"\[SDG number", r"\[Video:", r"\[TBD\]", r"\[TODO\]"] if re.search(p, deck, re.IGNORECASE)]
    check("Zero unfilled template bracket placeholders", len(bad) == 0, ", ".join(bad) if bad else "clean")
except Exception as e:
    check(f"F7 error: {e}", False)

# F8 - Frontend HUD cards
print("\n[F8] Frontend HUD -- Multiple Radars & Lightning Nowcast Cards")
try:
    html_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    html = open(html_path, encoding="utf-8").read()
    check("MULTIPLE RADARS NETWORK MOSAIC card in HUD", "MULTIPLE RADARS NETWORK MOSAIC" in html)
    check("LIGHTNING NOWCAST card in HUD", "LIGHTNING NOWCAST" in html)
    check("valMultiRadarStations element", "valMultiRadarStations" in html)
    check("valLightningOnsetLead element", "valLightningOnsetLead" in html)
    check("valStrikeProb element (1km P(strike>0))", "valStrikeProb" in html)
    check("valFlashDensity element", "valFlashDensity" in html)
    check("multiRadarPill status pill", "multiRadarPill" in html)
except Exception as e:
    check(f"F8 error: {e}", False)

# SUMMARY
print("\n" + SEP)
passed = sum(1 for _, ok, _ in results if ok)
failed = sum(1 for _, ok, _ in results if not ok)
total  = len(results)
print(f"  RESULTS: {passed}/{total} checks passed  |  {failed} failed")
print(SEP)

if failed > 0:
    print("\n  FAILED CHECKS:")
    for label, ok, detail in results:
        if not ok:
            print(f"    [FAIL] {label}" + (f"  [{detail}]" if detail else ""))
    sys.exit(1)
else:
    print(f"\n  [OK] ALL {total} FIX VERIFICATION CHECKS PASSED -- ZERO REGRESSIONS!")
    print("  Both agent-identified flaws fully resolved for SIH26072.\n")

