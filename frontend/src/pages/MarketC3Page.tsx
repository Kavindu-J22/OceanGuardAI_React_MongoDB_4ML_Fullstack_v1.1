import React, { useState } from 'react';
import { Box, Typography, Card, CardContent, Grid, TextField, Button, MenuItem, Select, FormControl, InputLabel, Paper, Chip, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Alert, Divider } from '@mui/material';
import StorefrontIcon from '@mui/icons-material/Storefront';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import AcUnitIcon from '@mui/icons-material/AcUnit';
import LocalShippingIcon from '@mui/icons-material/LocalShipping';
import { apiClient } from '../services/api';
import type { C3MarketResult } from '../types';

export const MarketC3Page: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<C3MarketResult | null>(null);

  const [form, setForm] = useState({
    species_id: 'SP_YELLOWFIN',
    catch_kg: 200.0,
    storage_temp_c: 4.0,
    hours_stored: 8.0,
    current_port_id: 'P_GALLE'
  });

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await apiClient.post('/ml/c3/predict', form);
      setResult(res.data);
    } catch (err) {
      console.error('C3 Market evaluation failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ pb: 6 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
          <StorefrontIcon sx={{ color: '#10b981', fontSize: 32 }} />
          <Typography variant="h4" sx={{ fontWeight: 800, color: '#f8fafc' }}>
            Component 3 • Fish Market Forecasting & Perishability Decisions
          </Typography>
        </Box>
        <Typography variant="body2" sx={{ color: '#94a3b8' }}>
          Deep learning model: <strong>Temporal Fusion Transformer (TFT)</strong> multi-horizon price forecasting integrated with <strong>Arrhenius / Q10 biological quality decay</strong> and economic decision optimization.
        </Typography>
      </Box>

      <Grid container spacing={3.5}>
        {/* Form Inputs */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 2 }}>
                Catch & Cold-Chain State
              </Typography>

              <form onSubmit={handlePredict}>
                <FormControl fullWidth size="small" sx={{ mb: 2 }}>
                  <InputLabel>Fish Species</InputLabel>
                  <Select
                    value={form.species_id}
                    label="Fish Species"
                    onChange={(e) => setForm({ ...form, species_id: e.target.value })}
                  >
                    <MenuItem value="SP_YELLOWFIN">Yellowfin Tuna (Thunnus albacares)</MenuItem>
                    <MenuItem value="SP_SKIPJACK">Skipjack Tuna (Katsuwonus pelamis)</MenuItem>
                    <MenuItem value="SP_SEER">Seer Fish / King Mackerel</MenuItem>
                    <MenuItem value="SP_MACKEREL">Indian Mackerel</MenuItem>
                    <MenuItem value="SP_SARDINE">Sardine</MenuItem>
                  </Select>
                </FormControl>

                <TextField
                  label="Landed Catch Weight (kg)"
                  type="number"
                  size="small"
                  fullWidth
                  value={form.catch_kg}
                  onChange={(e) => setForm({ ...form, catch_kg: parseFloat(e.target.value) })}
                  sx={{ mb: 2 }}
                />

                <TextField
                  label="Fish Hold Temperature (°C)"
                  type="number"
                  size="small"
                  inputProps={{ step: '0.5' }}
                  fullWidth
                  value={form.storage_temp_c}
                  onChange={(e) => setForm({ ...form, storage_temp_c: parseFloat(e.target.value) })}
                  helperText="Recommended: 0°C - 4°C with flake ice"
                  sx={{ mb: 2 }}
                />

                <TextField
                  label="Elapsed Storage Time (Hours)"
                  type="number"
                  size="small"
                  fullWidth
                  value={form.hours_stored}
                  onChange={(e) => setForm({ ...form, hours_stored: parseFloat(e.target.value) })}
                  sx={{ mb: 2 }}
                />

                <FormControl fullWidth size="small" sx={{ mb: 3 }}>
                  <InputLabel>Landing Harbour Port</InputLabel>
                  <Select
                    value={form.current_port_id}
                    label="Landing Harbour Port"
                    onChange={(e) => setForm({ ...form, current_port_id: e.target.value })}
                  >
                    <MenuItem value="P_GALLE">Galle Harbour</MenuItem>
                    <MenuItem value="P_MIRISSA">Mirissa Harbour</MenuItem>
                    <MenuItem value="P_TANGALLE">Tangalle Harbour</MenuItem>
                    <MenuItem value="P_NEGOMBO">Negombo Harbour</MenuItem>
                  </Select>
                </FormControl>

                <Button
                  type="submit"
                  variant="contained"
                  color="success"
                  fullWidth
                  size="large"
                  disabled={loading}
                  startIcon={<TrendingUpIcon />}
                  sx={{ py: 1.2, fontWeight: 700 }}
                >
                  {loading ? 'Evaluating Decisions...' : 'Evaluate Market Alternatives'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </Grid>

        {/* Results */}
        <Grid item xs={12} lg={8}>
          {result ? (
            <Card sx={{ p: 1 }}>
              <CardContent>
                {/* Recommendation Banner */}
                <Box sx={{ p: 2.5, borderRadius: 2, backgroundColor: 'rgba(16, 185, 129, 0.12)', border: '1px solid rgba(16, 185, 129, 0.3)', mb: 3 }}>
                  <Typography variant="overline" sx={{ color: '#10b981', fontWeight: 800 }}>
                    OPTIMAL ECONOMIC DECISION RECOMMENDATION
                  </Typography>
                  <Typography variant="h5" sx={{ fontWeight: 800, color: '#f1f5f9', mt: 0.5 }}>
                    {result.recommended_decision}
                  </Typography>
                </Box>

                {/* Key Metrics */}
                <Grid container spacing={2} sx={{ mb: 3 }}>
                  <Grid item xs={4}>
                    <Paper sx={{ p: 1.5, textAlign: 'center', backgroundColor: 'rgba(0,0,0,0.2)' }}>
                      <Typography variant="caption" sx={{ color: '#94a3b8' }}>Quality Retention</Typography>
                      <Typography variant="h5" sx={{ fontWeight: 800, color: '#2ec4b6' }}>
                        {result.quality_retention_percent}%
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#64748b' }}>Q10 kinetics</Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={4}>
                    <Paper sx={{ p: 1.5, textAlign: 'center', backgroundColor: 'rgba(0,0,0,0.2)' }}>
                      <Typography variant="caption" sx={{ color: '#94a3b8' }}>Total Catch Lot</Typography>
                      <Typography variant="h5" sx={{ fontWeight: 800, color: '#f1f5f9' }}>
                        {result.initial_catch_kg} kg
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#64748b' }}>{result.species_id}</Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={4}>
                    <Paper sx={{ p: 1.5, textAlign: 'center', backgroundColor: 'rgba(0,0,0,0.2)' }}>
                      <Typography variant="caption" sx={{ color: '#94a3b8' }}>Elapsed Duration</Typography>
                      <Typography variant="h5" sx={{ fontWeight: 800, color: '#00b4d8' }}>
                        {result.hours_since_catch} hrs
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#64748b' }}>at {result.storage_temp_c}°C</Typography>
                    </Paper>
                  </Grid>
                </Grid>

                <Divider sx={{ my: 2, borderColor: 'rgba(255, 255, 255, 0.08)' }} />

                {/* Multi-Market Comparison Table */}
                <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1.5 }}>
                  Comparative Selling Options (Expected Net Return = Revenue − Transport − Storage):
                </Typography>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Strategy</TableCell>
                        <TableCell>Market Destination</TableCell>
                        <TableCell>Price (LKR/kg)</TableCell>
                        <TableCell>Expected Revenue</TableCell>
                        <TableCell>Transport Cost</TableCell>
                        <TableCell>Ice Cost</TableCell>
                        <TableCell>Expected Net Return</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {result.market_evaluations.map((opt) => (
                        <TableRow key={opt.market_id} hover>
                          <TableCell>
                            <Chip
                              label={opt.decision_type}
                              size="small"
                              sx={{
                                backgroundColor: opt.decision_type === 'SELL_NOW' ? 'rgba(0, 180, 216, 0.2)' : opt.decision_type === 'WAIT' ? 'rgba(245, 158, 11, 0.2)' : 'rgba(16, 185, 129, 0.2)',
                                color: opt.decision_type === 'SELL_NOW' ? '#00b4d8' : opt.decision_type === 'WAIT' ? '#f59e0b' : '#10b981',
                                fontWeight: 700,
                                fontSize: '0.65rem'
                              }}
                            />
                          </TableCell>
                          <TableCell sx={{ fontWeight: 600 }}>{opt.market_name}</TableCell>
                          <TableCell>LKR {opt.forecasted_price_lkr_kg.toFixed(0)}</TableCell>
                          <TableCell>LKR {opt.expected_revenue_lkr.toLocaleString()}</TableCell>
                          <TableCell sx={{ color: '#f87171' }}>-LKR {opt.transport_cost_lkr.toLocaleString()}</TableCell>
                          <TableCell sx={{ color: '#f87171' }}>-LKR {opt.ice_storage_cost_lkr.toLocaleString()}</TableCell>
                          <TableCell sx={{ fontWeight: 800, color: '#34d399' }}>
                            LKR {opt.expected_net_return_lkr.toLocaleString()}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>

                <Alert severity="info" sx={{ mt: 3, fontSize: '0.75rem', borderRadius: 2 }}>
                  {result.scientific_disclaimer} Time-temperature quality decay is computed via species-specific Arrhenius/Q10 kinetics. This model provides economic decision support under price uncertainty, not microbiological food safety certification.
                </Alert>
              </CardContent>
            </Card>
          ) : (
            <Card sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', p: 4 }}>
              <Box sx={{ textAlign: 'center', color: '#64748b' }}>
                <StorefrontIcon sx={{ fontSize: 64, mb: 1.5, opacity: 0.4 }} />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Awaiting Catch & Temperature Inputs
                </Typography>
                <Typography variant="body2">
                  Select species, landed weight, and storage temperature to compute multi-market wholesale price forecasts and perishable selling decisions.
                </Typography>
              </Box>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};
