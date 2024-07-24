import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { AppBar, Toolbar, Typography, Button, Box, IconButton, MenuItem, Menu } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import { Link, useLocation } from 'react-router-dom';

export function Navigation() {
  const [userRole, setUserRole] = useState('');
  const [anchorEl, setAnchorEl] = useState(null);
  const [mobileMoreAnchorEl, setMobileMoreAnchorEl] = useState(null);
  const location = useLocation(); // Use the useLocation hook

  const checkAuth = async () => {
    try {
      const response = await axios.get('api/authentication/check-session/', { withCredentials: true });
      const data = response.data;
      if (response.status === 200) {
        setUserRole(data.role);  // Set the user role based on the response
      } else {
        setUserRole('');  // Clear the role if not authenticated
      }
    } catch (error) {
      console.error('Authentication check failed:', error);
      setUserRole('');
    }
  };

  useEffect(() => {
    checkAuth();
  }, [location]); // Run checkAuth whenever the location changes

  const handleMobileMenuOpen = (event) => {
    setMobileMoreAnchorEl(event.currentTarget);
  };

  const handleMobileMenuClose = () => {
    setMobileMoreAnchorEl(null);
  };

  const mobileMenuId = 'primary-search-account-menu-mobile';

  const renderMobileMenu = (
    <Menu
      anchorEl={mobileMoreAnchorEl}
      anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      id={mobileMenuId}
      keepMounted
      transformOrigin={{ vertical: 'top', horizontal: 'right' }}
      open={Boolean(mobileMoreAnchorEl)}
      onClose={handleMobileMenuClose}
    >
      {userRole && (
          <MenuItem key="home" component={Link} to="/">Home</MenuItem>
      )}
      {
        userRole === 'customer' && (
          <>
            <MenuItem key="customer-classes" component={Link} to="/customer-classes">Classes</MenuItem>
            <MenuItem key="bookings" component={Link} to="/bookings">Bookings</MenuItem>
            <MenuItem key="membership" component={Link} to="/purchase-membership">Membership</MenuItem>
            <MenuItem key="purchase-history" component={Link} to="/purchase-history">Purchase History</MenuItem>
            
          </>
        )
      }
      {userRole ? (
        <>
        <MenuItem key="profile" component={Link} to="/profile">Profile</MenuItem>
        <MenuItem key="logout" component={Link} to="/logout">Logout</MenuItem>
        </>
      ) : (
        <>
         {location.pathname === '/login' ? (
           <MenuItem key="signup" component={Link} to="/signup">Sign Up</MenuItem>
  
          ): 
          (          
            <MenuItem key="login" component={Link} to="/login">Login</MenuItem>
          )}

        </>
      )}
    </Menu>
  );

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static" sx={{ backgroundColor: '#5F0F40' }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            <Button component={Link} to="/" sx={{ color: 'white', fontWeight: 'bold' }}>
              Fitopia
            </Button>
          </Typography>
          <Box sx={{ display: { xs: 'none', md: 'flex' } }}>

          {userRole ? (
              <>
                <Button component={Link} to="/" sx={{ color: 'white' }}>
                  Home
                </Button>
      
              </>
              
            ) : [] }
              
            {userRole === 'customer' && (
              <>
                <Button component={Link} to="/customer-classes" sx={{ color: 'white' }}>
                  Classes
                </Button>
                <Button component={Link} to="/bookings" sx={{ color: 'white' }}>
                  Bookings
                </Button>
                <Button component={Link} to="/purchase-membership" sx={{ color: 'white' }}>
                  Membership
                </Button>
                <Button component={Link} to="/purchase-history" sx={{ color: 'white' }}>
                  Purchase History
                </Button>
              </>
            )}            
            {userRole ? (
              <>
                <Button component={Link} to="/profile" sx={{ color: 'white' }}>
                  Profile
                </Button>
                <Button component={Link} to="/logout" sx={{ color: 'white' }}>
                  Logout
                </Button>
              </>
              
            ) : (
              <>
                {location.pathname === '/login' ? (
                  <Button component={Link} to="/signup" sx={{ color: 'white' }}>
                    Sign Up
                  </Button>
                ) : (
                  <Button component={Link} to="/login" sx={{ color: 'white' }}>
                    Login
                  </Button>
                )}
              </>
            )}
          </Box>
          <Box sx={{ display: { xs: 'flex', md: 'none' } }}>
            <IconButton
              edge="end"
              color="inherit"
              aria-label="menu"
              aria-controls={mobileMenuId}
              aria-haspopup="true"
              onClick={handleMobileMenuOpen}
            >
              <MenuIcon />
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>
      {renderMobileMenu}
    </Box>
  );
}
