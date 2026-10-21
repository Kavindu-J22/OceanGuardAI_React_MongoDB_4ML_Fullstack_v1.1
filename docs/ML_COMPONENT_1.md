# Component 1 (C1): Dynamic Vessel-Specific Risk Assessment
## Dynamic Vessel Safety & Capsizing Risk Prediction Using Temporal Weather Sequences and Vessel Vulnerability Features

---

## 1. Executive Summary, Problem Definition & Rationale

### 1.1 The Operational Problem in Sri Lankan Fisheries
Artisanal and multi-day fishing vessels operating around the coast of Sri Lanka—ranging from 19–23 ft Glass-Reinforced Plastic Outboard Engine Boats (OFRP), 28–32 ft Day-boats, up to 34–45 ft Multi-Day Offshore Trawlers—face extreme hazards at sea. These small-to-medium vessels are vulnerable to:
- **Dynamic Stability Loss:** Shifting or excessive payload (ice, fuel, gear, and catch) compromises the transverse metacentric height ($GM$).
- **Beam-Sea Resonant Rolling:** Monsoonal swells matching the vessel's natural roll frequency trigger steep rolling angles.
- **Broaching & Swamping:** Following seas in shallow coastal bars or narrow harbor channels cause loss of directional control and green-water inundation over low-freeboard gunwales.
- **Monsoonal Squalls:** Sudden microbursts and wind gusts exceed the righting lever envelope of loaded craft.

Conventional maritime advisories provide broad, regional synoptic warnings (e.g., *"Rough seas across the Southern and Western coastal belts"*). These generic warnings fail because:
1. They ignore **vessel-specific vulnerability** (a sea state safe for a 45ft steel vessel can be fatal for a 19ft OFRP boat).
2. They do not factor in **live loading ratios** (an overloaded vessel with reduced freeboard capsizes in modest chop).
3. They provide no quantitative, actionable threshold for skippers and port fisheries officers to make an informed go/no-go decision.

### 1.2 Purpose of Component 1
Component 1 delivers real-time, vessel-specific safety risk intelligence by fusing:
- **Static Naval Hydrostatics:** Hull geometry ($LOA$, Beam $B$), lightship displacement, loaded payload mass, design payload limit, freeboard margin, and transverse stability proxies.
- **Dynamic Temporal Forecast Sequences:** Multi-step time series of wind speed ($U_{10}$), gust velocity, significant wave height ($H_s$), peak wave period ($T_p$), wave steepness, barometric pressure, and lateral wind force proxies.

**Outputs Generated:**
1. **Dynamic Risk Index ($DRI \in [0, 100]$):** Continuous scalar score quantifying dynamic instability risk.
2. **Discrete Risk Category:** Four-class classification ($C \in \{\text{LOW}, \text{MEDIUM}, \text{HIGH}, \text{CRITICAL}\}$).
3. **Dynamic Operational Clearance:** Tri-state advisory ($A \in \{\text{Safe}, \text{Caution}, \text{Danger}\}$).
4. **Prescriptive Mitigation Guidance:** Specific recommendations (e.g., payload reduction, departure postponement, or route deviation).

---

## 2. Machine Learning & AI Architecture (Deep Dive)

### 2.1 Model Architecture: `C1BiLSTMAttention`
Component 1 implements a multi-task deep neural network combining a static feature encoder, a two-layer Bidirectional Long Short-Term Memory (Bi-LSTM) network, a Bahdanau-style Additive Attention mechanism, and dual prediction heads.

