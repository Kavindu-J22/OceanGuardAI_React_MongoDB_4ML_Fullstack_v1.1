C1 | VESSEL SAFETY | 5000-RECORD PHYSICS-CONSTRAINED SYNTHETIC DATASET

1. C1_Master_5000_Trips.csv: 5,000 synthetic trip decisions (one row per trip).
2. C1_BiLSTM_Weather_60000_Steps.csv: 12 simulated forecast steps for each trip.
3. C1_Vessel_Registry_250.csv: 250 synthetic hull profiles.
4. C1_Data_Dictionary.csv: machine-readable variables and units.
5. C1_Method_and_Provenance.json: source links, assumptions and weights.
6. C1_Validation_Report.json: actual tests run and distributions.
7. generate_c1.py: reproduces every data file deterministically.
8. C1_Dataset_Justification_Sinhala.docx: Sinhala methodological explanation.

IMPORTANT: This IS NOT measured marine weather, observed accident data, validated seaworthiness certification, real hull specifications, nor a real-world risk probability.
Safe/Caution/Danger are SYNTHETIC PROXY labels computed from transparent, uncalibrated heuristics.
FAO/IMO sources supply qualitative context; they DO NOT endorse the numeric cutoffs or arbitrary vessel dimensions.
Archive data are not downloaded in this build. Need official measurements and expert labels before operational adoption.

Bi-LSTM input: join master by trip_id to 12 ordered steps, exclude heuristic_risk/score/label/provenance/scenario and all future-unknown signals.
For experiment, use synthetic forecast covariates and vessel geometry/weight, train using train split, tune with validation, hold test untouched.

9. C1_BiLSTM_Model_Ready_5000.npz: model-ready train-normalized arrays (5000,12,10) weather + (5000,11) vessel features.
10. prepare_c1_tensors.py and C1_BiLSTM_Feature_Manifest.json: preprocessing and feature specification.
