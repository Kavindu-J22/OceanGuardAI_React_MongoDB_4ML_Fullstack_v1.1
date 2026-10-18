import React, { useState } from 'react';
import { Box, Typography, Card, CardContent, Grid, TextField, Button, MenuItem, Select, FormControl, InputLabel, Chip, LinearProgress, Paper, Alert, Divider } from '@mui/material';
import SecurityIcon from '@mui/icons-material/Security';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import DangerousIcon from '@mui/icons-material/Dangerous';
import { apiClient } from '../services/api';
import type { C1RiskResult } from '../types';

export const SafetyC1Page: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<C1RiskResult | null>(null);

  const [form, setForm] = useState({
    vessel_type: 'OFRP',
    vessel_length_m: 6.8,
    vessel_beam_m: 1.8,
    lightship_mass_kg: 950.0,
    payload_mass_kg: 600.0,
    assumed_payload_limit_kg: 1200.0,
    assumed_lightship_freeboard_m: 0.9,
    planned_trip_duration_h: 12.0,
    forecast_max_wind_ms: 12.5,
    forecast_max_gust_ms: 16.0,
    forecast_max_wave_height_m: 1.6,
    forecast_min_pressure_hpa: 1009.0,
    worst_wave_peak_period_s: 7.2,
    worst_wave_steepness: 0.022,
    worst_lateral_wind_force_proxy_n: 850.0
  });

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await apiClient.post('/ml/c1/predict', form);
      setResult(res.data);
    } catch (err: any) {
      console.error('C1 Prediction failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (label: string) => {
    if (label === 'Safe') return '#10b981';
    if (label === 'Caution') return '#f59e0b';
    return '#ef4444';
  };

  const getRiskIcon = (label: string) => {
    if (label === 'Safe') return <CheckCircleIcon sx={{ fontSize: 44, color: '#10b981' }} />;
    if (label === 'Caution') return <WarningAmberIcon sx={{ fontSize: 44, color: '#f59e0b' }} />;
    return <DangerousIcon sx={{ fontSize: 44, color: '#ef4444' }} />;
  };

  return (
    <Box sx={{ pb: 6 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
          <SecurityIcon sx={{ color: '#00b4d8', fontSize: 32 }} />
          <Typography variant="h4" sx={{ fontWeight: 800, color: '#f8fafc' }}>
            Component 1 • Dynamic Vessel Safety Risk Prediction
          </Typography>
        </Box>
        <Typography variant="body2" sx={{ color: '#94a3b8' }}>
          Deep learning model: <strong>Bidirectional LSTM with Additive Temporal Attention</strong> fusing vessel static loading vulnerability with dynamic marine forecast history.
        </Typography>
      </Box>

      <Grid container spacing={3.5}>
        {/* Form Inputs */}
        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 2 }}>
                Vessel & Marine Weather Parameters
              </Typography>

              <form onSubmit={handlePredict}>
                <Typography variant="subtitle2" sx={{ color: '#00b4d8', fontWeight: 700, mb: 1.5 }}>
                  1. Craft Dimensions & Loading Condition
                </Typography>
                <Grid container spacing={2} sx={{ mb: 3 }}>
                  <Grid item xs={6} sm={4}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Vessel Type</InputLabel>
                      <Select
                        value={form.vessel_type}
                        label="Vessel Type"
                        onChange={(e) => setForm({ ...form, vessel_type: e.target.value })}
                      >
                        <MenuItem value="OFRP">OFRP (Outboard)</MenuItem>
                        <MenuItem value="IDAY">IDAY (1-Day)</MenuItem>
                        <MenuItem value="IMUL">IMUL (Multi-Day)</MenuItem>
                        <MenuItem value="NBSB">NBSB</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={6} sm={4}>
                    <TextField
                      label="Length Over All (m)"
                      type="number"
                      size="small"
                      inputProps={{ step: '0.1' }}
                      fullWidth
                      value={form.vessel_length_m}
                      onChange={(e) => setForm({ ...form, vessel_length_m: parseFloat(e.target.value) })}
                    />
                  </Grid>
                  <Grid item xs={6} sm={4}>
                    <TextField
                      label="Beam Width (m)"
                      type="number"
                      size="small"
                      inputProps={{ step: '0.1' }}
                      fullWidth
                      value={form.vessel_beam_m}
                      onChange={(e) => setForm({ ...form, vessel_beam_m: parseFloat(e.target.value) })}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      label="Current Payload (kg)"
                      type="number"
                      size="small"
                      fullWidth
                      value={form.payload_mass_kg}
                      onChange={(e) => setForm({ ...form, payload_mass_kg: parseFloat(e.target.value) })}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      label="Payload Limit (kg)"
                      type="number"
                      size="small"
                      fullWidth
                      value={form.assumed_payload_limit_kg}
                      onChange={(e) => setForm({ ...form, assumed_payload_limit_kg: parseFloat(e.target.value) })}
                    />
                  </Grid>
                </Grid>

                <Typography variant="subtitle2" sx={{ color: '#00b4d8', fontWeight: 700, mb: 1.5 }}>
                  2. Marine Weather Forecast
                </Typography>
                <Grid container spacing={2} sx={{ mb: 3 }}>
                  <Grid item xs={6}>
                    <TextField
                      label="Max Wind Speed (m/s)"
                      type="number"
                      size="small"
                      inputProps={{ step: '0.5' }}
                      fullWidth
                      value={form.forecast_max_wind_ms}
                      onChange={(e) => setForm({ ...form, forecast_max_wind_ms: parseFloat(e.target.value) })}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      label="Max Wind Gust (m/s)"
                      type="number"
                      size="small"
                      inputProps={{ step: '0.5' }}
                      fullWidth
                      value={form.forecast_max_gust_ms}
                      onChange={(e) => setForm({ ...form, forecast_max_gust_ms: parseFloat(e.target.value) })}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      label="Significant Wave Height (m)"
                      type="number"
                      size="small"
                      inputProps={{ step: '0.1' }}
                      fullWidth
                      value={form.forecast_max_wave_height_m}
                      onChange={(e) => setForm({ ...form, forecast_max_wave_height_m: parseFloat(e.target.value) })}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      label="Wave Peak Period (s)"
                      type="number"
                      size="small"
                      inputProps={{ step: '0.5' }}
                      fullWidth
                      value={form.worst_wave_peak_period_s}
                      onChange={(e) => setForm({ ...form, worst_wave_peak_period_s: parseFloat(e.target.value) })}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      label="Min Pressure (hPa)"
                      type="number"
                      size="small"
                      fullWidth
                      value={form.forecast_min_pressure_hpa}
                      onChange={(e) => setForm({ ...form, forecast_min_pressure_hpa: parseFloat(e.target.value) })}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      label="Planned Duration (h)"
                      type="number"
                      size="small"
                      fullWidth
                      value={form.planned_trip_duration_h}
                      onChange={(e) => setForm({ ...form, planned_trip_duration_h: parseFloat(e.target.value) })}
                    />
                  </Grid>
                </Grid>

                <Button
                  type="submit"
                  variant="contained"
                  color="primary"
                  fullWidth
                  size="large"
                  disabled={loading}
                  startIcon={<SecurityIcon />}
                  sx={{ py: 1.2, fontWeight: 700 }}
                >
                  {loading ? 'Evaluating Risk Pipeline...' : 'Run Dynamic Safety Risk Prediction'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </Grid>

        {/* Prediction Results Display */}
        <Grid item xs={12} lg={6}>
          {result ? (
            <Card sx={{ p: 1, border: `2px solid ${getRiskColor(result.risk_label)}` }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Box>
                    <Typography variant="overline" sx={{ color: '#94a3b8', fontWeight: 700 }}>
                      SAFETY ASSESSMENT VERDICT
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mt: 0.5 }}>
                      {getRiskIcon(result.risk_label)}
                      <Typography variant="h3" sx={{ fontWeight: 800, color: getRiskColor(result.risk_label) }}>
                        {result.risk_label.toUpperCase()}
                      </Typography>
                    </Box>
                  </Box>
                  <Chip
                    label={`Confidence: ${(result.confidence * 100).toFixed(1)}%`}
                    sx={{ backgroundColor: 'rgba(255, 255, 255, 0.08)', fontWeight: 600 }}
                  />
                </Box>

                <Divider sx={{ my: 2, borderColor: 'rgba(255, 255, 255, 0.08)' }} />

                {/* Score Gauge */}
                <Box sx={{ mb: 3 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.8 }}>
                    <Typography variant="body2" sx={{ color: '#cbd5e1' }}>
                      Dynamic Risk Index (DRI):
                    </Typography>
                    <Typography variant="body1" sx={{ fontWeight: 800, color: getRiskColor(result.risk_label) }}>
                      {result.dri_score.toFixed(1)} / 100
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={result.dri_score}
                    sx={{
                      height: 12,
                      borderRadius: 6,
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: getRiskColor(result.risk_label),
                        borderRadius: 6,
                      },
                    }}
                  />
                </Box>

                {/* Dominant Factor */}
                <Paper sx={{ p: 2, mb: 3, backgroundColor: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)' }}>
                  <Typography variant="caption" sx={{ color: '#94a3b8', fontWeight: 700, display: 'block', mb: 0.5 }}>
                    DOMINANT RISK FACTOR
                  </Typography>
                  <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#f8fafc', textTransform: 'capitalize' }}>
                    {result.dominant_risk_factor.replace(/_/g, ' ')}
                  </Typography>
                </Paper>

                {/* Contributing factors breakdown */}
                <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#f1f5f9', mb: 1.5 }}>
                  Contributing Risk Exposure Breakdown:
                </Typography>
                <Grid container spacing={1.5} sx={{ mb: 3 }}>
                  {Object.entries(result.contributing_factors).map(([k, v]) => (
                    <Grid item xs={6} key={k}>
                      <Box sx={{ p: 1.2, borderRadius: 2, backgroundColor: 'rgba(0, 0, 0, 0.2)' }}>
                        <Typography variant="caption" sx={{ color: '#94a3b8', display: 'block' }}>
                          {k.replace(/_/g, ' ')}
                        </Typography>
                        <Typography variant="body2" sx={{ fontWeight: 700, color: '#00b4d8' }}>
                          {v.toFixed(1)}% exposure
                        </Typography>
                      </Box>
                    </Grid>
                  ))}
                </Grid>

                {/* Model Metadata & Disclaimer */}
                <Box sx={{ pt: 1, borderTop: '1px solid rgba(255, 255, 255, 0.08)' }}>
                  <Typography variant="caption" sx={{ color: '#64748b', display: 'block' }}>
                    Model: {result.model_version} | Provenance: {result.data_provenance}
                  </Typography>
                  <Alert severity="info" sx={{ mt: 1.5, fontSize: '0.75rem', borderRadius: 2 }}>
                    {result.scientific_disclaimer}
                  </Alert>
                </Box>
              </CardContent>
            </Card>
          ) : (
            <Card sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', p: 4 }}>
              <Box sx={{ textAlign: 'center', color: '#64748b' }}>
                <SecurityIcon sx={{ fontSize: 64, mb: 1.5, opacity: 0.4 }} />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Awaiting Input Parameters
                </Typography>
                <Typography variant="body2">
                  Configure vessel dimensions and weather forecast, then click 'Run Dynamic Safety Risk Prediction'.
                </Typography>
              </Box>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};
