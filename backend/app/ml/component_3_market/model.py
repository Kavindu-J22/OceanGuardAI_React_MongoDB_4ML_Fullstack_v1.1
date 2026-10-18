import torch
import torch.nn as nn
import torch.nn.functional as F

class GatedLinearUnit(nn.Module):
    def __init__(self, in_features: int, out_features: int):
        super().__init__()
        self.fc = nn.Linear(in_features, out_features * 2)

    def forward(self, x: torch.Tensor):
        val, gate = self.fc(x).chunk(2, dim=-1)
        return val * torch.sigmoid(gate)

class GatedResidualNetwork(nn.Module):
    """Gated Residual Network (GRN) core block of Temporal Fusion Transformer."""
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int, context_dim: int = 0, dropout: float = 0.1):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.context_fc = nn.Linear(context_dim, hidden_dim, bias=False) if context_dim > 0 else None
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.glu = GatedLinearUnit(hidden_dim, output_dim)
        self.res_skip = nn.Linear(input_dim, output_dim) if input_dim != output_dim else nn.Identity()
        self.norm = nn.LayerNorm(output_dim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, context: torch.Tensor = None):
        h = self.fc1(x)
        if self.context_fc is not None and context is not None:
            if context.dim() == 2 and h.dim() == 3:
                h = h + self.context_fc(context).unsqueeze(1)
            else:
                h = h + self.context_fc(context)
        h = F.elu(h)
        h = self.dropout(self.fc2(h))
        gated = self.glu(h)
        return self.norm(self.res_skip(x) + gated)

class VariableSelectionNetwork(nn.Module):
    """Variable Selection Network (VSN) selects the most informative inputs."""
    def __init__(self, num_inputs: int, input_dim: int, hidden_dim: int, context_dim: int = 0):
        super().__init__()
        self.num_inputs = num_inputs
        self.single_grns = nn.ModuleList([
            GatedResidualNetwork(input_dim, hidden_dim, hidden_dim, context_dim)
            for _ in range(num_inputs)
        ])
        self.weight_grn = GatedResidualNetwork(num_inputs * input_dim, hidden_dim, num_inputs, context_dim)

    def forward(self, inputs: list, context: torch.Tensor = None):
        # inputs is a list of tensors [batch, seq_len, input_dim]
        stacked = torch.stack(inputs, dim=-2) # [batch, seq_len, num_inputs, input_dim]
        flattened = torch.cat(inputs, dim=-1) # [batch, seq_len, num_inputs * input_dim]
        
        weights = F.softmax(self.weight_grn(flattened, context), dim=-1).unsqueeze(-1) # [batch, seq_len, num_inputs, 1]
        processed = [grn(x, context) for grn, x in zip(self.single_grns, inputs)]
        processed_stack = torch.stack(processed, dim=-2) # [batch, seq_len, num_inputs, hidden_dim]
        
        combined = torch.sum(weights * processed_stack, dim=-2) # [batch, seq_len, hidden_dim]
        return combined, weights

class C3TemporalFusionTransformer(nn.Module):
    """
    Component 3: Temporal Fusion Transformer for Multi-Horizon Fish Market Price Forecasting.
    Combines static categorical entity embeddings (market, species), observed past covariates,
    and known future time indices through Gated Residual Networks and Temporal Multi-Head Attention.
    """
    def __init__(
        self,
        num_markets: int = 5,
        num_species: int = 5,
        embed_dim: int = 16,
        hist_features: int = 4, # price, supply, demand, shock
        future_features: int = 3, # day_of_week, weekend, month
        hidden_dim: int = 32,
        num_heads: int = 4,
        forecast_horizon: int = 3,
        dropout: float = 0.1
    ):
        super().__init__()
        self.forecast_horizon = forecast_horizon
        
        # 1. Static Entity Embeddings
        self.market_embed = nn.Embedding(num_markets, embed_dim)
        self.species_embed = nn.Embedding(num_species, embed_dim)
        self.static_context_grn = GatedResidualNetwork(embed_dim * 2, hidden_dim, hidden_dim)

        # 2. Variable Selection Network for Historical Covariates
        self.hist_proj = nn.ModuleList([nn.Linear(1, hidden_dim) for _ in range(hist_features)])
        self.hist_vsn = VariableSelectionNetwork(hist_features, hidden_dim, hidden_dim, context_dim=hidden_dim)

        # 3. Temporal Self-Attention
        self.temporal_attention = nn.MultiheadAttention(embed_dim=hidden_dim, num_heads=num_heads, batch_first=True, dropout=dropout)
        self.attn_norm = nn.LayerNorm(hidden_dim)

        # 4. Multi-Horizon Forecasting Head
        self.output_head = nn.Sequential(
            GatedResidualNetwork(hidden_dim, hidden_dim, hidden_dim),
            nn.Linear(hidden_dim, forecast_horizon) # Predict t+1, t+2, t+3 future prices
        )

    def forward(
        self,
        market_idx: torch.Tensor,
        species_idx: torch.Tensor,
        historical_feats: torch.Tensor, # [batch, seq_len, hist_features]
        future_feats: torch.Tensor = None
    ):
        # Static Context
        m_emb = self.market_embed(market_idx) # [batch, embed_dim]
        s_emb = self.species_embed(species_idx) # [batch, embed_dim]
        static_raw = torch.cat([m_emb, s_emb], dim=-1) # [batch, embed_dim * 2]
        static_context = self.static_context_grn(static_raw) # [batch, hidden_dim]

        # Historical Variable Selection
        hist_inputs = [
            self.hist_proj[i](historical_feats[:, :, i:i+1])
            for i in range(historical_feats.shape[-1])
        ]
        vsn_out, var_weights = self.hist_vsn(hist_inputs, context=static_context) # [batch, seq_len, hidden_dim]

        # Temporal Multi-Head Attention
        attn_out, attn_weights = self.temporal_attention(vsn_out, vsn_out, vsn_out)
        h_temporal = self.attn_norm(vsn_out + attn_out) # [batch, seq_len, hidden_dim]

        # Use last step's temporal context for multi-horizon forecast
        last_step_context = h_temporal[:, -1, :] # [batch, hidden_dim]
        forecast_prices = self.output_head(last_step_context) # [batch, forecast_horizon]

        return {
            "forecast_prices": forecast_prices,
            "variable_weights": var_weights,
            "attention_weights": attn_weights
        }
