import { useEffect, useState } from "react"
import axios from "axios";
import { useNavigate } from 'react-router-dom';

export const Logout = () => {
  const navigate = useNavigate();
    useEffect(() => {
        const logout = async () => {
          try {
            const response = await axios.post('api/authentication/logout/', { withCredentials: true });
            if (response.status === 200) {
                navigate('/login');
            } 
          } catch (error) {
            console.log('logout not working', error)
          }
        };
    
        logout();
      }, []);

    return (
        <div></div>
    )
}
