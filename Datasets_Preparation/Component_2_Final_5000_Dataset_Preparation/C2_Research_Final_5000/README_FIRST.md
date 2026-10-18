# Component 2 | ST-GCN Fishing Habitat Proxy Dataset

**SYNTHETIC PROTOTYPE / NOT FIELD-VALIDATED / NOT FOR MARINE NAVIGATION**

Main file: `C2_Master_5000_ZoneDays.csv` (100 synthetic zones x 50 consecutive dates = 5,000).
The *scores* and synthetic pseudo-probabilities **DO NOT measure real probability of catching fish**.

Files:
- `C2_Master_5000_ZoneDays.csv`: exactly 5,000 spatial-day rows, yellowfin and skipjack surrogate suitability.
- `C2_Zone_Registry_100.csv`: stable zone coordinates and spatial C1 crosswalk.
- `C2_Graph_Edges_360.csv`: directed 4-neighbour adjacency edge list.
- `C2_Port_Scenarios.csv`: demonstration departure ports, approximate coordinates.
- `C2_STGCN_Model_Ready_43_Windows.npz`: X [43,7,100,5], targets [43,100,2], adjacency [100,100]; 29/7/7 target-date split.
- `C2_Pareto_Example_Recommendations.csv`: exact non-dominated zone sets for two species/three port scenarios on final day; NOT navigational recommendations.
- `C2_Method_Provenance_and_Parameters.json`: explicit model, physics, coefficients, citations, data limitations.
- `C2_Independent_QA_and_Baseline.json`: deterministic QA and next-day persistence baseline; not field validation.
- `C2_Data_Dictionary.csv`: all field definitions.
- `generate_c2.py`: reproducible generator, use Python + NumPy; `python generate_c2.py`.
- `C2_Dataset_Justification_Sinhala.docx`: in-depth Sinhala report.

Satellite sources are documented as **sources to fetch in a next empirical phase**, not present in the synthetic CSV. The biological suitability coefficients, speed, route factor, consumption and fuel price are educational assumptions, NOT scientifically fitted values. Google Earth/coastline/bathymetry/EEZ restriction and safety constraints have not been checked.

Deployment gates: join C1 actual safety risk (weather-vessel), collect legally cleared fishing areas and port coordinates, integrate C4 vessel-calibrated fuel model, and empirically train/calibrate labels against catch+effort logbooks (CPUE).
