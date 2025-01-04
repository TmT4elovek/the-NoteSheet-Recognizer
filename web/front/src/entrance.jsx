import {BrowserRouter, Routes, Route} from 'react-router-dom'
import LogIn from './login.jsx'
import Register from './register.jsx'


function Entrance() {
    return (
        <BrowserRouter>
            <Routes>
                <Route exact path="/login" element={<LogIn />} />
                <Route exact path="/register" element={<Register />} />
            </Routes>
        </BrowserRouter>
    )
}

export default Entrance 