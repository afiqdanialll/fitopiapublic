import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Alert, Button, Table, Box, Typography, Grid, TableContainer, TableHead, TableRow, TableCell, TableBody, Paper, IconButton, CircularProgress } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import ClassForm from './ClassForm';
import Cookies from 'js-cookie';

function ClassTable() {
  const [classes, setClasses] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [editClassId, setEditClassId] = useState(null);
  const [successMessage, setSuccessMessage] = useState(false);
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true); 

  useEffect(() => {
    const checkSession = async () => {
      try {
        const response = await axios.get('api/authentication/check-session/', { withCredentials: true });
        const data = response.data;
        if (response.status === 200 && data.role === 'staff') {
          if (data.password_reset) {
            navigate('/user-reset-password');
          } else {
            setLoading(false);
            fetchClasses();
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

  const fetchClasses = async () => {
    try {
      const response = await axios.get('/api/data/classes/');
      setClasses(response.data || []);
    } catch (error) {
      console.error('Error fetching classes:', error);
    }
  };

  const handleShowModal = (id = null) => {
    setEditClassId(id);
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setEditClassId(null);
    setShowModal(false);
    fetchClasses();
  };

  const handleClassDetail = (id) => {
    navigate(`/classes/${id}`);
  };

  const handleDelete = async (id) => {
    try {
      await axios.delete(`/api/data/classes/${id}/`, {
        headers: {
          'X-CSRFToken': Cookies.get('csrftoken')
        },
        withCredentials: true
      });
      setSuccessMessage(true);
      fetchClasses(); 
    } catch (error) {
      console.error('Error deleting class:', error);
    }
  };


  const formatDateTime = (datetime) => {
    // Create a new Date object from the given datetime string
    const date = new Date(datetime);
    
    // Extract the date components
    const day = String(date.getUTCDate()).padStart(2, '0'); // Pad with leading zeros
    const month = String(date.getUTCMonth() + 1).padStart(2, '0'); // Add 1 to month since getMonth() returns 0-11
    const year = date.getUTCFullYear();

    // Extract the time components
    let hours = date.getUTCHours(); // Get the hours in UTC time
    const minutes = String(date.getUTCMinutes()).padStart(2, '0'); // Pad with leading zeros
    const ampm = hours >= 12 ? 'PM' : 'AM'; // Determine whether it is AM or PM
    
    hours = hours % 12; // Convert hours to 12-hour format
    hours = hours ? hours : 12; // Handle the special case of 0

    // Format the datetime string and return it
    return `${day}/${month}/${year}, ${hours}:${minutes} ${ampm}`;
  };

  if (loading) return <CircularProgress />;

  return (
    <Box sx={{ mt: 4, px: 4 }}>
      <Grid container justifyContent="space-between" alignItems="center">
        <Grid item>
          <Typography variant="h4" gutterBottom>
            Classes
          </Typography>
        </Grid>
        <Grid item>
          <Button variant="contained" color="primary" onClick={() => handleShowModal()}>
            Add Class
          </Button>
        </Grid>
      </Grid>
      {successMessage && (
        <Alert
          variant="outlined"
          severity="success"
          sx={{ width: '100%', mt: 5 }}
          action={
            <IconButton
              aria-label="close"
              color="inherit"
              size="small"
              onClick={() => setSuccessMessage(false)}
            >
              <CloseIcon fontSize="inherit" />
            </IconButton>
          }
        >
          Deletion of class successful.
        </Alert>
      )}
      <TableContainer component={Paper} sx={{ mt: 5, p: 3 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Start DateTime</TableCell>
              <TableCell sx={{ textAlign: 'right' }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {classes.map((classItem) => (
              <TableRow key={classItem.id}>
                <TableCell sx={{ fontWeight: 'normal' }}>{classItem.class_name}</TableCell>
                <TableCell sx={{ fontWeight: 'normal' }}>{classItem.description}</TableCell>
                <TableCell sx={{ fontWeight: 'normal' }}>{formatDateTime(classItem.start_datetime)}</TableCell>
                <TableCell sx={{ textAlign: 'right' }}>
                  <Box display="flex" gap={1} justifyContent="flex-end">
                    <Button variant="contained" color="success" onClick={() => handleClassDetail(classItem.id)}>
                      View
                    </Button>
                    <Button variant="contained" color="info" onClick={() => handleShowModal(classItem.id)}>
                      Edit
                    </Button>
                    <Button variant="contained" color="error" onClick={() => handleDelete(classItem.id)}>
                      Delete
                    </Button>
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <ClassForm
        show={showModal}
        handleClose={handleCloseModal}
        refreshClasses={fetchClasses}
        classId={editClassId}
      />
    </Box>
  );
}

export default ClassTable;
