import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Box, Container, Card, CardContent, Typography, Button, Grid, CircularProgress } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import theme from '../../styles/theme'; 
import { ElevatorSharp } from '@mui/icons-material';

function MembershipPurchase() {
    const navigate = useNavigate();
    const [hasActiveMembership, setHasActiveMembership] = useState(false);
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
                    navigate('/');
                }
            } catch (error) {
                navigate('/');
            }
        };

        checkSession();
    }, []);

    useEffect(() => {
        const checkMembership = async () => {
            try {
                const response = await axios.get('/api/data/check-membership/');
                setHasActiveMembership(response.data.has_active_membership);
            } catch (error) {
                console.error('Failed to check membership status:', error);
            }
        };

        checkMembership();
    }, []);

    const membershipOptions = [
        { duration: '1 Month', price: '$29.99', color: theme.palette.primary.main, benefits: ['Unlimited access to all fitness classes', 'Free shower facilities'] },
        { duration: '6 Months', price: '$159.99', color: theme.palette.secondary.main, benefits: ['Unlimited access to all fitness classes', 'Free shower facilities', 'Exclusive invite to all special events and workshops', 'Free energy drink'] },
        { duration: '12 Months', price: '$299.99', color: theme.palette.success.main, benefits: ['Unlimited access to all fitness classes', 'Free shower facilities', 'Exclusive invite to all special events and workshops', 'Free energy drink', 'Free meal bento', 'Free health plan', 'Priority booking for popular classes'] }
    ];

    const handleSelect = (option) => {
        navigate('/payment', { state: { option } });
    };

    if (hasActiveMembership) {
        return (
            <Container sx={{ mt: 5, textAlign: 'center' }}>
                <Typography variant="h4" gutterBottom>You currently have an active membership.</Typography>
                <Button variant="contained" onClick={() => navigate('/cust')}>Go to Homepage</Button>
            </Container>
        );
    }

    if (loading) return <CircularProgress />;

    return (
        <Container sx={{ mt: 5 }}>
            <Box sx={{ textAlign: 'center', mt: 4, mb: 6 }}>
                <Typography variant="h3" gutterBottom>
                    Purchase a Membership
                </Typography>
            </Box>
            <Grid container spacing={4}>
                {membershipOptions.map((option, idx) => (
                    <Grid item xs={12} sm={4} key={idx}>
                        <Card sx={{
                            height: '100%',
                            display: 'flex',
                            flexDirection: 'column',
                            justifyContent: 'space-between',
                            border: `2px solid ${option.color}`,
                            color: option.color,
                            boxShadow: 'none'
                        }}>
                            <CardContent sx={{ flexGrow: 1 }}>
                                <Typography variant="h5" component="div" sx={{ fontSize: '1.5rem', p: 2, textAlign: 'center' }}>
                                    {option.duration}
                                </Typography>
                                <Typography variant="h6" component="div">
                                    {option.price}
                                </Typography>
                                <ul>
                                    {option.benefits.map((benefit, idx) => (
                                        <Typography component="li" key={idx} sx={{ mt: 1 }}>
                                            {benefit}
                                        </Typography>
                                    ))}
                                </ul>
                            </CardContent>
                            <Button variant="contained" sx={{ m: 2, bgcolor: option.color, color: '#fff' }} onClick={() => handleSelect(option)}>
                                Select
                            </Button>
                        </Card>
                    </Grid>
                ))}
            </Grid>
        </Container>
    );
}

export default MembershipPurchase;
