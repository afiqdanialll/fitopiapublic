// App.js
import React from "react";
import 'bootstrap/dist/css/bootstrap.min.css';
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import { Home } from "./components/Home";
import { Signup } from "./components/Signup";
import { Login } from "./components/Login";
import { Navigation } from './components/Navigation';
import { Logout } from './components/Logout';
import { AdminPage } from './components/AdminPage';
import CustomerClassTable from './components/customer_components/CustomerClassTable';
import CustomerClassDetail from './components/customer_components/CustomerClassDetail';
import BookingHistory from './components/customer_components/CustomerBookingHistory';
import axios from "axios";
import StaffPage from './components/StaffPage';
import ClassDetail from './components/staff_components/ClassDetail';
import { TwoFactor } from "./components/Twofactor";
import { UserResetPassword } from "./components/UserResetPassword";
import { CustPage } from "./components/CustPage";
import ProfilePage from "./components/ProfilePage";
import MembershipPurchase from './components/customer_components/MembershipPurchase';
import Payment from './components/customer_components/Payment';
import PurchaseHistory from './components/customer_components/PurchaseHistory';
import { ThemeProvider, CssBaseline } from '@mui/material';
import theme from './styles/theme';
import ErrorPage from './components/ErrorPage';

// Testing with your ip address, change to your own ip address, uncomment this during testing
// axios.defaults.baseURL = "http://ipaddresshere:8000"


// Comment this out during testing
if (window.location.origin === "http://localhost:3000" || window.location.origin === "http://127.0.0.1:3000") {
  axios.defaults.baseURL = "http://localhost:8000";
} else {
  axios.defaults.baseURL = window.location.origin;
}

axios.defaults.withCredentials = true;

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Navigation />
        <Routes>
          <Route exact path="/" element={<Home />} />
          <Route path="signup" element={<Signup />} />
          <Route path="login" element={<Login />} />
          <Route path="logout" element={<Logout />} />
          <Route path="cust" element={<CustPage />} />
          <Route path="admin" element={<AdminPage />} />
          <Route path="staff" element={<StaffPage />} />
          <Route path="classes/:id" element={<ClassDetail />} />
          <Route path="/customer-classes" element={<CustomerClassTable />} />
          <Route path="/customer-classes/:id" element={<CustomerClassDetail />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/bookings" element={<BookingHistory />} />
          <Route path="/Twofactor" element={<TwoFactor />} />
          <Route path="/user-reset-password" element={<UserResetPassword />} />
          <Route path="/purchase-membership" element={<MembershipPurchase />} />
          <Route path="/payment" element={<Payment />} />
          <Route path="/purchase-history" element={<PurchaseHistory />} />
          <Route path="*" element={<ErrorPage />} /> {/* Catch-all route */}
        </Routes>
      </Router>
    </ThemeProvider>
  );
}
