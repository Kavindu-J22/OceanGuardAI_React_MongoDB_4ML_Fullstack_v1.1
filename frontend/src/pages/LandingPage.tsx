import React from 'react';
import { Box, Container, Typography, Button, Grid, Card, CardContent, Chip, Stack } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import SecurityIcon from '@mui/icons-material/Security';
import PhishingIcon from '@mui/icons-material/Phishing';
import LocalGasStationIcon from '@mui/icons-material/LocalGasStation';
import StorefrontIcon from '@mui/icons-material/Storefront';
import WifiOffIcon from '@mui/icons-material/WifiOff';
import WavesIcon from '@mui/icons-material/Waves';

export const LandingPage: React.FC = () => {
  return (
    <Box sx={{ minHeight: '90vh', py: { xs: 4, md: 8 } }}>
      <Container maxWidth="lg">
        {/* Hero Section */}
        <Box sx={{ textAlign: 'center', mb: 8 }}>
          <Chip
            icon={<WavesIcon style={{ color: '#00b4d8' }} />}
            label="SRI LANKA ARTISANAL FISHERIES RESEARCH PROJECT"
            variant="outlined"
            sx={{ mb: 2.5, borderColor: 'rgba(0, 180, 216, 0.4)', color: '#90e0ef', fontWeight: 600 }}
          />
          <Typography variant="h2" sx={{ fontWeight: 800, color: '#f8fafc', mb: 2, fontSize: { xs: '2.4rem', md: '3.6rem' } }}>
            OceanGuard <span style={{ color: '#00b4d8' }}>AI</span>
          </Typography>
          <Typography variant="h5" sx={{ color: '#94a3b8', maxWidth: 800, mx: 'auto', mb: 4, fontWeight: 400, lineHeight: 1.6 }}>
            An offline-first, scientific decision-support system integrating <strong>four deep learning research pipelines</strong> for small-scale and artisanal fishing vessels.
          </Typography>
          <Stack direction="row" spacing={2} justifyContent="center">
            <Button variant="contained" color="primary" size="large" component={RouterLink} to="/register" sx={{ px: 4, py: 1.5, fontSize: '1rem' }}>
              Launch System
            </Button>
            <Button variant="outlined" color="primary" size="large" component={RouterLink} to="/login" sx={{ px: 4, py: 1.5, fontSize: '1rem' }}>
              Skipper Sign In
            </Button>
          </Stack>
        </Box>

        {/* 4 Research Components Showcase */}
        <Typography variant="h4" sx={{ fontWeight: 700, textAlign: 'center', color: '#f1f5f9', mb: 4 }}>
          Four Integrated Deep Learning Research Pillars
        </Typography>

        <Grid container spacing={3.5}>
          {/* C1 */}
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column', p: 1 }}>
              <CardContent sx={{ flex: 1 }}>
                <Box sx={{ p: 1.5, borderRadius: 2, backgroundColor: 'rgba(0, 180, 216, 0.1)', width: 'fit-content', mb: 2 }}>
                  <SecurityIcon sx={{ color: '#00b4d8', fontSize: 32 }} />
                </Box>
                <Chip label="Component 1" size="small" sx={{ mb: 1.5, backgroundColor: 'rgba(0, 180, 216, 0.2)', color: '#38bdf8', fontWeight: 700 }} />
                <Typography variant="h6" sx={{ fontWeight: 700, mb: 1 }}>
                  Vessel Safety Risk
                </Typography>
                <Typography variant="body2" sx={{ color: '#94a3b8', lineHeight: 1.6 }}>
                  Bidirectional LSTM with Additive Attention evaluating hydrodynamic vulnerability, vessel loading ratios, and wave steepness.
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* C2 */}
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column', p: 1 }}>
              <CardContent sx={{ flex: 1 }}>
                <Box sx={{ p: 1.5, borderRadius: 2, backgroundColor: 'rgba(46, 196, 182, 0.1)', width: 'fit-content', mb: 2 }}>
                  <PhishingIcon sx={{ color: '#2ec4b6', fontSize: 32 }} />
                </Box>
                <Chip label="Component 2" size="small" sx={{ mb: 1.5, backgroundColor: 'rgba(46, 196, 182, 0.2)', color: '#2ec4b6', fontWeight: 700 }} />
                <Typography variant="h6" sx={{ fontWeight: 700, mb: 1 }}>
                  Fishing Ground ST-GCN
                </Typography>
                <Typography variant="body2" sx={{ color: '#94a3b8', lineHeight: 1.6 }}>
                  Spatiotemporal Graph Convolutional Network with Spatial Attention predicting tuna habitat suitability index across 100 coastal zones with Pareto multi-objective optimization.
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* C4 */}
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column', p: 1 }}>
              <CardContent sx={{ flex: 1 }}>
                <Box sx={{ p: 1.5, borderRadius: 2, backgroundColor: 'rgba(245, 158, 11, 0.1)', width: 'fit-content', mb: 2 }}>
                  <LocalGasStationIcon sx={{ color: '#f59e0b', fontSize: 32 }} />
                </Box>
                <Chip label="Component 4" size="small" sx={{ mb: 1.5, backgroundColor: 'rgba(245, 158, 11, 0.2)', color: '#fbbf24', fontWeight: 700 }} />
                <Typography variant="h6" sx={{ fontWeight: 700, mb: 1 }}>
                  PINN Fuel Predictor
                </Typography>
                <Typography variant="body2" sx={{ color: '#94a3b8', lineHeight: 1.6 }}>
                  Physics-Informed Neural Network constrained by ITTC-1957 skin friction correlation, wave drag, and brake power for voyage sufficiency.
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* C3 */}
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column', p: 1 }}>
              <CardContent sx={{ flex: 1 }}>
                <Box sx={{ p: 1.5, borderRadius: 2, backgroundColor: 'rgba(16, 185, 129, 0.1)', width: 'fit-content', mb: 2 }}>
                  <StorefrontIcon sx={{ color: '#10b981', fontSize: 32 }} />
                </Box>
                <Chip label="Component 3" size="small" sx={{ mb: 1.5, backgroundColor: 'rgba(16, 185, 129, 0.2)', color: '#34d399', fontWeight: 700 }} />
                <Typography variant="h6" sx={{ fontWeight: 700, mb: 1 }}>
                  Market & Perishability
                </Typography>
                <Typography variant="body2" sx={{ color: '#94a3b8', lineHeight: 1.6 }}>
                  Temporal Fusion Transformer price forecasting coupled with Arrhenius / Q10 fish decay modeling to optimize Sell Now vs Wait vs Transport.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Scientific Disclaimer Card */}
        <Box sx={{ mt: 8, p: 3, borderRadius: 3, backgroundColor: 'rgba(15, 29, 54, 0.6)', border: '1px solid rgba(255, 255, 255, 0.08)' }}>
          <Typography variant="subtitle2" sx={{ color: '#38bdf8', fontWeight: 700, mb: 1 }}>
            RESEARCH INTEGRITY & DATA PROVENANCE NOTICE
          </Typography>
          <Typography variant="body2" sx={{ color: '#94a3b8', lineHeight: 1.6 }}>
            OceanGuard AI is an academic research decision-support system. Synthetic labels, simulated biological suitability indices, and hydrodynamic approximations are explicitly distinguished from verified real-world incidents, recorded catches, and measured fuel consumptions. This system does not certify navigation clearance or substitute official maritime distress equipment.
          </Typography>
        </Box>
      </Container>
    </Box>
  );
};
