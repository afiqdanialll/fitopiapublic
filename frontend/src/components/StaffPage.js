import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Route, Routes } from 'react-router-dom';
import ClassTable from './staff_components/ClassTable';
import ClassDetail from './staff_components/ClassDetail';
import { Container, Typography, Box, CircularProgress } from '@mui/material';
import axios from 'axios';

function StaffPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true); // Add loading state
  useEffect(() => {
    const checkSession = async () => {
      try {
        const response = await axios.get('api/authentication/check-session/', { withCredentials: true });
        const data = response.data;
        if (response.status === 200 && data.role === 'staff') {
          if (data.password_reset)
            {
              navigate('/user-reset-password');
            }
          setLoading(false);
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

  if (loading) return <CircularProgress />;

  return (
    <Container>
      <Box sx={{ textAlign: 'center', mt: 4, mb: 4 }}>
        <Typography variant="h3" gutterBottom>
          Staff Dashboard
        </Typography>
      </Box>
      <ClassTable/>
    </Container>
  );
}

export default StaffPage;
