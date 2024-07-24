import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import { Alert, Button, Container, Card, CardContent, Typography, CircularProgress } from '@mui/material';
import Cookies from 'js-cookie';

const CustomerClassDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [classDetail, setClassDetail] = useState(null);
    const [loading, setLoading] = useState(true);
    const [loadingAuth, setLoadingAuth] = useState(true);
    const [successMessage, setSuccessMessage] = useState(false);

    const formatDateTime = (datetime) => {
        const date = new Date(datetime);
    
        // Extracting date components
        const day = String(date.getUTCDate()).padStart(2, '0');
        const month = String(date.getUTCMonth() + 1).padStart(2, '0');
        const year = date.getUTCFullYear();
    
        // Extracting time components
        let hours = date.getUTCHours();
        const minutes = String(date.getUTCMinutes()).padStart(2, '0');
        const ampm = hours >= 12 ? 'PM' : 'AM';
    
        hours = hours % 12;
        hours = hours ? hours : 12;
    
        return `${day}/${month}/${year}, ${hours}:${minutes} ${ampm}`;
        };
    
    

    useEffect(() => {
        const checkSession = async () => {
          try {
            const response = await axios.get('api/authentication/check-session/', { withCredentials: true });
            const data = response.data;
            if (response.status === 200 && data.role === 'customer') {
                if (data.password_reset)
                    {
                      navigate('/user-reset-password');
                    }
                else{
                    setLoadingAuth(false);
                }
            }
            else {
              navigate('/');
            }
          } catch (error) {
            navigate('/');
          }
        };
    
        checkSession();
    }, []);

    const escapeHtml = (text) => {
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    };

    const isValidId = (id) => {
        return !isNaN(id) && Number.isInteger(parseFloat(id));
    };

    const fetchClassDetail = useCallback(async () => {
        if (!isValidId(id)) {
            console.error('Invalid class ID.');
            setLoading(false);
            return;
        }

        try {
            const response = await axios.get(`/api/data/customer-classes/${id}/`);
            const sanitizedData = {
                ...response.data,
                class_name: escapeHtml(response.data.class_name),
                description: escapeHtml(response.data.description),
            };
            setClassDetail(sanitizedData);
        } catch (error) {
            console.error('Error fetching class details:', error);
            navigate('/')
        } finally {
            setLoading(false);
        }
    }, [id]);

    useEffect(() => {
        fetchClassDetail();
    }, [fetchClassDetail]);

    const handleConfirmBooking = async () => {
        try {
            await axios.post('/api/data/customer-book-class/', 
                {
                    class_id: id,
                    booking_datetime: new Date().toISOString(),
                },
                {
                    headers: {
                        'X-CSRFToken': Cookies.get('csrftoken')
                    },
                },
                { withCredentials: true }
            );
            setSuccessMessage(true);
            setTimeout(() => {
                navigate('/bookings');
              }, 1500); 
        } catch (error) {
            console.error('Error booking class:', error);
            alert('Error booking class. Please try again.');
        }
    };
    
    if (loading) return <CircularProgress />;
    if (loadingAuth) return <CircularProgress />;

    return (
        <Container sx={{ marginTop: 4, textAlign: 'center' }}>
            <Typography variant="h4" gutterBottom>Class Details</Typography>
            {classDetail ? (
                <Card variant="outlined">
                    <CardContent>
                        <Typography variant="h5" gutterBottom>{classDetail.class_name}</Typography>
                        <Typography variant="body1">Description: {classDetail.description}</Typography>
                        <Typography variant="body1">Start DateTime: {formatDateTime(classDetail.start_datetime)}</Typography>
                        <Button variant="contained" color="primary" onClick={handleConfirmBooking} sx={{ marginTop: 2 }}>
                            Confirm Booking
                        </Button>
                    </CardContent>
                </Card>
                
            ) : (
                <Typography variant="body1">No class details available</Typography>
            )}
            {successMessage && (
                <Alert variant="outlined" severity="success" sx={{ width: '100%', mt: 2}}>
                    Booking successful! Redirecting...
                </Alert>
                
            )}
        </Container>
    );
};

export default CustomerClassDetail;
