import React, { useState, useEffect } from 'react';
import { Box, Typography, Card, CardContent, Grid, Button, MenuItem, Select, FormControl, InputLabel, TextField, Chip, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Alert, LinearProgress } from '@mui/material';
import PhishingIcon from '@mui/icons-material/Phishing';
import ExploreIcon from '@mui/icons-material/Explore';
import { apiClient } from '../services/api';
import { FishingMap } from '../components/maps/FishingMap';
import type { RecommendedZone } from '../types';

export const FishingC2Page: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [departurePort, setDeparturePort] = useState('P_GALLE');
  const [targetSpecies, setTargetSpecies] = useState('SP_YELLOWFIN');
  const [maxDistance, setMaxDistance] = useState(140.0);
  const [candidateZones, setCandidateZones] = useState<RecommendedZone[]>([]);
  const [selectedZone, setSelectedZone] = useState<RecommendedZone | null>(null);

  const fetchRecommendations = async () => {
    setLoading(true);
    try {
      const res = await apiClient.post('/ml/c2/predict', {
        departure_port_id: departurePort,
        target_species: targetSpecies,
        max_distance_km: maxDistance
      });
      const zones = res.data.candidate_zones || [];
      setCandidateZones(zones);
      if (zones.length > 0) {
        setSelectedZone(zones[0]);
      }
    } catch (e) {
      console.error('Failed to load C2 recommendations:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, [departurePort, targetSpecies]);

  return (
    <Box sx={{ pb: 6 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
          <PhishingIcon sx={{ color: '#2ec4b6', fontSize: 32 }} />
          <Typography variant="h4" sx={{ fontWeight: 800, color: '#f8fafc' }}>
            Component 2 • Spatiotemporal Fishing Ground Recommendation
          </Typography>
        </Box>
        <Typography variant="body2" sx={{ color: '#94a3b8' }}>
          Deep learning model: <strong>ST-GCN with Spatial Attention</strong> & <strong>Pareto Multi-Objective Optimization</strong> balancing habitat suitability, distance, and fuel expenditure.
        </Typography>
      </Box>

      {/* Control Bar */}
      <Card sx={{ mb: 3.5, p: 1 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Departure Harbour</InputLabel>
                <Select
                  value={departurePort}
                  label="Departure Harbour"
                  onChange={(e) => setDeparturePort(e.target.value)}
                >
                  <MenuItem value="P_GALLE">Galle Fishery Harbour</MenuItem>
                  <MenuItem value="P_MIRISSA">Mirissa Fishery Harbour</MenuItem>
                  <MenuItem value="P_TANGALLE">Tangalle Fishery Harbour</MenuItem>
                  <MenuItem value="P_NEGOMBO">Negombo Fishery Harbour</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Target Fish Species</InputLabel>
                <Select
                  value={targetSpecies}
                  label="Target Fish Species"
                  onChange={(e) => setTargetSpecies(e.target.value)}
                >
                  <MenuItem value="SP_YELLOWFIN">Yellowfin Tuna (Thunnus albacares)</MenuItem>
                  <MenuItem value="SP_SKIPJACK">Skipjack Tuna (Katsuwonus pelamis)</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={2}>
              <TextField
                label="Max Range (km)"
                type="number"
                size="small"
                fullWidth
                value={maxDistance}
                onChange={(e) => setMaxDistance(parseFloat(e.target.value) || 100)}
              />
            </Grid>
            <Grid item xs={12} sm={2}>
              <Button
                variant="contained"
                color="secondary"
                fullWidth
                disabled={loading}
                onClick={fetchRecommendations}
                startIcon={<ExploreIcon />}
                sx={{ height: 40, fontWeight: 700 }}
              >
                Optimize
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {loading && <LinearProgress sx={{ mb: 3 }} />}

      {/* Map & Pareto List Grid */}
      <Grid container spacing={3.5} sx={{ mb: 4 }}>
        <Grid item xs={12} lg={7}>
          <Card sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1.5 }}>
              <Typography variant="h6" sx={{ fontWeight: 700 }}>
                Spatial Fishing Grid & Environmental Zones
              </Typography>
              {selectedZone && (
                <Chip
                  label={`Selected: ${selectedZone.zone_id} (HSI: ${selectedZone.habitat_suitability_index.toFixed(3)})`}
                  color="secondary"
                  size="small"
                  sx={{ fontWeight: 700 }}
                />
              )}
            </Box>
            <FishingMap
              zones={candidateZones}
              selectedZone={selectedZone}
              departurePortId={departurePort}
              height="480px"
            />
          </Card>
        </Grid>

        <Grid item xs={12} lg={5}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <CardContent sx={{ flex: 1 }}>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 1 }}>
                Pareto Non-Dominated Candidate Zones
              </Typography>
              <Typography variant="caption" sx={{ color: '#94a3b8', display: 'block', mb: 2 }}>
                Optimized over Max(HSI), Min(Distance), and Min(Fuel). Click a zone to highlight on map.
              </Typography>

              <TableContainer sx={{ maxHeight: 420 }}>
                <Table size="small" stickyHeader>
                  <TableHead>
                    <TableRow>
                      <TableCell>Zone</TableCell>
                      <TableCell>Suitability (HSI)</TableCell>
                      <TableCell>Distance</TableCell>
                      <TableCell>Fuel (L)</TableCell>
                      <TableCell>Rank</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {candidateZones.map((z) => {
                      const isSel = selectedZone?.zone_id === z.zone_id;
                      return (
                        <TableRow
                          key={z.zone_id}
                          hover
                          onClick={() => setSelectedZone(z)}
                          sx={{
                            cursor: 'pointer',
                            backgroundColor: isSel ? 'rgba(46, 196, 182, 0.15)' : 'transparent',
                          }}
                        >
                          <TableCell sx={{ fontWeight: 700, color: '#f1f5f9' }}>{z.zone_id}</TableCell>
                          <TableCell sx={{ fontWeight: 700, color: '#2ec4b6' }}>
                            {z.habitat_suitability_index.toFixed(3)}
                          </TableCell>
                          <TableCell>{z.distance_km.toFixed(1)} km</TableCell>
                          <TableCell>{z.estimated_fuel_l.toFixed(1)} L</TableCell>
                          <TableCell>
                            <Chip
                              label={`Rank ${z.pareto_rank}`}
                              size="small"
                              sx={{
                                backgroundColor: z.pareto_rank === 1 ? 'rgba(16, 185, 129, 0.2)' : 'rgba(255, 255, 255, 0.08)',
                                color: z.pareto_rank === 1 ? '#10b981' : '#94a3b8',
                                fontWeight: 700,
                                fontSize: '0.65rem'
                              }}
                            />
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Scientific Limitation & Disclaimers */}
      <Alert severity="warning" sx={{ borderRadius: 2 }}>
        <strong>SCIENTIFIC DISTINCTION NOTICE:</strong> Predicted Habitat Suitability Index (HSI) models physiological ocean preferences (SST, Chlorophyll, currents). It is NOT empirical proof of actual fish presence or catch guarantee. Any route paths shown are Great-Circle reference paths and MUST NOT be used as navigational clearance.
      </Alert>
    </Box>
  );
};
