import { useEffect, useState } from "react";
import { useNavigate } from 'react-router-dom';
import axios from "axios";
import Cookies from 'js-cookie';

export const Home = () => {
  const navigate = useNavigate();
    const [message, setMessage] = useState('');

    useEffect(() => {
      const checkSession = async () => {
        try {
          const response = await axios.get('api/authentication/check-session/', { withCredentials: true });
          const data = response.data;

          if (response.status === 200) {
            if (data.role === 'admin') {
              navigate('/admin');
            } else if (data.role === 'customer') {
              navigate('/cust');
            } else if (data.role === 'staff') {
              navigate('/staff');
            } else {
              navigate('/login');
            }
          } else {
            navigate('/login');
          }
        } catch (error) {
          navigate('/login');
        }
      };
  
      checkSession();
    }, []);

    return (
      <div className="form-signin mt-5 text-center">
        <h3>{message}</h3>
      </div>
    );
};
