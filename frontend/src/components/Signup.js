import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Container, Typography, TextField, Button, Box, Grid, Alert, CircularProgress, IconButton, InputAdornment } from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import axios from "axios";
import CSRFToken from './Csrftoken';
import Cookies from 'js-cookie';

export function Signup() {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    username: '',
    password: '',
  });

  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState({});


  const [validations, setValidations] = useState({
    first_name: true,
    last_name: true,
    username: true,
    password: {
      length: false,
      number: false,
      special: false
    }
  });

  const [touched, setTouched] = useState({
    first_name: false,
    last_name: false,
    username: false,
    password: false
  });

  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState(false);
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const checkSession = async () => {
    try {
      const response = await axios.get('api/authentication/check-session/', { withCredentials: true });
      const data = response.data;

      if (response.status === 200) {
        if (data.role === 'admin') {
          navigate('/admin');
        } else if (data.role === 'customer') {
          navigate('/cust');
        } else if (data.role === 'staff') {
          navigate('/staff');
        } 
      }
    } catch (error) {
      // If there's an error (e.g., 401 Unauthorized), redirect to the login page
      console.log(error)
    }
  };
  checkSession();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value.trim()
    });

    setTouched({
      ...touched,
      [name]: true
    });

    switch (name) {
      case 'first_name':
        setValidations({
          ...validations,
          first_name: /^[A-Za-z]+$/.test(value.trim())
        });
        break;
      case 'last_name':
        setValidations({
          ...validations,
          last_name: /^[A-Za-z]+$/.test(value.trim())
        });
        break;
      case 'username':
        setValidations({
          ...validations,
          username: /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim())
        });
        break;
      case 'password':
        setValidations({
          ...validations,
          password: {
            length: value.length >= 8,
            number: /\d/.test(value),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(value)
          }
        });
        break;
      default:
        break;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setTouched({
      first_name: true,
      last_name: true,
      username: true,
      password: true
    });

    if (
      validations.first_name &&
      validations.last_name &&
      validations.username &&
      validations.password.length &&
      validations.password.number &&
      validations.password.special
    ) {
      setLoading(true);
      try {
        const response = await axios.post(
          '/api/authentication/signup/',
          formData,
          {
            headers: {
              'X-CSRFToken': Cookies.get('csrftoken'),
              'Content-Type': 'application/json'
            },
            withCredentials: true
          }
        );

        if (response.status === 201) {
          console.log('Registration successful:', response.data);
          setSuccessMessage(true);
          setErrorMessage('');
          setTimeout(() => {
            navigate('/login');
          }, 1500); // Redirect after 1.5 seconds
        } else {
          console.error('Registration failed:', response.statusText);
          setErrorMessage('An unexpected error occurred. Please try again.');
        }
      } catch (error) {
        console.error('Registration failed:', error);
        if (error.response && error.response.status === 400 && error.response.data.username) {
          setErrorMessage('Email already exists. Please use a different email.');
        } else {
          setErrorMessage('An unexpected error occurred. Please try again.');
        }
      }
      setLoading(false);
    } else {
      setErrorMessage('Please fill out all fields correctly.');
    }
  };

  const handleClickShowPassword = () => {
    setShowPassword((prev) => !prev);
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
        <Typography component="h1" variant="h5" sx={{ fontWeight: 'medium' }}>
          Sign Up
        </Typography>
        <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
          <CSRFToken />
          <TextField
            margin="normal"
            required
            fullWidth
            id="first_name"
            label="First Name"
            name="first_name"
            autoComplete="given-name"
            autoFocus
            value={formData.first_name}
            onChange={handleChange}
            error={touched.first_name && !validations.first_name}
            helperText={touched.first_name && !validations.first_name ? "First name must contain only alphabets." : ""}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            id="last_name"
            label="Last Name"
            name="last_name"
            autoComplete="family-name"
            value={formData.last_name}
            onChange={handleChange}
            error={touched.last_name && !validations.last_name}
            helperText={touched.last_name && !validations.last_name ? "Last name must contain only alphabets." : ""}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            id="username"
            label="Email"
            name="username"
            autoComplete="email"
            value={formData.username}
            onChange={handleChange}
            error={touched.username && !validations.username}
            helperText={touched.username && !validations.username ? "Please enter a valid email address." : ""}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            name="password"
            label="Password"
            type={showPassword ? 'text' : 'password'} // I UPDATE HEREE
            id="password"
            autoComplete="current-password"
            value={formData.password}
            onChange={handleChange}
            error={
              touched.password && 
              (!validations.password.length ||
              !validations.password.number ||
              !validations.password.special)
            }
            helperText={
              touched.password && 
              (!validations.password.length ||
              !validations.password.number ||
              !validations.password.special)
                ? "Password must be at least 8 characters long, contain at least 1 number, and 1 special character."
                : ""
            }
            InputProps={{
              endAdornment: ( 
                <InputAdornment position="end"> 
                  <IconButton 
                    aria-label="toggle password visibility"
                    onClick={handleClickShowPassword}
                    edge="end"
                  > 
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton> 
                </InputAdornment>
              ) 
            }}
          />
          {errorMessage && (
            <Typography color="error" variant="body2" sx={{ mt: 2 }}>
              {errorMessage}
            </Typography>
          )}
          
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={loading || successMessage}
          >
            {loading ? <CircularProgress size={24} /> : 'Sign Up'}
          </Button>

          {successMessage && (
              <Alert variant="outlined" severity="success" sx={{ width: '100%', mb: 2 }}>
                  Sign up successful! Redirecting...
              </Alert>
          )}
          
          <Typography>
            Already have an account? <Link to="/login">Login.</Link>
          </Typography>
        </Box>
      </Box>
    </Container>
  );
}
