import React, { useState, useEffect } from 'react';
import { Box, Typography, Card, CardContent, Grid, TextField, Button, MenuItem, Select, FormControl, InputLabel, Alert, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, Paper } from '@mui/material';
import SosIcon from '@mui/icons-material/Sos';
import MyLocationIcon from '@mui/icons-material/MyLocation';
import WarningIcon from '@mui/icons-material/Warning';
import { apiClient } from '../services/api';
import { useStore } from '../store/useStore';
import type { EmergencyEvent } from '../types';

export const RescuePage: React.FC = () => {
  const { isOnline, showNotification } = useStore();
  const [events, setEvents] = useState<EmergencyEvent[]>([]);
  const [loading, setLoading] = useState(false);

  const [form, setForm] = useState({
    vessel_id: 'V038',
    latitude: 5.92,
    longitude: 80.45,
    distress_type: 'CAPSIZING_RISK',
    description: 'Rough swell causing excessive rolling; freeboard critically compromised.',
    souls_on_board: 4
  });

  const fetchEvents = async () => {
    try {
      const res = await apiClient.get('/rescue/events');
      setEvents(res.data);
    } catch (e) {
      console.error('Failed to load rescue events:', e);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, []);

  const handleCaptureLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setForm({
            ...form,
            latitude: parseFloat(pos.coords.latitude.toFixed(4)),
            longitude: parseFloat(pos.coords.longitude.toFixed(4))
          });
          showNotification('GPS Coordinates updated from device sensor.', 'info');
        },
        (err) => {
          showNotification('Could not acquire device GPS. Using manual coordinates.', 'warning');
        }
      );
    }
  };

  const handleSendSOS = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await apiClient.post('/rescue/emergency', {
        ...form,
        is_offline_sync: !isOnline
      });

      if (res.data._is_offline_queued) {
        showNotification('SOS queued locally in IndexedDB. Will transmit immediately upon shore connection.', 'warning');
      } else {
        showNotification('Distress event transmitted to shore coordination station.', 'error');
      }
      fetchEvents();
    } catch (err: any) {
      showNotification(err.response?.data?.detail || 'Failed to submit distress event.', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ pb: 6 }}>
      {/* Critical Legal Warning Banner */}
      <Alert severity="error" sx={{ mb: 4, borderRadius: 2, border: '1px solid #ef4444' }}>
        <strong>MANDATORY MARITIME NOTICE:</strong> This application is an experimental research system and NOT certified emergency apparatus. It DOES NOT substitute international GMDSS equipment, satellite EPIRBs, SARTs, or Marine VHF Channel 16. In life-threatening emergencies, immediately activate certified hardware distress beacons.
      </Alert>

      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
          <SosIcon sx={{ color: '#ef4444', fontSize: 36 }} />
          <Typography variant="h4" sx={{ fontWeight: 800, color: '#f8fafc' }}>
            Maritime Emergency & Rescue Subsystem
          </Typography>
        </Box>
        <Typography variant="body2" sx={{ color: '#94a3b8' }}>
          Distress telemetry logging with offline IndexedDB queueing and verified shore station transmission tracking.
        </Typography>
      </Box>

      <Grid container spacing={3.5}>
        {/* Form */}
        <Grid item xs={12} lg={5}>
          <Card sx={{ border: '2px solid rgba(239, 68, 68, 0.4)' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <WarningIcon sx={{ color: '#ef4444' }} />
                <Typography variant="h6" sx={{ fontWeight: 700, color: '#f8fafc' }}>
                  Log Distress Event
                </Typography>
              </Box>

              <form onSubmit={handleSendSOS}>
                <TextField
                  label="Vessel ID"
                  size="small"
                  fullWidth
                  value={form.vessel_id}
                  onChange={(e) => setForm({ ...form, vessel_id: e.target.value })}
                  sx={{ mb: 2 }}
                  required
                />

                <Grid container spacing={2} sx={{ mb: 2 }}>
                  <Grid item xs={6}>
                    <TextField
                      label="Latitude (°N)"
                      type="number"
                      size="small"
                      inputProps={{ step: '0.0001' }}
                      fullWidth
                      value={form.latitude}
                      onChange={(e) => setForm({ ...form, latitude: parseFloat(e.target.value) })}
                      required
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      label="Longitude (°E)"
                      type="number"
                      size="small"
                      inputProps={{ step: '0.0001' }}
                      fullWidth
                      value={form.longitude}
                      onChange={(e) => setForm({ ...form, longitude: parseFloat(e.target.value) })}
                      required
                    />
                  </Grid>
                </Grid>

                <Button
                  variant="outlined"
                  color="inherit"
                  size="small"
                  startIcon={<MyLocationIcon />}
                  onClick={handleCaptureLocation}
                  sx={{ mb: 2.5, width: '100%', borderColor: 'rgba(255,255,255,0.2)' }}
                >
                  Acquire Current GPS Fix
                </Button>

                <FormControl fullWidth size="small" sx={{ mb: 2 }}>
                  <InputLabel>Nature of Distress</InputLabel>
                  <Select
                    value={form.distress_type}
                    label="Nature of Distress"
                    onChange={(e) => setForm({ ...form, distress_type: e.target.value })}
                  >
                    <MenuItem value="CAPSIZING_RISK">Capsizing Risk / Freeboard Loss</MenuItem>
                    <MenuItem value="ENGINE_FAILURE">Complete Engine Breakdown / Adrift</MenuItem>
                    <MenuItem value="MEDICAL_EMERGENCY">Crew Critical Medical Emergency</MenuItem>
                    <MenuItem value="SINKING">Hull Ingress / Flooding</MenuItem>
                    <MenuItem value="COLLISION">Maritime Collision</MenuItem>
                  </Select>
                </FormControl>

                <TextField
                  label="Souls on Board"
                  type="number"
                  size="small"
                  fullWidth
                  value={form.souls_on_board}
                  onChange={(e) => setForm({ ...form, souls_on_board: parseInt(e.target.value) || 1 })}
                  sx={{ mb: 2 }}
                />

                <TextField
                  label="Distress Description"
                  multiline
                  rows={3}
                  fullWidth
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  sx={{ mb: 3 }}
                />

                <Button
                  type="submit"
                  variant="contained"
                  color="error"
                  fullWidth
                  size="large"
                  disabled={loading}
                  startIcon={<SosIcon />}
                  sx={{ py: 1.5, fontWeight: 800, fontSize: '1rem', letterSpacing: '0.05em' }}
                >
                  {loading ? 'Transmitting Distress...' : 'TRANSMIT SOS SIGNAL'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </Grid>

        {/* Transmission History & Emergency Contacts */}
        <Grid item xs={12} lg={7}>
          {/* Emergency Contacts */}
          <Paper sx={{ p: 2.5, mb: 3, backgroundColor: 'rgba(15, 29, 54, 0.8)', border: '1px solid rgba(255, 255, 255, 0.08)' }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#f8fafc', mb: 1 }}>
              Official Sri Lanka Maritime Emergency Contacts:
            </Typography>
            <Typography variant="body2" sx={{ color: '#cbd5e1' }}>
              • Sri Lanka Coast Guard Operations: <strong>+94 11 244 5368</strong> / VHF Ch 16<br />
              • Colombo Maritime Rescue Coordination Centre (MRCC): <strong>+94 11 244 1454</strong><br />
              • Fisheries Department Operations Room: <strong>011 244 6183</strong>
            </Typography>
          </Paper>

          {/* Events Log */}
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 2 }}>
                Distress Telemetry Log
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Event ID</TableCell>
                      <TableCell>Vessel</TableCell>
                      <TableCell>Coordinates</TableCell>
                      <TableCell>Distress Type</TableCell>
                      <TableCell>Souls</TableCell>
                      <TableCell>Transmission Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {events.map((evt) => (
                      <TableRow key={evt.event_id} hover>
                        <TableCell sx={{ fontWeight: 800, color: '#ef4444' }}>{evt.event_id}</TableCell>
                        <TableCell>{evt.vessel_id}</TableCell>
                        <TableCell>{evt.latitude.toFixed(2)}°N, {evt.longitude.toFixed(2)}°E</TableCell>
                        <TableCell>{evt.distress_type.replace(/_/g, ' ')}</TableCell>
                        <TableCell>{evt.souls_on_board}</TableCell>
                        <TableCell>
                          <Chip
                            label={evt.status}
                            size="small"
                            sx={{
                              backgroundColor: 'rgba(239, 68, 68, 0.15)',
                              color: '#f87171',
                              fontWeight: 700,
                              fontSize: '0.65rem'
                            }}
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                    {events.length === 0 && (
                      <TableRow>
                        <TableCell colSpan={6} sx={{ textAlign: 'center', py: 3, color: '#94a3b8' }}>
                          No distress events logged. All fleet craft reporting normal operations.
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};
