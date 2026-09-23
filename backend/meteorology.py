"""
NEXUS-NOWCAST: Meteorological Algorithms Engine
- Dynamic 0–6 Hour Lead-Time Blending Curve (Radar -> NWP transition)
- Satellite Convective Initiation (CI) Split-Window Detection
- Operational Lightning Jump Algorithm (2-sigma surge detection)
- Meteorological Verification Suite (CSI, POD, FAR, ETS, HSS)
"""

import math
from typing import Dict, Any, List, Tuple
import numpy as np


class BlendingEngine:
    """
    Computes lead-time dependent weights bridging 0-90min radar advection
    and 3-6hr NWP thermodynamic forecasting, overcoming the '2-Hour Radar Wall'.
    Includes NWP Forecast Age Attenuation factor to account for model latency.
    """
    def __init__(self, tau_minutes: float = 120.0, tau_nwp_age_hours: float = 18.0):
        self.tau = tau_minutes
        self.tau_nwp_age = tau_nwp_age_hours

    def get_weights(self, lead_time_min: int, nwp_age_hours: float = 2.0) -> Dict[str, float]:
        """
        W_radar = exp(-lead_time / tau)
        W_nwp_raw = 1.0 - W_radar
        W_nwp_eff = W_nwp_raw * exp(-nwp_age_hours / tau_nwp_age)
        """
        lead_time_min = max(0, min(360, lead_time_min))
        w_radar_raw = math.exp(-lead_time_min / self.tau)
        w_nwp_raw = 1.0 - w_radar_raw

        # Discount stale NWP
        age_discount = math.exp(-max(0.0, nwp_age_hours) / self.tau_nwp_age)
        w_nwp_eff = w_nwp_raw * age_discount
        w_radar_eff = 1.0 - w_nwp_eff

        return {
            "lead_time_min": lead_time_min,
            "nwp_age_hours": nwp_age_hours,
            "radar_weight": round(w_radar_eff, 4),
            "nwp_weight": round(w_nwp_eff, 4),
            "dominant_driver": "Radar Kinematic Advection" if w_radar_eff >= 0.5 else "NWP Thermodynamic Instability"
        }

    def blend_reflectivity(self, radar_dbz: float, nwp_conv_dbz: float, lead_time_min: int, nwp_age_hours: float = 2.0) -> float:
        """Blends high-res radar reflectivity with NWP simulated reflectivity."""
        w = self.get_weights(lead_time_min, nwp_age_hours)
        blended = (radar_dbz * w["radar_weight"]) + (nwp_conv_dbz * w["nwp_weight"])
        return round(max(0.0, min(75.0, blended)), 1)


class ConvectiveInitiationDetector:
    """
    Detects storm genesis 30-45 minutes BEFORE radar echoes appear
    using INSAT-3D Split-Window Brightness Temperature differences.
    Includes Spatial Roughness (Texture) Variance Filter to reject false alarms on cirrus shields.
    """
    def __init__(
        self,
        cooling_threshold: float = -1.5,      # °C / 15 min
        swd_threshold: float = 0.0,           # BT10.8 - BT12.0 < 0°C (glaciation)
        wv_threshold: float = -5.0,           # BT6.7 - BT10.8 >= -5°C (deep moisture)
        texture_var_threshold: float = 2.5    # Spatial variance >= 2.5K (rejects smooth cirrus anvils)
    ):
        self.cooling_threshold = cooling_threshold
        self.swd_threshold = swd_threshold
        self.wv_threshold = wv_threshold
        self.texture_var_threshold = texture_var_threshold

    def evaluate_node(
        self,
        bt_10_8: float,
        bt_12_0: float,
        bt_6_7: float,
        cooling_rate_15m: float,
        spatial_texture_std: float = 3.2 # Standard deviation of BT10.8 in 3x3 window
    ) -> Dict[str, Any]:
        """
        Evaluates satellite multispectral cloud features for pre-radar convective initiation.
        Rejects cirrus shield contamination if spatial variance is too smooth (<2.5K).
        """
        swd = bt_10_8 - bt_12_0
        wv_diff = bt_6_7 - bt_10_8

        is_rapid_cooling = cooling_rate_15m <= self.cooling_threshold
        is_glaciated = swd < self.swd_threshold
        is_deep_moisture = wv_diff >= self.wv_threshold
        is_convective_texture = spatial_texture_std >= self.texture_var_threshold

        ci_score = 0
        if is_rapid_cooling:
            ci_score += 35
        if is_glaciated:
            ci_score += 25
        if is_deep_moisture:
            ci_score += 20
        if is_convective_texture:
            ci_score += 20
        else:
            # Cirrus penalty: if cloud is cold but flat/laminar, penalize heavily
            ci_score = max(0, ci_score - 40)

        is_ci_alert = ci_score >= 80

        return {
            "swd_diff": round(swd, 2),
            "wv_diff": round(wv_diff, 2),
            "cooling_rate_15m": round(cooling_rate_15m, 2),
            "spatial_texture_std": round(spatial_texture_std, 2),
            "is_cirrus_shield": not is_convective_texture,
            "ci_score": ci_score,
            "ci_alert": is_ci_alert,
            "status": "CONVECTIVE_INITIATION_PRECURSOR" if is_ci_alert else ("CIRRUS_CONTAMINATED" if not is_convective_texture else "STABLE")
        }


