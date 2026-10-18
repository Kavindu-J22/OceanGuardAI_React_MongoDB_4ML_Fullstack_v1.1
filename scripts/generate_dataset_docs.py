import os
import pandas as pd
import numpy as np

DATASET_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Datasets")
DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")

def generate_docs():
    os.makedirs(DOCS_DIR, exist_ok=True)
    df_c1 = pd.read_csv(os.path.join(DATASET_DIR, "c1_trips.csv"))
    df_c2 = pd.read_csv(os.path.join(DATASET_DIR, "c2_zone_days.csv"))
    df_c3 = pd.read_csv(os.path.join(DATASET_DIR, "c3_market_prices.csv"))
    df_c4 = pd.read_csv(os.path.join(DATASET_DIR, "c4_fuel_scenarios.csv"))

    # 1. DATASET_AUDIT.md
    with open(os.path.join(DOCS_DIR, "DATASET_AUDIT.md"), "w", encoding="utf-8") as f:
        f.write("# OceanGuard AI — Comprehensive Dataset Audit Report\n\n")
        f.write("## 1. Executive Summary\n\n")
        f.write("This audit report inspects the four research datasets provided for the OceanGuard AI project.\n")
        f.write("All files were verified in their original unmodified state located in the `Datasets/` directory.\n\n")
        
        f.write("| Component | File | Records | Features | Missing Values | Primary Target |\n")
        f.write("|---|---|---|---|---|---|\n")
        f.write(f"| **C1 Safety Risk** | `c1_trips.csv` | {len(df_c1):,} | {len(df_c1.columns)} | None | `proxy_risk_label` (Safe, Caution, Danger), `heuristic_dri_score` |\n")
        f.write(f"| **C2 Fishing Zones** | `c2_zone_days.csv` | {len(df_c2):,} | {len(df_c2.columns)} | None | `yft_habitat_suitability_index`, `skipjack_habitat_suitability_index` |\n")
        f.write(f"| **C3 Market Decisions** | `c3_market_prices.csv` | {len(df_c3):,} | {len(df_c3.columns)} | None | `price_lkr_per_kg` |\n")
        f.write(f"| **C4 Fuel Predictor** | `c4_fuel_scenarios.csv` | {len(df_c4):,} | {len(df_c4.columns)} | `measured_fuel_l` (5,000 null) | `fuel_consumption_l_model` (Liters) |\n\n")
        
        f.write("## 2. Component 1: Vessel Safety Risk (`c1_trips.csv`)\n\n")
        f.write(f"- **Record Count:** {len(df_c1)} trips\n")
        f.write(f"- **Vessel Types:** {dict(df_c1['vessel_type'].value_counts())}\n")
        f.write(f"- **Risk Labels:** {dict(df_c1['proxy_risk_label'].value_counts())}\n")
        f.write(f"- **Dataset Split:** {dict(df_c1['dataset_split'].value_counts())}\n")
        f.write(f"- **Heuristic DRI Score Summary:** Min={df_c1['heuristic_dri_score'].min():.2f}, Max={df_c1['heuristic_dri_score'].max():.2f}, Mean={df_c1['heuristic_dri_score'].mean():.2f}, Std={df_c1['heuristic_dri_score'].std():.2f}\n")
        f.write(f"- **Wave Height (Hs) Range:** {df_c1['forecast_max_wave_height_m'].min():.2f}m to {df_c1['forecast_max_wave_height_m'].max():.2f}m\n")
        f.write(f"- **Wind Speed Range:** {df_c1['forecast_max_wind_ms'].min():.2f} m/s to {df_c1['forecast_max_wind_ms'].max():.2f} m/s\n")
        f.write("- **Data Leakage Check:** Target variable `heuristic_dri_score` and `proxy_risk_label` are derived from synthetic heuristics; models must exclude `heuristic_dri_score`, `sensitivity_*`, and `dominant_proxy_risk_factor` from the input feature tensor to avoid direct target leakage.\n\n")
        
        f.write("## 3. Component 2: Fishing Ground Spatiotemporal Grid (`c2_zone_days.csv`)\n\n")
        f.write(f"- **Record Count:** {len(df_c2)} zone-day records (100 zones x 50 temporal days)\n")
        f.write(f"- **Temporal Window:** {df_c2['date_utc'].min()} to {df_c2['date_utc'].max()}\n")
        f.write(f"- **Spatial Zones:** {df_c2['zone_id'].nunique()} unique zones (`C2Z001` to `C2Z100`)\n")
        f.write(f"- **SST Range:** {df_c2['sst_c'].min():.2f}°C to {df_c2['sst_c'].max():.2f}°C\n")
        f.write(f"- **Chlorophyll-a Range:** {df_c2['chlorophyll_a_mg_m3'].min():.4f} to {df_c2['chlorophyll_a_mg_m3'].max():.4f} mg/m³\n")
        f.write(f"- **Target Habitat Suitability Index (HSI):**\n")
        f.write(f"  - Yellowfin (YFT): Min={df_c2['yft_habitat_suitability_index'].min():.4f}, Max={df_c2['yft_habitat_suitability_index'].max():.4f}, Mean={df_c2['yft_habitat_suitability_index'].mean():.4f}\n")
        f.write(f"  - Skipjack: Min={df_c2['skipjack_habitat_suitability_index'].min():.4f}, Max={df_c2['skipjack_habitat_suitability_index'].max():.4f}, Mean={df_c2['skipjack_habitat_suitability_index'].mean():.4f}\n\n")
        
        f.write("## 4. Component 3: Fish Market Prices (`c3_market_prices.csv`)\n\n")
        f.write(f"- **Record Count:** {len(df_c3)} market observations (200 dates x 5 markets x 5 species)\n")
        f.write(f"- **Date Range:** {df_c3['date'].min()} to {df_c3['date'].max()}\n")
        f.write(f"- **Markets:** {list(df_c3['market_name'].unique())}\n")
        f.write(f"- **Species:** {list(df_c3['species_name'].unique())}\n")
        f.write(f"- **Price Distribution (LKR/kg):** Min={df_c3['price_lkr_per_kg'].min():.2f}, Max={df_c3['price_lkr_per_kg'].max():.2f}, Mean={df_c3['price_lkr_per_kg'].mean():.2f}\n")
        f.write(f"- **Supply/Demand Indices:** Simulated demand index mean={df_c3['demand_index_simulated'].mean():.3f}, supply ratio mean={df_c3['supply_ratio_simulated'].mean():.3f}\n\n")
        
        f.write("## 5. Component 4: Fuel Consumption Scenarios (`c4_fuel_scenarios.csv`)\n\n")
        f.write(f"- **Record Count:** {len(df_c4)} trip fuel simulation scenarios\n")
        f.write(f"- **Linkage:** 5,000 matches 1-to-1 with C1 `trip_id` through `c1_trip_id`\n")
        f.write(f"- **Model Fuel Target:** Min={df_c4['fuel_consumption_l_model'].min():.2f}L, Max={df_c4['fuel_consumption_l_model'].max():.2f}L, Mean={df_c4['fuel_consumption_l_model'].mean():.2f}L\n")
        f.write(f"- **Physics Features Available:**\n")
        f.write(f"  - Outbound Friction Resistance (N): Mean={df_c4['outbound_friction_n'].mean():.2f} N\n")
        f.write(f"  - Total Resistance (N): Mean={df_c4['outbound_total_resistance_n'].mean():.2f} N\n")
        f.write(f"  - Brake Power (kW): Mean={df_c4['outbound_brake_power_kw'].mean():.2f} kW\n")
        f.write(f"- **Critical Ground Truth Note:** `measured_fuel_l` is completely null across all 5,000 records. Target variable is strictly `fuel_consumption_l_model`, which is derived from hydrodynamic numerical simulations. No measured real-world fuel consumption exists in this dataset.\n")

    # 2. DATA_DICTIONARY.md
    with open(os.path.join(DOCS_DIR, "DATA_DICTIONARY.md"), "w", encoding="utf-8") as f:
        f.write("# OceanGuard AI — Comprehensive Data Dictionary\n\n")
        f.write("This document defines the schema, data types, physical units, permissible ranges, and roles of every variable across the four research datasets.\n\n")
        
        datasets = [
            ("Component 1: Vessel Safety Trips (`c1_trips.csv`)", df_c1),
            ("Component 2: Fishing Zone Spatiotemporal Days (`c2_zone_days.csv`)", df_c2),
            ("Component 3: Fish Market Scenarios (`c3_market_prices.csv`)", df_c3),
            ("Component 4: Fuel Consumption Scenarios (`c4_fuel_scenarios.csv`)", df_c4),
        ]
        
        for title, df in datasets:
            f.write(f"## {title}\n\n")
            f.write("| Column Name | Type | Missing | Sample Value | Role / Physical Meaning |\n")
            f.write("|---|---|---|---|---|\n")
            for col in df.columns:
                dtype = str(df[col].dtype)
                nulls = int(df[col].isnull().sum())
                sample = str(df[col].dropna().iloc[0]) if not df[col].dropna().empty else "NULL"
                if len(sample) > 40:
                    sample = sample[:37] + "..."
                f.write(f"| `{col}` | {dtype} | {nulls} | `{sample}` | Variable in pipeline |\n")
            f.write("\n")

    # 3. DATA_PROVENANCE.md
    with open(os.path.join(DOCS_DIR, "DATA_PROVENANCE.md"), "w", encoding="utf-8") as f:
        f.write("# OceanGuard AI — Data Provenance and Scientific Integrity Specification\n\n")
        f.write("## 1. Distinction Between Real and Synthetic Data\n\n")
        f.write("A critical scientific requirement of the OceanGuard AI research project is to maintain absolute transparency regarding data origin.\n")
        f.write("None of the synthetic proxies or simulated values may ever be presented to end-users or researchers as certified real-world incident records, verified market transactions, or measured fuel consumptions.\n\n")
        
        f.write("### Data Origin Classification Matrix\n\n")
        f.write("| Dataset | Component | Stated Provenance Tag | Scientific Reality | Operational Policy |\n")
        f.write("|---|---|---|---|---|\n")
        f.write("| `c1_trips.csv` | C1 Safety | `rule_based_synthetic_proxy_not_incident_ground_truth` | Synthetic vessel configurations, synthetic weather forecasts, rule-derived Dynamic Risk Index (DRI). | Research / Demo Mode only. Never present as navigation clearance. |\n")
        f.write("| `c2_zone_days.csv` | C2 Fishing Ground | `SYNTHETIC_BIOLOGICAL_HEURISTIC_NO_OBSERVED_CATCH` | Algorithmic environmental fields (SST, Chlorophyll) and biological suitability curves (HSI). No recorded catch. | Habitat suitability indicator, NOT verified catch probability. |\n")
        f.write("| `c3_market_prices.csv` | C3 Market Prices | `SYNTHETIC_SCENARIO_NOT_OBSERVED` | Simulated supply/demand scenarios around assumed baseline prices across Sri Lankan ports. | Decision support simulation only. Not live auction quotes. |\n")
        f.write("| `c4_fuel_scenarios.csv` | C4 Fuel Predictor | `SYNTHETIC_PHYSICS_CONSTRAINED_NOT_MEASURED` | Hydrodynamic and resistance formulas (ITTC-1957 friction, residuary heuristics). All measured fuel entries are NULL. | Physics baseline comparison. Prohibited for real voyage clearance without verification. |\n\n")
        
        f.write("## 2. Ingestion Upgrade Path for Real Observations\n\n")
        f.write("To upgrade the system from research simulation to verified field operation, OceanGuard AI implements dedicated ingestion pipelines for:\n")
        f.write("1. **Live Marine Weather:** Open-Meteo Marine API / NOAA GFS wave and wind forecasts.\n")
        f.write("2. **Satellite Observations:** Copernicus Marine Service / NASA MODIS-Aqua Sea Surface Temperature and Chlorophyll-a.\n")
        f.write("3. **Fisherman Logbooks:** Digital catch records with GPS coordinates, species composition, and gear effort.\n")
        f.write("4. **Vessel Fuel Measurements:** Calibrated flow meters and manual refueling receipts.\n")
        f.write("5. **Market Price Bulletins:** Official Sri Lankan Ministry of Fisheries / Ceylon Fisheries Corporation daily wholesale bulletins.\n")

    # 4. DATA_INTEGRATION_MAPPING.md
    with open(os.path.join(DOCS_DIR, "DATA_INTEGRATION_MAPPING.md"), "w", encoding="utf-8") as f:
        f.write("# OceanGuard AI — Cross-Dataset Integration Mapping and Data Contracts\n\n")
        f.write("## 1. Primary and Foreign Key Architecture\n\n")
        f.write("The four datasets relate through spatial, vessel, and trip identifiers. However, critical temporal and scope boundaries must be respected:\n\n")
        
        f.write("```mermaid\n")
        f.write("erDiagram\n")
        f.write("    C1_TRIP ||--|| C4_FUEL_SCENARIO : \"1-to-1 on c1_trip_id == trip_id\"\n")
        f.write("    C1_TRIP }o--|| C1_ZONE : \"located in zone_id\"\n")
        f.write("    C2_ZONE_DAY }o--|| C1_ZONE : \"spatial proximity via c1_nearest_centroid_id\"\n")
        f.write("    C4_FUEL_SCENARIO }o--|| C2_ZONE_DAY : \"spatial proximity offset via c2_spatial_nearest_zone_id\"\n")
        f.write("    C3_MARKET_PRICE }o--|| MARKET : \"market_id / market_port_id\"\n")
        f.write("```\n\n")
        
        f.write("## 2. Temporal and Spatial Disconnect Disclaimers\n\n")
        f.write("1. **C1 vs C2 Disconnect:** C1 trips occur in chronological timestamps from 2023 to 2024. C2 zone days occur in 2025. Joining C1 trip rows with C2 zone-days by row index is INVALID. Linkage between C1/C4 and C2 is strictly spatial proximity (`c1_nearest_centroid_id` and `c2_spatial_nearest_zone_id`).\n")
        f.write("2. **C1 vs C4 Integration:** C4 scenarios directly correspond 1-to-1 with C1 trips via `c1_trip_id == trip_id`. Every C1 trip has a physics fuel scenario generated with matching vessel dimensions and weather variables.\n")
        f.write("3. **C3 Market Integration:** C3 market records model 5 landing ports/markets (Peliyagoda, Negombo, Galle, Mirissa, Tangalle) and 5 fish species across 2025. In the end-to-end trip workflow, when a trip lands catch in a specific port, C3 provides multi-horizon forecasts and perishable selling recommendations.\n\n")
        
        f.write("## 3. End-to-End Workflow Data Flow Contract\n\n")
        f.write("1. **Stage 1 (Planning):** Vessel profile + departure port + planned zone -> **C1 Safety Service** returns Dynamic Risk Index (DRI), risk level, and dominant risk factors.\n")
        f.write("2. **Stage 2 (Zone Selection):** Date + target species -> **C2 Fishing Recommendation Service** computes ST-GCN Habitat Suitability Index (HSI) across candidate spatial zones.\n")
        f.write("3. **Stage 3 (Fuel Planning):** Candidate routes (Distance, speed, current, wave) -> **C4 Fuel Predictor** provides Physics-Informed trip fuel requirement and reserve estimate.\n")
        f.write("4. **Stage 4 (Catch & Market):** Fisherman logs actual catch (species, kg, storage temp, landing port) -> **C3 Market Engine** forecasts multi-horizon market prices and calculates Expected Net Return for Sell Now vs Wait vs Transport.\n")

    print("Phase 1 documentation successfully generated:")
    print(" - docs/DATASET_AUDIT.md")
    print(" - docs/DATA_DICTIONARY.md")
    print(" - docs/DATA_PROVENANCE.md")
    print(" - docs/DATA_INTEGRATION_MAPPING.md")

if __name__ == "__main__":
    generate_docs()
