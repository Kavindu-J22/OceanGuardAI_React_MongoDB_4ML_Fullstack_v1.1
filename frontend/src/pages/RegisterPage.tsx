import React, { useState } from 'react';
import { Box, Card, CardContent, Typography, TextField, Button, Alert, MenuItem, Select, FormControl, InputLabel } from '@mui/material';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import WavesIcon from '@mui/icons-material/Waves';
import { apiClient } from '../services/api';
import { useStore } from '../store/useStore';

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { showNotification } = useStore();
  
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('fisherman');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await apiClient.post('/auth/register', {
        full_name: fullName,
        email,
        password,
        role
      });
      showNotification('Registration successful! Please sign in with your credentials.', 'success');
      navigate('/login');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ minHeight: '80vh', display: 'flex', alignItems: 'center', justifyContent: 'center', p: 2 }}>
      <Card sx={{ maxWidth: 460, width: '100%', p: 2, borderRadius: 3 }}>
        <CardContent>
          <Box sx={{ textAlign: 'center', mb: 3 }}>
            <WavesIcon sx={{ color: '#00b4d8', fontSize: 44, mb: 1 }} />
            <Typography variant="h5" sx={{ fontWeight: 800 }}>
              Create Account
            </Typography>
            <Typography variant="body2" sx={{ color: '#94a3b8' }}>
              Join the OceanGuard AI maritime research platform
            </Typography>
          </Box>

          {error && <Alert severity="error" sx={{ mb: 2.5, borderRadius: 2 }}>{error}</Alert>}

          <form onSubmit={handleRegister}>
            <TextField
              label="Full Name"
              fullWidth
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
              sx={{ mb: 2 }}
            />
            <TextField
              label="Email Address"
              type="email"
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
              sx={{ mb: 2 }}
            />
            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel id="role-label">Platform Role</InputLabel>
              <Select
                labelId="role-label"
                value={role}
                label="Platform Role"
                onChange={(e) => setRole(e.target.value)}
              >
                <MenuItem value="fisherman">Fisherman / Vessel Skipper</MenuItem>
                <MenuItem value="researcher">Fisheries Research Specialist</MenuItem>
                <MenuItem value="admin">System Administrator</MenuItem>
              </Select>
            </FormControl>
            <Button
              type="submit"
              variant="contained"
              color="primary"
              fullWidth
              size="large"
              disabled={loading}
              sx={{ py: 1.2, fontWeight: 700 }}
            >
              {loading ? 'Registering...' : 'Complete Registration'}
            </Button>
          </form>

          <Box sx={{ textAlign: 'center', mt: 3 }}>
            <Typography variant="body2" sx={{ color: '#94a3b8' }}>
              Already registered?{' '}
              <RouterLink to="/login" style={{ color: '#00b4d8', textDecoration: 'none', fontWeight: 600 }}>
                Sign In
              </RouterLink>
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};
