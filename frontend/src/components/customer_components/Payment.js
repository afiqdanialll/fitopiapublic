import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
    Container,
    Card,
    CardContent,
    Typography,
    Button,
    Box,
    TextField,
    InputAdornment,
    Alert,
    List,
    ListItem,
    Grid,
    CircularProgress
} from '@mui/material';
import Cookies from 'js-cookie';

const Payment = () => {
    const navigate = useNavigate();
    const { state } = useLocation();
    const option = state ? state.option : null;
    const [cardNumber, setCardNumber] = useState('');
    const [cardType, setCardType] = useState('');
    const [expiry, setExpiry] = useState('');
    const [cvv, setCvv] = useState('');
    const [errors, setErrors] = useState({});
    const [error, setError] = useState('');
    const [successMessage, setSuccessMessage] = useState(false);
    const [loading, setLoading] = useState(true);


    useEffect(() => {        
        const checkSession = async () => {
            try {
                const response = await axios.get('api/authentication/check-session/', { withCredentials: true });
                const data = response.data;
                if (response.status === 200 && data.role === 'customer') {
                    if (data.password_reset) {
                        navigate('/user-reset-password');
                    }
                    else{
                        setLoading(false);
                    }
                } else {
                    navigate('/login');
                }
            } catch (error) {
                console.error('Session check failed', error);
                navigate('/login');
            }
        };

        checkSession();
    }, [navigate, option]);

    const detectCardType = (number) => {
        const rules = {
            visa: /^4[0-9]{12}(?:[0-9]{3})?$/,
            mastercard: /^5[1-5][0-9]{14}$/,
            amex: /^3[47][0-9]{13}$/
        };

        for (let [type, pattern] of Object.entries(rules)) {
            if (number.match(pattern)) return type;
        }

        return '';
    };

    const handleCardNumberChange = (e) => {
        const number = e.target.value;
        setCardNumber(number);
        setCardType(detectCardType(number));
    };

    const handleExpiryChange = (e) => {
        let value = e.target.value;
        if (value.length === 2 && expiry.length <= 2) {
            value += '/';
        }
        setExpiry(value);
    };

    const validateForm = () => {
        const newErrors = {};
        const currentYear = new Date().getFullYear() % 100;
        const currentMonth = new Date().getMonth() + 1;
        const expiryMonth = parseInt(expiry.slice(0, 2));
        const expiryYear = parseInt(expiry.slice(3));

        if (!cardNumber || !cardType) {
            newErrors.cardNumber = 'Invalid card type. Only Visa, MasterCard, and American Express are accepted.';
        }

        if (!expiry || !/^(0[1-9]|1[0-2])\/([0-9]{2})$/.test(expiry) || expiryYear < currentYear || (expiryYear === currentYear && expiryMonth < currentMonth)) {
            newErrors.expiry = 'Invalid or expired date. Format must be MM/YY.';
        }

        if (!cvv || !/^\d{3,4}$/.test(cvv)) {
            newErrors.cvv = 'CVV must be 3 or 4 digits long.';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (validateForm()) {
            try {
                const response = await axios.post('/api/data/purchase-membership/',
                    {
                        duration: state.option.duration,
                    },
                    {
                        headers: {
                            'X-CSRFToken': Cookies.get('csrftoken')
                        },
                    },
                    { withCredentials: true }
                );
                if (response.status === 201) {
                    setSuccessMessage(true);
                    setError('');
                    setErrors('');
                    setTimeout(() => {
                        navigate('/');
                    }, 1500); // Redirect after 1.5 seconds
                } else {
                    setError(response.data.error || 'Unable to process payment.');
                }
            } catch (error) {
                console.error('Payment failed:', error);
                setError('Payment failed. Please try again.');
            }
        }
    };

    const cardLogoUrl = {
        visa: "https://static-00.iconduck.com/assets.00/visa-icon-128x82-eslsnjez.png",
        mastercard: "https://static-00.iconduck.com/assets.00/mastercard-icon-128x82-ld30gpqe.png",
        amex: "https://static-00.iconduck.com/assets.00/amex-icon-128x82-md090uyw.png"
    };

    if (loading) return <CircularProgress />;
    
    return (
        <Container maxWidth="lg" sx={{ mt: 5 }}>
            <Typography variant="h4" align="center" gutterBottom>
                Checkout
            </Typography>
            <Alert severity="warning" sx={{ mb: 2 }}>
                Do not press the back button or refresh the page during payment, as it may result in a transaction failure.
            </Alert>
            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
            <Grid container spacing={4}>
                <Grid item xs={12} md={6}>
                    <Card>
                        <CardContent>
                            <Typography variant="h5" gutterBottom>
                                Payment Details
                            </Typography>
                            <Box display="flex" alignItems="center" my={2}>
                                <img src={cardLogoUrl.visa} alt="Visa" height="30" style={{ marginRight: '10px' }} />
                                <img src={cardLogoUrl.mastercard} alt="MasterCard" height="30" style={{ marginRight: '10px' }} />
                                <img src={cardLogoUrl.amex} alt="American Express" height="30" />
                            </Box>
                            <form onSubmit={handleSubmit}>
                                <Box sx={{ mb: 2 }}>
                                    <TextField
                                        fullWidth
                                        label="Card Number"
                                        id="card-number"
                                        value={cardNumber}
                                        onChange={handleCardNumberChange}
                                        error={!!errors.cardNumber}
                                        helperText={errors.cardNumber}
                                        InputProps={{
                                            endAdornment: cardType && (
                                                <InputAdornment position="end">
                                                    <img src={cardLogoUrl[cardType]} alt={cardType} height="30" />
                                                </InputAdornment>
                                            ),
                                        }}
                                    />
                                </Box>
                                <Box sx={{ mb: 2 }}>
                                    <TextField
                                        fullWidth
                                        label="MM/YY"
                                        id="expiry-date"
                                        value={expiry}
                                        onChange={handleExpiryChange}
                                        error={!!errors.expiry}
                                        helperText={errors.expiry}
                                    />
                                </Box>
                                <Box sx={{ mb: 2 }}>
                                    <TextField
                                        fullWidth
                                        label="CVV"
                                        id="cvv"
                                        value={cvv}
                                        onChange={(e) => setCvv(e.target.value)}
                                        error={!!errors.cvv}
                                        helperText={errors.cvv}
                                    />
                                </Box>
                                {successMessage && (
                                    <Alert variant="outlined" severity="success" sx={{ width: '100%', mb: 2}}>
                                        Purchase successful! Redirecting...
                                    </Alert>
                                    
                                )}
                                <Button variant="contained" color="primary" type="submit" id="pay-button" fullWidth>
                                    Pay Now
                                </Button>
                            </form>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} md={6}>
                    <Card>
                        <CardContent>
                            <Typography variant="h5" sx={{ textAlign: 'center' }} gutterBottom>
                                Your Selection
                            </Typography>
                            <Typography variant="h6" gutterBottom>
                                {option.duration}
                            </Typography>
                            <Typography variant="h6" gutterBottom>
                                Price: {option.price}
                            </Typography>
                            <Typography variant="body1" gutterBottom>
                                Included benefits:
                            </Typography>
                            <List>
                                {option.benefits.map((benefit, idx) => (
                                    <ListItem key={idx}>
                                        {benefit}
                                    </ListItem>
                                ))}
                            </List>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
        </Container>
    );
};

export default Payment;