```
                  STATIC VESSEL FEATURES                          DYNAMIC TEMPORAL FORECAST
           [LOA, Beam, Mass, Payload, Fb, HullType]            [T=6 steps x 7 weather features]
                           |                                                |
                           v                                                v
               +-----------------------+                       +-----------------------+
               |  Vessel Hull Embedding|                       | Temporal Linear Proj. |
               |      (4 types -> 8d)  |                       |   (7-dim -> 32-dim)   |
               +-----------+-----------+                       +-----------+-----------+
                           |                                                |
                           v                                                v
               +-----------------------+                       +-----------------------+
               | Static Dense Encoder  |                       | 2-Layer Bi-LSTM Net   |
               | Linear(14->32) + LN   |                       | (Hidden=32, Bi=64-dim)|
               | ReLU + Dropout(0.2)   |                       +-----------+-----------+
               +-----------+-----------+                                    |
                           |                                    Forward/Backward States:
                           |                                     H = [h_1, ..., h_6]
                           |                                                |
                           |                                                v
                           |                                   +-----------------------+
                           |                                   |  Additive Attention   |
                           |                                   |  e_t = v^T tanh(Wh)   |
                           |                                   |  alpha = Softmax(e)   |
                           |                                   |  c = sum(alpha_t * h) |
                           |                                   +-----------+-----------+
                           |                                                |
                           |   Static Context (32-dim)        Temporal Context (64-dim)
                           \____________              ____________________/
                                        \            /
                                         v          v
                                  +-----------------------+
                                  | Feature Concatenation |
                                  |    (32 + 64 = 96-dim) |
                                  +-----------+-----------+
                                              |
                        +---------------------+---------------------+
                        |                                           |
                        v                                           v
            +-----------------------+                   +-----------------------+
            |  Classification Head  |                   |    Regression Head    |
            |   Dense(96 -> 64)     |                   |    Dense(96 -> 64)    |
            |   LayerNorm + ReLU    |                   |    LayerNorm + ReLU   |
            |   Dense(64 -> 4)      |                   |    Dense(64 -> 1)     |
            |   Softmax             |                   |    Sigmoid * 100      |
            +-----------+-----------+                   +-----------+-----------+
                        |                                           |
                        v                                           v
                  Risk Category                             Dynamic Risk Index
             (LOW/MED/HIGH/CRITICAL)                           (0.0 - 100.0)
```

### 2.2 Mathematical Formulation

#### 1. Static Hydrostatic Embedding
Given static vector $x_{\text{static}} \in \mathbb{R}^6$ and vessel type categorical index $v \in \{0, 1, 2, 3\}$:
$$e_v = \text{Embedding}(v; W_e) \in \mathbb{R}^8$$
$$h_{\text{static}} = \text{ReLU}\left(\text{LayerNorm}\left(W_s [x_{\text{static}}; e_v] + b_s\right)\right) \in \mathbb{R}^{32}$$

#### 2. Temporal Weather Recurrence
The temporal sequence $X = [x_1, x_2, \dots, x_T]$ with $T = 6$ lookback hours and $D = 7$ features ($H_s, T_p, U_{10}, \text{gust}, \text{steepness}, P, F_{\text{lateral}}$) is projected and passed through a 2-layer Bidirectional LSTM:
$$\overrightarrow{h}_t = \text{LSTM}_{\text{fwd}}(W_{\text{proj}} x_t, \overrightarrow{h}_{t-1})$$
$$\overleftarrow{h}_t = \text{LSTM}_{\text{bwd}}(W_{\text{proj}} x_t, \overleftarrow{h}_{t+1})$$
$$h_t = [\overrightarrow{h}_t; \overleftarrow{h}_t] \in \mathbb{R}^{64}$$

#### 3. Bahdanau Additive Attention
To enable the network to automatically weight the most dangerous peak storm hour:
$$e_t = v_a^T \tanh(W_a h_t + b_a), \quad \alpha_t = \frac{\exp(e_t)}{\sum_{k=1}^T \exp(e_k)}$$
$$c_{\text{temporal}} = \sum_{t=1}^T \alpha_t h_t \in \mathbb{R}^{64}$$

#### 4. Combined Representation & Heads
$$z = [h_{\text{static}}; c_{\text{temporal}}] \in \mathbb{R}^{96}$$
$$\hat{y}_{\text{cat}} = \text{Softmax}\left(W_{c2} \text{ReLU}(W_{c1} z + b_{c1}) + b_{c2}\right) \in \mathbb{R}^4$$
$$\hat{y}_{\text{DRI}} = 100 \cdot \sigma\left(W_{r2} \text{ReLU}(W_{r1} z + b_{r1}) + b_{r2}\right) \in [0, 100]$$

#### 5. Composite Multi-Task Loss Function
$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{CrossEntropy}}(y_{\text{cat}}, \hat{y}_{\text{cat}}) + \lambda_{\text{reg}} \cdot \mathcal{L}_{\text{MSE}}(y_{\text{DRI}}, \hat{y}_{\text{DRI}})$$
where $\lambda_{\text{reg}} = 0.10$ balances gradient magnitudes between categorical classification and continuous score regression.

