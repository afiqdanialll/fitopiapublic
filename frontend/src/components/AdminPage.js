import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import Box from '@mui/material/Box';
import CircularProgress from '@mui/material/CircularProgress';
import { StaffTable, CustomerTable, TabPanel } from './admin_components/Admin_Table';
import axios from "axios";

export function AdminPage() {
  const navigate = useNavigate();
  const [value, setValue] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkSession = async () => {
      try {
        const response = await axios.get('api/authentication/check-session/', { withCredentials: true });
        const data = response.data;
        if (response.status === 200 && data.role === 'admin') {
          setLoading(false); // Set loading to false if session is valid
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

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  return (
    <Box sx={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider', width: '100%', display: 'flex', justifyContent: 'center' }}>
        <Tabs value={value} onChange={handleChange} aria-label="admin tabs" centered>
          <Tab label="Staff" />
          <Tab label="Customer" />
        </Tabs>
      </Box>
      <Box sx={{ width: '100%', mt: 2 }}>
        <TabPanel value={value} index={0}>
          <StaffTable />
        </TabPanel>
        <TabPanel value={value} index={1}>
          <CustomerTable />
        </TabPanel>
      </Box>
    </Box>
  );
}
