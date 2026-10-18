import React, { useState } from 'react';
import { Box, Typography, Card, CardContent, Grid, TextField, Button, LinearProgress, Paper, Chip, Alert, Divider } from '@mui/material';
import LocalGasStationIcon from '@mui/icons-material/LocalGasStation';
import SpeedIcon from '@mui/icons-material/Speed';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import { apiClient } from '../services/api';
import type { C4FuelResult } from '../types';

export const FuelC4Page: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<C4FuelResult | null>(null);

  const [form, setForm] = useState({
    vessel_length_m: 6.8,
    vessel_beam_m: 1.7,
    displacement_mass_kg: 1450.0,
    engine_rated_kw_assumed: 15.0,
    travel_roundtrip_distance_km: 45.0,
    planned_speed_kn: 5.5,
    forecast_wave_hs_m: 1.4,
    forecast_wind_speed_ms: 10.0,
    planned_duration_h: 10.0,
    available_fuel_l: 30.0
  });

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await apiClient.post('/ml/c4/predict', form);
      setResult(res.data);
    } catch (err) {
      console.error('C4 Fuel prediction failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusChip = (status: string) => {
    if (status === 'SUFFICIENT') {
      return (
        <Chip
          icon={<CheckCircleIcon />}
          label="FUEL SUFFICIENT"
          sx={{ backgroundColor: 'rgba(16, 185, 129, 0.2)', color: '#34d399', fontWeight: 800, px: 1 }}
        />
      );
    }
    if (status === 'DEFICIENT') {
      return (
        <Chip
          icon={<WarningAmberIcon />}
          label="DEFICIENT RESERVE MARGIN"
          sx={{ backgroundColor: 'rgba(245, 158, 11, 0.2)', color: '#fbbf24', fontWeight: 800, px: 1 }}
        />
      );
    }
    return (
      <Chip
        icon={<ErrorOutlineIcon />}
        label="CRITICAL SHORTAGE"
        sx={{ backgroundColor: 'rgba(239, 68, 68, 0.2)', color: '#f87171', fontWeight: 800, px: 1 }}
      />
    );
  };

  return (
    <Box sx={{ pb: 6 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
          <LocalGasStationIcon sx={{ color: '#f59e0b', fontSize: 32 }} />
          <Typography variant="h4" sx={{ fontWeight: 800, color: '#f8fafc' }}>
            Component 4 • Physics-Informed Fuel Predictor (PINN)
          </Typography>
        </Box>
        <Typography variant="body2" sx={{ color: '#94a3b8' }}>
          Physics-guided neural architecture enforcing <strong>ITTC-1957 skin friction correlation, Froude residuary drag, and brake power constraints</strong>.
        </Typography>
      </Box>

      <Grid container spacing={3.5}>
        {/* Form Input Card */}
        <Grid item xs={12} lg={5}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 2 }}>
                Voyage & Hydrodynamic Parameters
              </Typography>

              <form onSubmit={handlePredict}>
                <Typography variant="subtitle2" sx={{ color: '#f59e0b', fontWeight: 700, mb: 1.5 }}>
                  1. Hull & Engine Configuration
                </Typography>
                <Grid container spacing={2} sx={{ mb: 2.5 }}>
                  <Grid item xs={6}>
                    <TextField
                      label="Length (m)"
                      type="number"
                      size="small"
                      inputProps={{ step: '0.1' }}
                      fullWidth
                      value={form.vessel_length_m}
                      onChange={(e) => setForm({ ...form, vessel_length_m: parseFloat(e.target.value) })}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      label="Beam (m)"
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
                      label="Displacement (kg)"
                      type="number"
                      size="small"
                      fullWidth
                      value={form.displacement_mass_kg}
                      onChange={(e) => setForm({ ...form, displacement_mass_kg: parseFloat(e.target.value) })}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      label="Engine Power (kW)"
                      type="number"
                      size="small"
                      fullWidth
                      value={form.engine_rated_kw_assumed}
                      onChange={(e) => setForm({ ...form, engine_rated_kw_assumed: parseFloat(e.target.value) })}
                    />
                  </Grid>
                </Grid>

                <Typography variant="subtitle2" sx={{ color: '#f59e0b', fontWeight: 700, mb: 1.5 }}>
                  2. Route Distance & Weather Dynamics
                </Typography>
                <Grid container spacing={2} sx={{ mb: 3 }}>
                  <Grid item xs={6}>
                    <TextField
                      label="Roundtrip Distance (km)"
                      type="number"
                      size="small"
                      fullWidth
                      value={form.travel_roundtrip_distance_km}
                      onChange={(e) => setForm({ ...form, travel_roundtrip_distance_km: parseFloat(e.target.value) })}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      label="Target Speed (knots)"
                      type="number"
                      size="small"
                      inputProps={{ step: '0.5' }}
                      fullWidth
                      value={form.planned_speed_kn}
                      onChange={(e) => setForm({ ...form, planned_speed_kn: parseFloat(e.target.value) })}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      label="Wave Height (m)"
                      type="number"
                      size="small"
                      inputProps={{ step: '0.1' }}
                      fullWidth
                      value={form.forecast_wave_hs_m}
                      onChange={(e) => setForm({ ...form, forecast_wave_hs_m: parseFloat(e.target.value) })}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      label="Wind Speed (m/s)"
                      type="number"
                      size="small"
                      inputProps={{ step: '0.5' }}
                      fullWidth
                      value={form.forecast_wind_speed_ms}
                      onChange={(e) => setForm({ ...form, forecast_wind_speed_ms: parseFloat(e.target.value) })}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      label="Total Trip Duration (h)"
                      type="number"
                      size="small"
                      fullWidth
                      value={form.planned_duration_h}
                      onChange={(e) => setForm({ ...form, planned_duration_h: parseFloat(e.target.value) })}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      label="Available Fuel in Tank (L)"
                      type="number"
                      size="small"
                      fullWidth
                      value={form.available_fuel_l}
                      onChange={(e) => setForm({ ...form, available_fuel_l: parseFloat(e.target.value) })}
                    />
                  </Grid>
                </Grid>

                <Button
                  type="submit"
                  variant="contained"
                  color="warning"
                  fullWidth
                  size="large"
                  disabled={loading}
                  startIcon={<LocalGasStationIcon />}
                  sx={{ py: 1.2, fontWeight: 700 }}
                >
                  {loading ? 'Evaluating PINN Physics...' : 'Calculate Physics Fuel Requirement'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </Grid>

        {/* Results Display */}
        <Grid item xs={12} lg={7}>
          {result ? (
            <Card sx={{ p: 1 }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2.5 }}>
                  <Typography variant="overline" sx={{ color: '#94a3b8', fontWeight: 700 }}>
                    PINN OPERATIONAL FUEL ESTIMATE
                  </Typography>
                  {getStatusChip(result.fuel_sufficiency_status)}
                </Box>

                {/* Primary numbers */}
                <Grid container spacing={2} sx={{ mb: 3 }}>
                  <Grid item xs={4}>
                    <Paper sx={{ p: 2, textAlign: 'center', backgroundColor: 'rgba(255, 255, 255, 0.02)' }}>
                      <Typography variant="caption" sx={{ color: '#94a3b8', display: 'block' }}>Predicted Trip Fuel</Typography>
                      <Typography variant="h4" sx={{ fontWeight: 800, color: '#f59e0b' }}>
                        {result.predicted_total_fuel_l} L
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#64748b' }}>
                        Transit: {result.predicted_transit_fuel_l}L | Ops: {result.predicted_fishing_fuel_l}L
                      </Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={4}>
                    <Paper sx={{ p: 2, textAlign: 'center', backgroundColor: 'rgba(255, 255, 255, 0.02)' }}>
                      <Typography variant="caption" sx={{ color: '#94a3b8', display: 'block' }}>20% Safety Reserve</Typography>
                      <Typography variant="h4" sx={{ fontWeight: 800, color: '#00b4d8' }}>
                        +{result.recommended_reserve_l} L
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#64748b' }}>
                        Contingency margin
                      </Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={4}>
                    <Paper sx={{ p: 2, textAlign: 'center', backgroundColor: 'rgba(255, 255, 255, 0.04)', border: '1px solid rgba(245, 158, 11, 0.3)' }}>
                      <Typography variant="caption" sx={{ color: '#94a3b8', display: 'block' }}>Total Required</Typography>
                      <Typography variant="h4" sx={{ fontWeight: 800, color: '#f1f5f9' }}>
                        {result.total_required_fuel_l} L
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#64748b' }}>
                        Tank has: {result.available_fuel_l} L
                      </Typography>
                    </Paper>
                  </Grid>
                </Grid>

                <Divider sx={{ my: 2, borderColor: 'rgba(255, 255, 255, 0.08)' }} />

                {/* Hydrodynamic Physics Breakdown */}
                <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#f8fafc', mb: 1.5 }}>
                  Governing Hydrodynamic Resistance & Power Quantities:
                </Typography>
                <Grid container spacing={1.5} sx={{ mb: 3 }}>
                  <Grid item xs={6} sm={3}>
                    <Box sx={{ p: 1.2, backgroundColor: 'rgba(0,0,0,0.2)', borderRadius: 2 }}>
                      <Typography variant="caption" sx={{ color: '#94a3b8' }}>ITTC-1957 Friction</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 700 }}>
                        {result.physics_metrics.frictional_resistance_n} N
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Box sx={{ p: 1.2, backgroundColor: 'rgba(0,0,0,0.2)', borderRadius: 2 }}>
                      <Typography variant="caption" sx={{ color: '#94a3b8' }}>Wave Drag</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 700 }}>
                        {result.physics_metrics.wave_resistance_n} N
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Box sx={{ p: 1.2, backgroundColor: 'rgba(0,0,0,0.2)', borderRadius: 2 }}>
                      <Typography variant="caption" sx={{ color: '#94a3b8' }}>Total Resistance</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 700, color: '#f59e0b' }}>
                        {result.physics_metrics.total_resistance_n} N
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Box sx={{ p: 1.2, backgroundColor: 'rgba(0,0,0,0.2)', borderRadius: 2 }}>
                      <Typography variant="caption" sx={{ color: '#94a3b8' }}>Required Brake Power</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 700, color: '#00b4d8' }}>
                        {result.physics_metrics.brake_power_kw} kW
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>

                {/* Disclaimer */}
                <Alert severity="info" sx={{ fontSize: '0.75rem', borderRadius: 2 }}>
                  {result.scientific_disclaimer} Model: {result.model_version}. In the training dataset, real measured fuel values were completely null (100% simulated physics targets). Actual sea trials are required for field calibration.
                </Alert>
              </CardContent>
            </Card>
          ) : (
            <Card sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', p: 4 }}>
              <Box sx={{ textAlign: 'center', color: '#64748b' }}>
                <SpeedIcon sx={{ fontSize: 64, mb: 1.5, opacity: 0.4 }} />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Awaiting Voyage Parameters
                </Typography>
                <Typography variant="body2">
                  Input craft dimensions, trip distance, and engine power to compute ITTC-1957 hydrodynamic resistance and trip fuel requirements.
                </Typography>
              </Box>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};
