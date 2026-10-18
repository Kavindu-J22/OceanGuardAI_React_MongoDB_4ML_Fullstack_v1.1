import React, { useState } from 'react';
import { Box, Card, CardContent, Typography, TextField, Button, Alert, Chip, Divider, Stack } from '@mui/material';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import WavesIcon from '@mui/icons-material/Waves';
import { apiClient } from '../services/api';
import { useStore } from '../store/useStore';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { setUser, showNotification } = useStore();
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const res = await apiClient.post('/auth/login', { email, password });
      const { access_token, refresh_token, role, full_name, user_id } = res.data;
      
      localStorage.setItem('oceanguard_token', access_token);
      localStorage.setItem('oceanguard_refresh_token', refresh_token);
      
      setUser({
        user_id,
        email,
        full_name,
        role,
        is_active: true,
        created_at: new Date().toISOString()
      }, role);

      showNotification(`Welcome aboard, ${full_name}!`, 'success');
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  const fillDemo = (demoEmail: string, demoPass: string) => {
    setEmail(demoEmail);
    setPassword(demoPass);
  };

  return (
    <Box sx={{ minHeight: '80vh', display: 'flex', alignItems: 'center', justifyContent: 'center', p: 2 }}>
      <Card sx={{ maxWidth: 440, width: '100%', p: 2, borderRadius: 3 }}>
        <CardContent>
          <Box sx={{ textAlign: 'center', mb: 3 }}>
            <WavesIcon sx={{ color: '#00b4d8', fontSize: 44, mb: 1 }} />
            <Typography variant="h5" sx={{ fontWeight: 800 }}>
              OceanGuard Sign In
            </Typography>
            <Typography variant="body2" sx={{ color: '#94a3b8' }}>
              Access maritime safety, intelligence & fuel workflows
            </Typography>
          </Box>

          {error && <Alert severity="error" sx={{ mb: 2.5, borderRadius: 2 }}>{error}</Alert>}

          <form onSubmit={handleLogin}>
            <TextField
              label="Email Address"
              fullWidth
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              sx={{ mb: 2 }}
            />
            <TextField
              label="Password"
              type="password"
              fullWidth
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              sx={{ mb: 3 }}
            />
            <Button
              type="submit"
              variant="contained"
              color="primary"
              fullWidth
              size="large"
              disabled={loading}
              sx={{ py: 1.2, fontWeight: 700 }}
            >
              {loading ? 'Authenticating...' : 'Sign In'}
            </Button>
          </form>

          <Divider sx={{ my: 3, borderColor: 'rgba(255, 255, 255, 0.08)' }}>
            <Typography variant="caption" sx={{ color: '#64748b' }}>DEMO CREDENTIALS</Typography>
          </Divider>

          <Stack spacing={1}>
            <Chip
              label="Fisherman Skipper: fisherman@oceanguard.ai"
              clickable
              onClick={() => fillDemo('fisherman@oceanguard.ai', 'FishermanPass123!')}
              sx={{ backgroundColor: 'rgba(13, 148, 136, 0.15)', color: '#2dd4bf', border: '1px solid #0d9488' }}
            />
            <Chip
              label="Researcher: researcher@oceanguard.ai"
              clickable
              onClick={() => fillDemo('researcher@oceanguard.ai', 'ResearchPass123!')}
              sx={{ backgroundColor: 'rgba(2, 132, 199, 0.15)', color: '#38bdf8', border: '1px solid #0284c7' }}
            />
            <Chip
              label="Administrator: admin@oceanguard.ai"
              clickable
              onClick={() => fillDemo('admin@oceanguard.ai', 'AdminPass123!')}
              sx={{ backgroundColor: 'rgba(124, 58, 237, 0.15)', color: '#a78bfa', border: '1px solid #7c3aed' }}
            />
          </Stack>

          <Box sx={{ textAlign: 'center', mt: 3 }}>
            <Typography variant="body2" sx={{ color: '#94a3b8' }}>
              Don't have an account?{' '}
              <RouterLink to="/register" style={{ color: '#00b4d8', textDecoration: 'none', fontWeight: 600 }}>
                Register here
              </RouterLink>
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};
