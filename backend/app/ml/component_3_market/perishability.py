import numpy as np
from typing import Dict, Any

# Species-specific biological deterioration parameters
SPECIES_DECAY_PARAMS = {
    "SP_YELLOWFIN": {"k_ref": 0.008, "q10": 2.2, "t_ref": 0.0, "high_value": True},
    "SP_SKIPJACK": {"k_ref": 0.010, "q10": 2.4, "t_ref": 0.0, "high_value": False},
    "SP_MACKEREL": {"k_ref": 0.014, "q10": 2.5, "t_ref": 0.0, "high_value": False},
    "SP_SARDINE": {"k_ref": 0.020, "q10": 2.8, "t_ref": 0.0, "high_value": False},
    "SP_SEER": {"k_ref": 0.009, "q10": 2.1, "t_ref": 0.0, "high_value": True}
}

def calculate_quality_retention(species_id: str, storage_temp_c: float, elapsed_hours: float) -> float:
    """
    Computes post-harvest fish quality retention ratio using Q10 temperature-rate kinetics:
    k(T) = k_ref * Q10^((T - T_ref) / 10)
    Quality(t) = exp(-k(T) * t)
    """
    params = SPECIES_DECAY_PARAMS.get(species_id, {"k_ref": 0.010, "q10": 2.4, "t_ref": 0.0})
    k_ref = params["k_ref"]
    q10 = params["q10"]
    t_ref = params["t_ref"]
    
    # Effective degradation rate at storage temperature
    k_temp = k_ref * np.power(q10, (storage_temp_c - t_ref) / 10.0)
    quality_ratio = np.exp(-k_temp * elapsed_hours)
    
    return float(np.clip(quality_ratio, 0.20, 1.0))

def estimate_ice_storage_cost(catch_kg: float, elapsed_hours: float, target_temp_c: float = 2.0) -> float:
    """
    Estimates ice requirement and refrigeration expense in Sri Lankan Rupees (LKR).
    Rule of thumb: 1 kg ice per 1 kg fish for 24h at 25C ambient.
    Cost of flake ice in Sri Lankan harbours: ~15 LKR/kg.
    """
    # Ice melt rate proportional to hours
    ice_ratio = (elapsed_hours / 24.0) * 0.8
    ice_kg_needed = catch_kg * ice_ratio
    ice_cost_lkr = ice_kg_needed * 15.0 # 15 LKR per kg of ice
    return float(round(ice_cost_lkr, 2))
