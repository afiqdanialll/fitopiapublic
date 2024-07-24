import { useEffect, useState } from "react";
import axios from "axios";
import personalTraining from "../assets/personal-training.svg";
import Cookies from 'js-cookie';
import { Container, Typography, Box, Button, CircularProgress } from "@mui/material";
import { useNavigate } from 'react-router-dom';

export const CustPage = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true); // Add loading state
    const [authorized, setAuthorized] = useState(false); // Add authorized state

    useEffect(() => {
        const checkSession = async () => {
          try {
            const response = await axios.get('api/authentication/check-session/', { withCredentials: true });
            const data = response.data;
            if (response.status === 200 && data.role === 'customer') {
                if (data.password_reset) {
                    navigate('/user-reset-password');
                } else {
                    setAuthorized(true); // User is authorized
                }
            } else {
                navigate('/');
            }
          } catch (error) {
            navigate('/');
          } finally {
            setLoading(false); // Session check is complete
          }
        };
    
        checkSession();
    }, []);

    if (loading) {
        return <CircularProgress />; // Show loading spinner while checking session
    }

    if (!authorized) {
        return null; // Optionally show nothing if not authorized
    }
  
    return (
        <Container maxWidth="lg" sx={{ mt: 8, textAlign: 'center' }}>
            <Box sx={{ bgcolor: 'background.paper', pt: 8, pb: 6 }}>
                <Container maxWidth="sm">
                    <Typography
                        component="h1"
                        variant="h2"
                        align="center"
                        color="text.primary"
                        gutterBottom
                    >Welcome to Fitopia
                    </Typography>
                    <Typography variant="h5" align="center" color="text.secondary" paragraph>
                        Your journey to fitness begins here. Explore our classes, meet our trainers, and achieve your fitness goals with us.
                    </Typography>
                    <Box sx={{ mt: 4 }}>
                        <Box
                            component="img"
                            src={personalTraining}
                            alt="Fitness"
                            sx={{
                                maxWidth: '100%',
                                borderRadius: '10px',
                            }}
                        />
                    </Box>
                    <Box sx={{ mt: 4 }}>
                        <Button variant="contained" color="primary" href="/customer-classes">
                            Explore Classes
                        </Button>
                    </Box>
                </Container>
            </Box>
        </Container>
    );
}