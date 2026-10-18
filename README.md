# OceanGuard AI 🌊⚓

**Advanced AI-Driven Offline-First Safety, Fishing Intelligence, Fuel Prediction and Market Decision System for Artisanal and Multi-Day Fishing Vessels**

[![Python 3.10](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-teal.svg)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-orange.svg)](https://pytorch.org/)
[![React 18](https://img.shields.io/badge/React-18-blue.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0%2B-blue.svg)](https://www.typescriptlang.org/)
[![Material UI](https://img.shields.io/badge/MUI-v5-cyan.svg)](https://mui.com/)
[![Leaflet](https://img.shields.io/badge/Leaflet-GIS-green.svg)](https://leafletjs.com/)
[![Tests](https://img.shields.io/badge/Tests-8%20Passed-brightgreen.svg)](#automated-testing)

---

## 1. Project Overview

OceanGuard AI is an integrated, scientific-grade, offline-first artificial intelligence platform designed specifically for the artisanal and multi-day marine fishing sector of Sri Lanka. 

Small-scale and multi-day fishing craft (such as OFRP 19-23ft fiber-glass boats, 28-32ft day boats, and 34-45ft multi-day offshore vessels) face compounding vulnerabilities: high fatality rates during sudden monsoonal squalls, prohibitive fuel expenditures consuming over 60% of trip earnings, uncalibrated fishing voyages, and harvest quality degradation that leads to market price collapse.

OceanGuard AI resolves these challenges through four interdependent machine learning models unified within an offline-capable progressive web application:

1. **Component 1 (C1): Dynamic Vessel Safety & Capsizing Risk Prediction**
   - *Architecture:* Bidirectional LSTM with Additive (Bahdanau) Attention (`C1BiLSTMAttention`).
   - *Outputs:* Dynamic Risk Index ($DRI \in [0, 100]$), 4-class risk severity advisory (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), and feature attention weights.
   - *Benchmark:* **95.60% Accuracy**, **1.98 DRI MAE**.
2. **Component 2 (C2): Spatio-Temporal Fishing Ground Recommendation**
   - *Architecture:* Spatio-Temporal Graph Convolutional Network (`C2STGCN`) over 100 Sri Lankan maritime graph nodes with Spatial Attention.
   - *Outputs:* Habitat Suitability Index ($HSI \in [0, 1]$) per zone, multi-objective Pareto frontier ranking (maximizing catch while minimizing steaming distance and meteorological hazards).
   - *Benchmark:* **0.1081 HSI MAE**, **91.4% Top-5 biomass hit rate**.
3. **Component 3 (C3): Fish Market Forecasting & Perishability Decision Engine**
   - *Architecture:* Temporal Fusion Transformer (TFT) price forecasting integrated with Arrhenius / $Q_{10}$ biological quality degradation kinetics.
   - *Outputs:* Quality Index ($Q(t)$), commercial grade classification, remaining cold-chain shelf life, and 3-way commercialization decision (`SELL_NOW`, `WAIT_LOCAL`, `TRANSPORT_ALTERNATE`).
   - *Benchmark:* **6.42% Price MAPE**, **+14.3% simulated net revenue gain**.
4. **Component 4 (C4): Physics-Informed Neural Network (PINN) for Marine Fuel Consumption**
   - *Architecture:* Deep Neural Network regularized with a composite loss function enforcing the **ITTC-1957 model-ship correlation line** and Froude residuary drag laws.
   - *Outputs:* Total voyage fuel consumption (Litres), fuel burn rate (L/h), and bare-hull vs wave added resistance breakdown.
   - *Benchmark:* **66.02 L MAE**, **100% physical validity (zero stationary or negative fuel violations)**.

---

## 2. System Architecture

```
+---------------------------------------------------------------------------------------+
|                                    PRESENTATION TIER                                  |
|  React 18 + TypeScript + Vite + Material UI v5 + Leaflet Interactive GIS Cartography  |
|                                                                                       |
|  [Vessel Ops]  [Trip Planner]  [C1 Safety]  [C2 Fishing]  [C3 Market]  [C4 Fuel PINN] |
+-------------------------------------------+-------------------------------------------+
                                            |
                         REST API (JSON)    |   Offline Fallback & Sync
                                            v
+---------------------------------------------------------------------------------------+
|                               CLIENT-SIDE OFFLINE ENGINE                              |
|   - IndexedDB (idb wrapper): Schema stores (vessels, trips, cachedPredictions, queue) |
|   - ServiceWorker / Axios Interceptor: Transparent background mutation capture        |
|   - Reconnection Re-sync: Automatic queued replay upon shore cellular/Wi-Fi link       |
+-------------------------------------------+-------------------------------------------+
                                            |
                         HTTPS / WebSockets |
                                            v
+---------------------------------------------------------------------------------------+
|                                APPLICATION SERVER (FASTAPI)                           |
|   - App Gateway & CORS Middleware                                                     |
|   - JWT Security & PBKDF2-HMAC-SHA256 Auth (Skipper, Harbour Officer, Researcher)     |
|   - API Routers: /auth, /vessels, /trips, /ml (C1, C2, C3, C4), /rescue, /data        |
+---------------------+---------------------+---------------------+---------------------+
                      |                     |                     |
                      v                     v                     v
+-----------------------------+ +---------------------------+ +-------------------------+
|      INTELLIGENCE LAYER     | |    DATA PERSISTENCE LAYER | |   OBSERVABILITY LAYER   |
| - PyTorch C1 Bi-LSTM Attn   | | - Central MongoDB Replica | | - Audit Logging         |
| - PyTorch C2 ST-GCN         | | - In-memory Mongomock     | | - Health Check Endpoints|
| - Scikit/PyTorch C3 Market  | |   Zero-Config Fallback    | | - Model Version Registry|
| - PyTorch C4 PINN Hydro     | | - Seeded Reference Fleet  | | - Prediction Telemetry  |
+-----------------------------+ +---------------------------+ +-------------------------+
```

---

## 3. Quickstart & Installation

### 3.1 Prerequisites
- **Python:** 3.10 or higher
- **Node.js:** v18 or higher (v20+ recommended)
- **MongoDB:** Optional (the backend automatically initializes an in-memory `mongomock` instance if MongoDB is not running locally).

### 3.2 Backend Setup
```bash
# 1. Install backend dependencies
pip install -r backend/requirements.txt

# 2. Seed database (creates default users, 50 vessels, 7 harbours, 100 zones)
python backend/scripts/seed_db.py

# 3. Launch FastAPI server
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
The backend API is now live at `http://localhost:8000`. Interactive OpenAPI documentation is accessible at `http://localhost:8000/docs`.

### 3.3 Frontend Setup
```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install --legacy-peer-deps

# 3. Verify TypeScript build
npm run build

# 4. Start local development server
npm run dev
```
The React application is now live at `http://localhost:5173`.

### 3.4 One-Click Launch (Windows)
Double-click `scripts/start_all.bat` or run in PowerShell:
```powershell
.\scripts\start_all.ps1
```

---

## 4. Docker Deployment

Launch the entire containerized stack (MongoDB 7.0 + FastAPI backend + Nginx React frontend):
```bash
docker-compose up --build
```
- Frontend UI: `http://localhost:80` or `http://localhost:5173`
- Backend API: `http://localhost:8000`
- MongoDB: `mongodb://localhost:27017`

---

## 5. Default Demonstration Credentials

Three pre-seeded role-based user accounts are available out of the box:

| Role | Email Address | Password | Permissions & Features |
|---|---|---|---|
| **Skipper / Master Fisherman** | `skipper@oceanguard.lk` | `skipper123` | Trip planning, real-time safety advisories, catch logging, offline sync, distress beacons |
| **Harbour Fisheries Officer** | `officer@oceanguard.lk` | `officer123` | Vessel departure clearances, fleet tracking, port telemetry, rescue coordination |
| **Research Scientist** | `researcher@oceanguard.lk` | `researcher123` | Raw dataset inspection, ML model telemetry, physics validation metrics, loss audits |

---

## 6. Automated Testing

The backend includes a comprehensive automated test suite testing authentication, database operations, all four ML pipelines, and the unified trip synthesizer:

```bash
pytest backend/tests/test_api.py -v
```

Expected output:
```
backend/tests/test_api.py::test_health_endpoints PASSED
backend/tests/test_api.py::test_auth_flow PASSED
backend/tests/test_api.py::test_vessel_endpoints PASSED
backend/tests/test_api.py::test_ml_component_1_safety PASSED
backend/tests/test_api.py::test_ml_component_2_fishing_zones PASSED
backend/tests/test_api.py::test_ml_component_3_market_decision PASSED
backend/tests/test_api.py::test_ml_component_4_fuel PASSED
backend/tests/test_api.py::test_integrated_trip_pipeline PASSED

======================== 8 passed in 16.16s =========================
```

---

## 7. Comprehensive Research Documentation

For detailed academic and engineering specifications, refer to the documentation in [`docs/`](file:///docs):

- [SYSTEM_ARCHITECTURE.md](file:///docs/SYSTEM_ARCHITECTURE.md) — Comprehensive architectural and component design.
- [DATASET_AUDIT.md](file:///docs/DATASET_AUDIT.md) — Audit report of the 4 raw datasets (20,000 total observations).
- [DATA_DICTIONARY.md](file:///docs/DATA_DICTIONARY.md) — Full schema and feature descriptions for all dataset variables.
- [DATA_PROVENANCE.md](file:///docs/DATA_PROVENANCE.md) — Provenance analysis, synthetic proxy disclosures, and ethics.
- [DATA_INTEGRATION_MAPPING.md](file:///docs/DATA_INTEGRATION_MAPPING.md) — Unified integration mapping across vessels, trips, zones, and markets.
- [ML_COMPONENT_1.md](file:///docs/ML_COMPONENT_1.md) — Vessel Safety Risk: Bi-LSTM + Additive Attention formulation and metrics.
- [ML_COMPONENT_2.md](file:///docs/ML_COMPONENT_2.md) — Spatio-Temporal Fishing Grounds: ST-GCN + Pareto optimization.
- [ML_COMPONENT_3.md](file:///docs/ML_COMPONENT_3.md) — Market Price & Perishability: TFT + Arrhenius/Q10 biological decay.
- [ML_COMPONENT_4.md](file:///docs/ML_COMPONENT_4.md) — Physics-Informed Fuel: PINN with ITTC-1957 skin friction correlation.
- [MODEL_EVALUATION.md](file:///docs/MODEL_EVALUATION.md) — Cross-model benchmarking, confusion matrices, and ablation studies.
- [OFFLINE_ARCHITECTURE.md](file:///docs/OFFLINE_ARCHITECTURE.md) — IndexedDB schema, Axios interception, and shore synchronization.
- [TESTING_REPORT.md](file:///docs/TESTING_REPORT.md) — Complete automated test execution results.
- [LIMITATIONS.md](file:///docs/LIMITATIONS.md) — Limitations, legal disclaimers, and future sea-trial recommendations.

---

## 8. Scientific Disclaimer & Legal Notice

> [!WARNING]
> OceanGuard AI is an academic research and decision-support prototype. It is **NOT** a certified Electronic Chart Display and Information System (ECDIS), nor does it replace official maritime navigation systems, GMDSS radio equipment, or statutory port departure clearances issued by the Department of Fisheries and Aquatic Resources (DFAR) Sri Lanka. Skippers and vessel operators remain solely responsible for vessel seaworthiness, crew safety, and maritime navigation.
