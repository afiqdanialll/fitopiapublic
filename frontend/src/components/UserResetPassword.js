import React, { useEffect, useState } from 'react';
import { Container, TextField, Button, Alert, Typography, Box, Paper, IconButton, InputAdornment, CircularProgress } from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import Cookies from 'js-cookie';

export function UserResetPassword() {
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [currentPassword, setCurrentPassword] = useState('');
    const [showCurrentPassword, setShowCurrentPassword] = useState(false); // I UPDATE HEREE
    const [showNewPassword, setShowNewPassword] = useState(false); // I UPDATE HEREE
    const [showConfirmPassword, setShowConfirmPassword] = useState(false); // I UPDATE HEREE
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const checkSession = async () => {
            try {
                const response = await axios.get('api/authentication/check-session/', { withCredentials: true });
                const data = response.data;
                if (response.status === 200 && (data.role === 'staff' || data.role === 'customer')) {
                    // Session is valid
                    setLoading(false);
                } else {
                    navigate('/');
                }
            } catch (error) {
                navigate('/');
            }
        };

        checkSession();
    }, []);

    const validatePassword = (password) => {
        const errors = [];
        if (password.length < 8) {
            errors.push("Password must be at least 8 characters long.");
        }
        if (!/\d/.test(password)) {
            errors.push("Password must contain at least one number.");
        }
        if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
            errors.push("Password must contain at least one special character.");
        }
        return errors;
    };

    const sanitizeInput = (input) => {
        const element = document.createElement('div');
        element.innerText = input;
        return element.innerHTML;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        const sanitizedNewPassword = sanitizeInput(newPassword);
        const sanitizedConfirmPassword = sanitizeInput(confirmPassword);

        if (sanitizedNewPassword !== sanitizedConfirmPassword) {
            setError('Passwords do not match');
            return;
        }

        const validationErrors = validatePassword(sanitizedNewPassword);
        if (validationErrors.length > 0) {
            setError(validationErrors.join(' '));
            return;
        }

        try {
            const res = await axios.post(
                '/api/authentication/current-password/',
                { current_password: currentPassword, new_password: sanitizedNewPassword },
                {
                    headers: {
                        'X-CSRFToken': Cookies.get('csrftoken')
                    },
                },
                { withCredentials: true }
            );

            if (res.data.error) {
                setError(res.data.error);
                return;
            }

            if (!res.data.match) {
                setError('New password cannot be the same as the current password');
                return;
            }

            const resetRes = await axios.post(
                '/api/authentication/user-reset-password/',
                { new_password: sanitizedNewPassword },
                {
                    headers: {
                        'X-CSRFToken': Cookies.get('csrftoken')
                    },
                },
                { withCredentials: true }
            );

            if (resetRes.status === 200) {
                setSuccess('Password reset successfully');
                setTimeout(() => {
                    navigate('/');
                }, 1500);
            } else {
                setError('Failed to reset password');
            }
        } catch (error) {
            if (error.response && error.response.data && error.response.data.error) {
                setError(error.response.data.error);
            } else {
                setError('Failed to reset password');
            }
            console.log(error);
        }
    };

    const toggleShowCurrentPassword = () => setShowCurrentPassword(!showCurrentPassword);
    const toggleShowNewPassword = () => setShowNewPassword(!showNewPassword); 
    const toggleShowConfirmPassword = () => setShowConfirmPassword(!showConfirmPassword); 

    if (loading) return <CircularProgress />;

    return (
        <Container maxWidth="sm">
            <Paper elevation={3} sx={{ p: 4, mt: 4 }}>
                <Typography variant="h4" component="h1" gutterBottom>
                    Reset Password
                </Typography>
                <form onSubmit={handleSubmit}>
                    <Box mb={2}>
                        <TextField
                            fullWidth
                            label="Current Password"
                            type={showCurrentPassword ? 'text' : 'password'}
                            value={currentPassword}
                            onChange={(e) => setCurrentPassword(e.target.value)}
                            variant="outlined"
                            required
                            InputProps={{
                                endAdornment: (
                                    <InputAdornment position="end">
                                        <IconButton
                                            aria-label="toggle current password visibility"
                                            onClick={toggleShowCurrentPassword}
                                            edge="end"
                                        >
                                            {showCurrentPassword ? <VisibilityOff /> : <Visibility />}
                                        </IconButton>
                                    </InputAdornment>
                                ),
                            }}
                        />
                    </Box>
                    <Box mb={2}>
                        <TextField
                            fullWidth
                            label="New Password"
                            type={showNewPassword ? 'text' : 'password'}
                            value={newPassword}
                            onChange={(e) => setNewPassword(e.target.value)}
                            variant="outlined"
                            required
                            InputProps={{
                                endAdornment: (
                                    <InputAdornment position="end">
                                        <IconButton
                                            aria-label="toggle new password visibility"
                                            onClick={toggleShowNewPassword}
                                            edge="end"
                                        >
                                            {showNewPassword ? <VisibilityOff /> : <Visibility />}
                                        </IconButton>
                                    </InputAdornment>
                                ),
                            }}
                        />
                    </Box>
                    <Box mb={2}>
                        <TextField
                            fullWidth
                            label="Confirm Password"
                            type={showConfirmPassword ? 'text' : 'password'}
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            variant="outlined"
                            required
                            InputProps={{
                                endAdornment: (
                                    <InputAdornment position="end">
                                        <IconButton
                                            aria-label="toggle confirm password visibility"
                                            onClick={toggleShowConfirmPassword}
                                            edge="end"
                                        >
                                            {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                                        </IconButton>
                                    </InputAdornment>
                                ),
                            }}
                        />
                    </Box>
                    {error && <Alert variant="outlined" severity="error" sx={{ mb: 2 }}>{error}</Alert>}
                    {success && <Alert variant="outlined" severity="success" sx={{ mb: 2 }}>{success}</Alert>}
                    <Box mt={2}>
                        <Button type="submit" variant="contained" color="primary" fullWidth>
                            Reset Password
                        </Button>
                    </Box>
                </form>
            </Paper>
        </Container>
    );
}
