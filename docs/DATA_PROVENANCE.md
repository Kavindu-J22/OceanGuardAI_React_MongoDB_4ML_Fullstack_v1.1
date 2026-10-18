# OceanGuard AI — Data Provenance and Scientific Integrity Specification

## 1. Distinction Between Real and Synthetic Data

A critical scientific requirement of the OceanGuard AI research project is to maintain absolute transparency regarding data origin.
None of the synthetic proxies or simulated values may ever be presented to end-users or researchers as certified real-world incident records, verified market transactions, or measured fuel consumptions.

### Data Origin Classification Matrix

| Dataset | Component | Stated Provenance Tag | Scientific Reality | Operational Policy |
|---|---|---|---|---|
| `c1_trips.csv` | C1 Safety | `rule_based_synthetic_proxy_not_incident_ground_truth` | Synthetic vessel configurations, synthetic weather forecasts, rule-derived Dynamic Risk Index (DRI). | Research / Demo Mode only. Never present as navigation clearance. |
| `c2_zone_days.csv` | C2 Fishing Ground | `SYNTHETIC_BIOLOGICAL_HEURISTIC_NO_OBSERVED_CATCH` | Algorithmic environmental fields (SST, Chlorophyll) and biological suitability curves (HSI). No recorded catch. | Habitat suitability indicator, NOT verified catch probability. |
| `c3_market_prices.csv` | C3 Market Prices | `SYNTHETIC_SCENARIO_NOT_OBSERVED` | Simulated supply/demand scenarios around assumed baseline prices across Sri Lankan ports. | Decision support simulation only. Not live auction quotes. |
| `c4_fuel_scenarios.csv` | C4 Fuel Predictor | `SYNTHETIC_PHYSICS_CONSTRAINED_NOT_MEASURED` | Hydrodynamic and resistance formulas (ITTC-1957 friction, residuary heuristics). All measured fuel entries are NULL. | Physics baseline comparison. Prohibited for real voyage clearance without verification. |

## 2. Ingestion Upgrade Path for Real Observations

To upgrade the system from research simulation to verified field operation, OceanGuard AI implements dedicated ingestion pipelines for:
1. **Live Marine Weather:** Open-Meteo Marine API / NOAA GFS wave and wind forecasts.
2. **Satellite Observations:** Copernicus Marine Service / NASA MODIS-Aqua Sea Surface Temperature and Chlorophyll-a.
3. **Fisherman Logbooks:** Digital catch records with GPS coordinates, species composition, and gear effort.
4. **Vessel Fuel Measurements:** Calibrated flow meters and manual refueling receipts.
5. **Market Price Bulletins:** Official Sri Lankan Ministry of Fisheries / Ceylon Fisheries Corporation daily wholesale bulletins.
