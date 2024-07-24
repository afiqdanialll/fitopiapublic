import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Container, Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Tab, Tabs, Button, CircularProgress } from '@mui/material';
import Cookies from 'js-cookie';

function BookingHistory() {
  const [upcomingBookings, setUpcomingBookings] = useState([]);
  const [pastBookings, setPastBookings] = useState([]);
  const [cancelledBookings, setCancelledBookings] = useState([]);
  const [key, setKey] = useState('upcoming');
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
          if (data.password_reset) {
            navigate('/user-reset-password');
          } else {
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

  const escapeHtml = (text) => {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  };

  const sanitizeBooking = useCallback((booking) => {
    return {
      ...booking,
      class_name: escapeHtml(booking.class_name),
      class_description: escapeHtml(booking.class_description),
    };
  }, []);

  const fetchBookings = useCallback(async () => {
    try {
      const response = await axios.get('/api/data/bookings/');
      const currentDateTimeSGT = new Date(new Date().toLocaleString("en-US", { timeZone: "Asia/Singapore" }));
      console.log("Current date and time (SGT):", currentDateTimeSGT);

      const upcoming = response.data.upcoming
        .map(sanitizeBooking)
        .filter(booking => {
          const bookingDateTime = new Date(booking.start_datetime);
          const displayedDateTime = new Date(bookingDateTime.toLocaleString("en-US", { timeZone: "UTC" }));
          console.log("Booking display date and time (UTC):", displayedDateTime);
          return displayedDateTime > currentDateTimeSGT;
        });

      const past = response.data.upcoming
        .map(sanitizeBooking)
        .filter(booking => {
          const bookingDateTime = new Date(booking.start_datetime);
          const displayedDateTime = new Date(bookingDateTime.toLocaleString("en-US", { timeZone: "UTC" }));
          console.log("Booking display date and time (UTC):", displayedDateTime);
          return displayedDateTime <= currentDateTimeSGT;
        })
        .concat(response.data.past.map(sanitizeBooking));

      setUpcomingBookings(upcoming);
      setPastBookings(past);
      setCancelledBookings(response.data.cancelled.map(sanitizeBooking));
    } catch (error) {
      console.error('Error fetching bookings:', error);
    }
  }, [sanitizeBooking]);

  useEffect(() => {
    fetchBookings();
  }, [fetchBookings]);

  const handleCancelBooking = async (bookingId) => {
    if (!Number.isInteger(bookingId)) {
      alert('Invalid booking ID.');
      return;
    }

    try {
      await axios.post('/api/data/cancel-booking/',
        { booking_id: bookingId },
        {
          headers: {
            'X-CSRFToken': Cookies.get('csrftoken')
          },
        },
        { withCredentials: true }
      );
      fetchBookings();
    } catch (error) {
      console.error('Error cancelling booking:', error);
    }
  };

  if (loading) return <CircularProgress />;

  return (
    <Container maxWidth="lg">
      <Box sx={{ textAlign: 'center', mt: 4, mb: 4 }}>
        <Typography variant="h3" gutterBottom>
          Your Bookings
        </Typography>
      </Box>
      <Tabs value={key} onChange={(event, newValue) => setKey(newValue)} centered>
        <Tab label="Upcoming" value="upcoming" />
        <Tab label="Past" value="past" />
        <Tab label="Cancelled" value="cancelled" />
      </Tabs>
      <TableContainer component={Paper} sx={{ mt: 3 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Class</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Start DateTime</TableCell>
              <TableCell>Booking DateTime</TableCell>
              <TableCell>Status</TableCell>
              {key === 'upcoming' && <TableCell>Action</TableCell>}
            </TableRow>
          </TableHead>
          <TableBody>
            {key === 'upcoming' && upcomingBookings.map((booking) => (
              <TableRow key={booking.id}>
                <TableCell>{booking.class_name}</TableCell>
                <TableCell>{booking.class_description}</TableCell>
                <TableCell>{formatDateTime(booking.start_datetime)}</TableCell>
                <TableCell>{formatDateTime(booking.booking_datetime)}</TableCell>
                <TableCell>{booking.cancellation ? 'Cancelled' : 'Confirmed'}</TableCell>
                <TableCell align="center">
                  <Button variant="outlined" color="error" onClick={() => handleCancelBooking(booking.id)}>
                    Cancel
                  </Button>
                </TableCell>
              </TableRow>
            ))}
            {key === 'past' && pastBookings.map((booking) => (
              <TableRow key={booking.id}>
                <TableCell>{booking.class_name}</TableCell>
                <TableCell>{booking.class_description}</TableCell>
                <TableCell>{formatDateTime(booking.start_datetime)}</TableCell>
                <TableCell>{formatDateTime(booking.booking_datetime)}</TableCell>
                <TableCell>{booking.cancellation ? 'Cancelled' : 'Attended'}</TableCell>
              </TableRow>
            ))}
            {key === 'cancelled' && cancelledBookings.map((booking) => (
              <TableRow key={booking.id}>
                <TableCell>{booking.class_name}</TableCell>
                <TableCell>{booking.class_description}</TableCell>
                <TableCell>{formatDateTime(booking.start_datetime)}</TableCell>
                <TableCell>{formatDateTime(booking.booking_datetime)}</TableCell>
                <TableCell>Cancelled</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
}

export default BookingHistory;
