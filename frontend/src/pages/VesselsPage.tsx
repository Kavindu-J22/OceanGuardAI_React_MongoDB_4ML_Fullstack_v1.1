import React, { useEffect, useState } from 'react';
import { Box, Typography, Button, Card, CardContent, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Dialog, DialogTitle, DialogContent, DialogActions, TextField, MenuItem, Select, FormControl, InputLabel, Grid, Chip } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DirectionsBoatIcon from '@mui/icons-material/DirectionsBoat';
import { apiClient } from '../services/api';
import { useStore } from '../store/useStore';
import type { Vessel } from '../types';

export const VesselsPage: React.FC = () => {
  const { showNotification } = useStore();
  const [vessels, setVessels] = useState<Vessel[]>([]);
  const [openModal, setOpenModal] = useState(false);
  const [loading, setLoading] = useState(false);

  const [form, setForm] = useState({
    name: 'Sagara Rani 04',
    vessel_type: 'OFRP',
    length_m: 6.8,
    beam_m: 1.8,
    lightship_mass_kg: 980.0,
    payload_limit_kg: 1200.0,
    lightship_freeboard_m: 0.95,
    home_port_id: 'P_GALLE'
  });

  const fetchVessels = async () => {
    try {
      const res = await apiClient.get('/vessels');
      setVessels(res.data);
    } catch (e) {
      console.error('Failed to load vessels:', e);
    }
  };

  useEffect(() => {
    fetchVessels();
  }, []);

  const handleCreateVessel = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await apiClient.post('/vessels', form);
      showNotification('Vessel registered successfully!', 'success');
      setOpenModal(false);
      fetchVessels();
    } catch (err: any) {
      showNotification(err.response?.data?.detail || 'Failed to register vessel.', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ pb: 6 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 800, color: '#f8fafc' }}>
            Vessel Fleet Management
          </Typography>
          <Typography variant="body2" sx={{ color: '#94a3b8' }}>
            Registered artisanal and coastal fishing craft with hydro-physical profiles
          </Typography>
        </Box>
        <Button variant="contained" color="primary" startIcon={<AddIcon />} onClick={() => setOpenModal(true)}>
          Register Vessel
        </Button>
      </Box>

      <Card>
        <CardContent>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Vessel ID</TableCell>
                  <TableCell>Vessel Name</TableCell>
                  <TableCell>Craft Type</TableCell>
                  <TableCell>Length (m)</TableCell>
                  <TableCell>Beam (m)</TableCell>
                  <TableCell>Lightship Mass</TableCell>
                  <TableCell>Payload Limit</TableCell>
                  <TableCell>Freeboard (m)</TableCell>
                  <TableCell>Home Port</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {vessels.map((v) => (
                  <TableRow key={v.vessel_id} hover>
                    <TableCell sx={{ fontWeight: 700, color: '#00b4d8' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <DirectionsBoatIcon fontSize="small" sx={{ color: '#94a3b8' }} />
                        {v.vessel_id}
                      </Box>
                    </TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>{v.name}</TableCell>
                    <TableCell>
                      <Chip
                        label={v.vessel_type}
                        size="small"
                        sx={{
                          backgroundColor: v.vessel_type === 'IMUL' ? '#7c3aed' : v.vessel_type === 'OFRP' ? '#0284c7' : '#0d9488',
                          color: '#fff',
                          fontWeight: 700
                        }}
                      />
                    </TableCell>
                    <TableCell>{v.length_m.toFixed(2)} m</TableCell>
                    <TableCell>{v.beam_m.toFixed(2)} m</TableCell>
                    <TableCell>{v.lightship_mass_kg.toLocaleString()} kg</TableCell>
                    <TableCell>{v.payload_limit_kg.toLocaleString()} kg</TableCell>
                    <TableCell>{v.lightship_freeboard_m.toFixed(2)} m</TableCell>
                    <TableCell>{v.home_port_id}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Register Vessel Modal */}
      <Dialog open={openModal} onClose={() => setOpenModal(false)} maxWidth="sm" fullWidth PaperProps={{ sx: { backgroundColor: '#0f1d36', borderRadius: 3 } }}>
        <form onSubmit={handleCreateVessel}>
          <DialogTitle sx={{ fontWeight: 700, color: '#f8fafc' }}>
            Register New Fishing Craft
          </DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 0.5 }}>
              <Grid item xs={12} sm={8}>
                <TextField
                  label="Vessel Name"
                  fullWidth
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <FormControl fullWidth>
                  <InputLabel>Type</InputLabel>
                  <Select
                    value={form.vessel_type}
                    label="Type"
                    onChange={(e) => setForm({ ...form, vessel_type: e.target.value })}
                  >
                    <MenuItem value="OFRP">OFRP (Outboard)</MenuItem>
                    <MenuItem value="IDAY">IDAY (Inboard 1-Day)</MenuItem>
                    <MenuItem value="IMUL">IMUL (Multi-Day)</MenuItem>
                    <MenuItem value="NBSB">NBSB (Non-Motorized)</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={6}>
                <TextField
                  label="Length Over All (m)"
                  type="number"
                  inputProps={{ step: '0.1' }}
                  fullWidth
                  value={form.length_m}
                  onChange={(e) => setForm({ ...form, length_m: parseFloat(e.target.value) })}
                  required
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  label="Beam Width (m)"
                  type="number"
                  inputProps={{ step: '0.1' }}
                  fullWidth
                  value={form.beam_m}
                  onChange={(e) => setForm({ ...form, beam_m: parseFloat(e.target.value) })}
                  required
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  label="Lightship Mass (kg)"
                  type="number"
                  fullWidth
                  value={form.lightship_mass_kg}
                  onChange={(e) => setForm({ ...form, lightship_mass_kg: parseFloat(e.target.value) })}
                  required
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  label="Max Payload Limit (kg)"
                  type="number"
                  fullWidth
                  value={form.payload_limit_kg}
                  onChange={(e) => setForm({ ...form, payload_limit_kg: parseFloat(e.target.value) })}
                  required
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  label="Lightship Freeboard (m)"
                  type="number"
                  inputProps={{ step: '0.01' }}
                  fullWidth
                  value={form.lightship_freeboard_m}
                  onChange={(e) => setForm({ ...form, lightship_freeboard_m: parseFloat(e.target.value) })}
                  required
                />
              </Grid>
              <Grid item xs={6}>
                <FormControl fullWidth>
                  <InputLabel>Home Port</InputLabel>
                  <Select
                    value={form.home_port_id}
                    label="Home Port"
                    onChange={(e) => setForm({ ...form, home_port_id: e.target.value })}
                  >
                    <MenuItem value="P_GALLE">Galle Harbour</MenuItem>
                    <MenuItem value="P_MIRISSA">Mirissa Harbour</MenuItem>
                    <MenuItem value="P_TANGALLE">Tangalle Harbour</MenuItem>
                    <MenuItem value="P_NEGOMBO">Negombo Harbour</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions sx={{ p: 2.5 }}>
            <Button onClick={() => setOpenModal(false)} color="inherit">Cancel</Button>
            <Button type="submit" variant="contained" color="primary" disabled={loading}>
              {loading ? 'Saving...' : 'Register Vessel'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
};