class LightningJumpDetector:
    """
    Operational 2-Sigma Lightning Jump Algorithm:
    Flags rapid surges in total flash rate that precede severe ground strikes & squalls.
    Includes Range-Efficiency calibration for distance falloff.
    """
    def __init__(self, sigma_multiplier: float = 2.0, min_flash_rate: float = 10.0, range_decay_km: float = 350.0):
        self.sigma_multiplier = sigma_multiplier
        self.min_flash_rate = min_flash_rate
        self.range_decay_km = range_decay_km

    def calibrate_range_efficiency(self, observed_fr: float, distance_km: float) -> float:
        """Calibrates flash rate against network sensitivity drop with range."""
        eff = 0.95 * math.exp(-max(0.0, distance_km) / self.range_decay_km)
        eff = max(0.35, eff)
        return observed_fr / eff

    def detect_jump(self, current_fr: float, fr_history_60m: List[float], distance_km: float = 45.0) -> Dict[str, Any]:
        """
        Calibrates flash rate for distance and computes 2-sigma jump metric.
        """
        calibrated_fr = self.calibrate_range_efficiency(current_fr, distance_km)
        calibrated_history = [self.calibrate_range_efficiency(f, distance_km) for f in fr_history_60m]

        if not calibrated_history or len(calibrated_history) < 4:
            return {
                "jump_metric": 0.0,
                "is_jump": False,
                "status": "INSUFFICIENT_HISTORY"
            }

        dfr_history = [calibrated_history[i] - calibrated_history[i-1] for i in range(1, len(calibrated_history))]
        current_dfr = calibrated_fr - calibrated_history[-1]

        mu_dfr = float(np.mean(dfr_history))
        sigma_dfr = float(np.std(dfr_history))

        if sigma_dfr < 1e-4:
            sigma_dfr = 1.0

        jump_metric = (current_dfr - mu_dfr) / sigma_dfr
        is_jump = (jump_metric >= self.sigma_multiplier) and (calibrated_fr >= self.min_flash_rate)

        return {
            "observed_flash_rate": round(current_fr, 1),
            "calibrated_flash_rate": round(calibrated_fr, 1),
            "distance_km": round(distance_km, 1),
            "rate_of_change_dfr": round(current_dfr, 2),
            "jump_metric_sigma": round(jump_metric, 2),
            "threshold_sigma": self.sigma_multiplier,
            "is_lightning_jump": is_jump,
            "threat_level": "CRITICAL_SURGE" if is_jump else ("ELEVATED" if calibrated_fr > 20 else "NORMAL")
        }


