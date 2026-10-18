# OceanGuard AI — Scientific Limitations, Ethical Disclosures & Future Work

## 1. Ethical Overview & Academic Transparency

The development of machine learning systems for maritime applications carries significant ethical and human safety obligations. 

In accordance with rigorous academic integrity standards, this document explicitly outlines the known limitations, synthetic proxy dependencies, legal boundaries, and necessary validation prerequisites of the OceanGuard AI platform.

---

## 2. Dataset Limitations & Synthetic Proxy Features

### 2.1 Absence of Real Maritime Casualty Records
- **Context:** Sri Lankan maritime authorities do not publish open-access, micro-level sensor logs for vessel capsizing, hull broaching, or onboard fatalities due to legal and privacy protections.
- **Proxy Formulation:** The capsizing risk levels and Dynamic Risk Index ($DRI$) in `c1_trips.csv` were synthesized using semi-empirical naval architecture hydrostatic stability criteria (e.g., IMO Code on Intact Stability Resolution MSC.267(85) simplified proxies for small craft under 24m).
- **Impact:** While the Bi-LSTM model learns realistic relationships between wave steepness, wind squalls, and metacentric height ($GM$), it has **not** been benchmarked against unsimulated, real-world casualty incidents.

### 2.2 Synthetic Marine Environmental & Catch Proxies
- **Spatial Grid Data (`c2_zone_days.csv`):** Oceanographic variables (SST, Chlorophyll-a, Sea Level Anomaly, Salinity) reflect simulated spatio-temporal Gaussian distributions calibrated to seasonal monsoonal ranges in the Bay of Bengal and Laccadive Sea, rather than real-time Copernicus Marine (CMEMS) or NOAA AVHRR satellite API feeds.
- **Fish Presence:** Catch suitability indices ($HSI$) represent theoretical habitat suitability rather than verified acoustic sonar or automated logbook catch landings.

### 2.3 Synthetic Market Price & Fuel Records
- **Market Prices (`c3_market_prices.csv`):** Daily wholesale auction prices simulate seasonal supply-demand elasticities observed in Sri Lankan harbours (e.g., Galle, Negombo, Beruwala) rather than automated live transactions from the Ceylon Fisheries Harbours Corporation (CFHC).
- **Fuel Consumption (`c4_fuel_scenarios.csv`):** Fuel records were generated using ITTC-1957 skin friction and Holtrop-Mennen hydrodynamic equations regularized with standard operational noise.

---

## 3. Marine Engineering & Hydrodynamic Boundary Conditions

### 3.1 Calm-Water vs. Real-Seaway Hull Hydrodynamics
- **Bare-Hull Resistance:** The PINN model calculates frictional drag based on the ITTC-1957 correlation line assuming a smooth, clean hull. In real tropical artisanal vessels, marine biofouling (barnacles, algae, tube worms) can degrade hull hydrodynamics, increasing total resistance by 15% to 35%.
- **Propulsive Efficiency:** The model assumes an aggregate propulsive efficiency coefficient $\eta_{\text{prop}} \approx 0.55$. In practice, propulsive efficiency varies non-linearly with propeller cavitation, engine wear, gearbox reduction ratios, and wake fractions.
- **Wave Added Resistance:** Wave resistance is approximated using semi-empirical beam-wave reflection models rather than 3D boundary element boundary-value solutions (BEM) or computational fluid dynamics (CFD).

---

## 4. Biological Quality Decay Assumptions

- **Arrhenius & $Q_{10}$ Kinetics:** Spoilage modeling assumes a steady-state kinetic acceleration factor $Q_{10} = 2.2$ calibrated for tropical teleosts.
- **Microbial & Hygiene Confounders:** The model assumes proper gutting, bleeding, and initial sanitation. In practice, bacterial cross-contamination in fish holds, unwashed bilge water, or delayed icing will accelerate enzymatic breakdown beyond theoretical limits.
- **Ice Slurry Dynamics:** The model assumes constant hold temperature based on skipper entry, whereas flake ice melts over time, leading to spatial temperature gradients across the top and bottom layers of the fish hold.

---

## 5. Maritime Regulatory & Statutory Clearances Disclaimer

> [!CAUTION]
> **IMPORTANT REGULATORY NOTICE:**
> 1. OceanGuard AI is an experimental academic decision-support research prototype.
> 2. It is **NOT** a certified Electronic Chart Display and Information System (ECDIS) under IMO/SOLAS regulations.
> 3. It does **NOT** replace mandatory Global Maritime Distress and Safety System (GMDSS) equipment, Emergency Position Indicating Radio Beacons (EPIRBs), VHF marine radios, or official Sri Lankan Department of Fisheries and Aquatic Resources (DFAR) vessel monitoring systems (VMS).
> 4. Skippers, vessel owners, and harbour masters remain solely responsible for vessel seaworthiness, departure clearances, crew safety, and maritime navigation.

---

## 6. Recommendations for Future Research & Sea Trials

To transition OceanGuard AI from an academic prototype to a fully certified production marine platform, the following initiatives are recommended:

1. **IoT Sensor Sea Trials:** Deploy low-cost micro-controller telemetry boxes (ESP32 / Raspberry Pi with 6-DOF IMUs, GPS receivers, and fuel flow meters) aboard 10 pilot multi-day vessels operating out of Galle and Mirissa harbours to collect real-time motion and fuel datasets.
2. **Satellite API Integration:** Replace synthetic oceanographic matrices with live CMEMS (Copernicus) and Sentinel-3 chlorophyll and altimetry pipelines.
3. **Automated Fish Auction Feeds:** Integrate digital price reporting with CFHC harbour auction terminals to enable live, real-time market price arbitrage.
4. **Edge AI Model Quantization:** Quantize PyTorch models to ONNX Runtime / TensorFlow Lite for direct on-device execution on budget skipper smartphones.
