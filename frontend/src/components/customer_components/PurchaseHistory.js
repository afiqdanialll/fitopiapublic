import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  Box,
  Container,
  Typography,
  TableContainer,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Paper,
  CircularProgress,
} from '@mui/material';

const PurchaseHistory = () => {
  const navigate = useNavigate();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkSession = async () => {
      try {
        const response = await axios.get('api/authentication/check-session/', { withCredentials: true });
        const data = response.data;
        if (response.status === 200 && data.role === 'customer') {
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

    const fetchHistory = async () => {
      try {
        const { data } = await axios.get('/api/data/purchase-history/');
        console.log("Received history data:", data);
        setHistory(data);
      } catch (error) {
        console.error('Failed to fetch purchase history:', error);
      }
    };

    checkSession();
    fetchHistory();
  }, []);

  if (loading) return <CircularProgress />;
  
  return (
    <Container sx={{ mt: 5 }}>
      <Box sx={{ textAlign: 'center', mt: 4 }}>
                <Typography variant="h3" gutterBottom>
                Purchase History
                </Typography>
            </Box>
      <TableContainer component={Paper} sx={{ mt: 4 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>No.</TableCell>
              <TableCell>Membership Type</TableCell>
              <TableCell>Price</TableCell>
              <TableCell>Purchase Date</TableCell>
              <TableCell>Expiry Date</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {history.length > 0 ? (
              history.map((item, index) => (
                <TableRow key={index}>
                  <TableCell>{index + 1}</TableCell>
                  <TableCell>{item.membership_type} month(s)</TableCell>
                  <TableCell>{item.amount}</TableCell>
                  <TableCell>{new Date(item.purchase_datetime).toLocaleDateString()}</TableCell>
                  <TableCell>{new Date(item.expiry_date).toLocaleDateString()}</TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  You have no past transactions.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
};

export default PurchaseHistory;
