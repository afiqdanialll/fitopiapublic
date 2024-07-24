import React, { useState } from 'react';
import { Dialog, DialogActions, DialogContent, DialogTitle, TextField, Button } from '@mui/material';
import axios from "axios";
import Cookies from 'js-cookie';

export function AddStaffForm({ open, onClose, onSubmit }) {
  const [firstName, setFirstName] = useState(''); 
  const [lastName, setLastName] = useState(''); 
  const [email, setEmail] = useState(''); 
  const [errors, setErrors] = useState({});

  const handleSubmit = async () => {
    // Client-side validation
    if (!firstName.trim() || !lastName.trim() || !email.trim()) {
      alert('Please fill out all fields.');
      return;
    }

    const newErrors = validateInputs();
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    // Basic email format validation
    if (!isValidEmail(email)) {
      alert('Please enter a valid email address.');
      return;
    }

    // Create FormData object
    const formData = new FormData();
    formData.append('first_name', firstName);
    formData.append('last_name', lastName); 
    formData.append('username', email); //use email as username
    formData.append('email', email); 

    try {
      // Send FormData as multipart/form-data
      await axios.post('/api/authentication/addStaff/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'X-CSRFToken': Cookies.get('csrftoken')
        }
      });
      alert('Staff added successfully.');
      onSubmit();
      onClose();
    } catch (error) {
      console.error('Error adding staff:', error);
      alert('Failed to add staff. Please try again.');
    }

    // Clear form fields and close dialog
    setFirstName(''); 
    setLastName(''); 
    setEmail(''); 
    onClose();
  };


  const isValidEmail = (email) => {
    // Basic email format validation 
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const validateInputs = () => {
    const errors = {};
    if (!firstName.trim()) {
      errors.firstName = 'First name is required.';
    } else if (/[^a-zA-Z]/.test(firstName)) {
      errors.firstName = 'First name contains invalid characters.';
    }
  
    if (!lastName.trim()) {
      errors.lastName = 'Last name is required.';
    } else if (/[^a-zA-Z]/.test(lastName)) {
      errors.lastName = 'Last name contains invalid characters.';
    }
  
    if (!email.trim()) {
      errors.email = 'Email is required.';
    } else if (!isValidEmail(email)) {
      errors.email = 'Please enter a valid email address.';
    }
  
    return errors;
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>Add New Staff</DialogTitle>
      <DialogContent>
        <TextField
          autoFocus
          margin="dense"
          label="First Name"
          type="text"
          fullWidth
          value={firstName}
          onChange={(e) => setFirstName(e.target.value)}
          error={!!errors.firstName}
          helperText={errors.firstName}
        />
        <TextField
          margin="dense"
          label="Last Name"
          type="text"
          fullWidth
          value={lastName}
          onChange={(e) => setLastName(e.target.value)}
          error={!!errors.lastName}
          helperText={errors.lastName}
        />
        <TextField
          margin="dense"
          label="Email"
          type="text"
          fullWidth
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          error={!!errors.email}
          helperText={errors.email}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="primary">
          Cancel
        </Button>
        <Button onClick={handleSubmit} color="primary">
          Add
        </Button>
      </DialogActions>
    </Dialog>
  );
}