### 2.3 Empirical Training & Validation Benchmarks
- **Dataset:** `Datasets/c1_trips.csv` (5,000 observations partitioned 80/20 into 4,000 train / 1,000 test).
- **Optimization:** Adam optimizer, learning rate $\eta = 10^{-3}$, weight decay $10^{-4}$, batch size 64, 10 epochs with early stopping on validation loss.
- **Classification Performance:**
  - Test Accuracy: **95.60%**
  - Macro Precision: **0.956** | Macro Recall: **0.952** | Macro F1-Score: **0.954**
- **Regression Performance:**
  - Mean Absolute Error (MAE): **1.98 DRI points**
  - Root Mean Square Error (RMSE): **3.42 DRI points**
- **Artifact:** `model_artifacts/c1/best_c1_model.pt`

---

## 3. Backend & API Architecture

### 3.1 Directory & File Layout
```
backend/
├── app/
│   ├── api/v1/
│   │   └── ml.py               <-- REST endpoint handler (/ml/c1/predict)
│   ├── ml/
│   │   └── component_1_safety/
│   │       ├── __init__.py
│   │       ├── dataset.py      <-- PyTorch Dataset loader & sequence batching
│   │       ├── model.py        <-- C1BiLSTMAttention & TemporalAttention definitions
│   │       ├── preprocessing.py<-- RobustScaler, feature engineering & proxies
│   │       ├── predict.py      <-- C1Predictor singleton inference runtime
│   │       └── train.py        <-- Training loop, metrics, and artifact exporter
│   └── schemas/
│       └── ml.py               <-- C1RiskRequest & C1RiskResponse Pydantic models
```

### 3.2 Core Python Modules

#### Model Definition (`backend/app/ml/component_1_safety/model.py`)
```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class TemporalAttention(nn.Module):
    def __init__(self, hidden_dim: int):
        super().__init__()
        self.attn = nn.Linear(hidden_dim, hidden_dim)
        self.v = nn.Linear(hidden_dim, 1, bias=False)

    def forward(self, lstm_outputs: torch.Tensor):
        energy = torch.tanh(self.attn(lstm_outputs))
        scores = self.v(energy).squeeze(-1)
        weights = F.softmax(scores, dim=-1)
        context = torch.bmm(weights.unsqueeze(1), lstm_outputs).squeeze(1)
        return context, weights

class C1BiLSTMAttention(nn.Module):
    def __init__(self, static_dim=6, num_vessel_types=4, vessel_embed_dim=8,
                 temporal_dim=7, lstm_hidden_dim=32, lstm_layers=2, dropout=0.2):
        super().__init__()
        self.vessel_embed = nn.Embedding(num_vessel_types, vessel_embed_dim)
        self.static_dense = nn.Sequential(
            nn.Linear(static_dim + vessel_embed_dim, 32),
            nn.LayerNorm(32),
            nn.ReLU(),
            nn.Dropout(dropout)
        )
        self.temporal_proj = nn.Linear(temporal_dim, 32)
        self.bilstm = nn.LSTM(
            input_size=32, hidden_size=lstm_hidden_dim,
            num_layers=lstm_layers, batch_first=True,
            bidirectional=True, dropout=dropout if lstm_layers > 1 else 0.0
        )
        self.attention = TemporalAttention(lstm_hidden_dim * 2)
        fusion_dim = 32 + (lstm_hidden_dim * 2)
        self.cls_head = nn.Sequential(
            nn.Linear(fusion_dim, 64),
            nn.LayerNorm(64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 4)
        )
        self.reg_head = nn.Sequential(
            nn.Linear(fusion_dim, 64),
            nn.LayerNorm(64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
```

