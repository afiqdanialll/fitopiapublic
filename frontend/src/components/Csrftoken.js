import React, { useState, useEffect } from 'react';
import axios from 'axios';

const CSRFToken = () => {
    useEffect(() => {
        const fetchData = async () => {
            try {
                await axios.get('/api/authentication/csrf_cookie/');
            } catch (err) {

            }
        };

        fetchData();
    }, []);
};

export default CSRFToken;