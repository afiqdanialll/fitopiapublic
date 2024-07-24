import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Modal, Box, TextField, Button, Typography, CircularProgress } from '@mui/material';
import Cookies from 'js-cookie';

function ClassForm({ show, handleClose, refreshClasses, classId }) {
  const navigate = useNavigate();
  const [className, setClassName] = useState('');
  const [description, setDescription] = useState('');
  const [startDatetime, setStartDatetime] = useState('');
  const [createdBy, setCreatedBy] = useState('');
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(true); 

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
  }, []);
  
  useEffect(() => {
    if (classId && show) {
      axios.get(`/api/data/classes/${classId}/`)
        .then(response => {
          const { class_name, description, start_datetime, created_by } = response.data;
          setClassName(class_name);
          setDescription(description);
          setStartDatetime(start_datetime.slice(0, 16));
          setCreatedBy(created_by);
        })
        .catch(error => console.error('Error fetching class data:', error));
    } else if (show) {
      resetForm();
    }
  }, [classId, show]);

  const resetForm = () => {
    setClassName('');
    setDescription('');
    setStartDatetime('');
    setCreatedBy('');
    setErrors({});
  };

  const validateInputs = () => {
    let tempErrors = {};
    let isValid = true;

    if (!className.trim()) {
      tempErrors.className = "Class name is required.";
      isValid = false;
    } else if (/[^a-zA-Z0-9 .,]/g.test(className)) {
      tempErrors.className = "Class name contains invalid characters.";
      isValid = false;
    }

    if (!description.trim()) {
      tempErrors.description = "Description is required.";
      isValid = false;
    } else if (/[^a-zA-Z0-9 .,]/g.test(description)) {
      tempErrors.description = "Description contains invalid characters.";
      isValid = false;
    }

    if (!startDatetime) {
      tempErrors.startDatetime = "Start datetime is required.";
      isValid = false;
    } else if (!isValidFutureDate(startDatetime)) {
      tempErrors.startDatetime = "Datetime must be in the future (format: YYYY-MM-DDTHH:MM).";
      isValid = false;
    }

    setErrors(tempErrors);
    return isValid;
  };

  const isValidFutureDate = (dateStr) => {
    const inputDate = new Date(dateStr);
    const now = new Date();
    return inputDate > now;
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!validateInputs()) return;

    const classData = {
      class_name: className.trim(),
      description: description.trim(),
      start_datetime: startDatetime,
      created_by: createdBy 
    };

    const method = classId ? 'put' : 'post';
    const url = classId ? `/api/data/classes/${classId}/` : '/api/data/classes/';

    axios({
      method: method,
      url: url,
      data: classData,
      headers: {
        'X-CSRFToken': Cookies.get('csrftoken')
      },
      withCredentials: true
    })
    .then(response => {
      refreshClasses();
      handleClose();
    })
    .catch(error => {
      console.error('Error updating/creating class:', error);
      alert('An error occurred. Please try again.');
    });
  };

  if (loading) return <CircularProgress />;

  return (
    <Modal open={show} onClose={handleClose}>
      <Box sx={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        width: 400,
        bgcolor: 'background.paper',
        border: '2px solid #000',
        boxShadow: 24,
        p: 4,
      }}>
        <Typography variant="h6" component="h2">
          {classId ? 'Edit Class' : 'Create Class'}
        </Typography>
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
          <TextField
            fullWidth
            margin="normal"
            label="Class Name"
            value={className}
            onChange={e => setClassName(e.target.value)}
            required
            error={!!errors.className}
            helperText={errors.className}
          />
          <TextField
            fullWidth
            margin="normal"
            label="Description"
            value={description}
            onChange={e => setDescription(e.target.value)}
            required
            error={!!errors.description}
            helperText={errors.description}
          />
          <TextField
            fullWidth
            margin="normal"
            label="Start Datetime"
            type="datetime-local"
            value={startDatetime}
            onChange={e => setStartDatetime(e.target.value)}
            required
            InputLabelProps={{ shrink: true }}
            error={!!errors.startDatetime}
            helperText={errors.startDatetime}
          />
          <Button type="submit" variant="contained" color="primary" sx={{ mt: 2 }}>
            {classId ? 'Update Class' : 'Create Class'}
          </Button>
        </Box>
      </Box>
    </Modal>
  );
}

export default ClassForm;
