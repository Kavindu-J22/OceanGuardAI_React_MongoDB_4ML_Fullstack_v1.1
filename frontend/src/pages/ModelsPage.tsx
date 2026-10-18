import React, { useEffect, useState } from 'react';
import { Box, Typography, Grid, Card, CardContent, Chip, Button, Divider, Alert, Stack } from '@mui/material';
import MemoryIcon from '@mui/icons-material/Memory';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import AutorenewIcon from '@mui/icons-material/Autorenew';
import { apiClient } from '../services/api';
import { useStore } from '../store/useStore';

export const ModelsPage: React.FC = () => {
  const { role, showNotification } = useStore();
  const [models, setModels] = useState<any[]>([]);

  useEffect(() => {
    const fetchModels = async () => {
      try {
        const res = await apiClient.get('/models');
        setModels(res.data);
      } catch (e) {
        console.error('Failed to load models:', e);
      }
    };
    fetchModels();
  }, []);

  const handleTriggerRetrain = async (component: string) => {
    try {
      const res = await apiClient.post(`/models/${component}/training-jobs`);
      showNotification(`Retraining Job ${res.data.job_id} queued for ${component.toUpperCase()}!`, 'info');
    } catch (err: any) {
      showNotification(err.response?.data?.detail || 'Retraining trigger failed.', 'error');
    }
  };

  return (
    <Box sx={{ pb: 6 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
          <MemoryIcon sx={{ color: '#00b4d8', fontSize: 32 }} />
          <Typography variant="h4" sx={{ fontWeight: 800, color: '#f8fafc' }}>
            Model Management & MLOps Registry
          </Typography>
        </Box>
        <Typography variant="body2" sx={{ color: '#94a3b8' }}>
          Approved research model checkpoints, evaluation metrics, and controlled retraining pipelines.
        </Typography>
      </Box>

      {/* Model Cards */}
      <Grid container spacing={3}>
        {models.map((m) => (
          <Grid item xs={12} md={6} key={m.component}>
            <Card sx={{ height: '100%', p: 1 }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Box>
                    <Chip
                      label={m.component.toUpperCase()}
                      size="small"
                      sx={{ backgroundColor: 'rgba(0, 180, 216, 0.2)', color: '#38bdf8', fontWeight: 800, mb: 1 }}
                    />
                    <Typography variant="h6" sx={{ fontWeight: 800 }}>
                      {m.name}
                    </Typography>
                  </Box>
                  <Chip
                    icon={<CheckCircleIcon style={{ color: '#10b981' }} />}
                    label={m.active_version}
                    size="small"
                    sx={{ backgroundColor: 'rgba(16, 185, 129, 0.15)', color: '#34d399', fontWeight: 700 }}
                  />
                </Box>

                <Typography variant="body2" sx={{ color: '#cbd5e1', mb: 2, fontWeight: 500 }}>
                  Architecture: <span style={{ color: '#00b4d8' }}>{m.architecture}</span>
                </Typography>

                <Box sx={{ p: 1.5, borderRadius: 2, backgroundColor: 'rgba(0,0,0,0.25)', mb: 2.5 }}>
                  <Typography variant="caption" sx={{ color: '#94a3b8', display: 'block' }}>
                    Training Data Provenance:
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#f1f5f9', fontSize: '0.82rem' }}>
                    {m.data_provenance}
                  </Typography>
                </Box>

                <Divider sx={{ my: 2, borderColor: 'rgba(255, 255, 255, 0.08)' }} />

                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Chip label={m.status} size="small" variant="outlined" sx={{ borderColor: '#64748b', fontSize: '0.65rem' }} />
                  {role !== 'fisherman' && (
                    <Button
                      size="small"
                      variant="outlined"
                      color="primary"
                      startIcon={<AutorenewIcon />}
                      onClick={() => handleTriggerRetrain(m.component)}
                    >
                      Trigger Retraining
                    </Button>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Retraining Governance Notice */}
      <Alert severity="info" sx={{ mt: 4, borderRadius: 2 }}>
        <strong>CONTROLLED RETRAINING ARCHITECTURE:</strong> Models are NEVER trained on active API startup. Approved models load frozen checkpoints. Retraining jobs only incorporate verified ground-truth observations after independent review.
      </Alert>
    </Box>
  );
};