class LightningNowcastEngine:
    """
    Dedicated Lightning Nowcasting Engine:
    Predicts pre-strike lightning onset, 1km spatial ground-strike probability,
    and 0-6h flash density evolution BEFORE first strikes occur.
    Based on mixed-phase hydrometeor charge separation physics (Z > 35 dBZ above 0°C),
    cloud-top cooling rates, and NWP CAPE instability.
    """
    def __init__(self, prob_threshold: float = 0.65):
        self.prob_threshold = prob_threshold

    def predict_onset_and_density(
        self,
        radar_dbz_max: float,
        mixed_phase_dbz: float,
        cooling_rate_15m: float,
        cape_j_kg: float,
        current_flash_rate: float = 0.0,
        lead_time_min: int = 30
    ) -> Dict[str, Any]:
        """
        Computes 15-45 min pre-strike onset probability and future flash density.
        """
        z_score = max(0.0, (mixed_phase_dbz - 28.0) / 14.0)
        cooling_score = max(0.0, (-cooling_rate_15m - 0.8) / 1.5)
        cape_score = max(0.0, (cape_j_kg - 1200.0) / 1800.0)

        # Logistic strike probability model
        logit = 1.8 * z_score + 1.2 * cooling_score + 0.9 * cape_score - 2.1
        strike_prob = 1.0 / (1.0 + math.exp(-max(-6.0, min(6.0, logit))))

        # Onset lead time calculation (minutes before initial ground strike)
        if strike_prob >= self.prob_threshold and current_flash_rate < 2.0:
            onset_lead_time_min = int(round(15.0 + 30.0 * (1.0 - min(1.0, z_score))))
            onset_lead_time_min = max(15, min(45, onset_lead_time_min))
            onset_warning = True
        else:
            onset_lead_time_min = 0
            onset_warning = False

        # Forecast flash density (flashes/km^2/hr) for the target lead time
        decay_factor = math.exp(-lead_time_min / 150.0)
        proj_base_fr = (current_flash_rate * 0.4) + (strike_prob * 32.0 * min(1.0, cape_score))
        forecast_flash_density = round(max(0.0, proj_base_fr * decay_factor * 0.12), 2)

        return {
            "lead_time_min": lead_time_min,
            "strike_probability": round(strike_prob, 3),
            "is_onset_warning": onset_warning,
            "onset_lead_time_min": onset_lead_time_min,
            "forecast_flash_density_per_km2_hr": forecast_flash_density,
            "mixed_phase_dbz": round(mixed_phase_dbz, 1),
            "electrification_status": (
                "PRE_STRIKE_ONSET_ACTIVE" if onset_warning
                else ("HIGH_ELECTRIFICATION" if strike_prob >= 0.75
                else ("MODERATE_ELECTRIFICATION" if strike_prob >= 0.45 else "LOW_RISK"))
            )
        }



class VerificationMetricsCalculator:
    """
    Standard Operational Meteorological Verification Suite using 2x2 Contingency Table.
    """
    @staticmethod
    def calculate(hits: int, false_alarms: int, misses: int, correct_negs: int) -> Dict[str, float]:
        a = float(hits)
        b = float(false_alarms)
        c = float(misses)
        d = float(correct_negs)
        total = a + b + c + d

        # Critical Success Index (CSI)
        csi = a / (a + b + c) if (a + b + c) > 0 else 0.0

        # Probability of Detection (POD)
        pod = a / (a + c) if (a + c) > 0 else 0.0

        # False Alarm Ratio (FAR)
        far = b / (a + b) if (a + b) > 0 else 0.0

        # Equitable Threat Score (ETS)
        a_random = ((a + b) * (a + c)) / total if total > 0 else 0.0
        ets_denom = a + b + c - a_random
        ets = (a - a_random) / ets_denom if ets_denom > 0 else 0.0

        # Heidke Skill Score (HSS)
        expected = ((a + c) * (a + b) + (b + d) * (c + d)) / total if total > 0 else 0.0
        hss_denom = total - expected
        hss = ((a + d) - expected) / hss_denom if hss_denom > 0 else 0.0

        # Frequency Bias
        bias = (a + b) / (a + c) if (a + c) > 0 else 0.0

        return {
            "CSI": round(csi, 3),
            "POD": round(pod, 3),
            "FAR": round(far, 3),
            "ETS": round(ets, 3),
            "HSS": round(hss, 3),
            "Bias": round(bias, 3)
        }
