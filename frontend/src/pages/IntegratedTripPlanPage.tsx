import React, { useState, useEffect } from 'react';
import { Box, Typography, Card, CardContent, Grid, TextField, Button, MenuItem, Select, FormControl, InputLabel, Stepper, Step, StepLabel, Alert, Divider, Chip, Paper } from '@mui/material';
import HubIcon from '@mui/icons-material/Hub';
import SecurityIcon from '@mui/icons-material/Security';
import PhishingIcon from '@mui/icons-material/Phishing';
import LocalGasStationIcon from '@mui/icons-material/LocalGasStation';
import StorefrontIcon from '@mui/icons-material/Storefront';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { apiClient } from '../services/api';
import { useStore } from '../store/useStore';
import type { IntegratedTripEvaluation } from '../types';

export const IntegratedTripPlanPage: React.FC = () => {
  const { showNotification } = useStore();
  const [vessels, setVessels] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<IntegratedTripEvaluation | null>(null);

  const [form, setForm] = useState({
    vessel_id: '',
    departure_port_id: 'P_GALLE',
    target_species: 'SP_YELLOWFIN',
    planned_departure: new Date().toISOString().slice(0, 16),
    planned_duration_h: 12.0,
    payload_mass_kg: 450.0,
    available_fuel_l: 35.0
  });

  useEffect(() => {
    const fetchVessels = async () => {
      try {
        const res = await apiClient.get('/vessels');
        setVessels(res.data);
        if (res.data.length > 0) {
          setForm((prev) => ({ ...prev, vessel_id: res.data[0].vessel_id }));
        }
      } catch (e) {
        console.error('Failed to load vessels:', e);
      }
    };
    fetchVessels();
  }, []);

  const handleRunIntegratedPipeline = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await apiClient.post('/trip-planning/evaluate', form);
      setResult(res.data);
      showNotification('Integrated C1→C2→C4 pipeline evaluation completed!', 'success');
    } catch (err: any) {
      showNotification(err.response?.data?.detail || 'Pipeline execution failed.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const steps = [
    'Stage 1: C1 Safety Risk Evaluation',
    'Stage 2: C2 Spatiotemporal Zone Recommendation',
    'Stage 3: C4 Hydrodynamic Fuel Assessment',
    'Stage 4: Operational Clearance Synthesis'
  ];

  return (
    <Box sx={{ pb: 6 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
          <HubIcon sx={{ color: '#00b4d8', fontSize: 32 }} />
          <Typography variant="h4" sx={{ fontWeight: 800, color: '#f8fafc' }}>
            Integrated Multi-Component Trip Planning Pipeline
          </Typography>
        </Box>
        <Typography variant="body2" sx={{ color: '#94a3b8' }}>
          Coordinated orchestration pipeline executing <strong>C1 (Safety) → C2 (Fishing Grounds) → C4 (PINN Fuel)</strong> with typed data contracts and shared vessel profiles.
        </Typography>
      </Box>

      {/* Stepper overview */}
      <Card sx={{ mb: 4, p: 2 }}>
        <Stepper activeStep={result ? 4 : 1} alternativeLabel>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel sx={{ '& .MuiStepLabel-label': { color: '#94a3b8', fontSize: '0.8rem', fontWeight: 600 } }}>
                {label}
              </StepLabel>
            </Step>
          ))}
        </Stepper>
      </Card>

      <Grid container spacing={3.5}>
        {/* Form Inputs */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 2 }}>
                Voyage Planning Inputs
              </Typography>

              <form onSubmit={handleRunIntegratedPipeline}>
                <FormControl fullWidth size="small" sx={{ mb: 2 }}>
                  <InputLabel>Select Vessel</InputLabel>
                  <Select
                    value={form.vessel_id}
                    label="Select Vessel"
                    onChange={(e) => setForm({ ...form, vessel_id: e.target.value })}
                  >
                    {vessels.map((v) => (
                      <MenuItem key={v.vessel_id} value={v.vessel_id}>
                        {v.name} ({v.vessel_type}) - {v.length_m}m
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <FormControl fullWidth size="small" sx={{ mb: 2 }}>
                  <InputLabel>Departure Harbour</InputLabel>
                  <Select
                    value={form.departure_port_id}
                    label="Departure Harbour"
                    onChange={(e) => setForm({ ...form, departure_port_id: e.target.value })}
                  >
                    <MenuItem value="P_GALLE">Galle Harbour</MenuItem>
                    <MenuItem value="P_MIRISSA">Mirissa Harbour</MenuItem>
                    <MenuItem value="P_TANGALLE">Tangalle Harbour</MenuItem>
                    <MenuItem value="P_NEGOMBO">Negombo Harbour</MenuItem>
                  </Select>
                </FormControl>

                <FormControl fullWidth size="small" sx={{ mb: 2 }}>
                  <InputLabel>Target Species</InputLabel>
                  <Select
                    value={form.target_species}
                    label="Target Species"
                    onChange={(e) => setForm({ ...form, target_species: e.target.value })}
                  >
                    <MenuItem value="SP_YELLOWFIN">Yellowfin Tuna</MenuItem>
                    <MenuItem value="SP_SKIPJACK">Skipjack Tuna</MenuItem>
                  </Select>
                </FormControl>

                <TextField
                  label="Planned Departure"
                  type="datetime-local"
                  size="small"
                  fullWidth
                  value={form.planned_departure}
                  onChange={(e) => setForm({ ...form, planned_departure: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                  sx={{ mb: 2 }}
                />

                <TextField
                  label="Planned Voyage Duration (h)"
                  type="number"
                  size="small"
                  fullWidth
                  value={form.planned_duration_h}
                  onChange={(e) => setForm({ ...form, planned_duration_h: parseFloat(e.target.value) })}
                  sx={{ mb: 2 }}
                />

                <TextField
                  label="Outbound Gear/Ice Cargo (kg)"
                  type="number"
                  size="small"
                  fullWidth
                  value={form.payload_mass_kg}
                  onChange={(e) => setForm({ ...form, payload_mass_kg: parseFloat(e.target.value) })}
                  sx={{ mb: 2 }}
                />

                <TextField
                  label="Available Fuel in Vessel Tank (L)"
                  type="number"
                  size="small"
                  fullWidth
                  value={form.available_fuel_l}
                  onChange={(e) => setForm({ ...form, available_fuel_l: parseFloat(e.target.value) })}
                  sx={{ mb: 3 }}
                />

                <Button
                  type="submit"
                  variant="contained"
                  color="primary"
                  fullWidth
                  size="large"
                  disabled={loading || !form.vessel_id}
                  startIcon={<PlayArrowIcon />}
                  sx={{ py: 1.2, fontWeight: 700 }}
                >
                  {loading ? 'Executing Pipeline...' : 'Run Integrated Trip Evaluation'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </Grid>

        {/* Coordinated Pipeline Output */}
        <Grid item xs={12} lg={8}>
          {result ? (
            <Card sx={{ p: 1 }}>
              <CardContent>
                {/* Synthesis verdict */}
                <Box sx={{ p: 2.5, borderRadius: 2, backgroundColor: 'rgba(0, 180, 216, 0.1)', border: '1px solid rgba(0, 180, 216, 0.3)', mb: 3 }}>
                  <Typography variant="overline" sx={{ color: '#00b4d8', fontWeight: 800 }}>
                    INTEGRATED VOYAGE SYNTHESIS VERDICT
                  </Typography>
                  <Typography variant="h5" sx={{ fontWeight: 800, color: '#f1f5f9', mt: 0.5 }}>
                    {result.workflow_recommendation}
                  </Typography>
                </Box>

                {/* Individual Component Blocks */}
                <Grid container spacing={2}>
                  {/* C1 block */}
                  <Grid item xs={12} md={4}>
                    <Paper sx={{ p: 2, height: '100%', border: '1px solid rgba(255,255,255,0.08)' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
                        <SecurityIcon sx={{ color: '#00b4d8' }} />
                        <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>
                          C1 Safety Risk
                        </Typography>
                      </Box>
                      <Chip
                        label={result.c1_safety.risk_label.toUpperCase()}
                        size="small"
                        sx={{
                          backgroundColor: result.c1_safety.risk_label === 'Danger' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(16, 185, 129, 0.2)',
                          color: result.c1_safety.risk_label === 'Danger' ? '#ef4444' : '#10b981',
                          fontWeight: 700,
                          mb: 1
                        }}
                      />
                      <Typography variant="body2" sx={{ color: '#cbd5e1' }}>
                        DRI Score: <strong>{result.c1_safety.dri_score.toFixed(1)} / 100</strong>
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#64748b', display: 'block', mt: 0.5 }}>
                        Dominant: {result.c1_safety.dominant_risk_factor.replace(/_/g, ' ')}
                      </Typography>
                    </Paper>
                  </Grid>

                  {/* C2 block */}
                  <Grid item xs={12} md={4}>
                    <Paper sx={{ p: 2, height: '100%', border: '1px solid rgba(255,255,255,0.08)' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
                        <PhishingIcon sx={{ color: '#2ec4b6' }} />
                        <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>
                          C2 Optimal Zone
                        </Typography>
                      </Box>
                      <Typography variant="h6" sx={{ fontWeight: 800, color: '#2ec4b6', mb: 0.5 }}>
                        {result.c2_recommended_zone.zone_id}
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#cbd5e1' }}>
                        Suitability: <strong>{result.c2_recommended_zone.habitat_suitability_index.toFixed(3)}</strong>
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#64748b', display: 'block', mt: 0.5 }}>
                        Distance: {result.c2_recommended_zone.distance_km} km | Pareto Rank {result.c2_recommended_zone.pareto_rank}
                      </Typography>
                    </Paper>
                  </Grid>

                  {/* C4 block */}
                  <Grid item xs={12} md={4}>
                    <Paper sx={{ p: 2, height: '100%', border: '1px solid rgba(255,255,255,0.08)' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
                        <LocalGasStationIcon sx={{ color: '#f59e0b' }} />
                        <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>
                          C4 Fuel Plan
                        </Typography>
                      </Box>
                      <Typography variant="h6" sx={{ fontWeight: 800, color: '#fbbf24', mb: 0.5 }}>
                        {result.c4_fuel_plan.total_required_fuel_l} L
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#cbd5e1' }}>
                        Trip: {result.c4_fuel_plan.predicted_total_fuel_l}L (+{result.c4_fuel_plan.recommended_reserve_l}L rsv)
                      </Typography>
                      <Typography variant="caption" sx={{ color: result.c4_fuel_plan.fuel_sufficiency_status === 'SUFFICIENT' ? '#34d399' : '#f87171', display: 'block', mt: 0.5, fontWeight: 700 }}>
                        {result.c4_fuel_plan.fuel_sufficiency_status} (Tank: {result.c4_fuel_plan.available_fuel_l}L)
                      </Typography>
                    </Paper>
                  </Grid>
                </Grid>

                <Alert severity="info" sx={{ mt: 3, fontSize: '0.75rem', borderRadius: 2 }}>
                  Evaluation ID: {result.trip_evaluation_id} • Integrated research pipeline compliant with temporal separation constraints. All component decisions remain independently auditable.
                </Alert>
              </CardContent>
            </Card>
          ) : (
            <Card sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', p: 4 }}>
              <Box sx={{ textAlign: 'center', color: '#64748b' }}>
                <HubIcon sx={{ fontSize: 64, mb: 1.5, opacity: 0.4 }} />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Awaiting Pipeline Trigger
                </Typography>
                <Typography variant="body2">
                  Select vessel and planned parameters to coordinate C1 safety evaluation, C2 zone optimization, and C4 fuel planning into an integrated synthesis verdict.
                </Typography>
              </Box>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};
