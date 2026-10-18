# C3 Research Dataset, v1.0 - synthetic prototype

**PRIMARY DATASET: C3_Master_5000_Daily_Market_Prices.csv — 5,000 records exactly.**
25 daily series = 5 markets × 5 species; 2025-01-01 to 2025-07-19 inclusive.

**CRITICAL: NONE OF THE DATASET ROWS ARE REAL OBSERVATIONS, OFFICIAL FISH PRICES OR LAB MEASUREMENTS.**
All market prices are generated from a transparent demand–supply structural proxy. All fish-quality kinetic parameters, logistics costs and storage temperatures are scenario assumptions. No 2025 fish-price workbook was imported. See C3_Source_Provenance.csv.

## Contents
- C3_Master_5000_Daily_Market_Prices.csv: main 5,000 model observations.
- C3_Lot_Decision_Scenarios_1250.csv: 1,250 independent synthetic fish landing decisions.
- C3_Option_Economics_5000.csv: four comparable options per same lot (sell now, wait, transport to two alternative markets).
- C3_Option_Temperature_20000_Segments.csv: four full temperature/history segments per option; all heat/damage model inputs visible.
- C3_TFT_train_28to7.npz, C3_TFT_validation_28to7.npz, C3_TFT_test_28to7.npz: leakage-aware temporal samples, price forecasts with 28-day context, 7-day horizons.
- C3_TFT_Training_Scaler.csv: fitted on train period only.
- C3_Species_Assumptions.csv: illustrative not measured species kinetics / base prices.
- C3_Market_Registry.csv, C3_Full_Data_Dictionary.csv, C3_Source_Provenance.csv, C3_Manifest.json.
- build_c3.py: full deterministic synthetic generator.
- validate_c3.py: independent recalc and integrity tests.
- C3_Dataset_Justification_Sinhala.docx: Sinhala rationale and references.

## Usage
python build_c3.py
python validate_c3.py

Use pure market master for TFT price forecasting and scenario/options/temperature for the separate decision and degradation optimization module. Avoid training TFT on columns that contain ex-post next-day/oracle prices. C2 shares Galle/Mirissa/Tangalle port IDs and Yellowfin/Skipjack concepts but no actual catch ID join exists. Do not falsely join C1 (different periods) or claim integrated empirical validation.

## Food safety
The quality proxy is *not* a microbiological safety/edibility predictor; it cannot detect histamine. Never advise selling/eating fish based only on this synthetic quality index. Temperature control and verified inspection are required.
