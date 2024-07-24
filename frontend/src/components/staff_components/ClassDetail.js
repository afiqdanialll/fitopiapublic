import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import { Alert, IconButton, Card, CardContent, CardActions, Button, Container, Typography, Box, Grid, Divider, Dialog, DialogTitle, DialogContent, DialogActions, CircularProgress, List, ListItem, ListItemText } from '@mui/material';
import ClassForm from './ClassForm';
import Cookies from 'js-cookie';
import CloseIcon from '@mui/icons-material/Close';

function ClassDetail() {
  const { id } = useParams();
  const [classDetail, setClassDetail] = useState({});
  const [customerName, setCustomerName] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [open, setOpen] = useState(false);
  const [successMessage, setSuccessMessage] = useState(false);
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
        if (response.status === 200 && data.role === 'staff') {
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

  useEffect(() => {
    axios.get(`/api/data/classes/${id}/`)
      .then(response => {
        setClassDetail(response.data);
        axios.get(`/api/data/classes/${id}/customers/`)
          .then(res => {
            setCustomerName(res.data);
          })
          .catch(err => {
            console.error(err);
          });
      })
      .catch(error => {
        console.error(error);
        navigate('/');
      });
  }, [id]);

  const handleDelete = () => {
    axios.delete(`/api/data/classes/${id}/`, {
      headers: {
        'X-CSRFToken': Cookies.get('csrftoken')
      },
      withCredentials: true
    })
      .then(response => {
        setSuccessMessage(true);
        setTimeout(() => {
          navigate('/staff');
        }, 1500); 
      })
      .catch(error => {
        console.error(error);
      });
  };

  const handleEdit = () => {
    setShowForm(true);
  };

  const handleCloseForm = () => {
    setShowForm(false);
  };

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  if (loading) return <CircularProgress />;

  return (
    <Container sx={{ mt: 4 }}>
      <Box display="flex" justifyContent="center">
        <Card sx={{ maxWidth: 600, width: '100%' }}>
          <CardContent>
            <Box textAlign="center">
              <Typography variant="h3" component="div" gutterBottom>
                {classDetail.class_name}
              </Typography>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                {classDetail.description}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                Start DateTime: {formatDateTime(classDetail.start_datetime)}
              </Typography>
              <Divider sx={{ my: 2 }} />
            </Box>
          </CardContent>
          <CardActions sx={{ justifyContent: 'center', pb: 2 }}>
            <Grid container spacing={2} justifyContent="center">
              <Grid item>
                <Button variant="contained" color="primary" onClick={handleClickOpen}>
                  View Attendees
                </Button>
              </Grid>
              <Grid item>
                <Button variant="contained" color="info" onClick={handleEdit}>
                  Edit Class
                </Button>
              </Grid>
              <Grid item>
                <Button variant="contained" color="error" onClick={handleDelete}>
                  Delete Class
                </Button>
              </Grid>
            </Grid>
          </CardActions>
        </Card>
      </Box>
      {successMessage && (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', mt: 2 }}>
          <Alert
            variant="outlined"
            severity="success"
            sx={{ maxWidth: 600, width: '100%', textAlign: 'center' }}
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
            Deletion of class successful! Redirecting...
          </Alert>
        </Box>
      )}
      {showForm && (
        <ClassForm
          show={showForm}
          handleClose={handleCloseForm}
          refreshClasses={() => window.location.reload()}
          classId={id}
        />
      )}
      <Dialog open={open} onClose={handleClose} fullWidth maxWidth="sm">
        <DialogTitle>Attending Customers</DialogTitle>
        <DialogContent>
          <List>
            {customerName && customerName.map((first_name, index) => (
              <ListItem key={index}>
                <ListItemText primary={first_name} />
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} color="primary">
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}

export default ClassDetail;
