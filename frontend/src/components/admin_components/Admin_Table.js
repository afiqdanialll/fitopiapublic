import React, { useState, useEffect } from 'react';
import { DataGrid } from '@mui/x-data-grid';
import PropTypes from 'prop-types';
import { Button, Box } from '@mui/material';
import { AddStaffForm } from './Staff_Form';
import axios from "axios";
import Cookies from 'js-cookie';

// Function to handle disabling an account
const toggleAccountStatus = async (id, type, fetchData) => {
  try {
    const response = await axios.post('/api/authentication/toggleAccountStatus/', 
      { id, type },
      {
        headers: {
            'X-CSRFToken': Cookies.get('csrftoken')
        },
      },
      { withCredentials: true }
    );
    if (response.data) {
      alert('Account has been enabled successfully.');
    } else {
      alert('Account has been disabled successfully.');
    }
    fetchData();
  } catch (error) {
    console.error('Error toggling account status:', error);
    alert('Failed to toggle account status. Please try again.');
  }
};

// Function to handle resetting the password
const handleResetPassword = async (id, type) => {
  try {
    await axios.post('/api/authentication/resetPassword/', 
      { id, type },
      {
        headers: {
            'X-CSRFToken': Cookies.get('csrftoken')
        },
      },
      { withCredentials: true }
    );
    alert('Password has been reset successfully');
  } catch (error) {
    console.error('Error resetting password:', error);
    alert('Failed to reset password. Please try again.');
  }
};

const staff_columns = (fetchStaffData) => [
  { field: 'id', headerName: 'ID', width: 70 },
  { field: 'first_name', headerName: 'First Name', width: 170 },
  { field: 'last_name', headerName: 'Last Name', width: 170 },
  { field: 'email', headerName: 'Email', width: 300 },
  {
    field: 'status', headerName: 'Status', width: 100, valueFormatter: (params) => {
      return params ? 'Active' : 'Disabled';
    },
  },
  {
    field: 'actions',
    headerName: 'Actions',
    width: 400,
    renderCell: (params) => (
      <Box>
        {params.row.status ? (
          <Button
            variant="contained"
            color="secondary"
            onClick={() => toggleAccountStatus(params.row.id, 'staff', fetchStaffData)}
            style={{ marginRight: 8 }}
          >
            Disable Account
          </Button>
        ) : (
          <Button
            variant="contained"
            color="primary"
            onClick={() => toggleAccountStatus(params.row.id, 'staff', fetchStaffData)}
            style={{ marginRight: 8 }}
          >
            Enable Account
          </Button>
        )}
        <Button
          variant="contained"
          color="primary"
          onClick={() => handleResetPassword(params.row.id, 'staff')}
        >
          Reset Password
        </Button>
      </Box>
    ),
  },
];

const customer_columns = (fetchCustomerData) => [
  { field: 'id', headerName: 'ID', width: 70 },
  { field: 'first_name', headerName: 'First Name', width: 170 },
  { field: 'last_name', headerName: 'Last Name', width: 170 },
  { field: 'email', headerName: 'Email', width: 300 },
  {
    field: 'status', headerName: 'Status', width: 100, valueFormatter: (params) => {
      return params ? 'Active' : 'Disabled';
    },
  },
  {
    field: 'actions',
    headerName: 'Actions',
    width: 400,
    renderCell: (params) => (
      <Box>
        {params.row.status ? (
          <Button
            variant="contained"
            color="secondary"
            onClick={() => toggleAccountStatus(params.row.id, 'customer', fetchCustomerData)}
            style={{ marginRight: 8 }}
          >
            Disable Account
          </Button>
        ) : (
          <Button
            variant="contained"
            color="primary"
            onClick={() => toggleAccountStatus(params.row.id, 'customer', fetchCustomerData)}
            style={{ marginRight: 8 }}
          >
            Enable Account
          </Button>
        )}
        <Button
          variant="contained"
          color="primary"
          onClick={() => handleResetPassword(params.row.id, 'customer')}
        >
          Reset Password
        </Button>
      </Box>
    ),
  },
];


export function StaffTable() {
  const [staff_rows, setRows] = useState([]);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    // Fetch initial data or load from an API endpoint
    fetchStaffData();
  }, []);


  const fetchStaffData = async () => {
    try {
      const response = await axios.get('/api/authentication/getStaffData/'); // Replace with your API endpoint
      setRows(response.data); // Assuming the API returns an array of staff objects
    } catch (error) {
      console.error('Error fetching staff data:', error);
    }
  };

  const handleOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleAddStaff = () => {
    fetchStaffData();
    setOpen(false);
  };

  return (
    <Box>
      <Button variant="contained" color="primary" onClick={handleOpen}>
        Add New Staff
      </Button>
      <div style={{ height: 400, width: '100%', marginTop: 16 }}>
        <DataGrid rows={staff_rows} columns={staff_columns(fetchStaffData)} pageSize={5} />
      </div>
      <AddStaffForm open={open} onClose={handleClose} onSubmit={handleAddStaff} />
    </Box>
  );
}


export function CustomerTable() {
  const [customer_rows, setRows] = useState([]);

  useEffect(() => {
    // Fetch initial data or load from an API endpoint
    fetchCustomerData();
  }, []);


  const fetchCustomerData = async () => {
    try {
      const response = await axios.get('/api/authentication/getCustomerData/');
      setRows(response.data);
    } catch (error) {
      console.error('Error fetching staff data:', error);
    }
  };

  return (
    <div style={{ height: 400, width: '100%' }}>
      <DataGrid rows={customer_rows} columns={customer_columns(fetchCustomerData)} pageSize={5} />
    </div>
  );
}

export function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

TabPanel.propTypes = {
  children: PropTypes.node,
  index: PropTypes.number.isRequired,
  value: PropTypes.number.isRequired,
};
