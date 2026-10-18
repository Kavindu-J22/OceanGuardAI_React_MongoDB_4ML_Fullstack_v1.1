import React, { useState, useEffect } from 'react';
import { Box, Typography, Card, CardContent, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, Dialog, DialogTitle, DialogContent, DialogActions, TextField, MenuItem, Select, FormControl, InputLabel, Alert, Grid } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import VerifiedIcon from '@mui/icons-material/Verified';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import { apiClient } from '../services/api';
import { useStore } from '../store/useStore';
import type { Observation } from '../types';

export const ObservationsPage: React.FC = () => {
  const { role, showNotification } = useStore();
  const [observations, setObservations] = useState<Observation[]>([]);
  const [openModal, setOpenModal] = useState(false);

  const [form, setForm] = useState({
    type: 'CATCH_RECORD',
    vessel_id: 'V038',
    latitude: 5.92,
    longitude: 80.45,
    data_origin: 'observed',
    species: 'Yellowfin tuna',
    weight_kg: 160.0
  });

  const fetchObservations = async () => {
    try {
      const res = await apiClient.get('/observations');
      setObservations(res.data);
    } catch (e) {
      console.error('Failed to load observations:', e);
    }
  };

  useEffect(() => {
    fetchObservations();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.post('/observations', {
        type: form.type,
        vessel_id: form.vessel_id,
        latitude: form.latitude,
        longitude: form.longitude,
        data_origin: form.data_origin,
        payload: {
          species: form.species,
          weight_kg: form.weight_kg
        }
      });
      showNotification('Field observation submitted for research verification.', 'success');
      setOpenModal(false);
      fetchObservations();
    } catch (err: any) {
      showNotification(err.response?.data?.detail || 'Failed to submit observation.', 'error');
    }
  };

  const handleReview = async (obsId: string, status: 'approved' | 'rejected') => {
    try {
      await apiClient.post(`/observations/${obsId}/review`, {
        verification_status: status,
        review_notes: `Reviewed by ${role}`
      });
      showNotification(`Observation ${obsId} ${status}!`, status === 'approved' ? 'success' : 'warning');
      fetchObservations();
    } catch (err: any) {
      showNotification(err.response?.data?.detail || 'Review action failed.', 'error');
    }
  };

  return (
    <Box sx={{ pb: 6 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 800, color: '#f8fafc' }}>
            Field Observations & Ground Truth Verification
          </Typography>
          <Typography variant="body2" sx={{ color: '#94a3b8' }}>
            Scientific pipeline separating raw real-world fisherman logs from model-retraining candidate sets
          </Typography>
        </Box>
        <Button variant="contained" color="primary" startIcon={<AddIcon />} onClick={() => setOpenModal(true)}>
          Submit Observation
        </Button>
      </Box>

      <Card>
        <CardContent>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Observation ID</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Vessel</TableCell>
                  <TableCell>Data Origin</TableCell>
                  <TableCell>Payload</TableCell>
                  <TableCell>Verification Status</TableCell>
                  <TableCell>Timestamp</TableCell>
                  {role !== 'fisherman' && <TableCell align="right">Research Review</TableCell>}
                </TableRow>
              </TableHead>
              <TableBody>
                {observations.map((obs) => (
                  <TableRow key={obs.observation_id} hover>
                    <TableCell sx={{ fontWeight: 700, color: '#00b4d8' }}>{obs.observation_id}</TableCell>
                    <TableCell>{obs.type}</TableCell>
                    <TableCell>{obs.vessel_id || 'N/A'}</TableCell>
                    <TableCell>
                      <Chip
                        label={obs.data_origin.toUpperCase()}
                        size="small"
                        sx={{
                          backgroundColor: obs.data_origin === 'verified_outcome' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(0, 180, 216, 0.2)',
                          color: obs.data_origin === 'verified_outcome' ? '#10b981' : '#38bdf8',
                          fontWeight: 700,
                          fontSize: '0.65rem'
                        }}
                      />
                    </TableCell>
                    <TableCell sx={{ fontSize: '0.8rem', color: '#cbd5e1' }}>
                      {JSON.stringify(obs.payload)}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={obs.verification_status.toUpperCase()}
                        size="small"
                        variant="outlined"
                        color={obs.verification_status === 'approved' ? 'success' : obs.verification_status === 'rejected' ? 'error' : 'warning'}
                      />
                    </TableCell>
                    <TableCell sx={{ fontSize: '0.75rem', color: '#64748b' }}>
                      {new Date(obs.timestamp).toLocaleString()}
                    </TableCell>
                    {role !== 'fisherman' && (
                      <TableCell align="right">
                        {obs.verification_status === 'pending_review' && (
                          <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                            <Button size="small" color="success" onClick={() => handleReview(obs.observation_id, 'approved')}>
                              Approve
                            </Button>
                            <Button size="small" color="error" onClick={() => handleReview(obs.observation_id, 'rejected')}>
                              Reject
                            </Button>
                          </Box>
                        )}
                        {obs.verification_status === 'approved' && (
                          <VerifiedIcon color="success" fontSize="small" />
                        )}
                      </TableCell>
                    )}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* New Observation Dialog */}
      <Dialog open={openModal} onClose={() => setOpenModal(false)} maxWidth="sm" fullWidth PaperProps={{ sx: { backgroundColor: '#0f1d36', borderRadius: 3 } }}>
        <form onSubmit={handleCreate}>
          <DialogTitle sx={{ fontWeight: 700 }}>Log Field Observation</DialogTitle>
          <DialogContent>
            <FormControl fullWidth size="small" sx={{ mt: 1, mb: 2 }}>
              <InputLabel>Observation Type</InputLabel>
              <Select
                value={form.type}
                label="Observation Type"
                onChange={(e) => setForm({ ...form, type: e.target.value })}
              >
                <MenuItem value="CATCH_RECORD">Fisherman Catch Record</MenuItem>
                <MenuItem value="FUEL_LOG">Vessel Fuel Tank Dip Log</MenuItem>
                <MenuItem value="WEATHER_STATION">Port Weather Anemometer</MenuItem>
              </Select>
            </FormControl>

            <TextField
              label="Vessel ID"
              size="small"
              fullWidth
              value={form.vessel_id}
              onChange={(e) => setForm({ ...form, vessel_id: e.target.value })}
              sx={{ mb: 2 }}
            />

            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={6}>
                <TextField
                  label="Species / Item"
                  size="small"
                  fullWidth
                  value={form.species}
                  onChange={(e) => setForm({ ...form, species: e.target.value })}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  label="Quantity / Value"
                  type="number"
                  size="small"
                  fullWidth
                  value={form.weight_kg}
                  onChange={(e) => setForm({ ...form, weight_kg: parseFloat(e.target.value) })}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions sx={{ p: 2.5 }}>
            <Button onClick={() => setOpenModal(false)} color="inherit">Cancel</Button>
            <Button type="submit" variant="contained" color="primary">Submit for Review</Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
};
