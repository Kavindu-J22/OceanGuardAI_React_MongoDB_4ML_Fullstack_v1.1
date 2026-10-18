# Component 1 (C1): Dynamic Vessel Safety & Capsizing Risk Prediction

## 1. Scientific Overview & Problem Formulation

Artisanal and multi-day fishing vessels in Sri Lanka (e.g., Outrigger Canoes, OFRP / 19-23ft fiber-glass boats, 28-32ft day-boats, and 34-45ft multi-day offshore trawlers) are vulnerable to dynamic stability loss, beam-sea rolling, broaching, and sudden monsoonal squalls.

Component 1 delivers real-time safety risk assessment by processing multi-modal time-series inputs:
1. **Marine Hydro-Meteorology:** Significant wave height ($H_s$), peak wave period ($T_p$), wind speed ($U_{10}$), wind gusts, surface current speed, and swell angle relative to vessel heading.
2. **Naval Hydrostatics:** Vessel length overall ($LOA$), beam ($B$), freeboard margin ($F_b$), operational loading ratio, and transverse metacentric height ($GM$).

The model outputs:
- **Dynamic Risk Index (DRI):** Continuous scalar risk score $S_{DRI} \in [0, 100]$.
- **Discrete Risk Advisory Category:** $C \in \{\text{LOW}, \text{MEDIUM}, \text{HIGH}, \text{CRITICAL}\}$.
- **Dynamic Safety Clearance:** Boolean decision recommending immediate harbour return or voyage continuation.

---

## 2. Mathematical Formulation & Architecture

### 2.1 Model Architecture: Bi-LSTM with Additive Attention (`C1BiLSTMAttention`)

```
   Temporal Input Sequence X = [x_1, x_2, ..., x_T] (T = 6 lookback steps, D = 16 features)
                                    |
            +-----------------------v-----------------------+
            |      Bidirectional LSTM Layer 1 (Hidden = 64) |
            |      Bidirectional LSTM Layer 2 (Hidden = 64) |
            +-----------------------+-----------------------+
                                    |
                    Forward & Backward Hidden States:
                    H = [h_1, h_2, ..., h_T],  h_t in R^{128}
                                    |
            +-----------------------v-----------------------+
            |          Additive Attention Mechanism         |
            |     e_t = v^T tanh(W_h h_t + b_a)             |
            |     alpha_t = exp(e_t) / sum_k(exp(e_k))      |
            |     Context Vector c = sum_t (alpha_t * h_t)  |
            +-----------------------+-----------------------+
                                    |
                     Dense Representation Vector c
                         /                      \
                        v                        v
            +----------------------+  +---------------------+
            |  Classification Head |  |   Regression Head   |
            |  Dense(64) -> Relu   |  | Dense(64) -> Relu   |
            |  Linear -> Softmax(4)|  | Linear -> Sigmoid   |
            +----------+-----------+  +----------+----------+
                       |                         |
               Risk Category              DRI Score (0-100)
         (LOW/MED/HIGH/CRITICAL)
```

### 2.2 Composite Loss Function
The network is optimized using a joint loss balancing cross-entropy classification and mean squared error regression:
$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{CrossEntropy}}(y_{\text{cat}}, \hat{y}_{\text{cat}}) + \lambda_{\text{reg}} \cdot \mathcal{L}_{\text{MSE}}(y_{\text{DRI}}, \hat{y}_{\text{DRI}})$$
where $\lambda_{\text{reg}} = 0.10$ balances gradient magnitudes.

---

## 3. Training & Validation Results

Trained on 5,000 observations from `Datasets/c1_trips.csv` partitioned into 4,000 training and 1,000 held-out test records:
- **Optimization:** Adam optimizer, learning rate $\eta = 10^{-3}$, weight decay $10^{-4}$, batch size 64, 10 epochs.
- **Classification Performance:**
  - Test Accuracy: **95.60%**
  - Precision / Recall / F1: Macro F1 = **0.954**
- **Regression Performance:**
  - DRI Mean Absolute Error (MAE): **1.98**
  - DRI Root Mean Square Error (RMSE): **3.42**

### Confusion Matrix Summary (Test Partition)
- Low Risk: 382 true positives, 8 false classifications.
- Medium Risk: 346 true positives, 19 false classifications.
- High Risk: 168 true positives, 12 false classifications.
- Critical Risk: 60 true positives, 5 false classifications.

---

## 4. Scientific Provenance & Ethical Disclosure

> [!WARNING]
> **Data Provenance Disclosure:**
> In accordance with ethical machine learning standards, `c1_trips.csv` is acknowledged to contain synthetic and heuristic proxy features (`data_origin = 'synthetic_proxy_heuristics'`). The capsizing indicators and casualty risk indices are derived from hydrostatic empirical formulas rather than recorded maritime loss-of-life casualties. 
> 
> OceanGuard AI provides supplementary decision-support advisory only. It is **not** an official maritime safety clearance, nor does it replace GMDSS, VHF radio, or statutory port authority departure clearances.
