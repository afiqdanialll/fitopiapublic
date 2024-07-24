import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Container, Card, CardContent, Typography, TextField, Button, Box, Grid, CircularProgress, Alert } from '@mui/material';
import Cookies from 'js-cookie';

const ProfilePage = () => {
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState({});
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState({ first_name: '', last_name: '' });
  // Get the navigation function
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);

  const fetchProfile = async () => {
    try {
      const response = await axios.get('/api/data/profile/', {
        withCredentials: true,
        headers: {
          'Content-Type': 'application/json'
        }
      });
      console.log('Profile data fetched:', response.data);
      setProfile(response.data);
      setFormData({ first_name: response.data.first_name, last_name: response.data.last_name });
    } catch (error) {
      console.error('Error fetching profile:', error);
      setError('Failed to load profile information');
    }
  };

  useEffect(() => {
    const checkSession = async () => {
      try {
        const response = await axios.get('api/authentication/check-session/', { withCredentials: true });
        const data = response.data;
        if (response.status === 200) {
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
    fetchProfile();
  }, []);

  const validateInputs = () => {
    let tempErrors = {};
    let isValid = true;
  
    // Validate first name
    if (!formData.first_name.trim()) {
      tempErrors.first_name = "First name is required.";
      isValid = false;
    } else if (/[^a-zA-Z]/.test(formData.first_name)) {
      tempErrors.first_name = "First name contains invalid characters.";
      isValid = false;
    }
  
    // Validate last name
    if (!formData.last_name.trim()) {
      tempErrors.last_name = "Last name is required.";
      isValid = false;
    } else if (/[^a-zA-Z]/.test(formData.last_name)) {
      tempErrors.last_name = "Last name contains invalid characters.";
      isValid = false;
    }
  
    setError(tempErrors);
    return isValid;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };



  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateInputs()) return;

    try {
      console.log("Submitting form with data:", formData);
      const response = await axios.put('/api/data/profile/', formData, {
        withCredentials: true,
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': Cookies.get('csrftoken')
        }
      });
      console.log("Received response:", response.data);
      await fetchProfile();
      setEditMode(false);
    } catch (error) {
      console.error('Error updating profile:', error);
      setError('Failed to update profile information');
    }
  };

  // if (error) return <Typography color="error">{error}</Typography>;
  if (!profile) return <Typography>Loading...</Typography>;
  if (loading) return <CircularProgress />;

  const membership = profile.membership || {
    status: 'Inactive',
    start_date: '-',
    end_date: '-',
    duration: '-'
  };

  return (
    <Container>
      <Box mt={5} display="flex" flexDirection="column" alignItems="center">
        <Box sx={{ textAlign: 'center', mt: 4 }}>
          <Typography variant="h3" gutterBottom>
            Profile Information
          </Typography>
        </Box>
        <Card sx={{ width: '100%', maxWidth: 600 }}>
          <CardContent>
            <Box display="flex" justifyContent="flex-end" mb={2}>
              {!editMode && (
                <Button variant="contained" color="primary" onClick={() => setEditMode(true)}>
                  Edit
                </Button>
              )}
            </Box>
            {editMode ? (
              <Box component="form" onSubmit={handleSubmit}>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="First Name"
                      name="first_name"
                      value={formData.first_name}
                      onChange={handleChange}
                      required
                      error={!!error.first_name}
                      helperText={error.first_name}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Last Name"
                      name="last_name"
                      value={formData.last_name}
                      onChange={handleChange}
                      required
                      error={!!error.last_name}
                      helperText={error.last_name}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Button variant="contained" color="success" type="submit" sx={{ mr: 2 }}>
                      Save
                    </Button>
                    <Button variant="contained" color="secondary" onClick={() => setEditMode(false)}>
                      Cancel
                    </Button>
                  </Grid>
                </Grid>
                {error.general && <Alert severity="error" sx={{ mt: 2 }}>{error.general}</Alert>}
              </Box>
            ) : (
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant="body1">First Name</Typography>
                  <Typography variant="h6">{profile.first_name}</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="body1">Last Name</Typography>
                  <Typography variant="h6">{profile.last_name}</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="body1">Username</Typography>
                  <Typography variant="h6">{profile.username}</Typography>
                </Grid>

                {profile.is_customer && (
                  <>
                    <Grid item xs={12}>
                      <Typography variant="body1">Membership Start Date</Typography>
                      <Typography variant="h6">{membership.start_date === '-' ? '-' : new Date(membership.start_date).toLocaleDateString()}</Typography>
                    </Grid>
                    <Grid item xs={12}>
                      <Typography variant="body1">Membership End Date</Typography>
                      <Typography variant="h6">{membership.end_date === '-' ? '-' : new Date(membership.end_date).toLocaleDateString()}</Typography>
                    </Grid>
                    <Grid item xs={12}>
                      <Typography variant="body1">Membership Duration</Typography>
                      <Typography variant="h6">{membership.duration}</Typography>
                    </Grid>
                    <Grid item xs={12}>
                      <Typography variant="body1">Membership Status</Typography>
                      <Typography variant="h6">{membership.status}</Typography>
                    </Grid>
                  </>
                )}
                <Grid item xs={12}>
                  <Typography variant="body1">Account Created On</Typography>
                  <Typography variant="h6">{new Date(profile.date_joined).toLocaleDateString()}</Typography>
                </Grid>
              </Grid>
            )}
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
};

export default ProfilePage;
