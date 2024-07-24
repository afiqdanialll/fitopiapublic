import React, { useState, useEffect } from 'react';
import { Container, Box, TextField, Button, Typography, Alert, CircularProgress } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Cookies from 'js-cookie';

export function TwoFactor() {
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const checkPre2FA = async () => {
      try {
        const response = await axios.get('/api/authentication/check-pre-2fa/', {
          headers: { 'Content-Type': 'application/json' },
        });
        if (response.status !== 200) {
          navigate('/login'); // Redirect to login if not authenticated for 2FA
        }
      } catch (error) {
        console.error('Pre-2FA check failed:', error);
        navigate('/login'); // Redirect to login if an error occurs
      }
    };

    checkPre2FA();
  }, [navigate]);

  const handleChange = (e) => {
    const value = e.target.value.toUpperCase();
    if (/^[A-Z0-9]{0,6}$/.test(value)) {
      setOtp(value);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const response = await axios.post('/api/authentication/verify-otp/', { otp }, {
        headers: {
          'X-CSRFToken': Cookies.get('csrftoken'),
          'Content-Type': 'application/json'
        },
        withCredentials: true
      });

      if (response.status === 200) {
        navigate('/');
      } else {
        setError('Invalid OTP. Please try again.');
      }
    } catch (error) {
      // console.error('OTP verification failed:', error);
      // setError('Error verifying OTP. Please try again.');
      console.error('OTP verification failed:', error);
      if (error.response && error.response.status === 400) {
        if (error.response.data.error === "OTP has expired and is now invalidated." ||
          error.response.data.error === "Too many attempts. Try again later.") {
          setError('OTP expired or too many attempts. Redirecting to login...');
          setTimeout(() => {
            navigate('/login');
          }, 1500); // Redirect after 1.5 seconds
        }
        else{
          setError('Error verifying OTP. Please try again.');
        }
      } else {
        setError('Error verifying OTP. Please try again.');
      }
    }
    setLoading(false);
  };

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Typography component="h1" variant="h5">
          Two-Factor Authentication
        </Typography>
        <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
          <TextField
            margin="normal"
            required
            fullWidth
            id="otp"
            label="One-time password"
            name="otp"
            autoFocus
            value={otp}
            onChange={handleChange}
            disabled={loading}
            inputProps={{ maxLength: 6 }}
          />
          {error && <Alert severity="error">{error}</Alert>}
          <Button
            type="submit"
            id="verify_button"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Verify'}
          </Button>
        </Box>
      </Box>
    </Container>
  );
}