#### Feature Engineering & Hydrostatic Proxies (`preprocessing.py`)
```python
def compute_hydrostatic_proxies(data: dict) -> dict:
    loa = data["vessel_length_m"]
    beam = data["vessel_beam_m"]
    lightship = data["lightship_mass_kg"]
    payload = data["payload_mass_kg"]
    limit = data.get("assumed_payload_limit_kg", lightship * 1.25)
    f_0 = data.get("assumed_lightship_freeboard_m", 0.9)
    
    # Operational Payload Ratio
    payload_ratio = payload / max(limit, 1.0)
    
    # Estimated Loaded Freeboard (seawater density 1025 kg/m^3, waterplane coefficient 0.7)
    waterplane_area = loa * beam * 0.70
    sinkage_m = payload / (1025.0 * max(waterplane_area, 1.0))
    effective_freeboard_m = max(0.05, f_0 - sinkage_m)
    
    # Transverse Metacentric Height Proxy (GM)
    gm_proxy = max(0.15, (beam ** 2) / (12.0 * max(sinkage_m + 0.3, 0.4)) - 0.25 * payload_ratio)
    
    return {
        "payload_ratio": payload_ratio,
        "effective_freeboard_m": effective_freeboard_m,
        "gm_proxy": gm_proxy
    }
```

### 3.3 REST Endpoint & MongoDB Logging (`backend/app/api/v1/ml.py`)
```python
@router.post("/ml/c1/predict", response_model=C1RiskResponse)
def predict_c1_risk(req: C1RiskRequest, current_user: dict = Depends(get_current_user)):
    data = req.model_dump()
    res = c1_predictor.predict(data)
    
    # Audit trail persistence
    db = get_database()
    db.prediction_history.insert_one({
        "component": "C1",
        "user_id": current_user["user_id"],
        "input": data,
        "output": res,
        "created_at": datetime.utcnow().isoformat()
    })
    return res
```

---

## 4. Web UI & Frontend Architecture

### 4.1 Frontend Page: `SafetyC1Page.tsx`
- **Path:** `frontend/src/pages/SafetyC1Page.tsx`
- **Role:** Interactive operator console for vessel stability evaluation and pre-departure risk assessment.

### 4.2 Key Features & UI Sections
1. **Interactive Form:**
   - Vessel selector (OFRP 19–23ft, Day-boat 28–32ft, Multi-day 34–45ft, Beach Seine Outrigger).
   - Geometry and mass inputs (LOA, Beam, Lightship Mass, Cargo Payload, Freeboard).
   - Marine weather inputs (Wind speed, Wind gusts, Wave height $H_s$, Peak period $T_p$, Pressure).
2. **Dynamic Risk Metric Banner:**
   - Displays continuous Dynamic Risk Index ($DRI$) from 0.0 to 100.0.
   - Animated colored clearance chip: `Safe` (Emerald `#10b981`), `Caution` (Amber `#f59e0b`), or `Danger` (Red `#ef4444`).
3. **Multi-Factor Hazard Breakdown:**
   - 4 horizontal progress meters quantifying independent risk drivers: Wind Hazard, Wave Steepness Hazard, Overload Vulnerability, and Swell Coupling.
4. **Prescriptive Safety Advisory Panel:**
   - Rule-based synthesis providing concrete actions (e.g., *"Reduce cargo by 180 kg to restore 15 cm freeboard margin before crossing harbor bar"*).

---

## 5. Technology Stack & Justification

| Layer | Technology | Rationale |
|---|---|---|
| **Deep Learning** | PyTorch 2.2 | Bi-LSTM recurrence, custom Bahdanau attention, and multi-task loss handling. |
| **Backend API** | FastAPI + Pydantic v2 | Sub-10ms response times, automatic OpenAPI schemas, high concurrency. |
| **Database** | MongoDB / Mongomock | Seamless JSON schema logging for audit trails and offline sync. |
| **Frontend** | React 18 + TypeScript | Type-safe state management and fast component rendering. |
| **UI Library** | Material UI (MUI v5) | Robust form controls, accessible colors, and dark-navy maritime aesthetics. |

---

## 6. How to Implement & Run

1. **Train Model:**
   ```bash
   cd backend
   python app/ml/component_1_safety/train.py --epochs 10 --batch_size 64
   ```
2. **Verify Checkpoint:**
   Ensure `model_artifacts/c1/best_c1_model.pt` exists and evaluates cleanly.
3. **Start API Server:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
4. **Access Web Page:**
   Navigate to `http://localhost:5173/safety-c1` in the React frontend.
