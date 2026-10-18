"""
OceanGuard AI — Standalone ML Services Command-Line Tester
Enables direct, separate execution and testing of C1, C2, C3, and C4 deep learning pipelines.
"""

import os
import sys
import argparse
import json

# Setup backend import path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, "backend"))

from app.ml.component_1_safety.predict import c1_predictor
from app.ml.component_2_fishing.predict import c2_predictor
from app.ml.component_3_market.predict import c3_predictor
from app.ml.component_4_fuel.predict import c4_predictor

def test_c1():
    print("\n" + "="*70)
    print("[COMPONENT 1] Vessel Safety Risk Prediction (Bi-LSTM + Attention)")
    print("="*70)
    sample_input = {
        "vessel_type": "OFRP",
        "vessel_length_m": 6.8,
        "vessel_beam_m": 1.9,
        "lightship_mass_kg": 980.0,
        "payload_mass_kg": 650.0,
        "assumed_payload_limit_kg": 1200.0,
        "assumed_lightship_freeboard_m": 0.85,
        "forecast_max_wind_ms": 14.5,
        "forecast_max_gust_ms": 18.0,
        "forecast_max_wave_height_m": 2.2,
        "forecast_min_pressure_hpa": 1008.0,
        "worst_wave_peak_period_s": 8.5,
        "worst_wave_steepness": 0.025,
        "worst_lateral_wind_force_proxy_n": 950.0
    }
    result = c1_predictor.predict(sample_input)
    print(json.dumps(result, indent=2))
    return result

def test_c2():
    print("\n" + "="*70)
    print("[COMPONENT 2] Spatiotemporal Fishing Ground Recommendation (ST-GCN + Pareto)")
    print("="*70)
    result = c2_predictor.recommend_zones(
        departure_port_id="P_GALLE",
        target_species="SP_YELLOWFIN",
        max_distance_km=140.0
    )
    print(f"Top Recommended Zone: {result[0]['zone_id']} | Distance: {result[0]['distance_km']} km | HSI: {result[0]['habitat_suitability_index']}")
    print(f"Rank-1 Pareto Recommended Zones Found: {len(result)}")
    print(json.dumps(result[:2], indent=2))
    return result

def test_c3():
    print("\n" + "="*70)
    print("[COMPONENT 3] Market Price Forecast & Arrhenius Spoilage Engine")
    print("="*70)
    result = c3_predictor.predict_market_decision(
        species_id="SP_YELLOWFIN",
        catch_kg=400.0,
        current_port_id="P_GALLE",
        storage_temp_c=1.5,
        hours_stored=16.0
    )
    print(json.dumps(result, indent=2))
    return result

def test_c4():
    print("\n" + "="*70)
    print("[COMPONENT 4] Physics-Informed Fuel Predictor (PINN + ITTC-1957)")
    print("="*70)
    sample_input = {
        "speed_knots": 8.5,
        "displacement_tons": 18.0,
        "length_overall_m": 12.0,
        "beam_m": 3.8,
        "draft_m": 1.4,
        "significant_wave_height_m": 1.6,
        "peak_wave_period_s": 7.5,
        "wind_speed_ms": 11.0,
        "relative_wind_angle_deg": 45.0,
        "current_speed_ms": 0.6,
        "duration_hours": 48.0
    }
    result = c4_predictor.predict(sample_input)
    print(json.dumps(result, indent=2))
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test OceanGuard AI ML Services Separately")
    parser.add_argument("--component", choices=["c1", "c2", "c3", "c4", "all"], default="all",
                        help="Specify ML component to run (c1, c2, c3, c4, or all)")
    args = parser.parse_args()

    if args.component in ["c1", "all"]:
        test_c1()
    if args.component in ["c2", "all"]:
        test_c2()
    if args.component in ["c3", "all"]:
        test_c3()
    if args.component in ["c4", "all"]:
        test_c4()
    print("\n[SUCCESS] All requested ML inference services executed successfully.\n")
