import os
import pandas as pd
from typing import Dict, Any

from app.core.config import settings
from app.ml.component_3_market.decisions import evaluate_market_decisions

class C3Predictor:
    def __init__(self):
        self.c3_path = os.path.join(settings.DATASETS_DIR, "c3_market_prices.csv")

    def predict_market_decision(
        self,
        species_id: str = "SP_YELLOWFIN",
        catch_kg: float = 100.0,
        current_port_id: str = "P_GALLE",
        storage_temp_c: float = 4.0,
        hours_stored: float = 6.0
    ) -> Dict[str, Any]:
        """
        Runs multi-market forecast and economic decision engine.
        Fetches latest baseline market price quotes and computes net returns.
        """
        quotes = {
            "M_PELIYAGODA": 1420.0,
            "M_NEGOMBO": 1280.0,
            "M_GALLE": 1250.0,
            "M_MIRISSA": 1260.0,
            "M_TANGALLE": 1230.0
        }
        
        # Load empirical scenario quotes from c3 dataset if available
        if os.path.exists(self.c3_path):
            df_c3 = pd.read_csv(self.c3_path)
            latest_date = df_c3['date'].max()
            subset = df_c3[(df_c3['date'] == latest_date) & (df_c3['species_id'] == species_id)]
            for _, r in subset.iterrows():
                quotes[r['market_id']] = float(r['price_lkr_per_kg'])
                
        # Evaluate Decision
        result = evaluate_market_decisions(
            species_id=species_id,
            catch_kg=catch_kg,
            current_port_id=current_port_id,
            storage_temp_c=storage_temp_c,
            hours_stored=hours_stored,
            market_price_quotes=quotes
        )
        return result

c3_predictor = C3Predictor()
