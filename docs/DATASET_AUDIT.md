# OceanGuard AI — Comprehensive Dataset Audit Report

## 1. Executive Summary

This audit report inspects the four research datasets provided for the OceanGuard AI project.
All files were verified in their original unmodified state located in the `Datasets/` directory.

| Component | File | Records | Features | Missing Values | Primary Target |
|---|---|---|---|---|---|
| **C1 Safety Risk** | `c1_trips.csv` | 5,000 | 42 | None | `proxy_risk_label` (Safe, Caution, Danger), `heuristic_dri_score` |
| **C2 Fishing Zones** | `c2_zone_days.csv` | 5,000 | 34 | None | `yft_habitat_suitability_index`, `skipjack_habitat_suitability_index` |
| **C3 Market Decisions** | `c3_market_prices.csv` | 5,000 | 22 | None | `price_lkr_per_kg` |
| **C4 Fuel Predictor** | `c4_fuel_scenarios.csv` | 5,000 | 64 | `measured_fuel_l` (5,000 null) | `fuel_consumption_l_model` (Liters) |

## 2. Component 1: Vessel Safety Risk (`c1_trips.csv`)

- **Record Count:** 5000 trips
- **Vessel Types:** {'OFRP': 2675, 'IDAY': 1383, 'IMUL': 942}
- **Risk Labels:** {'Safe': 3685, 'Caution': 1218, 'Danger': 97}
- **Dataset Split:** {'train': 3500, 'validation': 750, 'test': 750}
- **Heuristic DRI Score Summary:** Min=0.45, Max=80.69, Mean=26.32, Std=15.74
- **Wave Height (Hs) Range:** 0.18m to 4.33m
- **Wind Speed Range:** 1.08 m/s to 30.06 m/s
- **Data Leakage Check:** Target variable `heuristic_dri_score` and `proxy_risk_label` are derived from synthetic heuristics; models must exclude `heuristic_dri_score`, `sensitivity_*`, and `dominant_proxy_risk_factor` from the input feature tensor to avoid direct target leakage.

## 3. Component 2: Fishing Ground Spatiotemporal Grid (`c2_zone_days.csv`)

- **Record Count:** 5000 zone-day records (100 zones x 50 temporal days)
- **Temporal Window:** 2025-01-01 to 2025-02-19
- **Spatial Zones:** 100 unique zones (`C2Z001` to `C2Z100`)
- **SST Range:** 26.99°C to 29.05°C
- **Chlorophyll-a Range:** 0.0802 to 0.7624 mg/m³
- **Target Habitat Suitability Index (HSI):**
  - Yellowfin (YFT): Min=0.6042, Max=0.8865, Mean=0.7672
  - Skipjack: Min=0.5380, Max=0.8763, Mean=0.7224

## 4. Component 3: Fish Market Prices (`c3_market_prices.csv`)

- **Record Count:** 5000 market observations (200 dates x 5 markets x 5 species)
- **Date Range:** 2025-01-01 to 2025-07-19
- **Markets:** ['Peliyagoda Central Fish Market', 'Negombo (scenario market)', 'Galle (scenario market)', 'Mirissa (scenario market)', 'Tangalle (scenario market)']
- **Species:** ['Skipjack tuna', 'Yellowfin tuna', 'Indian mackerel', 'Sardine (generic scenario)', 'Seer fish / king mackerel (generic)']
- **Price Distribution (LKR/kg):** Min=330.67, Max=2522.74, Mean=1058.25
- **Supply/Demand Indices:** Simulated demand index mean=0.977, supply ratio mean=0.995

## 5. Component 4: Fuel Consumption Scenarios (`c4_fuel_scenarios.csv`)

- **Record Count:** 5000 trip fuel simulation scenarios
- **Linkage:** 5,000 matches 1-to-1 with C1 `trip_id` through `c1_trip_id`
- **Model Fuel Target:** Min=2.32L, Max=3626.28L, Mean=227.11L
- **Physics Features Available:**
  - Outbound Friction Resistance (N): Mean=483.63 N
  - Total Resistance (N): Mean=3116.61 N
  - Brake Power (kW): Mean=19.52 kW
- **Critical Ground Truth Note:** `measured_fuel_l` is completely null across all 5,000 records. Target variable is strictly `fuel_consumption_l_model`, which is derived from hydrodynamic numerical simulations. No measured real-world fuel consumption exists in this dataset.
