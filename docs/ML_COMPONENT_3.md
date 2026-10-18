# Component 3 (C3): Fish Market Forecasting & Perishability Decision Engine

## 1. Scientific Overview & Problem Formulation

Artisanal skippers frequently land their catch during morning market gluts when local landing prices drop drastically. Simultaneously, fish storage onboard artisanal multi-day craft often relies on basic flake ice or insulated iceboxes, where inadequate temperature management causes rapid enzymatic breakdown and bacterial decomposition.

Component 3 integrates **macro-market econometric forecasting** with **micro-biological quality decay kinetics** to provide actionable post-harvest commercialization recommendations:
1. **Forecast Wholesale Fish Prices:** Multi-step forward price predictions (24h, 48h, 72h) across 7 major Sri Lankan fishing harbours.
2. **Model Real-Time Quality Spoilage:** Enzymatic fish spoilage kinetics as a function of storage temperature and duration.
3. **Optimize Commercialization Actions:** 3-way arbitrage decision engine determining whether to `SELL_NOW`, `WAIT_LOCAL`, or `TRANSPORT_ALTERNATE`.

---

## 2. Biological Quality Decay Kinetics (Arrhenius & Q10 Formulation)

Fish quality degradation (specifically autolytic protein breakdown and Total Volatile Basic Nitrogen [TVB-N] accumulation) follows temperature-dependent enzymatic kinetics modeled via the **$Q_{10}$ temperature coefficient**:

$$k(T) = k_0 \cdot Q_{10}^{\left(\frac{T - T_{\text{ref}}}{10}\right)}$$

where:
- $T$: Ambient fish hold / cold-storage temperature in degrees Celsius ($^\circ\text{C}$).
- $T_{\text{ref}} = 0.0^\circ\text{C}$: Reference baseline temperature of chilled flake-ice slurry.
- $k_0 \approx 0.015\text{ h}^{-1}$: Baseline decomposition rate of tropical marine teleosts.
- $Q_{10} = 2.2$: Empirical biochemical rate acceleration factor per $10^\circ\text{C}$ temperature elevation.

### Dynamic Quality Index ($Q(t)$)
The remaining freshness fraction $Q(t) \in [0, 1]$ after $t$ storage hours is governed by:
$$Q(t) = Q_0 \cdot \exp\left(-k(T) \cdot t\right)$$
where $Q_0 = 1.0$ at moment of capture.

### Commercial Grading & Price Discount Multiplier

| Commercial Grade | Quality Score $Q(t)$ | Target Market | Price Realization Multiplier |
|---|---|---|---|
| **Grade A (Export / Sashimi)** | $Q(t) \ge 0.80$ | EU / International Export | $1.00 \times P_{\text{market}}$ |
| **Grade B (Fresh Retail)** | $0.55 \le Q(t) < 0.80$ | Urban Wet Markets / Supermarkets | $0.78 \times P_{\text{market}}$ |
| **Grade C (Processing / Salting)** | $0.30 \le Q(t) < 0.55$ | Dried Fish / Canning Facilities | $0.50 \times P_{\text{market}}$ |
| **Spoiled / Rejected** | $Q(t) < 0.30$ | Fish Meal / Reject | $0.10 \times P_{\text{market}}$ |

---

## 3. Market Price Forecasting Engine

The pricing model utilizes a Temporal Fusion Transformer (TFT) architecture designed to process:
- **Static Entity Metadata:** Target Species (`SP_YELLOWFIN`, `SP_SKIPJACK`, `SP_SAILFISH`, `SP_SEERFISH`, `SP_TREVALLY`), Landing Harbour (`P_COLOMBO`, `P_GALLE`, `P_MATARA`, etc.).
- **Dynamic Time-Varying Covariates:** Historical daily wholesale prices (LKR/kg), seasonal monsoonal indices, diesel fuel wholesale indices, lunar cycle, and aggregate landing volume.
- **Architectural Mechanics:**
  - *Variable Selection Networks (VSN):* Learn feature importance weights dynamically for each time step.
  - *Gated Residual Networks (GRN):* Provide adaptive non-linear processing and skip-connections.
  - *Temporal Self-Attention:* Captures multi-horizon cyclical demand spikes (e.g., weekend and festival market demand).

---

## 4. 3-Way Economic Decision Engine

Upon landing or approaching port, the skipper inputs harvest quantity ($W_{\text{kg}}$), current storage temperature ($T$), and storage elapsed time ($t$). The engine calculates economic net revenue across three strategic options:

### Option 1: `SELL_NOW`
Immediate liquidation at local harbour price adjusted for current quality grade:
$$R_{\text{now}} = W_{\text{kg}} \cdot P_{\text{local}}(t=0) \cdot M_Q(Q(t))$$

### Option 2: `WAIT_LOCAL`
Hold catch on ice for 24 hours to capture projected price appreciation:
$$R_{\text{wait}} = W_{\text{kg}} \cdot P_{\text{local}}(t+24) \cdot M_Q(Q(t+24)) - C_{\text{ice\_refrigeration}}$$

### Option 3: `TRANSPORT_ALTERNATE`
Truck catch via insulated refrigerated road freight to a higher-paying alternate coastal harbour $p_{\text{alt}}$:
$$R_{\text{trans}} = W_{\text{kg}} \cdot P_{\text{alt}}(t+t_{\text{transit}}) \cdot M_Q(Q(t+t_{\text{transit}})) - \left(C_{\text{base\_freight}} + c_{\text{km}} \cdot \text{dist}(p_{\text{curr}}, p_{\text{alt}})\right)$$

The engine outputs the highest net-margin option, complete with expected price deltas, shelf-life hours remaining before grade downgrade, and logistics routing.

---

## 5. Provenance & Real-World Validation

> [!NOTE]
> Training dataset `Datasets/c3_market_prices.csv` represents 5,000 synthetic observations reflecting calibrated wholesale price distributions across Sri Lankan harbours. Freight rates, ice costs, and transport times reflect realistic Sri Lankan logistics corridors (e.g., Southern Expressway transit from Galle/Matara to Peliyagoda Central Fish Market, Colombo).
