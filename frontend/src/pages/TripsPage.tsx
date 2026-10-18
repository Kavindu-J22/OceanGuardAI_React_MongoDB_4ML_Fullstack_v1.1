import React, { useState, useEffect } from 'react';
import { Box, Typography, Card, CardContent, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Dialog, DialogTitle, DialogContent, DialogActions, TextField, MenuItem, Select, FormControl, InputLabel, Grid, Chip, IconButton, Tooltip } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import PhishingIcon from '@mui/icons-material/Phishing';
import DoneAllIcon from '@mui/icons-material/DoneAll';
import { apiClient } from '../services/api';
import { useStore } from '../store/useStore';
import type { Trip, Vessel } from '../types';

export const TripsPage: React.FC = () => {
  const { showNotification } = useStore();
  const [trips, setTrips] = useState<Trip[]>([]);
  const [vessels, setVessels] = useState<Vessel[]>([]);
  const [openCreate, setOpenCreate] = useState(false);
  const [openCatchModal, setOpenCatchModal] = useState(false);
  const [selectedTrip, setSelectedTrip] = useState<Trip | null>(null);

  // New trip form
  const [tripForm, setTripForm] = useState({
    vessel_id: '',
    departure_port_id: 'P_GALLE',
    target_zone_id: 'C2Z005',
    target_species: 'SP_YELLOWFIN',
    planned_departure: new Date().toISOString().slice(0, 16),
    planned_duration_h: 12.0,
    initial_cargo_kg: 350.0
  });

  // Catch logging form
  const [catchForm, setCatchForm] = useState({
    species_id: 'SP_YELLOWFIN',
    species_name: 'Yellowfin tuna',
    weight_kg: 180.0,
    storage_temp_c: 3.5,
    actual_fuel_consumed_l: 36.5
  });

  const fetchData = async () => {
    try {
      const [tRes, vRes] = await Promise.all([
        apiClient.get('/trips'),
        apiClient.get('/vessels')
      ]);
      setTrips(tRes.data);
      setVessels(vRes.data);
      if (vRes.data.length > 0 && !tripForm.vessel_id) {
        setTripForm((prev) => ({ ...prev, vessel_id: vRes.data[0].vessel_id }));
      }
    } catch (e) {
      console.error('Failed to load trips:', e);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreateTrip = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.post('/trips', tripForm);
      showNotification('Fishing trip planned and safety evaluated!', 'success');
      setOpenCreate(false);
      fetchData();
    } catch (err: any) {
      showNotification(err.response?.data?.detail || 'Failed to create trip.', 'error');
    }
  };

  const handleLogCatch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedTrip) return;

    try {
      await apiClient.patch(`/trips/${selectedTrip.trip_id}`, {
        status: 'completed',
        actual_fuel_consumed_l: catchForm.actual_fuel_consumed_l,
        catches: [
          {
            species_id: catchForm.species_id,
            species_name: catchForm.species_name,
            weight_kg: catchForm.weight_kg,
            storage_temp_c: catchForm.storage_temp_c,
            catch_time: new Date().toISOString()
          }
        ]
      });
      showNotification(`Catch logged and trip ${selectedTrip.trip_id} marked as completed!`, 'success');
      setOpenCatchModal(false);
      fetchData();
    } catch (err: any) {
      showNotification(err.response?.data?.detail || 'Failed to log catch.', 'error');
    }
  };

  return (
    <Box sx={{ pb: 6 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 800, color: '#f8fafc' }}>
            Fishing Trips Management
          </Typography>
          <Typography variant="body2" sx={{ color: '#94a3b8' }}>
            Voyage scheduling, real-time safety indices, and catch recording
          </Typography>
        </Box>
        <Button variant="contained" color="primary" startIcon={<AddIcon />} onClick={() => setOpenCreate(true)}>
          Plan New Voyage
        </Button>
      </Box>

      <Card>
        <CardContent>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Trip ID</TableCell>
                  <TableCell>Vessel</TableCell>
                  <TableCell>Departure Port</TableCell>
                  <TableCell>Target Zone</TableCell>
                  <TableCell>Target Species</TableCell>
                  <TableCell>Duration</TableCell>
                  <TableCell>Safety Verdict</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {trips.map((t) => (
                  <TableRow key={t.trip_id} hover>
                    <TableCell sx={{ fontWeight: 700, color: '#00b4d8' }}>{t.trip_id}</TableCell>
                    <TableCell>{t.vessel_id}</TableCell>
                    <TableCell>{t.departure_port_id}</TableCell>
                    <TableCell>{t.target_zone_id}</TableCell>
                    <TableCell>{t.target_species}</TableCell>
                    <TableCell>{t.planned_duration_h} hrs</TableCell>
                    <TableCell>
                      <Chip
                        label={t.c1_assessment?.risk_label || 'Safe'}
                        size="small"
                        sx={{
                          backgroundColor: t.c1_assessment?.risk_label === 'Danger' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(16, 185, 129, 0.2)',
                          color: t.c1_assessment?.risk_label === 'Danger' ? '#ef4444' : '#10b981',
                          fontWeight: 700
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={t.status.toUpperCase()}
                        size="small"
                        variant={t.status === 'completed' ? 'filled' : 'outlined'}
                        color={t.status === 'completed' ? 'success' : 'default'}
                      />
                    </TableCell>
                    <TableCell align="right">
                      {t.status === 'planned' && (
                        <Tooltip title="Log Catch & Complete Trip">
                          <IconButton
                            color="secondary"
                            onClick={() => {
                              setSelectedTrip(t);
                              setOpenCatchModal(true);
                            }}
                          >
                            <PhishingIcon />
                          </IconButton>
                        </Tooltip>
                      )}
                      {t.status === 'completed' && (
                        <Tooltip title="Completed Trip">
                          <DoneAllIcon color="success" fontSize="small" />
                        </Tooltip>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Plan New Voyage Modal */}
      <Dialog open={openCreate} onClose={() => setOpenCreate(false)} maxWidth="sm" fullWidth PaperProps={{ sx: { backgroundColor: '#0f1d36', borderRadius: 3 } }}>
        <form onSubmit={handleCreateTrip}>
          <DialogTitle sx={{ fontWeight: 700 }}>Plan New Fishing Voyage</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 0.5 }}>
              <Grid item xs={12}>
                <FormControl fullWidth size="small">
                  <InputLabel>Select Vessel</InputLabel>
                  <Select
                    value={tripForm.vessel_id}
                    label="Select Vessel"
                    onChange={(e) => setTripForm({ ...tripForm, vessel_id: e.target.value })}
                  >
                    {vessels.map((v) => (
                      <MenuItem key={v.vessel_id} value={v.vessel_id}>
                        {v.name} ({v.vessel_type})
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={6}>
                <FormControl fullWidth size="small">
                  <InputLabel>Departure Port</InputLabel>
                  <Select
                    value={tripForm.departure_port_id}
                    label="Departure Port"
                    onChange={(e) => setTripForm({ ...tripForm, departure_port_id: e.target.value })}
                  >
                    <MenuItem value="P_GALLE">Galle Harbour</MenuItem>
                    <MenuItem value="P_MIRISSA">Mirissa Harbour</MenuItem>
                    <MenuItem value="P_TANGALLE">Tangalle Harbour</MenuItem>
                    <MenuItem value="P_NEGOMBO">Negombo Harbour</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={6}>
                <TextField
                  label="Target Zone ID"
                  size="small"
                  fullWidth
                  value={tripForm.target_zone_id}
                  onChange={(e) => setTripForm({ ...tripForm, target_zone_id: e.target.value })}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  label="Duration (Hours)"
                  type="number"
                  size="small"
                  fullWidth
                  value={tripForm.planned_duration_h}
                  onChange={(e) => setTripForm({ ...tripForm, planned_duration_h: parseFloat(e.target.value) })}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  label="Initial Gear/Ice Cargo (kg)"
                  type="number"
                  size="small"
                  fullWidth
                  value={tripForm.initial_cargo_kg}
                  onChange={(e) => setTripForm({ ...tripForm, initial_cargo_kg: parseFloat(e.target.value) })}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions sx={{ p: 2.5 }}>
            <Button onClick={() => setOpenCreate(false)} color="inherit">Cancel</Button>
            <Button type="submit" variant="contained" color="primary">Create Voyage</Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Log Catch & Fuel Modal */}
      <Dialog open={openCatchModal} onClose={() => setOpenCatchModal(false)} maxWidth="sm" fullWidth PaperProps={{ sx: { backgroundColor: '#0f1d36', borderRadius: 3 } }}>
        <form onSubmit={handleLogCatch}>
          <DialogTitle sx={{ fontWeight: 700 }}>Log Landed Catch & Complete Trip</DialogTitle>
          <DialogContent>
            <Typography variant="body2" sx={{ color: '#94a3b8', mb: 2 }}>
              Recording actual catch parameters for Trip: <strong>{selectedTrip?.trip_id}</strong>
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth size="small">
                  <InputLabel>Caught Species</InputLabel>
                  <Select
                    value={catchForm.species_id}
                    label="Caught Species"
                    onChange={(e) => {
                      const sp = e.target.value;
                      setCatchForm({
                        ...catchForm,
                        species_id: sp,
                        species_name: sp === 'SP_YELLOWFIN' ? 'Yellowfin tuna' : 'Skipjack tuna'
                      });
                    }}
                  >
                    <MenuItem value="SP_YELLOWFIN">Yellowfin Tuna</MenuItem>
                    <MenuItem value="SP_SKIPJACK">Skipjack Tuna</MenuItem>
                    <MenuItem value="SP_SEER">Seer Fish</MenuItem>
                    <MenuItem value="SP_MACKEREL">Indian Mackerel</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Landed Weight (kg)"
                  type="number"
                  size="small"
                  fullWidth
                  value={catchForm.weight_kg}
                  onChange={(e) => setCatchForm({ ...catchForm, weight_kg: parseFloat(e.target.value) })}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Fish Hold Temp (°C)"
                  type="number"
                  size="small"
                  inputProps={{ step: '0.5' }}
                  fullWidth
                  value={catchForm.storage_temp_c}
                  onChange={(e) => setCatchForm({ ...catchForm, storage_temp_c: parseFloat(e.target.value) })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Actual Fuel Consumed (L)"
                  type="number"
                  size="small"
                  fullWidth
                  value={catchForm.actual_fuel_consumed_l}
                  onChange={(e) => setCatchForm({ ...catchForm, actual_fuel_consumed_l: parseFloat(e.target.value) })}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions sx={{ p: 2.5 }}>
            <Button onClick={() => setOpenCatchModal(false)} color="inherit">Cancel</Button>
            <Button type="submit" variant="contained" color="secondary">Confirm Catch</Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
};
