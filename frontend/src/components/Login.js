import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Container, Typography, TextField, Button, Box, Grid, Alert, CircularProgress, IconButton, InputAdornment } from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import CSRFToken from './Csrftoken';
import Cookies from 'js-cookie';

export function Login() {
    const [formData, setFormData] = useState({
        username: '',
        password: ''
    });
    const [showPassword, setShowPassword] = useState(false);
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
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setErrorMessage('');

        const { username, password } = formData;

        try {
            const res = await axios.post(
                "api/authentication/login/",
                {
                    username,
                    password,
                },
                {
                    headers: {
                        'X-CSRFToken': Cookies.get('csrftoken')
                    },
                    withCredentials: true
                }
            );

            if (res.status === 200 && res.data && res.data.Success) {
                setSuccessMessage(true);
                setErrorMessage('');
                setTimeout(() => {
                    navigate('/Twofactor');
                }, 1500); 
            } else {
                setErrorMessage('Wrong email or password. Please try again.');
            }
        } catch (error) {
            if (error.response && error.response.status === 401) {
                setErrorMessage('Wrong email or password. Please try again.');
            } else {
                setErrorMessage('An unexpected error occurred. Please try again later.');
            }
            console.log(error);
        }
        setLoading(false);
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
                <Typography component="h1" variant="h5">
                    Login
                </Typography>
                <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
                    <CSRFToken />
                    <TextField
                        margin="normal"
                        required
                        fullWidth
                        id="username"
                        label="Email"
                        name="username"
                        autoComplete="email"
                        autoFocus
                        value={formData.username}
                        onChange={handleChange}
                        error={!!errorMessage}
                    />
                    <TextField
                        margin="normal"
                        required
                        fullWidth
                        name="password"
                        label="Password"
                        type={showPassword ? 'text' : 'password'}
                        id="password"
                        autoComplete="current-password"
                        value={formData.password}
                        onChange={handleChange}
                        error={!!errorMessage}
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
                        <Alert severity="error" sx={{ mt: 2 }}>
                            {errorMessage}
                        </Alert>
                    )}
                    
                    <Button
                        type="submit"
                        id="login-button"
                        fullWidth
                        variant="contained"
                        sx={{ mt: 3, mb: 2 }}
                        disabled={loading || successMessage}
                    >
                        {loading ? <CircularProgress size={24} /> : 'Login'}
                    </Button>
                    {successMessage && (
                        <Alert variant="outlined" severity="success" sx={{ width: '100%', mb:2}}>
                            Login successful! Redirecting...
                        </Alert>
                    )}
                    
                    <Grid container>
                        <Grid item>
                            <Link to="/signup" variant="body2">
                                {"Don't have an account? Sign up."}
                            </Link>
                        </Grid>
                    </Grid>
                </Box>
            </Box>
        </Container>
    );
}
