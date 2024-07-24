import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Box, Container, TableContainer, Table, TableHead, TableRow, TableCell, TableBody, Button, TextField, Grid, Paper, Typography, CircularProgress } from '@mui/material';

function CustomerClassTable() {
  const [hasActiveMembership, setHasActiveMembership] = useState(false);
  const [membershipEndDate, setMembershipEndDate] = useState(null);
  const [classes, setClasses] = useState([]);
  const [filteredClasses, setFilteredClasses] = useState([]);
  const [bookedClasses, setBookedClasses] = useState([]);
  const [searchName, setSearchName] = useState('');
  const [searchDate, setSearchDate] = useState('');
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);

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
              setLoading(false);
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
  }, [navigate]);

  const fetchProfile = async () => {
    try {
      const response = await axios.get('/api/data/profile/', {
        withCredentials: true,
        headers: {
          'Content-Type': 'application/json'
        }
      });
      console.log('Profile data fetched:', response.data);
      const profile = response.data;
      const membership = profile.membership || {};
      if (membership.end_date) {
        setMembershipEndDate(new Date(membership.end_date));
      } else {
        console.error("Membership expiry date not found in the profile data:", profile);
      }
      setHasActiveMembership(membership.status === 'Active');
    } catch (error) {
      console.error('Error fetching profile:', error);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const escapeHtml = (text) => {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  };

  const sanitizeClass = useCallback((classItem) => {
    return {
      ...classItem,
      class_name: escapeHtml(classItem.class_name),
      description: escapeHtml(classItem.description),
    };
  }, []);

  const fetchBookedClasses = useCallback(async () => {
    try {
      const response = await axios.get('/api/data/bookings/');
      setBookedClasses(response.data.upcoming.map(booking => booking.class_id));
    } catch (error) {
      console.error('Error fetching booked classes:', error);
    }
  }, []);

  const fetchClasses = useCallback(async () => {
    try {
      const response = await axios.get('/api/data/customer-classes/');
      const currentDateTime = new Date();
      const tomorrow = new Date(currentDateTime);
      tomorrow.setDate(tomorrow.getDate() + 1);
      const validClasses = response.data
        .map(sanitizeClass)
        .filter(classItem => {
          const classDateTime = new Date(classItem.start_datetime);
          console.log("Class start date and time:", classDateTime);
          return classDateTime > tomorrow && !bookedClasses.includes(classItem.id);
        });
      setClasses(validClasses || []);
    } catch (error) {
      console.error('Error fetching classes:', error);
    }
  }, [sanitizeClass, bookedClasses]);

  useEffect(() => {
    fetchBookedClasses();
  }, [fetchBookedClasses]);

  useEffect(() => {
    fetchClasses();
  }, [fetchClasses]);

  useEffect(() => {
    const filterClasses = () => {
      const lowerCaseSearchName = escapeHtml(searchName.toLowerCase());
      const filtered = classes.filter((classItem) => {
        const classDate = new Date(classItem.start_datetime);
        const classDateString = classDate.toISOString().split('T')[0];
        const classTimeString = classDate.toTimeString().split(' ')[0].slice(0, 5);

        const matchesDate = searchDate ? (new Date(classDateString).getTime() === new Date(searchDate).getTime()) : true;
        const matchesName = classItem.class_name.toLowerCase().includes(lowerCaseSearchName);

        return matchesName && matchesDate;
      });
      setFilteredClasses(filtered);
    };

    filterClasses();
  }, [searchName, searchDate, classes]);

  const handleBookClass = (id) => {
    const selectedClass = classes.find(classItem => classItem.id === id);
    if (!isNaN(id) && Number.isInteger(parseFloat(id))) {
      if (hasActiveMembership && selectedClass) {
        const classDateTime = new Date(selectedClass.start_datetime);
        console.log("Selected class date and time:", classDateTime);
        console.log("Membership end date:", membershipEndDate);
        const isBookingValid = classDateTime <= membershipEndDate;
        console.log("Is booking valid:", isBookingValid);

        if (isBookingValid) {
          navigate(`/customer-classes/${id}`);
        } else {
          alert('You need an active membership that is valid for the class date to book a class.');
        }
      } else {
        alert('You need an active membership to book a class.');
      }
    } else {
      alert('Invalid class ID.');
    }
  };

  if (loading) return <CircularProgress />;

  return (
    <Container sx={{ my: 4 }}>
      <Box sx={{ textAlign: 'center', mt: 4, mb: 4 }}>
        <Typography variant="h3" gutterBottom>
          Available Classes
        </Typography>
      </Box>
      <Grid container spacing={3} sx={{ mb: 2 }}>
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Search by Name"
            value={searchName}
            onChange={(e) => setSearchName(e.target.value)}
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            type="date"
            label="Search by Start Date"
            InputLabelProps={{ shrink: true }}
            value={searchDate}
            onChange={(e) => setSearchDate(e.target.value)}
          />
        </Grid>
      </Grid>
      <TableContainer component={Paper}>
        <Table sx={{ minWidth: 650 }} aria-label="simple table">
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Start DateTime</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredClasses.length > 0 ? (
              filteredClasses.map((classItem) => (
                <TableRow key={classItem.id}>
                  <TableCell>{classItem.class_name}</TableCell>
                  <TableCell>{classItem.description}</TableCell>
                  <TableCell>{formatDateTime(classItem.start_datetime)}</TableCell>
                  <TableCell>
                    <Button variant="contained" color="primary" onClick={() => handleBookClass(classItem.id)}>
                      Book Class
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={4} align="center">No classes available</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
}

export default CustomerClassTable;
