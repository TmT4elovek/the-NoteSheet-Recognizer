import {BrowserRouter, Routes, Route} from 'react-router-dom'
import LogIn from './templates/login.jsx'
import Register from './templates/register.jsx'


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