import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useEffect } from 'react';

const RegisterUpl = () => {
    // const [selectedFile, setSelectedFile] = useState(null);

    // const handleFileChange = (event) => {
    //     setSelectedFile(event.target.files[0]);
    // };

    const handleSubmit = async (event) => {
        event.preventDefault();
        
        regUserData = {
            name: event.target.username.value,
            password: event.target.password.value
        };
        const navigate = useNavigate();
        
        useEffect(() => {
            axios.post('http://127.0.0.1:8000/api/add-user', regUserData) //! невероно отправляются данные
            .then((response) => {
            console.log(response);
            // navigate('/login');
        })
        })
        
    };
};

export default RegisterUpl